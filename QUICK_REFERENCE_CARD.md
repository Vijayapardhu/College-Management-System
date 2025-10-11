# EduVision - Quick Reference Card

## 🔐 Login Credentials

### Admin Access
```
📧 Email: admin@eduvision.com
🔑 Password: admin123
🔗 URL: http://127.0.0.1:8000/
```

### Default User Types
1. **Admin/HOD** - Full system access
2. **Staff** - Teaching and marking capabilities
3. **Student** - View records and submit requests
4. **Parent** - Monitor ward's progress
5. **Proctor** - Student mentoring

---

## 🎯 Quick Actions by Role

### 👤 Admin/HOD - Top 10 Actions

| # | Action | URL | Shortcut |
|---|--------|-----|----------|
| 1 | **View Dashboard** | `/admin/home` | Main overview |
| 2 | **Add Student** | `/admin/add_student/` | + Student |
| 3 | **Add Staff** | `/admin/add_staff/` | + Staff |
| 4 | **Take Attendance** | `/admin/view_attendance/` | 📊 Attendance |
| 5 | **Manage Leaves** | `/admin/admin_view_leave/` | 📋 Leaves |
| 6 | **Send Notification** | `/admin/send_notification/` | 📢 Notify |
| 7 | **View Feedback** | `/admin/staff_feedback/` | 💬 Feedback |
| 8 | **Add Results** | `/admin/add_result/` | 📝 Results |
| 9 | **Fee Management** | `/admin/fee-structure/` | 💰 Fees |
| 10 | **Placement Drives** | `/admin/placements/` | 💼 Placements |

### 👨‍🏫 Staff - Top 8 Actions

| # | Action | URL | Quick Access |
|---|--------|-----|--------------|
| 1 | **View Dashboard** | `/staff/home` | Home |
| 2 | **Take Attendance** | `/staff/take_attendance/` | ✓ Attendance |
| 3 | **Update Attendance** | `/staff/update_attendance/` | ✏️ Edit |
| 4 | **Enter Marks** | `/staff/enter-marks/` | 📊 Marks |
| 5 | **Apply Leave** | `/staff/apply_leave/` | 📅 Leave |
| 6 | **View Feedback** | `/staff/feedback/` | 💬 Feedback |
| 7 | **Create Online Exam** | `/staff/create-online-exam/` | 💻 Exam |
| 8 | **Approve Gate Pass** | `/staff/gate-pass-approvals/` | 🚪 Gate Pass |

### 👨‍🎓 Student - Top 10 Actions

| # | Action | URL | Quick Access |
|---|--------|-----|--------------|
| 1 | **View Dashboard** | `/student/home` | 🏠 Home |
| 2 | **Check Attendance** | `/student/view_attendance/` | 📊 Attendance |
| 3 | **View Results** | `/student/view_result/` | 📝 Results |
| 4 | **Apply Leave** | `/student/apply_leave/` | 📅 Leave |
| 5 | **Submit Feedback** | `/student/student_feedback/` | 💬 Feedback |
| 6 | **Take Online Exam** | `/student/online-exams/` | 💻 Exams |
| 7 | **Request Certificate** | `/student/request-certificate/` | 📜 Certificate |
| 8 | **Apply Gate Pass** | `/student/gate-pass/` | 🚪 Gate Pass |
| 9 | **View Notifications** | `/student/view_notification/` | 🔔 Notifications |
| 10 | **Apply Scholarship** | `/student/apply-scholarship/` | 🎓 Scholarship |

---

## 📋 Common Workflows

### ➕ Adding a New Student

```
1. Login as Admin
2. Navigate to: Manage Students → Add Student
3. Fill form:
   - Email (unique)
   - Roll Number (unique)
   - Name, Gender, DOB
   - Course & Department
   - Guardian details
   - Profile picture
4. Click "Add Student"
5. Student receives login credentials via email
```

### ➕ Adding a New Staff Member

```
1. Login as Admin
2. Navigate to: Manage Staff → Add Staff
3. Fill form:
   - Email (unique)
   - Employee ID (unique)
   - Name, Gender, DOB
   - Department
   - Designation
   - Profile picture
4. Assign subjects (optional)
5. Click "Add Staff"
```

### 📊 Taking Attendance

```
STAFF:
1. Go to: Take Attendance
2. Select:
   - Subject
   - Date
3. Mark Present/Absent for each student
4. Click "Submit Attendance"

ADMIN:
1. Go to: View Attendance
2. Select subject and date range
3. View/Export reports
```

### 📝 Publishing Results

```
1. Login as Admin
2. Go to: Manage Results → Add Result
3. Select:
   - Student
   - Subject
   - Session
4. Enter marks
5. Save (Draft mode)
6. Click "Publish Result" to make visible to students
```

