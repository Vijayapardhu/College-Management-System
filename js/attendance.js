// QR Code Generation for Faculty
async function generateAttendanceQR(classId, subjectId) {
    try {
        const timestamp = Date.now();
        const facultyId = auth.currentUser.uid;
        
        // Get faculty data
        const facultyDoc = await db.collection('users').doc(facultyId).get();
        const facultyData = facultyDoc.data();
        
        // Verify faculty teaches this subject
        if (!facultyData.subjects.includes(subjectId)) {
            throw new Error('You are not authorized to take attendance for this subject');
        }

        // Create session data with enhanced security
        const sessionData = {
            facultyId: facultyId,
            facultyName: facultyData.fullName,
            classId: classId,
            subjectId: subjectId,
            timestamp: timestamp,
            validFor: 300, // 5 minutes in seconds
            location: null, // Will be set by faculty's device
            deviceId: null, // Will be set by faculty's device
            active: true,
            attendanceCount: 0
        };
        
        // Generate a unique session ID with additional entropy
        const sessionId = `${classId}_${subjectId}_${timestamp}_${Math.random().toString(36).substring(7)}`;
        
        // Get device location if available
        if (navigator.geolocation) {
            try {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject);
                });
                
                sessionData.location = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
            } catch (error) {
                console.warn('Location access denied:', error);
            }
        }

        // Get device info
        sessionData.deviceId = await getDeviceFingerprint();

        // Store session data in Firestore (for persistence) and Realtime Database (for real-time updates)
        await Promise.all([
            db.collection('attendance_sessions').doc(sessionId).set(sessionData),
            realdb.ref(`attendance_sessions/${sessionId}`).set(sessionData)
        ]);

        // Generate QR Code with encrypted data
        const qrData = await encryptSessionData(sessionId, sessionData);
        const qrContainer = document.getElementById("qrCodeContainer");
        qrContainer.innerHTML = ''; // Clear previous QR code

        // Create QR code with session data
        const qr = new QRCode(qrContainer, {
            text: qrData,
            width: 200,
            height: 200
        });

        // Set up real-time listener for attendance count
        realdb.ref(`attendance_sessions/${sessionId}/attendanceCount`).on('value', (snapshot) => {
            const count = snapshot.val() || 0;
            document.getElementById('attendanceCount').textContent = count;
        });

        // Set timer to invalidate QR code
        const timer = setTimeout(async () => {
            await invalidateSession(sessionId);
            qrContainer.innerHTML = '<p>QR Code Expired</p>';
        }, 300000); // 5 minutes

        // Store timer reference
        sessionStorage.setItem('currentSessionTimer', timer);
        sessionStorage.setItem('currentSessionId', sessionId);

        return sessionId;
    } catch (error) {
        console.error('Error generating QR code:', error);
        throw error;
    }
}

