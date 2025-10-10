# 🚀 EduVision - Quick Start Guide

## Get Started in 5 Minutes!

This guide will help you set up and test all features of EduVision immediately.

---

## ✅ Current Status

- ✅ Server running at: **http://127.0.0.1:8000/**
- ✅ Admin panel: **http://127.0.0.1:8000/admin/**
- ✅ All features implemented
- ✅ Database migrations applied
- ✅ Ready to use!

---

## 🔐 Login Credentials

### HOD/Admin:
```
Email: admin@admin.com
Password: admin123
URL: http://127.0.0.1:8000/
```

---

## 🎯 Test Each Feature

### 1️⃣ Set Up a Proctor (2 minutes)

**Goal:** Enable a staff member as proctor and assign students

**Steps:**
1. Login as HOD: `admin@admin.com` / `admin123`
2. Sidebar → **"Add Staff"**
3. Create a staff member:
   ```
   Email: faculty@example.com
   Password: faculty123
   First Name: John
   Last Name: Doe
   Gender: M
   Course: Select any
   ```
4. Go to **"Manage Staff"**
5. Find the staff member, click **Edit**
6. Check **"Is proctor"** checkbox
7. Save

**Result:** Staff member is now a proctor! ✅

---

### 2️⃣ Assign Students to Proctor (1 minute)

**Steps:**
1. HOD Dashboard → Sidebar → **"PROCTOR SYSTEM"** → **"Assign Students"**
2. Select Staff: "John Doe"
3. Select Students: Check multiple students
4. Click **Submit**

**Result:** Students assigned to proctor! ✅

---

### 3️⃣ Login as Proctor (Staff) (1 minute)

**Steps:**
1. Logout from HOD
2. Login with: `faculty@example.com` / `faculty123`
3. You'll see **Staff Dashboard**
4. Look at sidebar → **"PROCTOR TOOLS"** section appears!
5. Click **"My Mentees"** → See assigned students
6. Click **"Absentee Reports"** → Generate reports

**Result:** Proctor features integrated in staff account! ✅

---

### 4️⃣ Upload Study Material (2 minutes)

**As Staff:**
1. Sidebar → **"RESOURCES"** → **"Upload Material"**
2. Fill in:
   ```
   Title: Introduction to Python
   Description: Python basics for beginners
   Type: Document (or Link or Video)
   Subject: Select your subject
   Tags: python, programming, basics
   
   For Document: Upload a PDF file
   For Link: Enter URL like: https://python.org
   For Video: YouTube URL like: https://youtube.com/watch?v=...
   ```
3. Submit

**Result:** Material uploaded and available to students! ✅

---

### 5️⃣ Create Assignment (2 minutes)

**As Staff:**
1. Sidebar → **"ASSIGNMENTS"** → **"Create Assignment"**
2. Fill in:
   ```
   Title: Python Homework 1
   Description: Complete exercises 1-10
   Subject: Select subject
   Due Date: Select future date
   Max Marks: 100
   Attachment: (optional) Upload question file
   ```
3. Submit

**Result:** Assignment created and visible to students! ✅

---

### 6️⃣ Student Submits Assignment (2 minutes)

**As Student:**
1. Create student or login with existing
2. Sidebar → **"ASSIGNMENTS"** → **"View Assignments"**
3. See the assignment with deadline countdown
4. Click **"Submit"**
5. Upload your file
6. Add remarks (optional)
7. Submit

**Result:** Assignment submitted! Staff can now grade it. ✅

---

### 7️⃣ Create and Approve Event (3 minutes)

**As Staff:**
1. Sidebar → **"EVENTS"** → **"Create Event"**
2. Fill in:
   ```
   Title: Tech Fest 2025
   Description: Annual technology festival
   Event Date: Future date/time
   Venue: Main Auditorium
   Max Participants: 100
   ```
3. Submit

**Result:** Event status = "Pending" (needs HOD approval)

**As HOD:**
1. Login as admin
2. Sidebar → **"EVENTS"** → **"Manage Events"**
3. See pending event
4. Click **"Approve"**