### 💰 Recording Fee Payment

```
1. Go to: Fee Management → Record Payment
2. Select Student
3. Enter:
   - Amount Paid
   - Payment Date
   - Payment Mode (Cash/Card/Online)
   - Transaction ID
   - Receipt Number
4. Click "Record Payment"
5. Receipt generated automatically
```

### 💼 Creating Placement Drive

```
1. Go to: Placement Management
2. Click "Add Placement Drive"
3. Fill details:
   - Company Name
   - Position
   - Eligibility (CGPA, Year)
   - Salary Package
   - Drive Date
   - Last Date to Apply
4. Save
5. Students can now apply
6. Review applications → Shortlist → Update status
```

---

## 🔢 Important Status Codes

### Leave Status
- 🟡 **Pending** - Awaiting approval
- 🟢 **Approved** - Leave granted
- 🔴 **Rejected** - Leave denied

### Result Status
- 📝 **Draft** - Not visible to students
- ✅ **Published** - Visible to students

### Gate Pass Status
- ⏳ **Pending** - Awaiting approval
- ✅ **Approved** - Can leave campus
- ❌ **Rejected** - Cannot leave

### Grievance Status
- 🆕 **New** - Just submitted
- 🔄 **In Progress** - Being handled
- ✅ **Resolved** - Issue closed

### Scholarship Status
- 📋 **Applied** - Application submitted
- 🔍 **Under Review** - Being evaluated
- ✅ **Approved** - Scholarship granted
- 🏦 **Disbursed** - Amount transferred
- ❌ **Rejected** - Not eligible

---

## 🎯 Feature Access Matrix

| Feature | Admin | Staff | Student | Parent |
|---------|-------|-------|---------|--------|
| Dashboard | ✅ | ✅ | ✅ | ✅ |
| Take Attendance | ✅ | ✅ | ❌ | ❌ |
| View Attendance | ✅ | ✅ | ✅ (Own) | ✅ (Ward) |
| Enter Marks | ✅ | ✅ | ❌ | ❌ |
| View Results | ✅ | ✅ | ✅ (Own) | ✅ (Ward) |
| Apply Leave | ✅ | ✅ | ✅ | ❌ |
| Approve Leave | ✅ | ❌ | ❌ | ❌ |
| Send Notifications | ✅ | ❌ | ❌ | ❌ |
| Fee Management | ✅ | ❌ | ✅ (View) | ✅ (View/Pay) |
| Hostel Allocation | ✅ | ❌ | ✅ (View) | ✅ (View) |
| Library Issue/Return | ✅ | ✅ | ✅ (View) | ❌ |
| Create Online Exam | ✅ | ✅ | ❌ | ❌ |
| Take Online Exam | ❌ | ❌ | ✅ | ❌ |
| Request Certificate | ❌ | ❌ | ✅ | ❌ |
| Issue Certificate | ✅ | ❌ | ❌ | ❌ |
| Gate Pass Request | ❌ | ❌ | ✅ | ❌ |
| Gate Pass Approval | ✅ | ✅ | ❌ | ❌ |
| Classroom Booking | ✅ | ✅ | ❌ | ❌ |
| Report Ragging | ❌ | ❌ | ✅ | ✅ |
| Scholarship Apply | ❌ | ❌ | ✅ | ❌ |
| Scholarship Approve | ✅ | ❌ | ❌ | ❌ |

---

## ⌨️ Keyboard Shortcuts

### Global
- `Ctrl + /` - Show help
- `Esc` - Close modal/dialog
- `Ctrl + S` - Save form (when in form)

### Navigation
- `Alt + H` - Go to Home/Dashboard
- `Alt + P` - View Profile
- `Alt + N` - View Notifications
- `Alt + L` - Logout

### Tables
- `Ctrl + F` - Focus search box
- `Arrow Keys` - Navigate rows
- `Enter` - View/Edit selected row

---

## 📊 Common Reports

### For Admin

| Report | Location | Frequency |
|--------|----------|-----------|
| **Attendance Summary** | `/admin/view_attendance/` | Daily |
| **Fee Defaulters** | `/admin/fee-defaulters/` | Weekly |
| **Leave Requests** | `/admin/admin_view_leave/` | Daily |
| **Result Analytics** | `/admin/results/` | Per Semester |
| **Placement Stats** | `/admin/placements/` | Per Drive |
| **Hostel Occupancy** | `/admin/hostel-allocations/` | Monthly |
| **Library Statistics** | `/admin/library-issues/` | Monthly |
| **Feedback Summary** | `/admin/staff_feedback/` | Semester |

### For Staff