// Mark Attendance for Students
async function markAttendance(sessionId, qrData) {
    try {
        // Verify session exists and is active
        const sessionDoc = await db.collection('attendance_sessions').doc(sessionId).get();
        if (!sessionDoc.exists) {
            throw new Error('Invalid session');
        }

        const sessionData = sessionDoc.data();
        if (!sessionData.active) {
            throw new Error('Session has expired');
        }

        const studentId = auth.currentUser.uid;
        const timestamp = Date.now();

        // Check if student has already marked attendance
        const existingAttendance = await db.collection('attendance')
            .where('sessionId', '==', sessionId)
            .where('studentId', '==', studentId)
            .get();

        if (!existingAttendance.empty) {
            throw new Error('Attendance already marked for this session');
        }

        // Get student data
        const studentDoc = await db.collection('users').doc(studentId).get();
        const studentData = studentDoc.data();

        // Verify student belongs to the class
        if (studentData.section !== sessionData.classId) {
            throw new Error('You are not authorized to mark attendance for this class');
        }

        // Get student's device location
        let studentLocation = null;
        if (navigator.geolocation) {
            try {
                const position = await new Promise((resolve, reject) => {
                    navigator.geolocation.getCurrentPosition(resolve, reject);
                });
                
                studentLocation = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    accuracy: position.coords.accuracy
                };
            } catch (error) {
                throw new Error('Location access required to mark attendance');
            }
        }

        // Verify student's location is close to faculty's location
        if (sessionData.location && studentLocation) {
            const distance = calculateDistance(
                sessionData.location.latitude,
                sessionData.location.longitude,
                studentLocation.latitude,
                studentLocation.longitude
            );
            
            if (distance > 100) { // 100 meters threshold
                throw new Error('You are too far from the class location');
            }
        }

        // Get student's device fingerprint
        const studentDeviceId = await getDeviceFingerprint();

        // Create attendance record with security metadata
        const attendanceData = {
            studentId: studentId,
            studentName: studentData.fullName,
            rollNumber: studentData.rollNumber,
            classId: sessionData.classId,
            subjectId: sessionData.subjectId,
            facultyId: sessionData.facultyId,
            facultyName: sessionData.facultyName,
            timestamp: timestamp,
            sessionId: sessionId,
            location: studentLocation,
            deviceId: studentDeviceId,
            verified: true
        };

        // Save attendance record
        await db.collection('attendance').add(attendanceData);

        // Update attendance count in session
        await realdb.ref(`attendance_sessions/${sessionId}/attendanceCount`)
            .transaction(current => (current || 0) + 1);

        // Update student's attendance stats
        await updateStudentAttendanceStats(studentId, sessionData.subjectId);

        return true;
    } catch (error) {
        console.error('Error marking attendance:', error);
        throw error;
    }
}

// Helper Functions

// Get device fingerprint using available device data
async function getDeviceFingerprint() {
    const deviceData = {
        userAgent: navigator.userAgent,
        language: navigator.language,
        platform: navigator.platform,
        screenResolution: `${window.screen.width}x${window.screen.height}`,
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        timestamp: Date.now()
    };
    
    // Create a hash of the device data
    const deviceString = JSON.stringify(deviceData);
    const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(deviceString));
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// Calculate distance between two points using Haversine formula
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371e3; // Earth's radius in meters
    const φ1 = lat1 * Math.PI/180;
    const φ2 = lat2 * Math.PI/180;
    const Δφ = (lat2-lat1) * Math.PI/180;
    const Δλ = (lon2-lon1) * Math.PI/180;

    const a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
            Math.cos(φ1) * Math.cos(φ2) *
            Math.sin(Δλ/2) * Math.sin(Δλ/2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

    return R * c; // Distance in meters
}

// Encrypt session data for QR code
async function encryptSessionData(sessionId, sessionData) {
    try {
        // Create a simple encrypted string for QR code
        // In production, use proper encryption
        const data = {
            id: sessionId,
            timestamp: sessionData.timestamp,
            hash: await getDeviceFingerprint()
        };
        return btoa(JSON.stringify(data));
    } catch (error) {
        console.error('Error encrypting session data:', error);
        throw error;
    }
}

// Invalidate session
async function invalidateSession(sessionId) {
    try {
        await Promise.all([
            db.collection('attendance_sessions').doc(sessionId).update({
                active: false
            }),
            realdb.ref(`attendance_sessions/${sessionId}`).update({
                active: false
            })
        ]);

        // Clear any existing timer
        const timer = sessionStorage.getItem('currentSessionTimer');
        if (timer) {
            clearTimeout(timer);
            sessionStorage.removeItem('currentSessionTimer');
        }

        // Remove realtime listener
        realdb.ref(`attendance_sessions/${sessionId}/attendanceCount`).off();
    } catch (error) {
        console.error('Error invalidating session:', error);
        throw error;
    }
}

