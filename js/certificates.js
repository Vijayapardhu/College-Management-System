// Certificate Generation Module

// Initialize certificate module
function initializeCertificateModule() {
    const certificateContainer = document.getElementById('certificateContainer');
    if (!certificateContainer) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const isAdmin = userData.role === 'admin';

    certificateContainer.innerHTML = `
        ${isAdmin ? `
            <div class="certificate-actions">
                <button onclick="showCertificateForm()" class="primary-button">
                    <i class="material-icons">add</i>
                    Generate Certificate
                </button>
                <button onclick="showBulkGenerateForm()" class="secondary-button">
                    <i class="material-icons">group_add</i>
                    Bulk Generate
                </button>
            </div>
        ` : ''}
        <div class="certificates-list">
            <h3>My Certificates</h3>
            <div id="certificatesList"></div>
        </div>
    `;

    // Load certificates
    loadCertificates();
}

// Show certificate generation form
function showCertificateForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Generate Certificate</h2>
            <form id="certificateForm">
                <div class="form-group">
                    <select id="certificateType" required>
                        <option value="">Select Certificate Type</option>
                        <option value="completion">Course Completion</option>
                        <option value="merit">Merit Certificate</option>
                        <option value="participation">Participation Certificate</option>
                        <option value="achievement">Achievement Certificate</option>
                    </select>
                </div>
                <div class="form-group">
                    <select id="studentId" required>
                        <option value="">Select Student</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" id="certificateTitle" placeholder="Certificate Title" required>
                </div>
                <div class="form-group">
                    <textarea id="certificateDescription" placeholder="Description/Achievement" required></textarea>
                </div>
                <div class="form-group">
                    <input type="date" id="certificateDate" required>
                </div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="primary-button">
                        Generate
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Load students
    loadStudents();

    // Handle form submission
    document.getElementById('certificateForm').addEventListener('submit', handleCertificateGeneration);
}