**Result:** Event approved! Now visible to students. ✅

---

### 8️⃣ Student Registers for Event (1 minute)

**As Student:**
1. Sidebar → **"EVENTS"** → **"Events & Registration"**
2. See approved events
3. Click **"Register"** for an event
4. Confirmation message appears

**Result:** Student registered! Shows in "My Registrations". ✅

---

### 9️⃣ Send Message (1 minute)

**From Any User:**
1. Sidebar → **"COMMUNICATION"** → **"Messages"**
2. Click **"Send Message"** or go to `/message/send/`
3. Select:
   ```
   Recipient: Choose from dropdown
   Subject: Test Message
   Message: Hello, this is a test!
   ```
4. Submit

**Result:** Message sent! Appears in recipient's inbox. ✅

---

### 🔟 Browse Resource Library (1 minute)

**As Student:**
1. Sidebar → **"RESOURCES"** → **"Resource Library"**
2. See all study materials for your course
3. Use search box or filters
4. Click **Download** icon → File downloads (logged)
5. Click **Bookmark** icon → Saves to bookmarks
6. Rate material → Give 1-5 stars

**Result:** Complete resource management! ✅

---

## 📊 Quick Testing Checklist

### HOD Features:
- [ ] Can add/edit/delete staff
- [ ] Can add/edit/delete students
- [ ] Can assign proctors to students
- [ ] Can create approved events
- [ ] Can approve staff event proposals
- [ ] Can view resource analytics
- [ ] Can view all assignments
- [ ] Can post announcements
- [ ] Can send messages
- [ ] Can view feedback/leave requests

### Staff Features:
- [ ] Can take attendance
- [ ] Can upload study materials
- [ ] Can create assignments
- [ ] Can grade submissions
- [ ] Can propose events
- [ ] Can send messages
- [ ] Can view announcements
- [ ] **If Proctor:**
  - [ ] Can view assigned students
  - [ ] Can generate absentee reports
  - [ ] Can monitor student performance

### Student Features:
- [ ] Can view attendance
- [ ] Can view results
- [ ] Can browse resource library
- [ ] Can bookmark materials
- [ ] Can rate materials
- [ ] Can download resources
- [ ] Can view assignments
- [ ] Can submit assignments
- [ ] Can register for events
- [ ] Can send messages
- [ ] Can view announcements
- [ ] Can apply for leave
- [ ] Can send feedback

---

## 🎨 UI Navigation

### Sidebar Sections:

**HOD Sidebar:**
```
- Home
- View/Edit Profile
- Notifications

STAFF MANAGEMENT
- Add Staff
- Manage Staff

STUDENT MANAGEMENT
- Add Student
- Manage Student

COURSES & SUBJECTS
- Add Course
- Manage Course
- Add Subject
- Manage Subject

SESSIONS
- Add Session
- Manage Session

PROCTOR SYSTEM ← NEW
- Manage Proctors
- Assign Students

ATTENDANCE
- View Attendance

FEEDBACK
- Student Feedback
- Staff Feedback

LEAVE
- Staff Leave
- Student Leave

EVENTS ← NEW
- Manage Events
- Create Event

ACADEMIC RESOURCES ← NEW
- Study Materials
- Resource Analytics
- All Assignments

COMMUNICATION ← NEW
- Messages
- Post Announcement
- View Announcements
```

**Staff Sidebar:**
```
- Home
- View/Edit Profile
- Add Result
- Edit Result
- Take Attendance
- View/Update Attendance
- View Notifications
- Apply For Leave
- Feedback

RESOURCES ← NEW
- Upload Material
- My Materials

ASSIGNMENTS ← NEW
- Create Assignment
- My Assignments

EVENTS ← NEW
- Events
- Create Event

COMMUNICATION ← NEW
- Messages
- Announcements

PROCTOR TOOLS ← NEW (only if is_proctor)
- My Mentees
- Absentee Reports
```

