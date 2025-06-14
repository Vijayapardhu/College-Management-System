// Marks Management Module

// Initialize test creator form
function initializeTestCreator() {
    const testCreator = document.getElementById('testCreator');
    if (!testCreator) return;

    testCreator.innerHTML = `
        <form id="createTestForm" class="quick-test-form">
            <div class="form-group">
                <input type="text" id="testName" placeholder="Test Name" required>
            </div>
            <div class="form-row">
                <div class="form-group">
                    <input type="number" id="maxMarks" placeholder="Maximum Marks" required>
                </div>
                <div class="form-group">
                    <select id="subject" required>
                        <option value="">Select Subject</option>
                    </select>
                </div>
            </div>
            <div class="form-group">
                <input type="date" id="testDate" required>
            </div>
            <button type="submit" class="primary-button">Create Test</button>
        </form>
    `;

    // Load subjects for faculty
    loadFacultySubjects();

    // Handle form submission
    document.getElementById('createTestForm').addEventListener('submit', handleTestCreation);
}

// Load faculty's subjects
async function loadFacultySubjects() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        const subjectSelect = document.getElementById('subject');
        userData.subjects.forEach(subject => {
            const option = document.createElement('option');
            option.value = subject;
            option.textContent = subject;
            subjectSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading subjects:', error);
        showToast('Error loading subjects', 'error');
    }
}

