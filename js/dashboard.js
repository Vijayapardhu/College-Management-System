// Dashboard loading functions
function loadStudentDashboard() {
    const dashboardHTML = `
        <div class="dashboard-grid">
            <div class="dashboard-card attendance-card">
                <h3><i class="material-icons">timeline</i>Attendance Overview</h3>
                <canvas id="attendanceChart"></canvas>
                <div class="attendance-stats">
                    <div class="stat-item">
                        <div class="value" id="overallAttendance">--%</div>
                        <div class="label">Overall</div>
                    </div>
                    <div class="stat-item">
                        <div class="value" id="monthlyAttendance">--%</div>
                        <div class="label">This Month</div>
                    </div>
                    <div class="stat-item">
                        <div class="value" id="weeklyAttendance">--%</div>
                        <div class="label">This Week</div>
                    </div>
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3><i class="material-icons">schedule</i>Upcoming Classes</h3>
                <div class="upcoming-classes" id="upcomingClasses">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3><i class="material-icons">grade</i>Recent Marks</h3>
                <div class="marks-list" id="recentMarks">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3><i class="material-icons">assignment</i>Pending Assignments</h3>
                <div class="assignments-list" id="pendingAssignments">
                    <div class="loading">Loading...</div>
                </div>
            </div>
            
            <div class="dashboard-card">
                <h3><i class="material-icons">notifications</i>Recent Announcements</h3>
                <div class="announcements-list" id="recentAnnouncements">
                    <div class="loading">Loading...</div>
                </div>
            </div>
        </div>
    `;
    
    dashboardSection.innerHTML = dashboardHTML;
    initializeStudentDashboard();
}

function loadFacultyDashboard() {
    const dashboardHTML = `
        <div class="dashboard-grid">
            <div class="dashboard-card qr-card">
                <h3>Generate Attendance QR</h3>
                <div id="qrCodeContainer"></div>
                <button onclick="generateQRCode()">Generate New QR Code</button>
            </div>
            
            <div class="dashboard-card class-stats-card">
                <h3>Class Statistics</h3>
                <canvas id="classPerformanceChart"></canvas>
            </div>
            
            <div class="dashboard-card tasks-card">
                <h3>Pending Tasks</h3>
                <div id="pendingTasksList"></div>
            </div>
            
            <div class="dashboard-card upload-card">
                <h3>Quick Upload</h3>
                <div id="uploadForm"></div>
            </div>
        </div>
    `;
    
    dashboardSection.innerHTML = dashboardHTML;
    initializeFacultyDashboard();
}

function loadAdminDashboard() {
    const dashboardHTML = `
        <div class="dashboard-grid">
            <div class="dashboard-card users-card">
                <h3>User Management</h3>
                <div id="userManagement"></div>
            </div>
            
            <div class="dashboard-card dept-stats-card">
                <h3>Department Statistics</h3>
                <canvas id="deptPerformanceChart"></canvas>
            </div>
            
            <div class="dashboard-card complaints-card">
                <h3>Recent Complaints</h3>
                <div id="complaintsList"></div>
            </div>
            
            <div class="dashboard-card system-card">
                <h3>System Status</h3>
                <div id="systemStatus"></div>
            </div>
        </div>
    `;
    
    dashboardSection.innerHTML = dashboardHTML;
    initializeAdminDashboard();
}

// Initialize dashboard components
async function initializeStudentDashboard() {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData) throw new Error('User data not found');

        // Set user avatar
        const avatar = document.querySelector('.user-avatar');
        avatar.textContent = userData.fullName.charAt(0).toUpperCase();

        // Start all data fetching in parallel
        const [
            attendanceData,
            upcomingClasses,
            recentMarks,
            announcements
        ] = await Promise.all([
            loadAttendanceData(userData),
            loadUpcomingClasses(userData),
            loadRecentMarks(userData),
            loadAnnouncements(userData)
        ]);

        // Initialize all dashboard widgets
        initializeAttendanceWidget(attendanceData);
        initializeUpcomingClasses(upcomingClasses);
        initializeMarksChart(recentMarks);
        initializeAnnouncements(announcements);

        // Set up real-time listeners
        setupRealTimeListeners(userData);

    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showToast('Error loading dashboard data', 'error');
    }
}

async function initializeFacultyDashboard() {
    await loadClassStatistics();
    await loadPendingTasks();
    setupUploadForm();
}

async function initializeAdminDashboard() {
    await loadUserManagement();
    await loadDepartmentStats();
    await loadComplaints();
    await loadSystemStatus();
}

