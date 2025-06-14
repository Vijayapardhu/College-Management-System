// Faculty Dashboard Implementation

// Initialize Faculty Dashboard
async function initializeFacultyDashboard() {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        // Set user avatar
        const avatar = document.querySelector('.user-avatar');
        avatar.textContent = userData.fullName.charAt(0).toUpperCase();

        // Load all dashboard data in parallel
        const [
            classPerformance,
            attendanceStats,
            pendingTasks,
            recentUploads
        ] = await Promise.all([
            loadClassPerformance(userData),
            loadAttendanceStats(userData),
            loadPendingTasks(userData),
            loadRecentUploads(userData)
        ]);

        // Initialize dashboard widgets
        initializePerformanceChart(classPerformance);
        initializeAttendanceStats(attendanceStats);
        initializePendingTasks(pendingTasks);
        initializeUploadSection(recentUploads);

        // Setup real-time listeners
        setupFacultyListeners(userData);

    } catch (error) {
        console.error('Error initializing faculty dashboard:', error);
        showToast('Error loading dashboard data', 'error');
    }
}

// Load Class Performance Data
async function loadClassPerformance(userData) {
    try {
        const performanceData = {
            labels: [],
            averages: [],
            highest: [],
            lowest: []
        };

        // Get all classes taught by the faculty
        const classesSnapshot = await db.collection('classes')
            .where('facultyId', '==', userData.userId)
            .get();

        for (const classDoc of classesSnapshot.docs) {
            const classData = classDoc.data();
            
            // Get marks for this class
            const marksSnapshot = await db.collection('marks')
                .where('classId', '==', classDoc.id)
                .get();

            const scores = marksSnapshot.docs.map(doc => doc.data().score);
            
            if (scores.length > 0) {
                performanceData.labels.push(classData.subject);
                performanceData.averages.push(calculateAverage(scores));
                performanceData.highest.push(Math.max(...scores));
                performanceData.lowest.push(Math.min(...scores));
            }
        }

        return performanceData;
    } catch (error) {
        console.error('Error loading class performance:', error);
        throw error;
    }
}

// Initialize Performance Chart
function initializePerformanceChart(data) {
    const ctx = document.getElementById('performanceChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [
                {
                    label: 'Average',
                    data: data.averages,
                    backgroundColor: '#1B8B7E',
                    borderRadius: 4
                },
                {
                    label: 'Highest',
                    data: data.highest,
                    backgroundColor: '#4CAF50',
                    borderRadius: 4
                },
                {
                    label: 'Lowest',
                    data: data.lowest,
                    backgroundColor: '#FFC107',
                    borderRadius: 4
                }
            ]
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
                    position: 'bottom'
                }
            }
        }
    });
}

// Initialize Quick Test Creator
function initializeTestCreator() {
    const container = document.getElementById('testCreator');
    
    container.innerHTML = `
        <form id="quickTestForm" class="quick-test-form">
            <div class="form-group">
                <input type="text" id="testName" placeholder="Test Name" required>
            </div>
            <div class="form-group">
                <select id="testSubject" required>
                    <option value="">Select Subject</option>
                </select>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <input type="number" id="maxMarks" placeholder="Max Marks" required>
                </div>
                <div class="form-group">
                    <input type="date" id="testDate" required>
                </div>
            </div>
            <button type="submit">Create Test</button>
        </form>
    `;

    // Handle form submission
    document.getElementById('quickTestForm').addEventListener('submit', handleTestCreation);
}

// Initialize Material Upload Section
function initializeUploadSection(recentUploads) {
    const container = document.getElementById('uploadSection');
    
    container.innerHTML = `
        <div class="upload-zone" id="dropZone">
            <i class="material-icons">cloud_upload</i>
            <p>Drag & drop files here or click to upload</p>
            <input type="file" id="fileInput" multiple accept=".pdf,.doc,.docx" hidden>
        </div>
        <div class="recent-uploads">
            <h3>Recent Uploads</h3>
            <div id="recentUploadsList"></div>
        </div>
    `;

    // Setup drag and drop handlers
    setupDragAndDrop();
    displayRecentUploads(recentUploads);
}

// Setup Drag and Drop
function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');

    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', async (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        handleFileUpload(files);
    });

    fileInput.addEventListener('change', () => {
        handleFileUpload(fileInput.files);
    });
}

// Handle File Upload
async function handleFileUpload(files) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        
        for (const file of files) {
            showToast(`Uploading ${file.name}...`, 'info');
            
            // Upload file to Firebase Storage
            const storageRef = storage.ref(`materials/${userData.department}/${file.name}`);
            await storageRef.put(file);
            const downloadURL = await storageRef.getDownloadURL();

            // Save metadata to Firestore
            await db.collection('materials').add({
                title: file.name,
                fileUrl: downloadURL,
                uploadedBy: userData.userId,
                uploadedAt: new Date().toISOString(),
                department: userData.department,
                fileType: file.type,
                fileSize: file.size
            });

            showToast(`${file.name} uploaded successfully!`, 'success');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showToast('Error uploading file', 'error');
    }
}

// Helper Functions
function calculateAverage(numbers) {
    return numbers.reduce((a, b) => a + b, 0) / numbers.length;
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const userData = sessionStorage.getItem('userData');
    if (userData && JSON.parse(userData).role === 'faculty') {
        initializeFacultyDashboard();
    }
}); 