// Handle test creation
async function handleTestCreation(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const testData = {
            name: document.getElementById('testName').value,
            maxMarks: parseInt(document.getElementById('maxMarks').value),
            subject: document.getElementById('subject').value,
            date: document.getElementById('testDate').value,
            createdBy: auth.currentUser.uid,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        // Create test document
        const testRef = await db.collection('tests').add(testData);

        showToast('Test created successfully', 'success');
        document.getElementById('createTestForm').reset();

        // Refresh tests list
        loadTests();
    } catch (error) {
        console.error('Error creating test:', error);
        showToast('Error creating test', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load tests for faculty
async function loadTests() {
    try {
        const user = auth.currentUser;
        const tests = await db.collection('tests')
            .where('createdBy', '==', user.uid)
            .orderBy('createdAt', 'desc')
            .get();

        const testsList = document.getElementById('testsList');
        if (!testsList) return;

        testsList.innerHTML = '';

        tests.forEach(doc => {
            const test = doc.data();
            testsList.innerHTML += `
                <div class="test-card" data-test-id="${doc.id}">
                    <div class="test-header">
                        <h3>${test.name}</h3>
                        <span class="test-subject">${test.subject}</span>
                    </div>
                    <div class="test-info">
                        <p>Max Marks: ${test.maxMarks}</p>
                        <p>Date: ${test.date}</p>
                    </div>
                    <button onclick="uploadMarks('${doc.id}')" class="secondary-button">
                        Upload Marks
                    </button>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading tests:', error);
        showToast('Error loading tests', 'error');
    }
}

// Upload marks for a test
async function uploadMarks(testId) {
    try {
        // Get test data
        const testDoc = await db.collection('tests').doc(testId).get();
        const test = testDoc.data();

        // Get students for the subject
        const students = await db.collection('users')
            .where('role', '==', 'student')
            .where('subjects', 'array-contains', test.subject)
            .get();

        // Create marks upload form
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Upload Marks - ${test.name}</h2>
                <form id="marksForm">
                    <table class="marks-table">
                        <thead>
                            <tr>
                                <th>Roll No</th>
                                <th>Name</th>
                                <th>Marks</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${students.docs.map(doc => {
                                const student = doc.data();
                                return `
                                    <tr>
                                        <td>${student.rollNo}</td>
                                        <td>${student.fullName}</td>
                                        <td>
                                            <input type="number" 
                                                name="marks_${doc.id}" 
                                                min="0" 
                                                max="${test.maxMarks}" 
                                                required>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                    <div class="modal-actions">
                        <button type="button" onclick="closeModal()" class="secondary-button">
                            Cancel
                        </button>
                        <button type="submit" class="primary-button">
                            Upload Marks
                        </button>
                    </div>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        // Handle marks form submission
        document.getElementById('marksForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            showLoadingSpinner();

            try {
                const batch = db.batch();

                students.docs.forEach(doc => {
                    const marks = parseInt(document.querySelector(`[name="marks_${doc.id}"]`).value);
                    const markRef = db.collection('marks').doc();
                    
                    batch.set(markRef, {
                        testId,
                        studentId: doc.id,
                        score: marks,
                        maxMarks: test.maxMarks,
                        subject: test.subject,
                        date: test.date,
                        uploadedBy: auth.currentUser.uid,
                        uploadedAt: firebase.firestore.FieldValue.serverTimestamp()
                    });
                });

                await batch.commit();
                showToast('Marks uploaded successfully', 'success');
                closeModal();

                // Send notifications to students
                students.docs.forEach(doc => {
                    notificationsService.sendMarksNotification(doc.id, test);
                });
            } catch (error) {
                console.error('Error uploading marks:', error);
                showToast('Error uploading marks', 'error');
            } finally {
                hideLoadingSpinner();
            }
        });
    } catch (error) {
        console.error('Error preparing marks upload:', error);
        showToast('Error preparing marks upload', 'error');
    }
}

// Close modal
function closeModal() {
    const modal = document.querySelector('.modal');
    if (modal) {
        modal.remove();
    }
}

// Load student's marks
async function loadStudentMarks() {
    try {
        const user = auth.currentUser;
        const marks = await db.collection('marks')
            .where('studentId', '==', user.uid)
            .orderBy('uploadedAt', 'desc')
            .get();

        const marksList = document.getElementById('marksList');
        if (!marksList) return;

        marksList.innerHTML = '';

        marks.forEach(doc => {
            const mark = doc.data();
            const percentage = ((mark.score / mark.maxMarks) * 100).toFixed(1);
            
            marksList.innerHTML += `
                <div class="mark-card">
                    <div class="mark-header">
                        <h3>${mark.subject}</h3>
                        <span class="mark-date">${mark.date}</span>
                    </div>
                    <div class="mark-score">
                        <div class="score-circle ${getScoreClass(percentage)}">
                            ${percentage}%
                        </div>
                        <p>${mark.score}/${mark.maxMarks}</p>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading marks:', error);
        showToast('Error loading marks', 'error');
    }
}

// Get score class for styling
function getScoreClass(percentage) {
    if (percentage >= 75) return 'excellent';
    if (percentage >= 60) return 'good';
    if (percentage >= 35) return 'average';
    return 'poor';
}

// Initialize module based on user role
async function initializeMarksModule() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        if (userData.role === 'faculty') {
            initializeTestCreator();
            loadTests();
        } else if (userData.role === 'student') {
            loadStudentMarks();
        }
    } catch (error) {
        console.error('Error initializing marks module:', error);
        showToast('Error initializing marks module', 'error');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeMarksModule();
        }
    });
});

// Create a new test
async function createTest(testData) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        const test = {
            ...testData,
            createdBy: userData.userId,
            createdAt: new Date().toISOString(),
            department: userData.department
        };

        const testRef = await db.collection('tests').add(test);
        return testRef.id;
    } catch (error) {
        console.error('Error creating test:', error);
        throw error;
    }
}

// Get tests for faculty
async function getFacultyTests() {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        const testsSnapshot = await db.collection('tests')
            .where('createdBy', '==', userData.userId)
            .orderBy('date', 'desc')
            .get();

        return testsSnapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));
    } catch (error) {
        console.error('Error getting faculty tests:', error);
        throw error;
    }
}

// Get student's marks
async function getStudentMarks() {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'student') {
            throw new Error('Unauthorized access');
        }

        const marksSnapshot = await db.collection('marks')
            .where('studentId', '==', userData.userId)
            .get();

        const marks = [];
        for (const doc of marksSnapshot.docs) {
            const markData = doc.data();
            const testDoc = await db.collection('tests').doc(markData.testId).get();
            marks.push({
                id: doc.id,
                ...markData,
                test: testDoc.data()
            });
        }

        return marks;
    } catch (error) {
        console.error('Error getting student marks:', error);
        throw error;
    }
}

// Get marks for a specific test
async function getTestMarks(testId) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        const marksSnapshot = await db.collection('marks')
            .where('testId', '==', testId)
            .get();

        return marksSnapshot.docs.map(doc => ({
            id: doc.id,
            ...doc.data()
        }));
    } catch (error) {
        console.error('Error getting test marks:', error);
        throw error;
    }
}

// Update marks
async function updateMarks(markId, updatedData) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        await db.collection('marks').doc(markId).update({
            ...updatedData,
            modifiedAt: new Date().toISOString()
        });
    } catch (error) {
        console.error('Error updating marks:', error);
        throw error;
    }
}

// Delete a test and its marks
async function deleteTest(testId) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        const batch = db.batch();

        // Delete the test
        batch.delete(db.collection('tests').doc(testId));

        // Delete all marks for this test
        const marksSnapshot = await db.collection('marks')
            .where('testId', '==', testId)
            .get();

        marksSnapshot.docs.forEach(doc => {
            batch.delete(doc.ref);
        });

        await batch.commit();
    } catch (error) {
        console.error('Error deleting test:', error);
        throw error;
    }
}

// Generate test report
async function generateTestReport(testId) {
    try {
        const userData = JSON.parse(sessionStorage.getItem('userData'));
        if (!userData || userData.role !== 'faculty') {
            throw new Error('Unauthorized access');
        }

        const testDoc = await db.collection('tests').doc(testId).get();
        const test = testDoc.data();

        const marksSnapshot = await db.collection('marks')
            .where('testId', '==', testId)
            .get();

        const marks = marksSnapshot.docs.map(doc => doc.data());

        // Calculate statistics
        const scores = marks.map(m => m.score);
        const stats = {
            highest: Math.max(...scores),
            lowest: Math.min(...scores),
            average: scores.reduce((a, b) => a + b, 0) / scores.length,
            total: marks.length,
            passed: scores.filter(s => s >= test.maxMarks * 0.4).length,
            failed: scores.filter(s => s < test.maxMarks * 0.4).length
        };

        return {
            test,
            marks,
            stats
        };
    } catch (error) {
        console.error('Error generating test report:', error);
        throw error;
    }
}

// Export functions
export {
    createTest,
    uploadMarks,
    getFacultyTests,
    getStudentMarks,
    getTestMarks,
    updateMarks,
    deleteTest,
    generateTestReport
}; 