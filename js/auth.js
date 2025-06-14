// Firebase Authentication Module

// Initialize Firebase Auth
const auth = firebase.auth();
const db = firebase.firestore();

// Handle login form submission
async function handleLogin(e) {
    e.preventDefault();
    clearError();
    showLoading();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        // Sign in user
        const userCredential = await auth.signInWithEmailAndPassword(email, password);
        
        // Get user data from Firestore
        const userDoc = await db.collection('users').doc(userCredential.user.uid).get();
        
        if (!userDoc.exists) {
            throw new Error('User data not found');
        }

        const userData = userDoc.data();
        
        // Store user data in session
        sessionStorage.setItem('userData', JSON.stringify({
            userId: userCredential.user.uid,
            email: userCredential.user.email,
            role: userData.role,
            fullName: userData.fullName,
            department: userData.department,
            section: userData.section
        }));

        // Route to appropriate dashboard based on role
        await handleSuccessfulLogin(userData);

    } catch (error) {
        console.error('Login error:', error);
        showError(error.message);
    } finally {
        hideLoading();
    }
}

// Handle successful login and routing
async function handleSuccessfulLogin(userData) {
    switch (userData.role) {
        case 'student':
            window.location.href = 'student.html';
            break;
        case 'faculty':
            window.location.href = 'faculty.html';
            break;
        case 'hod':
            window.location.href = 'hod.html';
            break;
        case 'admin':
            window.location.href = 'admin.html';
            break;
        default:
            throw new Error('Invalid user role');
    }
}

// Handle logout
function handleLogout() {
    auth.signOut()
        .then(() => {
            sessionStorage.clear();
            window.location.href = 'index.html';
        })
        .catch(error => {
            console.error('Logout error:', error);
            showError('Error logging out');
        });
}

// Check authentication state
function checkAuth() {
    auth.onAuthStateChanged(async user => {
        if (user) {
            try {
                const userDoc = await db.collection('users').doc(user.uid).get();
                if (!userDoc.exists) {
                    auth.signOut();
                    return;
                }

                const userData = userDoc.data();
                const currentPage = window.location.pathname.split('/').pop();

                // Redirect if user is on wrong page
                const rolePages = {
                    'student.html': ['student'],
                    'faculty.html': ['faculty'],
                    'hod.html': ['hod'],
                    'admin.html': ['admin'],
                    'index.html': []
                };

                const allowedRoles = rolePages[currentPage] || [];
                if (!allowedRoles.includes(userData.role)) {
                    handleSuccessfulLogin(userData);
                }
            } catch (error) {
                console.error('Auth check error:', error);
                auth.signOut();
            }
        } else if (window.location.pathname.split('/').pop() !== 'index.html') {
            window.location.href = 'index.html';
        }
    });
}

// Show login form
function showLoginForm() {
    const authSection = document.querySelector('.auth-section');
    if (!authSection) return;

    authSection.innerHTML = `
        <h2>Login to CMS</h2>
        <form id="loginForm">
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" required>
            </div>
            <div class="form-group">
                <label for="password">Password</label>
                <input type="password" id="password" required>
            </div>
            <div class="error-message" id="errorMessage"></div>
            <button type="submit">Login</button>
        </form>
    `;

    document.getElementById('loginForm').addEventListener('submit', handleLogin);
}

// Error handling functions
function showError(message) {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.textContent = message;
        errorElement.classList.add('show');
    }
}

function clearError() {
    const errorElement = document.getElementById('errorMessage');
    if (errorElement) {
        errorElement.textContent = '';
        errorElement.classList.remove('show');
    }
}

// Loading state functions
function showLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) loadingSpinner.classList.remove('hidden');
}

function hideLoading() {
    const loadingSpinner = document.getElementById('loadingSpinner');
    if (loadingSpinner) loadingSpinner.classList.add('hidden');
}

// Initialize auth module
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    showLoginForm();
});