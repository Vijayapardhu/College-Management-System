// DOM Elements
const loginForm = document.getElementById('loginForm');
const loginSection = document.getElementById('loginSection');
const dashboardSection = document.getElementById('dashboardSection');
const errorMessage = document.getElementById('errorMessage');

// Initialize Firebase Auth State Observer
auth.onAuthStateChanged((user) => {
    console.log('Auth state changed:', user ? 'User logged in' : 'No user');
    if (user) {
        handleSuccessfulLogin(user);
    } else {
        showLoginForm();
    }
});

// Login Form Submit Handler
loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearError();
    showLoading();

    const userId = document.getElementById('userId').value;
    const password = document.getElementById('password').value;

    try {
        console.log('Attempting login for user ID:', userId);
        
        // First, get user data from Firestore using userId
        const userSnapshot = await db.collection('users')
            .where('userId', '==', userId)
            .limit(1)
            .get();

        if (userSnapshot.empty) {
            throw new Error('User ID not found. Please check your User ID and try again.');
        }

        const userData = userSnapshot.docs[0].data();
        console.log('User found:', userData.role);

        // Attempt to sign in with email and password
        try {
            const email = `${userId}@cms.edu`;
            console.log('Attempting authentication with email:', email);
            
            const userCredential = await auth.signInWithEmailAndPassword(email, password);
            console.log('Authentication successful');
            
            // Update last login timestamp
            await db.collection('users').doc(userCredential.user.uid).update({
                lastLogin: new Date().toISOString()
            });

            // Store user role in session storage
            sessionStorage.setItem('userRole', userData.role);
            sessionStorage.setItem('userData', JSON.stringify(userData));

            handleSuccessfulLogin(userCredential.user);
        } catch (authError) {
            console.error('Authentication error:', authError);
            if (authError.code === 'auth/wrong-password') {
                showError('Incorrect password. The default password is "eduvision"');
            } else if (authError.code === 'auth/user-not-found') {
                showError('User not found. Please check your User ID.');
            } else {
                showError('Login failed: ' + authError.message);
            }
        }
    } catch (error) {
        console.error('Login error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
});

// Handle successful login
async function handleSuccessfulLogin(user) {
    try {
        console.log('Handling successful login for:', user.email);
        
        // Get user data
        const userDoc = await db.collection('users').doc(user.uid).get();
        const userData = userDoc.data();

        if (!userData) {
            console.error('No user data found in Firestore');
            showError('User data not found. Please contact administrator.');
            auth.signOut();
            return;
        }

        console.log('User role:', userData.role);

        // Hide login form and show appropriate dashboard
        loginSection.classList.add('hidden');
        dashboardSection.classList.remove('hidden');

        // Show appropriate dashboard based on role
        switch(userData.role) {
            case 'admin':
                loadAdminDashboard();
                break;
            case 'faculty':
                loadFacultyDashboard();
                break;
            case 'student':
                loadStudentDashboard();
                break;
            default:
                console.error('Unknown user role:', userData.role);
                showError('Invalid user role. Please contact administrator.');
                auth.signOut();
        }
    } catch (error) {
        console.error('Error in handleSuccessfulLogin:', error);
        showError('Error loading dashboard: ' + error.message);
    }
}

// Show login form
function showLoginForm() {
    console.log('Showing login form');
    dashboardSection.classList.add('hidden');
    loginSection.classList.remove('hidden');
    loginForm.reset();
    clearError();
}

// Error handling functions
function showError(message) {
    console.error('Error:', message);
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function clearError() {
    errorMessage.textContent = '';
    errorMessage.classList.add('hidden');
}

// Loading spinner functions
function showLoading() {
    document.getElementById('loadingSpinner').classList.remove('hidden');
}

function hideLoading() {
    document.getElementById('loadingSpinner').classList.add('hidden');
}

// Logout handler
document.getElementById('logoutBtn')?.addEventListener('click', () => {
    auth.signOut().then(() => {
        console.log('User signed out');
        sessionStorage.clear();
        showLoginForm();
    }).catch((error) => {
        console.error('Error signing out:', error);
        showError('Error signing out: ' + error.message);
    });
});