// Data loading functions
async function loadAttendanceData(userData) {
    try {
        const now = new Date();
        const startOfWeek = new Date(now.setDate(now.getDate() - now.getDay()));
        const startOfMonth = new Date(now.getFullYear(), now.getMonth(), 1);

        const attendanceRef = db.collection('attendance')
            .where('studentId', '==', userData.userId);
            
        const snapshot = await attendanceRef.get();
        const attendanceRecords = snapshot.docs.map(doc => doc.data());

        // Calculate attendance percentages
        const overall = calculateAttendancePercentage(attendanceRecords);
        const monthly = calculateAttendancePercentage(
            attendanceRecords.filter(record => new Date(record.timestamp) >= startOfMonth)
        );
        const weekly = calculateAttendancePercentage(
            attendanceRecords.filter(record => new Date(record.timestamp) >= startOfWeek)
        );

        return { overall, monthly, weekly, records: attendanceRecords };
    } catch (error) {
        console.error('Error loading attendance:', error);
        throw error;
    }
}

async function loadUpcomingClasses(userData) {
    try {
        const now = new Date();
        const endOfDay = new Date(now.setHours(23, 59, 59, 999));
        
        const classesRef = db.collection('classes')
            .where('section', '==', userData.section)
            .where('startTime', '>=', now)
            .where('startTime', '<=', endOfDay)
            .orderBy('startTime');
            
        const snapshot = await classesRef.get();
        return snapshot.docs.map(doc => doc.data());
    } catch (error) {
        console.error('Error loading classes:', error);
        throw error;
    }
}

async function loadRecentMarks(userData) {
    try {
        const marksRef = db.collection('marks')
            .where('studentId', '==', userData.userId)
            .orderBy('date', 'desc')
            .limit(5);
            
        const snapshot = await marksRef.get();
        return snapshot.docs.map(doc => doc.data());
    } catch (error) {
        console.error('Error loading marks:', error);
        throw error;
    }
}

async function loadPendingAssignments(userData) {
    try {
        const now = new Date();
        const assignmentsRef = db.collection('assignments')
            .where('section', '==', userData.section)
            .where('dueDate', '>=', now)
            .orderBy('dueDate');
            
        const snapshot = await assignmentsRef.get();
        return snapshot.docs.map(doc => ({
            ...doc.data(),
            id: doc.id
        }));
    } catch (error) {
        console.error('Error loading assignments:', error);
        throw error;
    }
}

async function loadAnnouncements(userData) {
    try {
        const announcementsRef = db.collection('announcements')
            .where('targetGroups', 'array-contains', userData.section)
            .orderBy('timestamp', 'desc')
            .limit(5);
            
        const snapshot = await announcementsRef.get();
        return snapshot.docs.map(doc => doc.data());
    } catch (error) {
        console.error('Error loading announcements:', error);
        throw error;
    }
}

// Display functions
function updateAttendanceDisplay(data) {
    // Update attendance percentages
    document.getElementById('overallAttendance').textContent = `${data.overall.toFixed(1)}%`;
    document.getElementById('monthlyAttendance').textContent = `${data.monthly.toFixed(1)}%`;
    document.getElementById('weeklyAttendance').textContent = `${data.weekly.toFixed(1)}%`;

    // Update attendance chart
    const ctx = document.getElementById('attendanceChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.records.slice(-30).map(record => 
                new Date(record.timestamp).toLocaleDateString()
            ),
            datasets: [{
                label: 'Attendance',
                data: data.records.slice(-30).map(record => record.present ? 100 : 0),
                borderColor: '#1976d2',
                tension: 0.1,
                fill: true,
                backgroundColor: 'rgba(25, 118, 210, 0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100,
                    ticks: {
                        callback: value => `${value}%`
                    }
                }
            }
        }
    });
}

function displayUpcomingClasses(classes) {
    const container = document.getElementById('upcomingClasses');
    if (!classes.length) {
        container.innerHTML = '<div class="no-data">No classes scheduled for today</div>';
        return;
    }

    container.innerHTML = classes.map(classData => `
        <div class="class-item">
            <div>
                <div class="class-subject">${classData.subject}</div>
                <div class="class-time">${formatTime(classData.startTime)} - ${formatTime(classData.endTime)}</div>
            </div>
            <div class="class-faculty">${classData.facultyName}</div>
        </div>
    `).join('');
}

function displayRecentMarks(marks) {
    const container = document.getElementById('recentMarks');
    if (!marks.length) {
        container.innerHTML = '<div class="no-data">No recent marks available</div>';
        return;
    }

    container.innerHTML = marks.map(mark => `
        <div class="list-item">
            <div>
                <div class="title">${mark.subject}</div>
                <div class="date">${new Date(mark.date).toLocaleDateString()}</div>
            </div>
            <div class="score">${mark.score}/${mark.total}</div>
        </div>
    `).join('');
}

function displayPendingAssignments(assignments) {
    const container = document.getElementById('pendingAssignments');
    if (!assignments.length) {
        container.innerHTML = '<div class="no-data">No pending assignments</div>';
        return;
    }

    container.innerHTML = assignments.map(assignment => `
        <div class="list-item">
            <div>
                <div class="title">${assignment.title}</div>
                <div class="date">Due: ${new Date(assignment.dueDate).toLocaleDateString()}</div>
            </div>
            <div class="assignment-status ${assignment.submitted ? 'status-submitted' : 'status-pending'}">
                ${assignment.submitted ? 'Submitted' : 'Pending'}
            </div>
        </div>
    `).join('');
}

