// Study Materials Module

// Initialize upload section
function initializeUploadSection() {
    const uploadSection = document.getElementById('uploadSection');
    if (!uploadSection) return;

    uploadSection.innerHTML = `
        <div class="upload-zone" id="dropZone">
            <i class="material-icons">cloud_upload</i>
            <p>Drag & drop files here or click to select</p>
            <input type="file" id="fileInput" accept=".pdf,.doc,.docx" multiple hidden>
        </div>
        <div class="form-group">
            <select id="materialSubject" required>
                <option value="">Select Subject</option>
            </select>
        </div>
        <div class="form-group">
            <input type="text" id="materialTopic" placeholder="Topic/Chapter" required>
        </div>
        <div class="form-group">
            <input type="text" id="materialTags" placeholder="Tags (comma separated)">
        </div>
        <button id="uploadButton" class="primary-button" disabled>
            Upload Materials
        </button>
        <div id="uploadProgress" class="upload-progress hidden"></div>
        <div id="recentUploads" class="recent-uploads">
            <h3>Recent Uploads</h3>
            <div id="uploadsList"></div>
        </div>
    `;

    // Load subjects
    loadFacultySubjects();

    // Setup drag and drop
    setupDragAndDrop();

    // Setup file input
    document.getElementById('dropZone').addEventListener('click', () => {
        document.getElementById('fileInput').click();
    });

    document.getElementById('fileInput').addEventListener('change', handleFileSelect);
    document.getElementById('uploadButton').addEventListener('click', handleMaterialUpload);
}

// Setup drag and drop
function setupDragAndDrop() {
    const dropZone = document.getElementById('dropZone');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    dropZone.addEventListener('drop', handleDrop, false);
}

// Prevent default drag behaviors
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

// Highlight drop zone
function highlight(e) {
    document.getElementById('dropZone').classList.add('dragover');
}

// Remove highlight
function unhighlight(e) {
    document.getElementById('dropZone').classList.remove('dragover');
}

// Handle file drop
function handleDrop(e) {
    const dt = e.dataTransfer;
    const files = dt.files;
    handleFiles(files);
}

// Handle file selection
function handleFileSelect(e) {
    const files = e.target.files;
    handleFiles(files);
}

// Process selected files
function handleFiles(files) {
    if (files.length > 0) {
        document.getElementById('uploadButton').disabled = false;
        showToast(`${files.length} file(s) selected`, 'info');
    }
}

// Handle material upload
async function handleMaterialUpload() {
    const files = document.getElementById('fileInput').files;
    const subject = document.getElementById('materialSubject').value;
    const topic = document.getElementById('materialTopic').value;
    const tags = document.getElementById('materialTags').value.split(',').map(tag => tag.trim());

    if (!files.length || !subject || !topic) {
        showToast('Please fill all required fields', 'error');
        return;
    }

    showLoadingSpinner();
    const progressDiv = document.getElementById('uploadProgress');
    progressDiv.classList.remove('hidden');

    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const fileName = `${subject}/${topic}/${file.name}`;
            const storageRef = firebase.storage().ref().child(`materials/${fileName}`);

            // Upload file
            const uploadTask = storageRef.put(file);

            // Monitor upload progress
            uploadTask.on('state_changed', 
                (snapshot) => {
                    const progress = (snapshot.bytesTransferred / snapshot.totalBytes) * 100;
                    progressDiv.innerHTML = `Uploading ${file.name}: ${Math.round(progress)}%`;
                },
                (error) => {
                    console.error('Error uploading file:', error);
                    showToast(`Error uploading ${file.name}`, 'error');
                },
                async () => {
                    // Get download URL
                    const downloadURL = await uploadTask.snapshot.ref.getDownloadURL();

                    // Save material metadata to Firestore
                    await db.collection('materials').add({
                        name: file.name,
                        subject: subject,
                        topic: topic,
                        tags: tags,
                        url: downloadURL,
                        uploadedBy: user.uid,
                        department: userData.department,
                        uploadedAt: firebase.firestore.FieldValue.serverTimestamp(),
                        type: file.type,
                        size: file.size
                    });

                    showToast(`${file.name} uploaded successfully`, 'success');

                    if (i === files.length - 1) {
                        // Reset form after all files are uploaded
                        document.getElementById('fileInput').value = '';
                        document.getElementById('materialTopic').value = '';
                        document.getElementById('materialTags').value = '';
                        document.getElementById('uploadButton').disabled = true;
                        progressDiv.classList.add('hidden');
                        loadRecentUploads();
                    }
                }
            );
        }
    } catch (error) {
        console.error('Error uploading materials:', error);
        showToast('Error uploading materials', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load recent uploads
async function loadRecentUploads() {
    try {
        const user = auth.currentUser;
        const materials = await db.collection('materials')
            .where('uploadedBy', '==', user.uid)
            .orderBy('uploadedAt', 'desc')
            .limit(5)
            .get();

        const uploadsList = document.getElementById('uploadsList');
        if (!uploadsList) return;

        uploadsList.innerHTML = '';

        materials.forEach(doc => {
            const material = doc.data();
            uploadsList.innerHTML += `
                <div class="upload-item">
                    <i class="material-icons">description</i>
                    <div class="upload-info">
                        <div class="upload-name">${material.name}</div>
                        <div class="upload-meta">
                            ${material.subject} - ${material.topic}
                        </div>
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading recent uploads:', error);
        showToast('Error loading recent uploads', 'error');
    }
}

// Load materials for students
async function loadStudentMaterials() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        const materials = await db.collection('materials')
            .where('department', '==', userData.department)
            .orderBy('uploadedAt', 'desc')
            .get();

        const materialsList = document.getElementById('materialsList');
        if (!materialsList) return;

        // Group materials by subject
        const materialsBySubject = {};
        materials.forEach(doc => {
            const material = doc.data();
            if (!materialsBySubject[material.subject]) {
                materialsBySubject[material.subject] = [];
            }
            materialsBySubject[material.subject].push({
                id: doc.id,
                ...material
            });
        });

        // Display materials grouped by subject
        materialsList.innerHTML = '';
        Object.entries(materialsBySubject).forEach(([subject, materials]) => {
            materialsList.innerHTML += `
                <div class="subject-materials">
                    <h3>${subject}</h3>
                    <div class="materials-grid">
                        ${materials.map(material => `
                            <div class="material-card">
                                <div class="material-icon">
                                    <i class="material-icons">description</i>
                                </div>
                                <div class="material-info">
                                    <h4>${material.topic}</h4>
                                    <p>${material.name}</p>
                                    <div class="material-tags">
                                        ${material.tags.map(tag => `
                                            <span class="tag">${tag}</span>
                                        `).join('')}
                                    </div>
                                </div>
                                <a href="${material.url}" target="_blank" class="download-button">
                                    <i class="material-icons">download</i>
                                    Download
                                </a>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        });
    } catch (error) {
        console.error('Error loading materials:', error);
        showToast('Error loading materials', 'error');
    }
}

// Initialize module based on user role
async function initializeMaterialsModule() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        if (userData.role === 'faculty') {
            initializeUploadSection();
            loadRecentUploads();
        } else if (userData.role === 'student') {
            loadStudentMaterials();
        }
    } catch (error) {
        console.error('Error initializing materials module:', error);
        showToast('Error initializing materials module', 'error');
    }
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeMaterialsModule();
        }
    });
}); 