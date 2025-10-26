# 🔧 Developer Guide

**For developers with technical knowledge**

**[← Back to README](README.md)** | **[← Beginner Guide](BEGINNER_GUIDE.md)**

---

## 📋 Quick Reference

### Project Structure
```
main_app/
├── models.py              # 89 database models
├── *_views.py (25 files)  # View logic
├── *_forms.py (7 files)   # Form definitions
├── urls.py                # URL routing
└── templates/ (334 files) # HTML templates
```

### View Modules (25)
```
hod_views.py           # Admin panel
staff_views.py         # Faculty panel
student_views.py       # Student panel
management_views.py    # Management panel
analytics_views.py     # Analytics (NEW)
performance_views.py   # Performance monitoring (NEW)
parent_views.py        # Parent panel
message_views.py       # Messaging
placement_views.py     # Placements
admission_views.py     # Admissions
payroll_views.py       # Payroll
alumni_views.py        # Alumni
lms_views.py          # LMS
... and 12 more
```

---

## 🗄️ Database Models (89 Total)

### Core Models
```python
CustomUser          # Extended Django user (email auth)
Student             # Student profiles
Staff               # Faculty profiles
Management          # Admin staff profiles
ParentGuardian      # Parent information
```

### Academic Models
```python
Department          # Departments (CSE, ECE, etc.)
Program             # Degree programs
Course              # Courses
Subject             # Subjects
Session             # Academic years
Timetable           # Class schedules
Classroom           # Classroom info
```

### Attendance & Leave
```python
Attendance          # Attendance records
AttendanceReport    # Attendance summaries
LeaveReportStudent  # Student leaves
LeaveReportStaff    # Staff leaves
GatePass            # Gate passes
```

### Examination
```python
Exam                # Exam definitions
ExamSchedule        # Exam scheduling
OnlineExam          # Online exams
OnlineExamQuestion  # Exam questions
OnlineExamAttempt   # Student attempts
AdmitCard           # Admit cards
```

### Results
```python
StudentResult       # Subject results
SemesterResult      # Semester results
SubjectResult       # Detailed results
```

### Administrative
```python
# Fee Management
FeeStructure        # Fee structures
FeePayment          # Payment records
FeeConcession       # Concessions
FeeInstallment      # Installments

# Hostel
Hostel              # Hostel info
HostelAllocation    # Room allocations
HostelVisitorLog    # Visitor tracking

# Transport
Transport           # Routes
TransportAllocation # Transport assignments

# Library
Library             # Book catalog
LibraryIssue        # Issue/return tracking

# Scholarships
Scholarship         # Scholarship programs
ScholarshipApplication # Applications
```

### Placement
```python
Company             # Companies
PlacementDrive      # Placement drives
PlacementApplication # Student applications
Internship          # Internships
```

### Communication
```python
Message             # Internal messaging
Announcement        # Announcements
Discussion          # Forums
NotificationStudent # Student notifications
NotificationStaff   # Staff notifications
```

### Others
```python
Assignment, StudyMaterial, Event, Certificate,
Grievance, Alumni, Research, DisciplinaryAction,
ActivityLog, MedicalRecord, PayrollStructure, etc.
```

---

## 🔗 URL Routing

### URL Pattern
```python
# In urls.py
path("student/home/", student_views.student_home, name='student_home')

# Template link
<a href="{% url 'student_home' %}">Dashboard</a>
```

### Role-Based Routes

**Students**: `/student/*`
```
/student/home/
/student/view/attendance/
/student/view/results/
/student/assignments/
/student/apply/leave/
```

**Staff**: `/staff/*`
```
/staff/home/
/staff/attendance/
/staff/results/
/staff/assignments/
/staff/materials/
```

**HOD/Admin**: `/admin/*`
```
/admin/home/
/admin/manage-staff/
/admin/manage-student/
/admin/analytics/
/admin/timetable/
```

**Management**: `/management/*`
```
/management/home/
/management/transport/
/management/hostels/
/management/library/
/management/fees/
/management/reports/financial/
/management/reports/operational/
```

**Analytics** (NEW): `/analytics/*`
```
/analytics/                    # Dashboard
/analytics/attendance/         # Attendance analytics
/analytics/academic-performance/ # Performance
/analytics/financial/          # Financial
/analytics/report-builder/    # Custom reports
/analytics/export/             # Export data
```

**Performance** (NEW): `/performance/*`
```
/performance/                  # Dashboard
/performance/slow-queries/     # Query analysis
/performance/error-logs/       # Error tracking
/performance/system-resources/ # Resource monitoring
/performance/database-analysis/ # DB stats
/performance/cache-analysis/   # Cache metrics
/performance/optimization-recommendations/ # Tips
```

---

## 🎨 Template Structure

### Base Template
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>EduVision</title>
    {% block custom_css %}{% endblock %}
</head>
<body>
    {% block content %}{% endblock %}
    {% block custom_js %}{% endblock %}
</body>
</html>
```

### Child Template
```html
<!-- student/home.html -->
{% extends 'main_app/base.html' %}

{% block content %}
    <h1>Student Dashboard</h1>
{% endblock %}
```

---

## 🔐 User Authentication

### Login Flow
```python
# In views.py
@login_required  # Must be logged in
def student_home(request):
    # Check user type
    if request.user.user_type != '3':
        return redirect('login')
    
    # Show dashboard
    return render(request, 'student_template/home.html')
