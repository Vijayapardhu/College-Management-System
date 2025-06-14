// Notifications Service using Firebase Cloud Messaging

class NotificationsService {
    constructor() {
        this.messaging = firebase.messaging();
        this.vapidKey = 'YOUR_VAPID_KEY'; // Replace with your VAPID key
    }

    // Initialize notifications
    async initialize() {
        try {
            const permission = await Notification.requestPermission();
            if (permission === 'granted') {
                // Get registration token
                const token = await this.messaging.getToken({
                    vapidKey: this.vapidKey
                });
                
                // Save the token to user's document
                const user = auth.currentUser;
                if (user) {
                    await db.collection('users').doc(user.uid).update({
                        fcmToken: token
                    });
                }

                // Setup message handler
                this.setupMessageHandler();
            }
        } catch (error) {
            console.error('Error initializing notifications:', error);
        }
    }

    // Setup message handler for foreground messages
    setupMessageHandler() {
        this.messaging.onMessage((payload) => {
            console.log('Message received:', payload);
            this.showNotification(payload);
        });
    }

    // Show notification
    showNotification(payload) {
        const { title, body } = payload.notification;
        
        // Show toast notification
        showToast(body, 'info');

        // Show system notification if supported
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(title, {
                body: body,
                icon: '/assets/logo.png'
            });
        }
    }

    // Subscribe to topics based on user role
    async subscribeToTopics(userData) {
        try {
            // Subscribe to role-specific topics
            await this.messaging.subscribeToTopic(`role_${userData.role}`);
            
            // Subscribe to department topics
            if (userData.department) {
                await this.messaging.subscribeToTopic(`dept_${userData.department}`);
            }

            // Subscribe to class-specific topics for students
            if (userData.role === 'student' && userData.section) {
                await this.messaging.subscribeToTopic(`class_${userData.section}`);
            }

            // Subscribe to subject topics for faculty
            if (userData.role === 'faculty' && userData.subjects) {
                for (const subject of userData.subjects) {
                    await this.messaging.subscribeToTopic(`subject_${subject}`);
                }
            }
        } catch (error) {
            console.error('Error subscribing to topics:', error);
        }
    }

    // Send notification to specific users or topics
    async sendNotification(notification) {
        try {
            const { title, body, data, target } = notification;

            // Prepare notification data
            const message = {
                notification: {
                    title,
                    body
                },
                data: data || {}
            };

            // Add target (topic or token)
            if (target.type === 'topic') {
                message.topic = target.value;
            } else if (target.type === 'token') {
                message.token = target.value;
            }

            // Send notification using Cloud Functions
            const sendNotification = firebase.functions().httpsCallable('sendNotification');
            await sendNotification(message);

            return true;
        } catch (error) {
            console.error('Error sending notification:', error);
            throw error;
        }
    }

    // Send notification for new marks
    async sendMarksNotification(studentId, testData) {
        try {
            // Get student's FCM token
            const studentDoc = await db.collection('users').doc(studentId).get();
            const fcmToken = studentDoc.data().fcmToken;

            if (fcmToken) {
                await this.sendNotification({
                    title: 'New Marks Available',
                    body: `Your marks for ${testData.name} have been uploaded`,
                    data: {
                        type: 'marks',
                        testId: testData.id
                    },
                    target: {
                        type: 'token',
                        value: fcmToken
                    }
                });
            }
        } catch (error) {
            console.error('Error sending marks notification:', error);
        }
    }

    // Send notification for new notice
    async sendNoticeNotification(notice) {
        try {
            // Send to all target audiences
            for (const audience of notice.targetAudience) {
                await this.sendNotification({
                    title: 'New Notice',
                    body: notice.title,
                    data: {
                        type: 'notice',
                        noticeId: notice.id
                    },
                    target: {
                        type: 'topic',
                        value: `role_${audience}`
                    }
                });
            }
        } catch (error) {
            console.error('Error sending notice notification:', error);
        }
    }

    // Send notification for leave request status update
    async sendLeaveStatusNotification(leaveRequest) {
        try {
            // Get student's FCM token
            const studentDoc = await db.collection('users').doc(leaveRequest.studentId).get();
            const fcmToken = studentDoc.data().fcmToken;

            if (fcmToken) {
                await this.sendNotification({
                    title: 'Leave Request Update',
                    body: `Your leave request has been ${leaveRequest.status}`,
                    data: {
                        type: 'leave',
                        requestId: leaveRequest.id
                    },
                    target: {
                        type: 'token',
                        value: fcmToken
                    }
                });
            }
        } catch (error) {
            console.error('Error sending leave status notification:', error);
        }
    }
}

// Create and export notifications service instance
const notificationsService = new NotificationsService();
export default notificationsService; 