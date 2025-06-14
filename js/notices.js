// Notice Board Module

// Initialize notice board
function initializeNoticeBoard() {
    const noticeBoard = document.getElementById('noticeBoard');
    if (!noticeBoard) return;

    // Check user role
    const userData = JSON.parse(sessionStorage.getItem('userData'));
    const canPost = ['admin', 'hod'].includes(userData.role);

    noticeBoard.innerHTML = `
        ${canPost ? `
            <div class="notice-form">
                <h2>Post New Notice</h2>
                <form id="noticeForm">
                    <div class="form-group">
                        <input type="text" id="noticeTitle" placeholder="Notice Title" required>
                    </div>
                    <div class="form-group">
                        <textarea id="noticeContent" placeholder="Notice Content" required></textarea>
                    </div>
                    <div class="form-group">
                        <label>Target Audience:</label>
                        <div class="checkbox-group">
                            <label>
                                <input type="checkbox" name="audience" value="student"> Students
                            </label>
                            <label>
                                <input type="checkbox" name="audience" value="faculty"> Faculty
                            </label>
                            <label>
                                <input type="checkbox" name="audience" value="hod"> HoDs
                            </label>
                        </div>
                    </div>
                    <button type="submit" class="primary-button">Post Notice</button>
                </form>
            </div>
        ` : ''}
        <div class="notices-container">
            <h2>Notices</h2>
            <div id="noticesList"></div>
        </div>
    `;

    if (canPost) {
        document.getElementById('noticeForm').addEventListener('submit', handleNoticeSubmit);
    }

    loadNotices();
}

// Handle notice submission
async function handleNoticeSubmit(e) {
    e.preventDefault();
    showLoadingSpinner();

    try {
        const title = document.getElementById('noticeTitle').value;
        const content = document.getElementById('noticeContent').value;
        const audience = Array.from(document.getElementsByName('audience'))
            .filter(checkbox => checkbox.checked)
            .map(checkbox => checkbox.value);

        if (!title || !content || audience.length === 0) {
            showToast('Please fill all required fields', 'error');
            return;
        }

        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        // Create notice document
        const noticeRef = await db.collection('notices').add({
            title,
            content,
            targetAudience: audience,
            postedBy: user.uid,
            postedByName: userData.fullName,
            postedByRole: userData.role,
            department: userData.department,
            postedAt: firebase.firestore.FieldValue.serverTimestamp(),
            status: 'active'
        });

        showToast('Notice posted successfully', 'success');
        document.getElementById('noticeForm').reset();

        // Send notifications
        notificationsService.sendNoticeNotification({
            id: noticeRef.id,
            title,
            targetAudience: audience
        });

        // Refresh notices list
        loadNotices();
    } catch (error) {
        console.error('Error posting notice:', error);
        showToast('Error posting notice', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Load notices
async function loadNotices() {
    try {
        const user = auth.currentUser;
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        // Get notices for user's role
        const notices = await db.collection('notices')
            .where('targetAudience', 'array-contains', userData.role)
            .where('status', '==', 'active')
            .orderBy('postedAt', 'desc')
            .get();

        const noticesList = document.getElementById('noticesList');
        if (!noticesList) return;

        noticesList.innerHTML = '';

        notices.forEach(doc => {
            const notice = doc.data();
            const date = notice.postedAt.toDate();
            
            noticesList.innerHTML += `
                <div class="notice-card">
                    <div class="notice-header">
                        <h3>${notice.title}</h3>
                        <span class="notice-date">
                            ${date.toLocaleDateString()} ${date.toLocaleTimeString()}
                        </span>
                    </div>
                    <div class="notice-content">
                        ${notice.content}
                    </div>
                    <div class="notice-footer">
                        <span class="notice-author">
                            Posted by: ${notice.postedByName} (${notice.postedByRole})
                        </span>
                        ${['admin', 'hod'].includes(userData.role) ? `
                            <button onclick="deleteNotice('${doc.id}')" class="danger-button">
                                Delete
                            </button>
                        ` : ''}
                    </div>
                </div>
            `;
        });

        // If no notices
        if (notices.empty) {
            noticesList.innerHTML = `
                <div class="no-notices">
                    <i class="material-icons">notifications_off</i>
                    <p>No notices to display</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading notices:', error);
        showToast('Error loading notices', 'error');
    }
}

// Delete notice
async function deleteNotice(noticeId) {
    if (!confirm('Are you sure you want to delete this notice?')) return;

    showLoadingSpinner();

    try {
        await db.collection('notices').doc(noticeId).update({
            status: 'deleted',
            deletedAt: firebase.firestore.FieldValue.serverTimestamp(),
            deletedBy: auth.currentUser.uid
        });

        showToast('Notice deleted successfully', 'success');
        loadNotices();
    } catch (error) {
        console.error('Error deleting notice:', error);
        showToast('Error deleting notice', 'error');
    } finally {
        hideLoadingSpinner();
    }
}

// Initialize module
document.addEventListener('DOMContentLoaded', () => {
    auth.onAuthStateChanged(user => {
        if (user) {
            initializeNoticeBoard();
        }
    });
}); 