| Report | Location | Frequency |
|--------|----------|-----------|
| **Attendance (My Subjects)** | `/staff/update_attendance/` | Daily |
| **Student Performance** | `/staff/view-results/` | Per Exam |
| **My Leave Balance** | `/staff/apply_leave/` | On Demand |
| **Student Feedback** | `/staff/feedback/` | Semester |

### For Students

| Report | Location | Frequency |
|--------|----------|-----------|
| **My Attendance** | `/student/view_attendance/` | Weekly |
| **My Results** | `/student/view_result/` | Per Exam |
| **Fee Status** | `/student/fees/` | Semester |
| **My Applications** | Various sections | On Demand |

---

## 🆘 Troubleshooting

### Cannot Login
1. **Check email format** - Must be valid email
2. **Check password** - Case sensitive
3. **Use Roll Number** (Students) or Employee ID (Staff)
4. **Reset password** - Use "Forgot Password" link

### Cannot See Results
1. **Check if results are published** (Students)
2. **Verify subject assignment** (Staff)
3. **Check session year**

### Attendance Not Showing
1. **Verify date range**
2. **Check subject selection**
3. **Ensure attendance was submitted**

### Cannot Submit Form
1. **Fill all required fields** (marked with *)
2. **Check file size** (Max 2MB for images)
3. **Verify unique fields** (Email, Roll Number)

### Features Not Loading
1. **Clear browser cache** (Ctrl + Shift + Del)
2. **Try different browser**
3. **Check internet connection**
4. **Contact admin if issue persists**

---

## 📞 Contact & Support

### Technical Support
- Check logs for errors
- Review `README.md` for setup
- See `SETUP_GUIDE.md` for installation

### Feature Help
- Check `FEATURES_GUIDE.md` for detailed feature documentation
- Each page has contextual help

---

## 💡 Pro Tips

### For Admins
- ✅ **Backup database regularly** (weekly recommended)
- ✅ **Review feedback monthly** to improve quality
- ✅ **Send notifications** before important dates
- ✅ **Monitor fee defaulters** weekly
- ✅ **Update academic calendar** at semester start

### For Staff
- ✅ **Take attendance on time** (same day)
- ✅ **Enter marks before deadline**
- ✅ **Respond to feedback** to show engagement
- ✅ **Apply leaves in advance** (3 days notice)
- ✅ **Keep question papers** for reference

### For Students
- ✅ **Check attendance weekly** to avoid defaulting
- ✅ **Apply for leaves** before absence
- ✅ **Submit feedback** constructively
- ✅ **Update profile** with current contact info
- ✅ **Check notifications daily**
- ✅ **Apply for scholarships** before deadline

---

## 📈 Best Practices

### Data Entry
- ✅ Use consistent naming conventions
- ✅ Double-check unique IDs (Roll No, Employee ID)
- ✅ Verify email addresses
- ✅ Upload clear profile pictures
- ✅ Fill all mandatory fields

### Security
- ✅ **Change default password** immediately
- ✅ **Logout after use** (especially on shared computers)
- ✅ **Don't share credentials**
- ✅ **Use strong passwords** (8+ chars, mixed case, numbers)
- ✅ **Review activity logs** regularly (Admin)

### Performance
- ✅ Use filters to narrow search results
- ✅ Export large reports instead of viewing online
- ✅ Clear browser cache periodically
- ✅ Close unused tabs

---

## 🎯 System Limits

| Item | Limit | Notes |
|------|-------|-------|
| **Profile Picture** | 2 MB | JPG, PNG only |
| **Document Upload** | 5 MB | PDF, DOC, DOCX |
| **Bulk Upload** | 500 rows | CSV/Excel |
| **Online Exam Duration** | 3 hours | Max per exam |
| **Password Length** | 8-50 chars | Min-Max |
| **Email Length** | 255 chars | Standard |
| **Notification Message** | 1000 chars | Max |

---

## 📅 Academic Calendar Workflow

### Start of Semester
1. ✅ Create/Activate Session
2. ✅ Add new students (if any)
3. ✅ Assign subjects to staff
4. ✅ Set up timetable
5. ✅ Configure fee structure
6. ✅ Send welcome notifications

### Mid-Semester
1. ✅ Monitor attendance (weekly)
2. ✅ Conduct mid-term exams
3. ✅ Enter mid-term marks
4. ✅ Review feedback
5. ✅ Address grievances

### End of Semester
1. ✅ Conduct final exams
2. ✅ Enter final marks
3. ✅ Publish results
4. ✅ Generate transcripts
5. ✅ Collect feedback
6. ✅ Archive session data

---

**Print this card and keep it handy for quick reference!**

**Version**: 2.0  
**Last Updated**: October 2024  
**Status**: ✅ Production Ready

