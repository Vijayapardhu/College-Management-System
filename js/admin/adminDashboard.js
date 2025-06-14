 // Admin Dashboard Functions
function loadAdminDashboard() {
    const dashboardHTML = `
        <div class="admin-dashboard">
            <div class="admin-header">
                <h2>Admin Dashboard</h2>
                <div class="quick-actions">
                    <button onclick="showAddUserModal()">Add New User</button>
                    <button onclick="showBulkUploadModal()">Bulk Upload</button>
                </div>
            </div>
            
            <div class="admin-content">
                <div class="users-section">
                    <div class="filters">
                        <select id="roleFilter" onchange="filterUsers()">
                            <option value="">All Roles</option>
                            <option value="student">Students</option>
                            <option value="faculty">Faculty</option>
                            <option value="admin">Admins</option>
                        </select>
                        <select id="deptFilter" onchange="filterUsers()">
                            <option value="">All Departments</option>
                        </select>
                        <input type="text" id="searchUser" placeholder="Search users..." onkeyup="filterUsers()">
                    </div>
                    
                    <div class="users-table">
                        <table>
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
            </div>
        </div>

        <!-- Add User Modal -->
        <div id="addUserModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('addUserModal')">&times;</span>
                <h3>Add New User</h3>
                <form id="addUserForm" onsubmit="return handleAddUser(event)">
                    <div class="form-group">
                        <label for="userRole">Role*</label>
                        <select id="userRole" required onchange="toggleRoleSpecificFields()">
                            <option value="">Select Role</option>
                            <option value="student">Student</option>
                            <option value="faculty">Faculty</option>
                            <option value="admin">Admin</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="userId">User ID*</label>
                        <input type="text" id="userId" required>
                        <small>For students: 20XX[Dept]XX, Faculty: FACXXX, Admin: ADMXXX</small>
                    </div>

                    <div class="form-group">
                        <label for="fullName">Full Name*</label>
                        <input type="text" id="fullName" required>
                    </div>

                    <div class="form-group">
                        <label for="department">Department*</label>
                        <select id="department" required>
                            <option value="">Select Department</option>
                            <option value="CSE">Computer Science</option>
                            <option value="ECE">Electronics</option>
                            <option value="ME">Mechanical</option>
                            <option value="CE">Civil</option>
                        </select>
                    </div>

                    <!-- Student Specific Fields -->
                    <div id="studentFields" style="display: none;">
                        <div class="form-group">
                            <label for="currentYear">Current Year*</label>
                            <select id="currentYear">
                                <option value="1">First Year</option>
                                <option value="2">Second Year</option>
                                <option value="3">Third Year</option>
                                <option value="4">Fourth Year</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="section">Section*</label>
                            <input type="text" id="section">
                        </div>
                        <div class="form-group">
                            <label for="parentName">Parent Name*</label>
                            <input type="text" id="parentName">
                        </div>
                        <div class="form-group">
                            <label for="parentContact">Parent Contact*</label>
                            <input type="tel" id="parentContact">
                        </div>
                    </div>

                    <!-- Faculty Specific Fields -->
                    <div id="facultyFields" style="display: none;">
                        <div class="form-group">
                            <label for="designation">Designation*</label>
                            <input type="text" id="designation">
                        </div>
                        <div class="form-group">
                            <label for="qualification">Qualification*</label>
                            <input type="text" id="qualification">
                        </div>
                        <div class="form-group">
                            <label for="specialization">Specialization</label>
                            <input type="text" id="specialization">
                        </div>
                        <div class="form-group">
                            <label for="experience">Experience</label>
                            <input type="text" id="experience">
                        </div>
                    </div>

                    <!-- Admin Specific Fields -->
                    <div id="adminFields" style="display: none;">
                        <div class="form-group">
                            <label for="adminDesignation">Designation*</label>
                            <input type="text" id="adminDesignation">
                        </div>
                        <div class="form-group">
                            <label for="permissions">Permissions</label>
                            <select id="permissions" multiple>
                                <option value="user_management">User Management</option>
                                <option value="course_management">Course Management</option>
                                <option value="system_settings">System Settings</option>
                            </select>
                        </div>
                    </div>

                    <button type="submit">Create User</button>
                </form>
            </div>
        </div>

        <!-- Bulk Upload Modal -->
        <div id="bulkUploadModal" class="modal">
            <div class="modal-content">
                <span class="close" onclick="closeModal('bulkUploadModal')">&times;</span>
                <h3>Bulk Upload Users</h3>
                <form id="bulkUploadForm" onsubmit="return handleBulkUpload(event)">
                    <div class="form-group">
                        <label for="userRole">Role*</label>
                        <select id="bulkUserRole" required>
                            <option value="">Select Role</option>
                            <option value="student">Student</option>
                            <option value="faculty">Faculty</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="csvFile">Upload CSV File*</label>
                        <input type="file" id="csvFile" accept=".csv" required>
                        <small>Download template: 
                            <a href="#" onclick="downloadTemplate('student')">Student Template</a> | 
                            <a href="#" onclick="downloadTemplate('faculty')">Faculty Template</a>
                        </small>
                    </div>
                    <button type="submit">Upload</button>
                </form>
            </div>
        </div>
    `;
    
    document.getElementById('mainContent').innerHTML = dashboardHTML;
    loadUsers();
    loadDepartments();
}

// Toggle role-specific fields in the add user form
function toggleRoleSpecificFields() {
    const role = document.getElementById('userRole').value;
    document.getElementById('studentFields').style.display = role === 'student' ? 'block' : 'none';
    document.getElementById('facultyFields').style.display = role === 'faculty' ? 'block' : 'none';
    document.getElementById('adminFields').style.display = role === 'admin' ? 'block' : 'none';
}