// Load students
async function loadStudents() {
    try {
        const students = await db.collection('users')
            .where('role', '==', 'student')
            .get();

        const studentSelect = document.getElementById('studentId');
        
        students.forEach(doc => {
            const student = doc.data();
            const option = document.createElement('option');
            option.value = doc.id;
            option.textContent = `${student.fullName} (${student.rollNo})`;
            studentSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Error loading students:', error);
        showToast('Error loading students', 'error');
    }
}

// Handle certificate generation
async function handleCertificateGeneration(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const certificateData = {
            type: document.getElementById('certificateType').value,
            studentId: document.getElementById('studentId').value,
            title: document.getElementById('certificateTitle').value,
            description: document.getElementById('certificateDescription').value,
            date: document.getElementById('certificateDate').value,
            issuedBy: auth.currentUser.uid,
            issuedAt: firebase.firestore.FieldValue.serverTimestamp()
        };

        // Get student data
        const studentDoc = await db.collection('users').doc(certificateData.studentId).get();
        const studentData = studentDoc.data();

        // Generate certificate PDF
        const certificateUrl = await generateCertificatePDF({
            ...certificateData,
            studentName: studentData.fullName,
            rollNo: studentData.rollNo
        });

        // Save certificate data
        const certificateRef = await db.collection('certificates').add({
            ...certificateData,
            studentName: studentData.fullName,
            rollNo: studentData.rollNo,
            url: certificateUrl,
            qrCode: await generateQRCode(certificateUrl)
        });

        showToast('Certificate generated successfully', 'success');
        closeModal();
        loadCertificates();
    } catch (error) {
        console.error('Error generating certificate:', error);
        showToast('Error generating certificate', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Generate certificate PDF
async function generateCertificatePDF(data) {
    try {
        // Create PDF document
        const doc = new jsPDF();
        
        // Add certificate template
        const template = await loadCertificateTemplate(data.type);
        doc.addImage(template, 'JPEG', 0, 0, 210, 297);

        // Add certificate content
        doc.setFont('times', 'bold');
        doc.setFontSize(36);
        doc.setTextColor(44, 62, 80);
        doc.text(data.title, 105, 120, { align: 'center' });

        doc.setFont('times', 'normal');
        doc.setFontSize(24);
        doc.text(data.studentName, 105, 150, { align: 'center' });

        doc.setFontSize(16);
        doc.text(data.description, 105, 170, { align: 'center', maxWidth: 150 });

        doc.setFontSize(14);
        doc.text(`Roll No: ${data.rollNo}`, 105, 190, { align: 'center' });
        doc.text(`Date: ${new Date(data.date).toLocaleDateString()}`, 105, 200, { align: 'center' });

        // Add QR code
        const qrCode = await generateQRCode(window.location.origin + '/verify/' + data.certificateId);
        doc.addImage(qrCode, 'PNG', 20, 240, 30, 30);

        // Upload to Firebase Storage
        const pdfBlob = doc.output('blob');
        const storageRef = firebase.storage().ref();
        const certificateRef = storageRef.child(`certificates/${data.studentId}/${Date.now()}.pdf`);
        
        await certificateRef.put(pdfBlob);
        return await certificateRef.getDownloadURL();
    } catch (error) {
        console.error('Error generating PDF:', error);
        throw error;
    }
}

// Load certificate template
function loadCertificateTemplate(type) {
    return new Promise((resolve, reject) => {
        const img = new Image();
        img.onload = () => resolve(img);
        img.onerror = reject;
        img.src = `/assets/templates/${type}_certificate.jpg`;
    });
}

// Generate QR code
function generateQRCode(url) {
    return new Promise((resolve, reject) => {
        QRCode.toDataURL(url, {
            width: 300,
            height: 300,
            color: {
                dark: '#000000',
                light: '#ffffff'
            }
        }, (err, url) => {
            if (err) reject(err);
            else resolve(url);
        });
    });
}

// Load certificates
async function loadCertificates() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        let certificatesQuery = db.collection('certificates');
        
        if (userData.role === 'student') {
            certificatesQuery = certificatesQuery.where('studentId', '==', user.uid);
        } else if (userData.role === 'admin') {
            certificatesQuery = certificatesQuery.where('issuedBy', '==', user.uid);
        }

        const certificates = await certificatesQuery.orderBy('issuedAt', 'desc').get();
        const certificatesList = document.getElementById('certificatesList');
        
        if (!certificatesList) return;

        certificatesList.innerHTML = '';

        certificates.forEach(doc => {
            const certificate = doc.data();
            certificatesList.innerHTML += `
                <div class="certificate-card">
                    <div class="certificate-icon">
                        <i class="material-icons">workspace_premium</i>
                    </div>
                    <div class="certificate-info">
                        <h4>${certificate.title}</h4>
                        <p>${certificate.studentName}</p>
                        <p class="certificate-date">
                            Issued on ${new Date(certificate.date).toLocaleDateString()}
                        </p>
                    </div>
                    <div class="certificate-actions">
                        <a href="${certificate.url}" target="_blank" class="primary-button">
                            <i class="material-icons">download</i>
                            Download
                        </a>
                        <button onclick="verifyCertificate('${doc.id}')" class="secondary-button">
                            <i class="material-icons">verified</i>
                            Verify
                        </button>
                    </div>
                </div>
            `;
        });

        if (certificates.empty) {
            certificatesList.innerHTML = `
                <div class="no-certificates">
                    <i class="material-icons">emoji_events</i>
                    <p>No certificates available</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading certificates:', error);
        showToast('Error loading certificates', 'error');
    }
}

// Verify certificate
async function verifyCertificate(certificateId) {
    try {
        const certificateDoc = await db.collection('certificates').doc(certificateId).get();
        
        if (!certificateDoc.exists) {
            showToast('Certificate not found', 'error');
            return;
        }

        const certificate = certificateDoc.data();
        
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Certificate Verification</h2>
                <div class="verification-details">
                    <p><strong>Certificate ID:</strong> ${certificateId}</p>
                    <p><strong>Student Name:</strong> ${certificate.studentName}</p>
                    <p><strong>Roll No:</strong> ${certificate.rollNo}</p>
                    <p><strong>Title:</strong> ${certificate.title}</p>
                    <p><strong>Issue Date:</strong> ${new Date(certificate.date).toLocaleDateString()}</p>
                    <div class="qr-code">
                        <img src="${certificate.qrCode}" alt="QR Code">
                    </div>
                </div>
                <div class="modal-actions">
                    <button onclick="closeModal()" class="primary-button">Close</button>
                </div>
            </div>
        `;

        document.body.appendChild(modal);
    } catch (error) {
        console.error('Error verifying certificate:', error);
        showToast('Error verifying certificate', 'error');
    }
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeCertificateModule();
        }
    });
}); 