```

### User Types
```python
USER_TYPE = (
    (1, "HOD"),         # user_type='1'
    (2, "Staff"),       # user_type='2'
    (3, "Student"),     # user_type='3'
    (4, "Management"),  # user_type='4'
)
```

---

## 📊 Working with Data

### Get Data from Database
```python
# Get all students
students = Student.objects.all()

# Get one student
student = Student.objects.get(id=1)

# Filter students
cs_students = Student.objects.filter(course__name="Computer Science")

# Count students
total = Student.objects.count()
```

### Save Data to Database
```python
# Create new student
student = Student.objects.create(
    roll_number="2021001",
    name="John Doe"
)

# Update existing
student.name = "Jane Doe"
student.save()
```

### Pass Data to Template
```python
def student_list(request):
    students = Student.objects.all()
    
    context = {
        'students': students,
        'total_count': students.count()
    }
    
    return render(request, 'students.html', context)
```

### Use Data in Template
```html
<h2>Total Students: {{ total_count }}</h2>

{% for student in students %}
    <p>{{ student.name }} - {{ student.roll_number }}</p>
{% endfor %}
```

---

## 🔧 Common Development Tasks

### 1. Add a New Page

**Step 1**: Create view function
```python
# In student_views.py
def my_new_page(request):
    context = {'page_title': 'My New Page'}
    return render(request, 'student_template/my_page.html', context)
```

**Step 2**: Add URL
```python
# In urls.py
path("student/my-page/", student_views.my_new_page, name='my_new_page')
```

**Step 3**: Create HTML template
```html
<!-- student_template/my_page.html -->
{% extends 'main_app/base.html' %}
{% block content %}
    <h1>My New Page</h1>
{% endblock %}
```

### 2. Add a New Model

**Step 1**: Define model
```python
# In models.py
class MyModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

**Step 2**: Create migration
```bash
python manage.py makemigrations
```

**Step 3**: Apply migration
```bash
python manage.py migrate
```

### 3. Add Form Handling

**Step 1**: Create form
```python
# In forms.py
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['name', 'roll_number']
```

**Step 2**: Handle in view
```python
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Student added!')
            return redirect('students')
    else:
        form = StudentForm()
    
    return render(request, 'add_student.html', {'form': form})
```

---

## 📦 Dependencies (requirements.txt)

### Core (Must Have)
```
Django==4.2.7          # Web framework
Pillow==10.0.1         # Image handling
```

### Database
```
psycopg2-binary==2.9.11  # PostgreSQL
```

### API
```
djangorestframework==3.14.0
```

### File Processing
```
openpyxl==3.1.2        # Excel files
reportlab==4.0.4       # PDF generation
qrcode==7.4.2          # QR codes
```

### Caching
```
redis==5.0.1
django-redis==5.4.0
```

### Production
```
gunicorn==21.2.0       # Server
whitenoise==6.6.0      # Static files
```

**Total: 45+ packages** (see `requirements.txt`)

---

## 🐛 Debugging Tips

### Error: Module not found
```bash
pip install <module-name>
```

### Error: Migration issue
```bash
python manage.py makemigrations
python manage.py migrate
```

### Error: Static files not loading
```bash
python manage.py collectstatic
```

### Error: Port already in use
```bash
# Kill the process or use different port
python manage.py runserver 8001
```

---

## 🔍 Code Organization

### Views by Role
- `hod_views.py` - 164 templates
- `staff_views.py` - 50 templates
- `student_views.py` - 65 templates
- `management_views.py` - 37 templates (33 + 4 NEW)
- `parent_views.py` - 10 templates

### Templates by Role
```
templates/
├── hod_template/ (164 files)
├── staff_template/ (50 files)
├── student_template/ (65 files)
├── management_template/ (37 files)
└── parent_template/ (10 files)
```

---

## 🚀 Git Workflow

```bash
# 1. Create branch
git checkout -b feature/my-feature

# 2. Make changes
# ... edit files ...

# 3. Commit
git add .
git commit -m "Add: my feature description"

# 4. Push
git push origin feature/my-feature

# 5. Create Pull Request
# ... on GitHub/GitLab ...
```

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific Test
```bash
python manage.py test main_app.tests.test_views
```

---

## 📊 Analytics Module (NEW)

### Files
- `analytics_views.py` - 7 functions
- 6 templates with Chart.js

### Features
- Attendance trends
- Performance analytics
- Financial reports
- Custom report builder
- CSV export

### Usage
```python
# In analytics_views.py
def attendance_analytics(request):
    # Calculate monthly trends
    # Generate charts
    # Show low attendance alerts
```

---

## ⚡ Performance Module (NEW)

### Files
- `performance_views.py` - 11 functions
- 10 templates with metrics

### Features
- System health monitoring
- Slow query detection
- Error log tracking
- Resource usage (CPU, memory)
- Cache analysis
- Optimization tips

---

## 📈 Management Reporting (NEW)

### Files
- Added to `management_views.py`
- 4 new executive report templates

### Features
- Financial reports
- Operational metrics
- Academic oversight
- Institutional KPIs

---

## 🔒 Security Best Practices

1. **Never commit `.env` file**
2. **Use environment variables**
3. **Always use `@login_required`**
4. **Validate all user inputs**
5. **Use CSRF tokens in forms**
6. **Set DEBUG=False in production**

---

## 📞 Contact

**Project Lead**: Team member who developed everything  
**HTML/CSS Help**: Team member with HTML knowledge  
**Questions**: Ask in team chat

---

**[← Back to README](README.md)** | **[← Beginner Guide](BEGINNER_GUIDE.md)**