**Student Sidebar:**
```
- Home
- View/Edit Profile
- View Attendance
- View Notifications
- Apply For Leave
- Feedback

RESOURCES ← NEW
- Resource Library
- My Bookmarks

ASSIGNMENTS ← NEW
- View Assignments

EVENTS ← NEW
- Events & Registration

COMMUNICATION ← NEW
- Messages
- Announcements
```

---

## 🔍 Where to Find Features

### Study Materials:
- **Upload:** Staff → RESOURCES → Upload Material
- **View (Staff):** Staff → RESOURCES → My Materials
- **Browse (Student):** Student → RESOURCES → Resource Library
- **Bookmarks:** Student → RESOURCES → My Bookmarks
- **Analytics:** HOD → ACADEMIC RESOURCES → Resource Analytics

### Assignments:
- **Create:** Staff → ASSIGNMENTS → Create Assignment
- **View (Staff):** Staff → ASSIGNMENTS → My Assignments
- **Grade:** Staff → My Assignments → Click assignment → Grade
- **Submit (Student):** Student → ASSIGNMENTS → View Assignments → Submit
- **All Assignments:** HOD → ACADEMIC RESOURCES → All Assignments

### Events:
- **Create (Staff):** Staff → EVENTS → Create Event (pending)
- **Create (HOD):** HOD → EVENTS → Create Event (auto-approved)
- **Approve:** HOD → EVENTS → Manage Events → Approve/Reject
- **Register (Student):** Student → EVENTS → Events & Registration → Register
- **View Participation:** HOD → Manage Events → Click event

### Messages:
- **Send:** Any user → COMMUNICATION → Messages → Send
- **Inbox:** COMMUNICATION → Messages → Inbox tab
- **Reply:** Open message → Reply button

### Announcements:
- **Create:** HOD → COMMUNICATION → Post Announcement
- **View:** Any user → COMMUNICATION → Announcements

### Proctor:
- **Assign:** HOD → PROCTOR SYSTEM → Assign Students
- **View Mentees:** Staff (is_proctor) → PROCTOR TOOLS → My Mentees
- **Reports:** Staff (is_proctor) → PROCTOR TOOLS → Absentee Reports

---

## 🎓 Tips & Best Practices

### For HOD:
1. Set up courses and subjects first
2. Add staff and assign to subjects
3. Add students and assign to courses
4. Designate proctors and assign students
5. Create initial academic session
6. Post welcome announcement

### For Staff:
1. Upload class materials regularly
2. Create assignments with clear deadlines
3. Grade submissions promptly
4. If proctor: Check mentees weekly
5. Respond to messages quickly

### For Students:
1. Check announcements daily
2. Bookmark important materials
3. Submit assignments before deadline
4. Register for events early
5. Rate resources to help others
6. Monitor attendance percentage

---

## 🐛 Troubleshooting

### Proctor Tools Not Showing?
**Solution:** Ensure staff has `is_proctor=True` in admin panel

### Can't Upload Files?
**Solution:** Check file size and type. Ensure media folder has write permissions.

### Assignment Not Showing?
**Solution:** Verify course assignment matches between assignment and student.

### Event Registration Failed?
**Solution:** Check event status (must be 'approved') and capacity (not full).

### Messages Not Sending?
**Solution:** Verify recipient exists and you have permission to message them.

---

## 📞 Support

### Access Django Admin for Full Control:
```
URL: http://127.0.0.1:8000/admin/
Login: admin@admin.com / admin123

Here you can:
- View all database records
- Manually create/edit any data
- See relationships
- Run bulk operations
- Export data
```

---

## 🎉 You're Ready!

Your **EduVision College Management System** is now **fully operational** with:

✅ All features implemented
✅ Proctor system integrated (no separate login)
✅ Resource library with ratings & bookmarks
✅ Complete assignment system
✅ Event management with approvals
✅ Multi-channel communication
✅ Discussion forums
✅ Announcements system
✅ Analytics and reporting

**Start using it right now!**

Navigate to: **http://127.0.0.1:8000/**

---

**Happy managing! 🎓**


