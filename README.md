# 🎓 College Management System (ERP)

A comprehensive **Django-based College Management System** designed to automate academic and administrative operations. Built with modern web technologies and featuring role-based access control for Students, Faculty, HODs, Management, and Administrators.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-3.2+-green.svg)](https://www.djangoproject.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Features

### 👨‍🎓 **Student Panel**
- **Academic Management**
  - View attendance records and performance analytics
  - Access study materials and course resources
  - Take online exams and view results
  - Submit assignments and track submissions
  - View semester-wise results and transcripts
  
- **Services & Applications**
  - Apply for scholarships with status tracking
  - Request certificates (Bonafide, TC, etc.)
  - Book hostel accommodation
  - Apply for gate passes
  - Track placement drives and apply
  - Register internships and activities
  
- **Communication**
  - Internal messaging system
  - Announcements and notifications
  - Discussion forums
  - Raise grievances and track resolution

### 👨‍🏫 **Faculty/Staff Panel**
- **Academic Operations**
  - Mark attendance (QR-based available)
  - Enter and manage student marks
  - Upload study materials and resources
  - Create and manage assignments
  - Create online exams with auto-grading
  
- **Administrative Tasks**
  - View timetable and exam duties
  - Manage placement activities
  - Handle gate pass approvals
  - Library book issue/return
  - Research publication management
  - Resolve assigned grievances

### 👔 **HOD/Admin Panel**
- **User Management**
  - Manage students, faculty, and staff
  - Assign courses and subjects
  - Department management
  - Proctor assignment
  
- **Academic Administration**
  - Timetable creation and management
  - Exam schedule and admit card generation
  - Result publishing and analytics
  - Online exam management
  - Certificate issuance
  
- **Student Services**
  - Fee structure management and tracking
  - Hostel allocation and visitor logs
  - Library inventory management
  - Transport allocation
  - Scholarship review and disbursement
  - Placement drive coordination
  
- **Advanced Features**
  - Alumni database management
  - Sports & cultural activities tracking
  - Disciplinary action records
  - Anti-ragging incident management
  - Student council management
  - Internship tracking
  - Gate pass oversight
  - Grievance resolution workflow
  
- **Analytics & Reports**
  - Attendance analytics
  - Performance dashboards
  - Faculty performance metrics
  - Fee defaulter reports
  - Custom report generation

### 🏢 **Management Panel**
- Administrative operations management
- Non-academic staff coordination
- Facility management
- Financial oversight
- Compliance and documentation

### 📚 **Classroom Management**
- Classroom booking and scheduling
- Real-time availability tracking
- Maintenance request management
- Booking approval workflow
- Weekly schedule visualization

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Django 3.2+
- **Database:** SQLite (Development) / PostgreSQL (Production)
- **Authentication:** Django Auth + Custom Email/ID Login
- **API:** Django REST Framework (optional)

### Frontend
- **Template Engine:** Django Templates
- **UI Framework:** AdminLTE 3
- **CSS Framework:** Bootstrap 4
- **Icons:** Font Awesome
- **JavaScript:** jQuery, DataTables.js
- **Charts:** Chart.js
- **Calendar:** FullCalendar

### Additional Libraries
- **Forms:** Django Crispy Forms
- **File Upload:** Django Storages
- **Notifications:** Django Messages
- **PDF Generation:** ReportLab
- **Excel Export:** openpyxl

---

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

---

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/Vijayapardhu/College-Management-System.git
cd College-Management-System
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Database
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Collect Static Files
```bash
python manage.py collectstatic
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit: `http://127.0.0.1:8000`

---

## 👥 Default User Types

The system supports 4 user types:

1. **HOD/Admin** - Full system access
2. **Staff/Faculty** - Academic operations
3. **Student** - Student services
4. **Management** - Administrative operations

### Login Options
Users can login using:
- Email address
- Roll Number (Students)
- Employee ID (Staff/Faculty)

---

## 📁 Project Structure

```
College-Management-System/
├── main_app/                 # Core application
│   ├── models.py            # Database models
│   ├── views.py             # View functions
│   ├── hod_views.py         # HOD panel views
│   ├── staff_views.py       # Staff panel views
│   ├── student_views.py     # Student panel views
│   ├── management_views.py  # Management panel views
│   ├── forms.py             # Form definitions
│   ├── urls.py              # URL routing
│   └── templates/           # HTML templates
│       ├── hod_template/
│       ├── staff_template/
│       ├── student_template/
│       └── management_template/
├── student_management_system/ # Project settings
├── static/                   # Static files (CSS, JS, images)
├── media/                    # User uploaded files
├── requirements.txt          # Python dependencies
└── manage.py                # Django management script
```

---

## 🗄️ Database Models

### Core Models
- `CustomUser` - Extended user model
- `Admin`, `Staff`, `Student`, `Management` - User profiles
- `Course`, `Subject`, `Session` - Academic structure
- `Attendance`, `Result` - Academic records

### Extended Models
- `Fee`, `Scholarship`, `Certificate` - Student services
- `Hostel`, `Transport`, `Library` - Facility management
- `Placement`, `Internship`, `Alumni` - Career services
- `Grievance`, `Activity`, `Council` - Student welfare
- `Classroom`, `ClassroomBooking` - Resource management

---

## 🔐 Security Features

- Password hashing with Django's built-in security
- CSRF protection on all forms
- SQL injection prevention via ORM
- XSS protection in templates
- Session management
- Role-based access control
- Secure file upload validation

---

## 📱 Mobile Responsive

- Fully responsive design
- Mobile-friendly interface
- Touch-optimized controls
- PWA ready (Progressive Web App)
- Offline capability (service workers)

---

## 🎨 UI Features

- Modern AdminLTE 3 dashboard
- Interactive DataTables
- Real-time charts and graphs
- Calendar integration
- Modal dialogs
- Toast notifications
- Drag & drop file upload
- Print-friendly layouts

---

## 🚦 Getting Started

### For Students
1. Login with your email or roll number
2. Complete your profile
3. View attendance and marks
4. Access study materials
5. Apply for services (scholarship, hostel, etc.)

### For Faculty
1. Login with email or employee ID
2. Mark attendance
3. Upload study materials
4. Enter marks and grades
5. Manage assignments

### For HOD/Admin
1. Access admin dashboard
2. Manage users and courses
3. Generate reports
4. Oversee all operations
5. Configure system settings

---

## 📊 Sample Data (Optional)

To populate the system with demo data:

```bash
python populate_complete_erp_data.py
```

This will create sample:
- Departments and courses
- Students and faculty
- Attendance records
- Exam results
- And more...

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Vijayapardhu**
- GitHub: [@Vijayapardhu](https://github.com/Vijayapardhu)
- Repository: [College-Management-System](https://github.com/Vijayapardhu/College-Management-System)

---

## 📞 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact via repository discussions

---

## 🙏 Acknowledgments

- Django Documentation
- AdminLTE Template
- Bootstrap Framework
- Font Awesome Icons
- All open-source contributors

---

## 📈 Roadmap

- [ ] API Development (REST/GraphQL)
- [ ] Mobile App (Flutter/React Native)
- [ ] Email notifications
- [ ] SMS integration
- [ ] Payment gateway integration
- [ ] Video conferencing integration
- [ ] AI-powered analytics
- [ ] Multi-language support

---

## ⭐ Star History

If you find this project useful, please consider giving it a star ⭐

---

**Made with ❤️ using Django**