// Update student's attendance statistics
async function updateStudentAttendanceStats(studentId, subjectId) {
    try {
        const studentRef = db.collection('users').doc(studentId);
        
        await db.runTransaction(async (transaction) => {
            const studentDoc = await transaction.get(studentRef);
            const studentData = studentDoc.data();
            
            // Initialize or update subject attendance
            if (!studentData.attendance.subjects[subjectId]) {
                studentData.attendance.subjects[subjectId] = {
                    present: 1,
                    total: 1
                };
            } else {
                studentData.attendance.subjects[subjectId].present += 1;
                studentData.attendance.subjects[subjectId].total += 1;
            }
            
            // Update overall attendance
            let totalPresent = 0;
            let totalClasses = 0;
            Object.values(studentData.attendance.subjects).forEach(subject => {
                totalPresent += subject.present;
                totalClasses += subject.total;
            });
            
            studentData.attendance.overall = (totalPresent / totalClasses) * 100;
            
            transaction.update(studentRef, {
                attendance: studentData.attendance
            });
        });
    } catch (error) {
        console.error('Error updating attendance stats:', error);
        throw error;
    }
}

// Get Attendance Report for Faculty
async function getAttendanceReport(classId, subjectId, startDate, endDate) {
    try {
        const attendanceRef = db.collection('attendance')
            .where('classId', '==', classId)
            .where('subjectId', '==', subjectId);
            
        const snapshot = await attendanceRef.get();
        
        const attendanceData = {};
        snapshot.forEach(doc => {
            const data = doc.data();
            if (!attendanceData[data.studentId]) {
                attendanceData[data.studentId] = {
                    studentName: data.studentName,
                    present: 0,
                    total: 0
                };
            }
            attendanceData[data.studentId].present += 1;
        });
        
        // Calculate total classes
        const totalClasses = await db.collection('attendance_sessions')
            .where('classId', '==', classId)
            .where('subjectId', '==', subjectId)
            .get();
            
        const total = totalClasses.size;
        
        // Calculate percentage for each student
        Object.values(attendanceData).forEach(student => {
            student.total = total;
            student.percentage = (student.present / total) * 100;
        });
        
        return attendanceData;
    } catch (error) {
        console.error('Error getting attendance report:', error);
        throw error;
    }
}

// Get Student's Personal Attendance
async function getStudentAttendance(studentId, subjectId) {
    try {
        const attendanceRef = db.collection('attendance')
            .where('studentId', '==', studentId)
            .where('subjectId', '==', subjectId);
            
        const snapshot = await attendanceRef.get();
        const present = snapshot.size;
        
        // Get total classes
        const totalClasses = await db.collection('attendance_sessions')
            .where('subjectId', '==', subjectId)
            .get();
            
        const total = totalClasses.size;
        const percentage = (present / total) * 100;
        
        return {
            present,
            total,
            percentage
        };
    } catch (error) {
        console.error('Error getting student attendance:', error);
        throw error;
    }
}

// Initialize QR Scanner (for students)
function initQRScanner(videoElement) {
    // Check if browser supports getUserMedia
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        alert('Sorry, your browser does not support webcam access');
        return;
    }
    
    navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
        .then(stream => {
            videoElement.srcObject = stream;
            videoElement.play();
            
            // Start QR code detection
            detectQRCode(videoElement);
        })
        .catch(error => {
            console.error('Error accessing camera:', error);
            alert('Could not access camera');
        });
}

// Detect QR Code from video stream
function detectQRCode(videoElement) {
    // This is a placeholder for QR code detection logic
    // You would typically use a library like jsQR here
    // For now, we'll simulate with a button click
    document.getElementById('scanButton').addEventListener('click', () => {
        // Simulate successful QR code scan
        const sessionId = prompt('Enter session ID (simulating QR scan):');
        if (sessionId) {
            markAttendance(sessionId)
                .then(() => alert('Attendance marked successfully!'))
                .catch(error => alert('Error: ' + error.message));
        }
    });
}