// Handle adding a new user
async function handleAddUser(event) {
    event.preventDefault();
    showLoading();

    try {
        const role = document.getElementById('userRole').value;
        const userId = document.getElementById('userId').value;
        const email = `${userId}@cms.edu`;

        // Create base user data
        const userData = {
            userId: userId,
            email: email,
            fullName: document.getElementById('fullName').value,
            role: role,
            department: document.getElementById('department').value,
            status: 'active',
            createdAt: new Date().toISOString()
        };

        // Add role-specific data
        switch(role) {
            case 'student':
                Object.assign(userData, {
                    currentYear: document.getElementById('currentYear').value,
                    section: document.getElementById('section').value,
                    parentName: document.getElementById('parentName').value,
                    parentContact: document.getElementById('parentContact').value,
                    rollNumber: userId
                });
                break;

            case 'faculty':
                Object.assign(userData, {
                    designation: document.getElementById('designation').value,
                    qualification: document.getElementById('qualification').value,
                    specialization: document.getElementById('specialization').value,
                    experience: document.getElementById('experience').value,
                    employeeId: userId
                });
                break;

            case 'admin':
                Object.assign(userData, {
                    designation: document.getElementById('adminDesignation').value,
                    permissions: Array.from(document.getElementById('permissions').selectedOptions).map(option => option.value),
                    employeeId: userId
                });
                break;
        }

        // Create authentication user
        const userCredential = await auth.createUserWithEmailAndPassword(email, 'eduvision');
        
        // Store user data in Firestore
        await db.collection('users').doc(userCredential.user.uid).set(userData);

        // Log activity
        await logAdminActivity('User Creation', `Created new ${role}: ${userId}`);

        hideLoading();
        showSuccess('User created successfully');
        closeModal('addUserModal');
        loadUsers();

    } catch (error) {
        hideLoading();
        showError('Error creating user: ' + error.message);
    }
}

// Handle bulk upload
async function handleBulkUpload(event) {
    event.preventDefault();
    showLoading();

    try {
        const file = document.getElementById('csvFile').files[0];
        const role = document.getElementById('bulkUserRole').value;

        const reader = new FileReader();
        reader.onload = async function(e) {
            const text = e.target.result;
            const rows = text.split('\n');
            
            // Skip header row
            for(let i = 1; i < rows.length; i++) {
                if(!rows[i].trim()) continue;
                
                const columns = rows[i].split(',');
                const userId = columns[0].trim();
                const email = `${userId}@cms.edu`;

                try {
                    // Create user data based on role
                    const userData = role === 'student' ? 
                        createStudentData(columns) : 
                        createFacultyData(columns);

                    // Create authentication user
                    const userCredential = await auth.createUserWithEmailAndPassword(email, 'eduvision');
                    
                    // Store user data
                    await db.collection('users').doc(userCredential.user.uid).set(userData);
                    
                } catch (error) {
                    console.error(`Error processing row ${i + 1}:`, error);
                }
            }

            hideLoading();
            showSuccess('Bulk upload completed');
            closeModal('bulkUploadModal');
            loadUsers();
        };

        reader.readAsText(file);

    } catch (error) {
        hideLoading();
        showError('Error in bulk upload: ' + error.message);
    }
}

// Helper function to create student data from CSV
function createStudentData(columns) {
    return {
        userId: columns[0].trim(),
        fullName: columns[1].trim(),
        role: 'student',
        department: columns[2].trim(),
        currentYear: columns[3].trim(),
        section: columns[4].trim(),
        parentName: columns[5].trim(),
        parentContact: columns[6].trim(),
        email: `${columns[0].trim()}@cms.edu`,
        status: 'active',
        createdAt: new Date().toISOString(),
        rollNumber: columns[0].trim()
    };
}

// Helper function to create faculty data from CSV
function createFacultyData(columns) {
    return {
        userId: columns[0].trim(),
        fullName: columns[1].trim(),
        role: 'faculty',
        department: columns[2].trim(),
        designation: columns[3].trim(),
        qualification: columns[4].trim(),
        specialization: columns[5].trim(),
        experience: columns[6].trim(),
        email: `${columns[0].trim()}@cms.edu`,
        status: 'active',
        createdAt: new Date().toISOString(),
        employeeId: columns[0].trim()
    };
}

// Download CSV template
function downloadTemplate(role) {
    let headers = '';
    if(role === 'student') {
        headers = 'UserID,FullName,Department,CurrentYear,Section,ParentName,ParentContact\n';
        headers += '20CSE01,John Doe,CSE,1,A,Parent Name,1234567890';
    } else {
        headers = 'UserID,FullName,Department,Designation,Qualification,Specialization,Experience\n';
        headers += 'FAC001,Dr. John Doe,CSE,Assistant Professor,Ph.D,AI/ML,5 years';
    }

    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(headers));
    element.setAttribute('download', `${role}_template.csv`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Modal functions
function showAddUserModal() {
    document.getElementById('addUserModal').style.display = 'block';
}

function showBulkUploadModal() {
    document.getElementById('bulkUploadModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Load existing users
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
                    <td>${userData.department}</td>
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
        showError('Error loading users: ' + error.message);
    }
}

// Log admin activity
async function logAdminActivity(action, description) {
    try {
        await db.collection('admin_logs').add({
            adminId: auth.currentUser.uid,
            action: action,
            description: description,
            timestamp: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error logging activity:', error);
    }
}