function displayAnnouncements(announcements) {
    const container = document.getElementById('recentAnnouncements');
    if (!announcements.length) {
        container.innerHTML = '<div class="no-data">No recent announcements</div>';
        return;
    }

    container.innerHTML = announcements.map(announcement => `
        <div class="list-item">
            <div>
                <div class="title">${announcement.title}</div>
                <div class="date">${new Date(announcement.timestamp).toLocaleDateString()}</div>
            </div>
        </div>
    `).join('');
}

// Helper functions
function calculateAttendancePercentage(records) {
    if (!records.length) return 0;
    const present = records.filter(record => record.present).length;
    return (present / records.length) * 100;
}

function formatTime(timestamp) {
    return new Date(timestamp).toLocaleTimeString([], { 
        hour: '2-digit', 
        minute: '2-digit' 
    });
}

// Real-time updates
function setupRealTimeListeners(userData) {
    // Listen for new announcements
    db.collection('announcements')
        .where('targetAudience', 'array-contains', userData.section)
        .orderBy('postedAt', 'desc')
        .limit(5)
        .onSnapshot(snapshot => {
            snapshot.docChanges().forEach(change => {
                if (change.type === 'added') {
                    const announcement = change.doc.data();
                    showToast(`New Announcement: ${announcement.title}`, 'info');
                }
            });
            
            const announcements = snapshot.docs.map(doc => doc.data());
            initializeAnnouncements(announcements);
        });

    // Listen for marks updates
    db.collection('marks')
        .where('studentId', '==', userData.userId)
        .onSnapshot(snapshot => {
            snapshot.docChanges().forEach(change => {
                if (change.type === 'added') {
                    showToast('New marks have been uploaded', 'info');
                }
            });
        });
}

// QR Code generation for faculty
function generateQRCode() {
    const timestamp = Date.now();
    const sessionData = {
        facultyId: auth.currentUser.uid,
        timestamp: timestamp,
        validFor: 300 // 5 minutes in seconds
    };
    
    const qrCode = new QRCode(document.getElementById("qrCodeContainer"), {
        text: JSON.stringify(sessionData),
        width: 200,
        height: 200
    });
}

// Initialize Attendance Donut Chart
function initializeAttendanceWidget(data) {
    const ctx = document.getElementById('attendanceDonut').getContext('2d');
    
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Present', 'Absent'],
            datasets: [{
                data: [data.overall, 100 - data.overall],
                backgroundColor: ['#1B8B7E', '#E8F3F3'],
                borderWidth: 0
            }]
        },
        options: {
            cutout: '80%',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });

    // Update attendance stats
    document.getElementById('overallAttendance').textContent = `${data.overall.toFixed(1)}%`;
    document.getElementById('monthlyAttendance').textContent = `${data.monthly.toFixed(1)}%`;
    document.getElementById('weeklyAttendance').textContent = `${data.weekly.toFixed(1)}%`;
}

// Initialize Upcoming Classes
function initializeUpcomingClasses(classes) {
    const container = document.getElementById('upcomingClasses');
    
    if (!classes.length) {
        container.innerHTML = '<div class="no-data">No classes scheduled for today</div>';
        return;
    }

    container.innerHTML = classes.map(classData => `
        <div class="class-item">
            <div class="class-info">
                <div class="class-subject">${classData.subject}</div>
                <div class="class-time">${formatTime(classData.startTime)} - ${formatTime(classData.endTime)}</div>
            </div>
            <div class="class-faculty">${classData.facultyName}</div>
        </div>
    `).join('');
}

// Initialize Marks Chart
function initializeMarksChart(marks) {
    const ctx = document.getElementById('marksChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: marks.map(mark => mark.test.name),
            datasets: [{
                label: 'Score',
                data: marks.map(mark => mark.score),
                backgroundColor: '#1B8B7E',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 100
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Initialize Announcements
function initializeAnnouncements(announcements) {
    const container = document.getElementById('recentAnnouncements');
    
    if (!announcements.length) {
        container.innerHTML = '<div class="no-data">No recent announcements</div>';
        return;
    }

    container.innerHTML = announcements.map(announcement => `
        <div class="announcement-item">
            <div class="announcement-date">${formatDate(announcement.postedAt)}</div>
            <div class="announcement-title">${announcement.title}</div>
        </div>
    `).join('');
}

// Toast Notification System
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="material-icons">${getToastIcon(type)}</i>
        <span>${message}</span>
    `;

    const container = document.getElementById('toastContainer');
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Helper Functions
function getToastIcon(type) {
    switch(type) {
        case 'success': return 'check_circle';
        case 'error': return 'error';
        case 'warning': return 'warning';
        default: return 'info';
    }
}

function formatDate(timestamp) {
    return new Date(timestamp).toLocaleDateString([], {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Check if user is logged in
    const userData = sessionStorage.getItem('userData');
    if (userData) {
        initializeStudentDashboard();
    }
});