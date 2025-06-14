// Leave Request Module

// Initialize leave request module
function initializeLeaveModule() {
    const leaveContainer = document.getElementById('leaveContainer');
    if (!leaveContainer) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const isStudent = userData.role === 'student';

    leaveContainer.innerHTML = `
        <div class="leave-header">
            <h2>Leave Requests</h2>
            ${isStudent ? `
                <button onclick="showLeaveForm()" class="primary-button">
                    <i class="material-icons">add</i>
                    Apply for Leave
                </button>
            ` : ''}
        </div>
        <div class="leave-summary">
            <div class="summary-card">
                <h3>Total Leaves</h3>
                <div class="count" id="totalLeaves">0</div>
            </div>
            <div class="summary-card">
                <h3>Approved</h3>
                <div class="count approved" id="approvedLeaves">0</div>
            </div>
            <div class="summary-card">
                <h3>Rejected</h3>
                <div class="count rejected" id="rejectedLeaves">0</div>
            </div>
            <div class="summary-card">
                <h3>Pending</h3>
                <div class="count pending" id="pendingLeaves">0</div>
            </div>
        </div>
        <div class="leave-list">
            <div class="list-header">
                <h3>Recent Requests</h3>
                ${!isStudent ? `
                    <div class="filter-group">
                        <select id="statusFilter" onchange="filterLeaves()">
                            <option value="all">All Status</option>
                            <option value="pending">Pending</option>
                            <option value="approved">Approved</option>
                            <option value="rejected">Rejected</option>
                        </select>
                    </div>
                ` : ''}
            </div>
            <div id="leavesList"></div>
        </div>
    `;

    // Load leave requests
    loadLeaveRequests();
}

// Show leave application form
function showLeaveForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Apply for Leave</h2>
            <form id="leaveForm">
                <div class="form-group">
                    <select id="leaveType" required>
                        <option value="">Select Leave Type</option>
                        <option value="medical">Medical Leave</option>
                        <option value="personal">Personal Leave</option>
                        <option value="event">Event/Competition</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <label>From Date</label>
                        <input type="date" id="fromDate" required>
                    </div>
                    <div class="form-group">
                        <label>To Date</label>
                        <input type="date" id="toDate" required>
                    </div>
                </div>
                <div class="form-group">
                    <textarea id="leaveReason" placeholder="Reason for Leave" required></textarea>
                </div>
                <div class="form-group">
                    <div class="upload-zone" id="documentDropZone">
                        <i class="material-icons">attach_file</i>
                        <p>Attach supporting document (optional)</p>
                        <input type="file" id="leaveDocument" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" hidden>
                    </div>
                </div>
                <div id="uploadProgress" class="upload-progress hidden"></div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="primary-button">
                        Submit Request
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Setup document upload
    setupLeaveDocument();

    // Handle form submission
    document.getElementById('leaveForm').addEventListener('submit', handleLeaveSubmit);

    // Set minimum date as today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('fromDate').min = today;
    document.getElementById('toDate').min = today;

    // Update to date min when from date changes
    document.getElementById('fromDate').addEventListener('change', (e) => {
        document.getElementById('toDate').min = e.target.value;
    });
}

// Setup leave document upload
function setupLeaveDocument() {
    const dropZone = document.getElementById('documentDropZone');
    const fileInput = document.getElementById('leaveDocument');

    dropZone.addEventListener('click', () => fileInput.click());

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    dropZone.addEventListener('drop', handleDocumentDrop, false);
    fileInput.addEventListener('change', handleDocumentSelect);
}

