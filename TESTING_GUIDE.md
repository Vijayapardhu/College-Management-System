# EduVision - Testing Guide

## 🧪 How to Test New Features

This guide will help you test all the newly implemented features in EduVision.

---

## Prerequisites

### 1. Ensure migrations are applied
```bash
python manage.py migrate
```

### 2. Start the development server
```bash
python manage.py runserver
```

### 3. Access Admin Panel
Navigate to: `http://127.0.0.1:8000/admin/`
Login with: `admin@admin.com` / `admin123`

---

## 🎯 Testing Proctor Features

### Step 1: Create a Proctor Account
1. Go to Django Admin: `http://127.0.0.1:8000/admin/`
2. Click on **"Custom users"** → **"Add Custom User"**
3. Fill in:
   - Email: `proctor@example.com`
   - Password: `proctor123` (set using "this form" link)
   - User type: **Proctor**
   - Gender: **M** or **F**
   - First name: `John`
   - Last name: `Proctor`
4. Save

> **Note:** A Proctor profile is automatically created via Django signals!

### Step 2: Assign Students to Proctor
1. In Admin, go to **"Proctor students"** → **"Add proctor student"**
2. Select:
   - Proctor: The proctor you just created
   - Student: Any existing student
   - Is active: ✓ (checked)
3. Save
4. Repeat to assign multiple students

### Step 3: Login as Proctor
1. Logout from admin
2. Go to: `http://127.0.0.1:8000/`
3. Login with: `proctor@example.com` / `proctor123`
4. You should be redirected to: `/proctor/home/`

### Step 4: Test Proctor Features
Navigate to these URLs to test:

- **Dashboard:** `/proctor/home/`
  - Shows total assigned students
  - Low attendance warnings
  - Recent attendance records
  - Upcoming events
  - Unread messages count

- **View Students:** `/proctor/students/`
  - Lists all assigned students
  - Shows attendance percentage
  - Shows average marks

- **Student Details:** `/proctor/student/1/` (replace 1 with student ID)
  - Complete attendance history
  - Academic results
  - Leave applications
  - Event participations

- **Generate Absentee List:** `/proctor/absentee/`
  - Select date range
  - View students absent during period
  - Includes subject information

- **Profile:** `/proctor/profile/`
  - View/edit personal information

---

## 🎉 Testing Event Management

### Step 1: Create Events (as HOD)

1. Login as HOD: `admin@admin.com` / `admin123`
2. Go to: `/admin/event/create/`
3. Fill in:
   - Title: `Tech Fest 2025`
   - Description: `Annual technology festival`
   - Event Date: Select future date/time
   - Venue: `Main Auditorium`
   - Course: Select a course (optional)
   - Max Participants: `100` (0 = unlimited)
4. Submit

**Result:** Event is auto-approved (created by HOD)

### Step 2: Create Event Proposal (as Staff)

1. Login as staff member
2. Go to: `/staff/event/create/`
3. Fill in event details
4. Submit

**Result:** Event status = "Pending" (requires HOD approval)

### Step 3: Approve/Reject Events (as HOD)

1. Login as HOD
2. Go to: `/admin/events/`
3. View all events with their status
4. For pending events:
   - Click "Approve" or "Reject"
   - Event status updates instantly

### Step 4: Register for Events (as Student)

1. Login as student
2. Go to: `/student/events/`
3. View upcoming approved events
4. Click **"Register"** button
5. System checks:
   - Not already registered
   - Event not full
   - Event still open

**Result:** Student registered successfully

### Step 5: View Event Participations

**As Student:**
- Go to: `/student/events/`
- See "Registered Events" tab
- See "Past Participations" tab

**As Proctor:**
- Go to: `/proctor/events/`
- See all events
- See which assigned students registered

**As HOD:**
- Go to: `/admin/events/`
- See participant counts
- Access Django Admin for detailed participant list

---

## 💬 Testing Messaging System

### Step 1: Send a Message

**From any user type:**
1. Login to your account
2. Go to: `/message/send/`
3. Select:
   - Recipient: Choose from dropdown (filtered by role permissions)
   - Subject: `Test Message`
   - Message: `This is a test message content`
4. Submit

**Result:** Message sent and appears in recipient's inbox

### Step 2: View Messages

1. Go to: `/messages/` or role-specific URL:
   - HOD: `/admin/messages/`
   - Staff: `/staff/messages/`
   - Student: `/student/messages/`
   - Proctor: `/proctor/messages/`

2. You'll see two tabs:
   - **Inbox:** Messages received
   - **Sent:** Messages sent

3. Unread messages shown in **bold** or with indicator

### Step 3: Read and Reply

1. Click on a message to view: `/message/{id}/`
2. Message automatically marked as read
3. View message thread (original + replies)
4. Use reply form to respond
5. Replies linked to original message

### Step 4: Test Message Features

**Mark as Read:**
- Use AJAX call: `/message/{id}/mark_read/` (POST)

**Mark All as Read:**
- Use AJAX call: `/messages/mark_all_read/` (POST)

**Delete Message:**
- Use AJAX call: `/message/{id}/delete/` (POST)
- Only sender or receiver can delete

---

## 🧩 Testing Communication Permissions

### HOD Can Message:
- ✅ Other HOD users
- ✅ All Staff
- ✅ All Students
- ✅ All Proctors

### Staff Can Message:
- ✅ HOD
- ✅ Other Staff
- ✅ Students
- ❌ Proctors (unless specifically allowed)

### Students Can Message:
- ✅ HOD
- ✅ Faculty/Staff
- ✅ Their assigned proctors
- ❌ Other students

### Proctors Can Message:
- ✅ HOD
- ✅ Faculty/Staff
- ✅ Their assigned students only
- ❌ Students not assigned to them

