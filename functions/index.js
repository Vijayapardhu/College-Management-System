const functions = require('firebase-functions');
const admin = require('firebase-admin');
admin.initializeApp();

// Send notification
exports.sendNotification = functions.https.onCall(async (data, context) => {
    // Verify authentication
    if (!context.auth) {
        throw new functions.https.HttpsError('unauthenticated', 'User must be authenticated');
    }

    try {
        // Send notification
        await admin.messaging().send(data);
        return { success: true };
    } catch (error) {
        console.error('Error sending notification:', error);
        throw new functions.https.HttpsError('internal', error.message);
    }
});

// Trigger notification when new marks are uploaded
exports.onMarksUploaded = functions.firestore
    .document('marks/{markId}')
    .onCreate(async (snap, context) => {
        const markData = snap.data();
        
        try {
            // Get student data
            const studentDoc = await admin.firestore()
                .collection('users')
                .doc(markData.studentId)
                .get();
            
            if (!studentDoc.exists) return;
            
            const studentData = studentDoc.data();
            const fcmToken = studentData.fcmToken;
            
            if (!fcmToken) return;

            // Get test data
            const testDoc = await admin.firestore()
                .collection('tests')
                .doc(markData.testId)
                .get();
            
            const testData = testDoc.data();

            // Send notification
            await admin.messaging().send({
                notification: {
                    title: 'New Marks Available',
                    body: `Your marks for ${testData.name} have been uploaded`
                },
                data: {
                    type: 'marks',
                    testId: markData.testId,
                    score: markData.score.toString()
                },
                token: fcmToken
            });
        } catch (error) {
            console.error('Error in onMarksUploaded:', error);
        }
    });

// Trigger notification when new notice is posted
exports.onNoticeCreated = functions.firestore
    .document('notices/{noticeId}')
    .onCreate(async (snap, context) => {
        const notice = snap.data();
        
        try {
            // Send to all target audiences
            for (const audience of notice.targetAudience) {
                await admin.messaging().send({
                    notification: {
                        title: 'New Notice',
                        body: notice.title
                    },
                    data: {
                        type: 'notice',
                        noticeId: context.params.noticeId
                    },
                    topic: `role_${audience}`
                });
            }
        } catch (error) {
            console.error('Error in onNoticeCreated:', error);
        }
    });

// Trigger notification when leave request status changes
exports.onLeaveStatusUpdate = functions.firestore
    .document('leaveRequests/{requestId}')
    .onUpdate(async (change, context) => {
        const newData = change.after.data();
        const previousData = change.before.data();
        
        // Only send notification if status has changed
        if (newData.status === previousData.status) return;
        
        try {
            // Get student data
            const studentDoc = await admin.firestore()
                .collection('users')
                .doc(newData.studentId)
                .get();
            
            if (!studentDoc.exists) return;
            
            const studentData = studentDoc.data();
            const fcmToken = studentData.fcmToken;
            
            if (!fcmToken) return;

            // Send notification
            await admin.messaging().send({
                notification: {
                    title: 'Leave Request Update',
                    body: `Your leave request has been ${newData.status}`
                },
                data: {
                    type: 'leave',
                    requestId: context.params.requestId,
                    status: newData.status
                },
                token: fcmToken
            });
        } catch (error) {
            console.error('Error in onLeaveStatusUpdate:', error);
        }
    });

// Trigger notification when new material is uploaded
exports.onMaterialUploaded = functions.firestore
    .document('materials/{materialId}')
    .onCreate(async (snap, context) => {
        const material = snap.data();
        
        try {
            // Send notification to department
            await admin.messaging().send({
                notification: {
                    title: 'New Study Material',
                    body: `New material uploaded: ${material.title}`
                },
                data: {
                    type: 'material',
                    materialId: context.params.materialId
                },
                topic: `dept_${material.department}`
            });
        } catch (error) {
            console.error('Error in onMaterialUploaded:', error);
        }
    });

// Trigger notification when complaint status changes
exports.onComplaintStatusUpdate = functions.firestore
    .document('complaints/{complaintId}')
    .onUpdate(async (change, context) => {
        const newData = change.after.data();
        const previousData = change.before.data();
        
        // Only send notification if status has changed
        if (newData.status === previousData.status) return;
        
        try {
            // Get user data
            const userDoc = await admin.firestore()
                .collection('users')
                .doc(newData.raisedBy)
                .get();
            
            if (!userDoc.exists) return;
            
            const userData = userDoc.data();
            const fcmToken = userData.fcmToken;
            
            if (!fcmToken) return;

            // Send notification
            await admin.messaging().send({
                notification: {
                    title: 'Complaint Update',
                    body: `Your complaint status has been updated to ${newData.status}`
                },
                data: {
                    type: 'complaint',
                    complaintId: context.params.complaintId,
                    status: newData.status
                },
                token: fcmToken
            });
        } catch (error) {
            console.error('Error in onComplaintStatusUpdate:', error);
        }
    }); 