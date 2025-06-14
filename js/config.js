// Firebase configuration
const firebaseConfig = {
    apiKey: "AIzaSyD8fnRcdgHzaLzG_xLxRu46-IkQO_s-XT8",
    authDomain: "cme-g-63ebf.firebaseapp.com",
    databaseURL: "https://cme-g-63ebf-default-rtdb.firebaseio.com",
    projectId: "cme-g-63ebf",
    storageBucket: "cme-g-63ebf.appspot.com",
    messagingSenderId: "909124913952",
    appId: "1:909124913952:android:781a2d6f8f091754f82545"
};

// Initialize Firebase
firebase.initializeApp(firebaseConfig);

// Initialize services
const auth = firebase.auth();
const db = firebase.firestore();
const storage = firebase.storage();
const realdb = firebase.database();

// Enable persistence for offline capabilities
db.enablePersistence()
    .catch((err) => {
        if (err.code == 'failed-precondition') {
            // Multiple tabs open, persistence can only be enabled in one tab at a time.
            console.log('Multiple tabs open, persistence can only be enabled in one tab at a time.');
        } else if (err.code == 'unimplemented') {
            // The current browser doesn't support all of the features required to enable persistence
            console.log('The current browser doesn\'t support all of the features required to enable persistence');
        }
    });

// Export the services
window.auth = auth;
window.db = db;
window.storage = storage;
window.realdb = realdb;