// Handle leave submission
async function handleLeaveSubmit(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const fromDate = document.getElementById('fromDate').value;
        const toDate = document.getElementById('toDate').value;
        
        // Validate dates
        if (new Date(fromDate) > new Date(toDate)) {
            showToast('From date cannot be after to date', 'error');
            return;
        }

        const leaveData = {
            type: document.getElementById('leaveType').value,
            fromDate,
            toDate,
            reason: document.getElementById('leaveReason').value,
            status: 'pending',
            studentId: auth.currentUser.uid,
            submittedAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        // Upload document if selected
        const file = document.getElementById('leaveDocument').files[0];
        if (file) {
            const documentUrl = await uploadLeaveDocument(file);
            leaveData.documentUrl = documentUrl;
        }

        // Get student data
        const studentDoc = await db.collection('users').doc(auth.currentUser.uid).get();
        const studentData = studentDoc.data();

        // Add student details to leave data
        leaveData.studentName = studentData.fullName;
        leaveData.rollNo = studentData.rollNo;
        leaveData.section = studentData.section;

        // Save leave request
        await db.collection('leaveRequests').add(leaveData);

        showToast('Leave request submitted successfully', 'success');
        closeModal();
        loadLeaveRequests();
    } catch (error) {
        console.error('Error submitting leave request:', error);
        showToast('Error submitting leave request', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Upload leave document
async function uploadLeaveDocument(file) {
    const progressDiv = document.getElementById('uploadProgress');
    progressDiv.classList.remove('hidden');

    try {
        const storageRef = firebase.storage().ref();
        const documentRef = storageRef.child(`leave-documents/${auth.currentUser.uid}/${Date.now()}_${file.name}`);
        
        const uploadTask = documentRef.put(file);

        // Monitor upload progress
        uploadTask.on('state_changed', 
            (snapshot) => {
                const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
                progressDiv.innerHTML = `Uploading: ${Math.round(progress)}%`;
            }
        );

        await uploadTask;
        return await documentRef.getDownloadURL();
    } catch (error) {
        console.error('Error uploading document:', error);
        throw error;
    } finally {
        progressDiv.classList.add('hidden');
    }
}

// Load leave requests
async function loadLeaveRequests() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        let leaveQuery = db.collection('leaveRequests');
        
        if (userData.role === 'student') {
            leaveQuery = leaveQuery.where('studentId', '==', user.uid);
        } else if (userData.role === 'faculty') {
            leaveQuery = leaveQuery.where('section', '==', userData.section);
        }

        const leaves = await leaveQuery.orderBy('submittedAt', 'desc').get();
        const leavesList = document.getElementById('leavesList');
        
        if (!leavesList) return;

        // Update summary counts
        let totalLeaves = 0;
        let approvedLeaves = 0;
        let rejectedLeaves = 0;
        let pendingLeaves = 0;

        leavesList.innerHTML = '';

        leaves.forEach(doc => {
            const leave = doc.data();
            totalLeaves++;

            switch (leave.status) {
                case 'approved': approvedLeaves++; break;
                case 'rejected': rejectedLeaves++; break;
                case 'pending': pendingLeaves++; break;
            }

            const fromDate = new Date(leave.fromDate);
            const toDate = new Date(leave.toDate);
            
            leavesList.innerHTML += `
                <div class="leave-card ${leave.status}">
                    <div class="leave-header">
                        <div class="leave-type">
                            <i class="material-icons">${getLeaveIcon(leave.type)}</i>
                            <span>${leave.type.charAt(0).toUpperCase() + leave.type.slice(1)} Leave</span>
                        </div>
                        <div class="leave-status">
                            <span class="status-badge ${leave.status}">
                                ${leave.status.charAt(0).toUpperCase() + leave.status.slice(1)}
                            </span>
                        </div>
                    </div>
                    <div class="leave-info">
                        ${userData.role !== 'student' ? `
                            <p class="student-info">
                                <strong>${leave.studentName}</strong>
                                <span>(${leave.rollNo})</span>
                            </p>
                        ` : ''}
                        <p class="leave-dates">
                            ${fromDate.toLocaleDateString()} - ${toDate.toLocaleDateString()}
                            <span class="leave-duration">
                                (${calculateDuration(fromDate, toDate)} days)
                            </span>
                        </p>
                        <p class="leave-reason">${leave.reason}</p>
                        ${leave.documentUrl ? `
                            <a href="${leave.documentUrl}" target="_blank" class="document-link">
                                <i class="material-icons">attachment</i>
                                View Attachment
                            </a>
                        ` : ''}
                    </div>
                    ${userData.role !== 'student' && leave.status === 'pending' ? `
                        <div class="leave-actions">
                            <button onclick="updateLeaveStatus('${doc.id}', 'approved')" class="success-button">
                                <i class="material-icons">check</i>
                                Approve
                            </button>
                            <button onclick="showRejectForm('${doc.id}')" class="danger-button">
                                <i class="material-icons">close</i>
                                Reject
                            </button>
                        </div>
                    ` : ''}
                    ${leave.remarks ? `
                        <div class="leave-remarks">
                            <p><strong>Remarks:</strong> ${leave.remarks}</p>
                        </div>
                    ` : ''}
                </div>
            `;
        });

        // Update summary
        document.getElementById('totalLeaves').textContent = totalLeaves;
        document.getElementById('approvedLeaves').textContent = approvedLeaves;
        document.getElementById('rejectedLeaves').textContent = rejectedLeaves;
        document.getElementById('pendingLeaves').textContent = pendingLeaves;

        if (leaves.empty) {
            leavesList.innerHTML = `
                <div class="no-leaves">
                    <i class="material-icons">event_busy</i>
                    <p>No leave requests found</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading leave requests:', error);
        showToast('Error loading leave requests', 'error');
    }
}

// Show reject form
function showRejectForm(leaveId) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Reject Leave Request</h2>
            <form id="rejectForm">
                <div class="form-group">
                    <textarea id="rejectRemarks" placeholder="Reason for rejection" required></textarea>
                </div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="danger-button">
                        Reject
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Handle form submission
    document.getElementById('rejectForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const remarks = document.getElementById('rejectRemarks').value;
        updateLeaveStatus(leaveId, 'rejected', remarks);
    });
}

// Update leave status
async function updateLeaveStatus(leaveId, status, remarks = '') {
    showLoadingSpinner();

    try {
        await db.collection('leaveRequests').doc(leaveId).update({
            status,
            remarks,
            actionBy: auth.currentUser.uid,
            actionAt: firebase.firestore.FieldValue.serverTimestamp()
        });

        showToast(`Leave request ${status}`, 'success');
        closeModal();
        loadLeaveRequests();
    } catch (error) {
        console.error('Error updating leave status:', error);
        showToast('Error updating leave status', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Get leave icon
function getLeaveIcon(type) {
    const icons = {
        medical: 'local_hospital',
        personal: 'person',
        event: 'event',
        other: 'more_horiz'
    };

    return icons[type] || 'event_busy';
}

// Calculate duration
function calculateDuration(fromDate, toDate) {
    const diffTime = Math.abs(toDate - fromDate);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
}

// Filter leaves
function filterLeaves() {
    const status = document.getElementById('statusFilter').value;
    const leaves = document.querySelectorAll('.leave-card');

    leaves.forEach(leave => {
        if (status === 'all' || leave.classList.contains(status)) {
            leave.style.display = 'block';
        } else {
            leave.style.display = 'none';
        }
    });
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeLeaveModule();
        }
    });
}); 