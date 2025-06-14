// Fee Management Module

// Initialize fee management
function initializeFeeManagement() {
    const feeContainer = document.getElementById('feeContainer');
    if (!feeContainer) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const isAdmin = userData.role === 'admin';

    feeContainer.innerHTML = `
        ${isAdmin ? `
            <div class="fee-actions">
                <button onclick="showAddFeeForm()" class="primary-button">
                    <i class="material-icons">add</i>
                    Add Fee
                </button>
                <button onclick="showBulkUploadForm()" class="secondary-button">
                    <i class="material-icons">upload_file</i>
                    Bulk Upload
                </button>
            </div>
        ` : ''}
        <div class="fee-summary">
            <div class="summary-card total-fee">
                <h3>Total Fee</h3>
                <div class="amount" id="totalFee">₹0</div>
            </div>
            <div class="summary-card paid-fee">
                <h3>Paid Amount</h3>
                <div class="amount" id="paidAmount">₹0</div>
            </div>
            <div class="summary-card due-fee">
                <h3>Due Amount</h3>
                <div class="amount" id="dueAmount">₹0</div>
            </div>
        </div>
        <div class="fee-details">
            <h3>Fee Details</h3>
            <div class="fee-table-container">
                <table class="fee-table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Due Date</th>
                            <th>Amount</th>
                            <th>Status</th>
                            ${isAdmin ? '<th>Actions</th>' : ''}
                        </tr>
                    </thead>
                    <tbody id="feeTableBody"></tbody>
                </table>
            </div>
        </div>
        ${!isAdmin ? `
            <div class="payment-history">
                <h3>Payment History</h3>
                <div id="paymentHistory"></div>
            </div>
        ` : ''}
    `;

    // Load fee data
    loadFeeData();
}

// Show add fee form
function showAddFeeForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Add Fee</h2>
            <form id="feeForm">
                <div class="form-group">
                    <input type="text" id="feeDescription" placeholder="Fee Description" required>
                </div>
                <div class="form-row">
                    <div class="form-group">
                        <input type="number" id="feeAmount" placeholder="Amount" required>
                    </div>
                    <div class="form-group">
                        <input type="date" id="feeDueDate" required>
                    </div>
                </div>
                <div class="form-group">
                    <select id="feeSection" required>
                        <option value="">Select Section</option>
                    </select>
                </div>
                <div class="form-group">
                    <select id="feeType" required>
                        <option value="">Select Fee Type</option>
                        <option value="tuition">Tuition Fee</option>
                        <option value="exam">Exam Fee</option>
                        <option value="library">Library Fee</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="primary-button">
                        Add Fee
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Load sections
    loadSections();

    // Handle form submission
    document.getElementById('feeForm').addEventListener('submit', handleFeeSubmit);
}