**Test:** Try sending messages between different roles to verify permissions work correctly.

---

## 📊 Testing via Django Admin

### View All Data:

1. Login to: `http://127.0.0.1:8000/admin/`
2. You'll see these new sections:
   - **Proctors** - View all proctor profiles
   - **Proctor students** - See student-proctor assignments
   - **Events** - Manage all events
   - **Event participations** - See who registered for what
   - **Messages** - View all messages in system

### Useful Admin Actions:

**Bulk Operations:**
- Select multiple items
- Use dropdown actions (e.g., Delete selected)

**Filters:**
- Use right sidebar filters
- Filter by date, status, user type, etc.

**Search:**
- Use search boxes to find specific records
- Search by email, name, title, etc.

---

## 🔍 Testing Scenarios

### Scenario 1: Complete Event Lifecycle

1. **Staff creates event** → Status: Pending
2. **HOD approves** → Status: Approved
3. **Students register** → EventParticipation created
4. **Check capacity** → Registration stops when full
5. **Event occurs** → Can mark attended=True

### Scenario 2: Proctor Monitoring Student

1. **Assign student to proctor** (via admin)
2. **Proctor logs in** → Sees student in dashboard
3. **Student is absent** → Shows in attendance records
4. **Proctor generates absentee report** → Student appears
5. **Proctor sends message** → Student receives

### Scenario 3: Cross-Role Communication

1. **Student has question** → Sends message to faculty
2. **Faculty replies** → Threaded conversation
3. **Proctor monitors** → Can view student's concerns
4. **HOD intervenes** → Sends message to all parties

### Scenario 4: Event Registration

1. **Event created** with max_participants=2
2. **Student 1 registers** → Success
3. **Student 2 registers** → Success
4. **Student 3 tries to register** → Error: "Event is full"
5. **Student 2 unregisters** → Spot opens
6. **Student 3 registers** → Success

---

## 🐛 Common Issues & Solutions

### Issue: Proctor profile not created
**Solution:** Check signals in models.py. Manually create via admin if needed.

### Issue: Can't see assigned students
**Solution:** Verify ProctorStudent relationship exists with is_active=True

### Issue: Event approval button not working
**Solution:** Check CSRF token. Use @csrf_exempt or include {% csrf_token %} in template

### Issue: Message recipient list empty
**Solution:** Ensure users exist with appropriate roles. Check permission logic in message_views.py

### Issue: Migration errors
**Solution:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 📝 Test Data Creation Script

Create this in Django shell to quickly populate test data:

```python
python manage.py shell
```

```python
from main_app.models import *
from datetime import datetime, timedelta
from django.contrib.auth.hashers import make_password

# Create Course
course = Course.objects.create(name="Computer Science")
session = Session.objects.create(
    start_year=datetime.now().date(),
    end_year=(datetime.now() + timedelta(days=365)).date()
)

# Create Proctor
proctor_user = CustomUser.objects.create(
    email="proctor1@example.com",
    password=make_password("proctor123"),
    user_type="4",
    first_name="Jane",
    last_name="Proctor",
    gender="F",
    address="123 Campus Rd"
)

# Create Students
for i in range(1, 6):
    student_user = CustomUser.objects.create(
        email=f"student{i}@example.com",
        password=make_password("student123"),
        user_type="3",
        first_name=f"Student{i}",
        last_name="Test",
        gender="M" if i % 2 == 0 else "F",
        address=f"{i} Student Ave"
    )
    # Assign to proctor
    ProctorStudent.objects.create(
        proctor=Proctor.objects.get(admin=proctor_user),
        student=Student.objects.get(admin=student_user),
        is_active=True
    )

# Create Events
hod = CustomUser.objects.get(user_type="1")
Event.objects.create(
    title="Welcome Ceremony",
    description="New student welcome event",
    event_date=datetime.now() + timedelta(days=7),
    venue="Main Hall",
    created_by=hod,
    approved_by=hod,
    status="approved",
    max_participants=0,
    course=course
)

print("✅ Test data created successfully!")
```

---

## ✅ Verification Checklist

Use this to verify all features work:

### Proctor Features:
- [ ] Proctor can login
- [ ] Dashboard shows assigned students count
- [ ] Can view list of assigned students
- [ ] Can view individual student details
- [ ] Can generate absentee reports
- [ ] Can update profile
- [ ] Can send messages to students

### Event Features:
- [ ] HOD can create approved events
- [ ] Staff can create pending events
- [ ] HOD can approve/reject events
- [ ] Students can view approved events
- [ ] Students can register for events
- [ ] Registration respects capacity limits
- [ ] Students can unregister before event
- [ ] Proctors can see student participations

### Messaging Features:
- [ ] Can send message to appropriate recipients
- [ ] Messages appear in inbox
- [ ] Can read messages
- [ ] Messages mark as read
- [ ] Can reply to messages
- [ ] Replies appear in thread
- [ ] Can delete messages
- [ ] Unread count updates

### Integration:
- [ ] Login redirects to correct dashboard
- [ ] All URLs accessible without 404
- [ ] Django admin shows all models
- [ ] No migration errors
- [ ] No linter errors

---

## 🚀 Ready for Production?

Before deploying, ensure:
1. ✅ All features tested and working
2. ✅ Create proper frontend templates
3. ✅ Add proper error handling
4. ✅ Implement CSRF protection properly
5. ✅ Add email notifications
6. ✅ Set up proper permissions and middleware
7. ✅ Test with large datasets
8. ✅ Security audit
9. ✅ Performance optimization
10. ✅ Backup and recovery procedures

---

**Happy Testing! 🎉**

For issues or questions, refer to IMPLEMENTATION_SUMMARY.md or README.md


