 // Load admin dashboard
function loadAdminDashboard() {
    const dashboardHTML = `
        <div class="dashboard-grid">
            <div class="dashboard-card stats-card">
                <h3>System Overview</h3>
                <div id="systemStats"></div>
            </div>
            
            <div class="dashboard-card quick-actions">
                <h3>Quick Actions</h3>
                <button onclick="showAddUserModal()">Add New User</button>
                <button onclick="showAddDepartmentModal()">Add Department</button>
                <button onclick="showBulkUploadModal()">Bulk Upload Users</button>
            </div>
            
            <div class="dashboard-card recent-activities">
                <h3>Recent Activities</h3>
                <div id="recentActivities"></div>
            </div>
        </div>
    `;
    
    dashboardSection.innerHTML = dashboardHTML;
    loadSystemStats();
    loadRecentActivities();
}

// Load user management section
function loadUserManagement() {
    const userManagementHTML = `
        <div class="user-management">
            <div class="filters">
                <select id="roleFilter">
                    <option value="">All Roles</option>
                    <option value="student">Students</option>
                    <option value="faculty">Faculty</option>
                    <option value="admin">Admins</option>
                </select>
                <select id="departmentFilter">
                    <option value="">All Departments</option>
                </select>
                <input type="text" id="searchUser" placeholder="Search users...">
            </div>
            
            <div class="users-table-container">
                <table id="usersTable">
                    <thead>
                        <tr>
                            <th>User ID</th>
                            <th>Name</th>
                            <th>Role</th>
                            <th>Department</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="usersTableBody"></tbody>
                </table>
            </div>
        </div>
    `;
    
    dashboardSection.innerHTML = userManagementHTML;
    loadUsers();
    setupFilters();
}

// Add new user
async function addNewUser(userData) {
    try {
        showLoading();
        
        // Create email from userId
        const email = `${userData.userId}@cms.edu`;
        
        // Create auth user with default password
        const userCredential = await auth.createUserWithEmailAndPassword(email, 'eduvision');
        const uid = userCredential.user.uid;
        
        // Add user data to Firestore
        await db.collection('users').doc(uid).set({
            ...userData,
            email: email,
            createdAt: new Date().toISOString(),
            status: 'active'
        });
        
        // Log activity
        await logActivity('User created', `New ${userData.role} added: ${userData.fullName}`);
        
        hideLoading();
        alert('User created successfully');
        loadUsers();
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Bulk upload users
async function bulkUploadUsers(file) {
    try {
        showLoading();
        
        const reader = new FileReader();
        reader.onload = async function(e) {
            const text = e.target.result;
            const rows = text.split('\n');
            
            // Skip header row
            for(let i = 1; i < rows.length; i++) {
                const [userId, fullName, role, department] = rows[i].split(',');
                
                if(userId && fullName && role) {
                    const userData = {
                        userId: userId.trim(),
                        fullName: fullName.trim(),
                        role: role.trim().toLowerCase(),
                        department: department ? department.trim() : null
                    };
                    
                    await addNewUser(userData);
                }
            }
            
            hideLoading();
            alert('Bulk upload completed');
            loadUsers();
        };
        
        reader.readAsText(file);
    } catch (error) {
        hideLoading();
        showError(error.message);
    }
}

// Load and display users
async function loadUsers() {
    try {
        const usersSnapshot = await db.collection('users').get();
        const tableBody = document.getElementById('usersTableBody');
        tableBody.innerHTML = '';
        
        usersSnapshot.forEach(doc => {
            const userData = doc.data();
            const row = `
                <tr>
                    <td>${userData.userId}</td>
                    <td>${userData.fullName}</td>
                    <td>${userData.role}</td>
                    <td>${userData.department || '-'}</td>
                    <td>${userData.status}</td>
                    <td>
                        <button onclick="editUser('${doc.id}')">Edit</button>
                        <button onclick="toggleUserStatus('${doc.id}', '${userData.status}')">
                            ${userData.status === 'active' ? 'Deactivate' : 'Activate'}
                        </button>
                        <button onclick="resetPassword('${doc.id}')">Reset Password</button>
                    </td>
                </tr>
            `;
            tableBody.innerHTML += row;
        });
    } catch (error) {
        showError(error.message);
    }
}

// Toggle user status
async function toggleUserStatus(userId, currentStatus) {
    try {
        const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
        await db.collection('users').doc(userId).update({
            status: newStatus
        });
        
        await logActivity('User status changed', `User ${userId} ${newStatus}`);
        loadUsers();
    } catch (error) {
        showError(error.message);
    }
}

// Reset user password
async function resetPassword(userId) {
    try {
        const userDoc = await db.collection('users').doc(userId).get();
        const userData = userDoc.data();
        
        // Reset password to default
        const user = await auth.getUserByEmail(userData.email);
        await auth.updatePassword(user, 'eduvision');
        
        await logActivity('Password reset', `Password reset for user ${userData.userId}`);
        alert('Password reset to default: eduvision');
    } catch (error) {
        showError(error.message);
    }
}

// Log admin activity
async function logActivity(action, description) {
    try {
        await db.collection('admin_logs').add({
            action: action,
            description: description,
            adminId: auth.currentUser.uid,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error logging activity:', error);
    }
}

// Load system statistics
async function loadSystemStats() {
    try {
        const stats = {
            totalStudents: 0,
            totalFaculty: 0,
            totalDepartments: 0,
            activeUsers: 0
        };
        
        // Get user counts
        const usersSnapshot = await db.collection('users').get();
        usersSnapshot.forEach(doc => {
            const userData = doc.data();
            if(userData.role === 'student') stats.totalStudents++;
            if(userData.role === 'faculty') stats.totalFaculty++;
            if(userData.status === 'active') stats.activeUsers++;
        });
        
        // Get department count
        const deptsSnapshot = await db.collection('departments').get();
        stats.totalDepartments = deptsSnapshot.size;
        
        // Display stats
        document.getElementById('systemStats').innerHTML = `
            <div class="stats-grid">
                <div class="stat-item">
                    <h4>Total Students</h4>
                    <p>${stats.totalStudents}</p>
                </div>
                <div class="stat-item">
                    <h4>Total Faculty</h4>
                    <p>${stats.totalFaculty}</p>
                </div>
                <div class="stat-item">
                    <h4>Departments</h4>
                    <p>${stats.totalDepartments}</p>
                </div>
                <div class="stat-item">
                    <h4>Active Users</h4>
                    <p>${stats.activeUsers}</p>
                </div>
            </div>
        `;
    } catch (error) {
        showError(error.message);
    }
}

// Load recent activities
async function loadRecentActivities() {
    try {
        const logsSnapshot = await db.collection('admin_logs')
            .orderBy('timestamp', 'desc')
            .limit(10)
            .get();
            
        const activitiesList = document.getElementById('recentActivities');
        activitiesList.innerHTML = '';
        
        logsSnapshot.forEach(doc => {
            const log = doc.data();
            const date = new Date(log.timestamp).toLocaleString();
            
            activitiesList.innerHTML += `
                <div class="activity-item">
                    <span class="activity-time">${date}</span>
                    <span class="activity-action">${log.action}</span>
                    <p class="activity-description">${log.description}</p>
                </div>
            `;
        });
    } catch (error) {
        showError(error.message);
    }
}