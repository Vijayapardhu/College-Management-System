// Document Management Module

// Initialize document management
function initializeDocumentManagement() {
    const documentContainer = document.getElementById('documentContainer');
    if (!documentContainer) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const isStudent = userData.role === 'student';

    documentContainer.innerHTML = `
        <div class="document-header">
            <h2>My Documents</h2>
            <button onclick="showUploadForm()" class="primary-button">
                <i class="material-icons">upload_file</i>
                Upload Document
            </button>
        </div>
        <div class="documents-grid" id="documentsGrid"></div>
    `;

    // Load documents
    loadDocuments();
}

// Show upload form
function showUploadForm() {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Upload Document</h2>
            <form id="documentForm">
                <div class="form-group">
                    <select id="documentType" required>
                        <option value="">Select Document Type</option>
                        <option value="id">ID Card</option>
                        <option value="marksheet">Mark Sheet</option>
                        <option value="certificate">Certificate</option>
                        <option value="other">Other</option>
                    </select>
                </div>
                <div class="form-group">
                    <input type="text" id="documentTitle" placeholder="Document Title" required>
                </div>
                <div class="form-group">
                    <textarea id="documentDescription" placeholder="Description (optional)"></textarea>
                </div>
                <div class="upload-zone" id="documentDropZone">
                    <i class="material-icons">cloud_upload</i>
                    <p>Drag & drop file here or click to select</p>
                    <input type="file" id="documentFile" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png" hidden>
                </div>
                <div id="uploadProgress" class="upload-progress hidden"></div>
                <div class="modal-actions">
                    <button type="button" onclick="closeModal()" class="secondary-button">
                        Cancel
                    </button>
                    <button type="submit" class="primary-button">
                        Upload
                    </button>
                </div>
            </form>
        </div>
    `;

    document.body.appendChild(modal);

    // Setup drag and drop
    setupDocumentUpload();

    // Handle form submission
    document.getElementById('documentForm').addEventListener('submit', handleDocumentUpload);
}

// Setup document upload
function setupDocumentUpload() {
    const dropZone = document.getElementById('documentDropZone');
    const fileInput = document.getElementById('documentFile');

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

// Handle document drop
function handleDocumentDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleDocumentFiles(files);
}

// Handle document selection
function handleDocumentSelect(e) {
    const files = e.target.files;
    handleDocumentFiles(files);
}

// Process document files
function handleDocumentFiles(files) {
    if (files.length !== 1) {
        showToast('Please select a single file', 'error');
        return;
    }

    const file = files[0];
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (file.size > maxSize) {
        showToast('File size should not exceed 5MB', 'error');
        return;
    }

    document.getElementById('documentFile').files = files;
    showToast('File selected', 'info');
}

// Handle document upload
async function handleDocumentUpload(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const file = document.getElementById('documentFile').files[0];
        if (!file) {
            showToast('Please select a file', 'error');
            return;
        }

        const documentData = {
            type: document.getElementById('documentType').value,
            title: document.getElementById('documentTitle').value,
            description: document.getElementById('documentDescription').value || '',
            uploadedBy: auth.currentUser.uid,
            uploadedAt: firebase.firestore.FieldValue.serverTimestamp(),
            fileType: file.type,
            fileName: file.name
        };

        // Upload file to Firebase Storage
        const storageRef = firebase.storage().ref();
        const documentRef = storageRef.child(`documents/${auth.currentUser.uid}/${Date.now()}_${file.name}`);
        
        // Show upload progress
        const progressDiv = document.getElementById('uploadProgress');
        progressDiv.classList.remove('hidden');

        const uploadTask = documentRef.put(file);

        uploadTask.on('state_changed', 
            (snapshot) => {
                const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
                progressDiv.innerHTML = `Uploading: ${Math.round(progress)}%`;
            },
            (error) => {
                console.error('Error uploading file:', error);
                showToast('Error uploading file', 'error');
            },
            async () => {
                // Get download URL
                const downloadURL = await uploadTask.snapshot.ref.getDownloadURL();

                // Save document metadata to Firestore
                await db.collection('documents').add({
                    ...documentData,
                    url: downloadURL
                });

                showToast('Document uploaded successfully', 'success');
                closeModal();
                loadDocuments();
            }
        );
    } catch (error) {
        console.error('Error uploading document:', error);
        showToast('Error uploading document', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load documents
async function loadDocuments() {
    try {
        const user = auth.currentUser;
        const documents = await db.collection('documents')
            .where('uploadedBy', '==', user.uid)
            .orderBy('uploadedAt', 'desc')
            .get();

        const documentsGrid = document.getElementById('documentsGrid');
        if (!documentsGrid) return;

        documentsGrid.innerHTML = '';

        documents.forEach(doc => {
            const document = doc.data();
            const uploadDate = document.uploadedAt.toDate();
            
            documentsGrid.innerHTML += `
                <div class="document-card">
                    <div class="document-icon">
                        ${getDocumentIcon(document.type)}
                    </div>
                    <div class="document-info">
                        <h4>${document.title}</h4>
                        <p>${document.description}</p>
                        <p class="document-meta">
                            Uploaded on ${uploadDate.toLocaleDateString()}
                        </p>
                    </div>
                    <div class="document-actions">
                        <a href="${document.url}" target="_blank" class="primary-button">
                            <i class="material-icons">download</i>
                            Download
                        </a>
                        <button onclick="deleteDocument('${doc.id}')" class="danger-button">
                            <i class="material-icons">delete</i>
                            Delete
                        </button>
                    </div>
                </div>
            `;
        });

        if (documents.empty) {
            documentsGrid.innerHTML = `
                <div class="no-documents">
                    <i class="material-icons">folder_open</i>
                    <p>No documents uploaded yet</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading documents:', error);
        showToast('Error loading documents', 'error');
    }
}

// Get document icon
function getDocumentIcon(type) {
    const icons = {
        id: 'badge',
        marksheet: 'assessment',
        certificate: 'workspace_premium',
        other: 'description'
    };

    return `<i class="material-icons">${icons[type] || 'description'}</i>`;
}

// Delete document
async function deleteDocument(documentId) {
    if (!confirm('Are you sure you want to delete this document?')) return;

    showLoadingSpinner();

    try {
        // Get document data
        const documentDoc = await db.collection('documents').doc(documentId).get();
        const document = documentDoc.data();

        // Delete file from Storage
        const storageRef = firebase.storage().refFromURL(document.url);
        await storageRef.delete();

        // Delete document metadata from Firestore
        await db.collection('documents').doc(documentId).delete();

        showToast('Document deleted successfully', 'success');
        loadDocuments();
    } catch (error) {
        console.error('Error deleting document:', error);
        showToast('Error deleting document', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeDocumentManagement();
        }
    });
}); 