// Show bulk upload form
function showBulkUploadForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Bulk Upload Fee</h2>
            <div class="upload-zone" id="bulkUploadZone">
                <i class="material-icons">upload_file</i>
                <p>Upload Excel file with fee details</p>
                <input type="file" id="bulkFileInput" accept=".xlsx,.xls" hidden>
            </div>
            <div class="template-link">
                <a href="#" onclick="downloadTemplate()">
                    <i class="material-icons">download</i>
                    Download Template
                </a>
            </div>
            <div id="uploadProgress" class="upload-progress hidden"></div>
        </div>
    `;

    document.body.appendChild(modal);

    // Setup file upload
    setupBulkUpload();
}

// Setup bulk upload
function setupBulkUpload() {
    const dropZone = document.getElementById('bulkUploadZone');
    const fileInput = document.getElementById('bulkFileInput');

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

    dropZone.addEventListener('drop', handleBulkDrop, false);
    fileInput.addEventListener('change', handleBulkSelect);
}

// Handle bulk file drop
function handleBulkDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleBulkFiles(files);
}

// Handle bulk file selection
function handleBulkSelect(e) {
    const files = e.target.files;
    handleBulkFiles(files);
}

// Process bulk files
async function handleBulkFiles(files) {
    if (files.length !== 1) {
        showToast('Please upload a single Excel file', 'error');
        return;
    }

    const file = files[0];
    showLoadingSpinner();

    try {
        // Read Excel file
        const data = await readExcelFile(file);
        
        // Validate data
        if (!validateFeeData(data)) {
            showToast('Invalid file format', 'error');
            return;
        }

        // Upload fee data
        await uploadBulkFeeData(data);

        showToast('Fee data uploaded successfully', 'success');
        closeModal();
        loadFeeData();
    } catch (error) {
        console.error('Error processing bulk upload:', error);
        showToast('Error processing file', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Read Excel file
function readExcelFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = e.target.result;
                const workbook = XLSX.read(data, { type: 'binary' });
                const sheetName = workbook.SheetNames[0];
                const sheet = workbook.Sheets[sheetName];
                const jsonData = XLSX.utils.sheet_to_json(sheet);
                resolve(jsonData);
            } catch (error) {
                reject(error);
            }
        };
        reader.onerror = reject;
        reader.readAsBinaryString(file);
    });
}

// Validate fee data
function validateFeeData(data) {
    if (!Array.isArray(data) || data.length === 0) return false;

    const requiredFields = ['description', 'amount', 'dueDate', 'section', 'type'];
    return data.every(row => 
        requiredFields.every(field => row.hasOwnProperty(field))
    );
}

// Upload bulk fee data
async function uploadBulkFeeData(data) {
    const batch = db.batch();

    data.forEach(row => {
        const feeRef = db.collection('fees').doc();
        batch.set(feeRef, {
            description: row.description,
            amount: Number(row.amount),
            dueDate: new Date(row.dueDate),
            section: row.section,
            type: row.type,
            status: 'pending',
            createdBy: auth.currentUser.uid,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        });
    });

    await batch.commit();
}

// Handle fee submission
async function handleFeeSubmit(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const feeData = {
            description: document.getElementById('feeDescription').value,
            amount: Number(document.getElementById('feeAmount').value),
            dueDate: document.getElementById('feeDueDate').value,
            section: document.getElementById('feeSection').value,
            type: document.getElementById('feeType').value,
            status: 'pending',
            createdBy: auth.currentUser.uid,
            createdAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        await db.collection('fees').add(feeData);

        showToast('Fee added successfully', 'success');
        closeModal();
        loadFeeData();
    } catch (error) {
        console.error('Error adding fee:', error);
        showToast('Error adding fee', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load fee data
async function loadFeeData() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        let feeQuery = db.collection('fees');
        
        if (userData.role === 'student') {
            feeQuery = feeQuery.where('section', '==', userData.section);
        }

        const fees = await feeQuery.orderBy('dueDate').get();
        const feeTableBody = document.getElementById('feeTableBody');
        
        if (!feeTableBody) return;

        let totalFee = 0;
        let paidAmount = 0;

        feeTableBody.innerHTML = '';

        fees.forEach(doc => {
            const fee = doc.data();
            const dueDate = new Date(fee.dueDate);
            totalFee += fee.amount;
            
            if (fee.status === 'paid') {
                paidAmount += fee.amount;
            }

            feeTableBody.innerHTML += `
                <tr>
                    <td>${fee.description}</td>
                    <td>${dueDate.toLocaleDateString()}</td>
                    <td>₹${fee.amount}</td>
                    <td>
                        <span class="status-badge ${fee.status}">
                            ${fee.status.charAt(0).toUpperCase() + fee.status.slice(1)}
                        </span>
                    </td>
                    ${userData.role === 'admin' ? `
                        <td>
                            <button onclick="editFee('${doc.id}')" class="icon-button">
                                <i class="material-icons">edit</i>
                            </button>
                            <button onclick="deleteFee('${doc.id}')" class="icon-button danger">
                                <i class="material-icons">delete</i>
                            </button>
                        </td>
                    ` : ''}
                </tr>
            `;
        });

        // Update summary
        document.getElementById('totalFee').textContent = `₹${totalFee}`;
        document.getElementById('paidAmount').textContent = `₹${paidAmount}`;
        document.getElementById('dueAmount').textContent = `₹${totalFee - paidAmount}`;

        // Load payment history for students
        if (userData.role === 'student') {
            loadPaymentHistory(userData.section);
        }
    } catch (error) {
        console.error('Error loading fee data:', error);
        showToast('Error loading fee data', 'error');
    }
}

// Load payment history
async function loadPaymentHistory(section) {
    try {
        const payments = await db.collection('payments')
            .where('section', '==', section)
            .orderBy('paidAt', 'desc')
            .limit(5)
            .get();

        const paymentHistory = document.getElementById('paymentHistory');
        if (!paymentHistory) return;

        paymentHistory.innerHTML = '';

        payments.forEach(doc => {
            const payment = doc.data();
            const paidDate = payment.paidAt.toDate();

            paymentHistory.innerHTML += `
                <div class="payment-item">
                    <div class="payment-info">
                        <h4>${payment.description}</h4>
                        <p>Paid on ${paidDate.toLocaleDateString()}</p>
                    </div>
                    <div class="payment-amount">₹${payment.amount}</div>
                </div>
            `;
        });

        if (payments.empty) {
            paymentHistory.innerHTML = `
                <div class="no-payments">
                    <i class="material-icons">receipt_long</i>
                    <p>No payment history available</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading payment history:', error);
        showToast('Error loading payment history', 'error');
    }
}

// Edit fee
function editFee(feeId) {
    // Implement fee editing
}

// Delete fee
async function deleteFee(feeId) {
    if (!confirm('Are you sure you want to delete this fee?')) return;

    showLoadingSpinner();

    try {
        await db.collection('fees').doc(feeId).delete();
        showToast('Fee deleted successfully', 'success');
        loadFeeData();
    } catch (error) {
        console.error('Error deleting fee:', error);
        showToast('Error deleting fee', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Download template
function downloadTemplate() {
    const template = [
        {
            description: 'Sample Fee',
            amount: 1000,
            dueDate: '2024-03-01',
            section: 'CSE-A',
            type: 'tuition'
        }
    ];

    const ws = XLSX.utils.json_to_sheet(template);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Fee Template');
    XLSX.writeFile(wb, 'fee_template.xlsx');
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeFeeManagement();
        }
    });
}); 