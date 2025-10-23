# EduVision College Management System

[![Django Version](https://img.shields.io/badge/Django-5.2+-green.svg)](https://djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen.svg)](https://github.com/yourusername/eduvision-college-management)

A comprehensive, modern college management system built with Django, designed to streamline academic and administrative operations for educational institutions.

## 🌟 Features

### 🎓 Academic Management
- **Student Information System**: Complete student profiles with academic records
- **Course & Subject Management**: Flexible course structure and subject allocation
- **Attendance Tracking**: Real-time attendance marking and reporting
- **Grade Management**: Comprehensive grading system with report cards
- **Timetable Management**: Automated timetable generation and management
- **Exam Management**: Exam scheduling, admit cards, and result processing

### 👥 User Management
- **Multi-Role System**: Students, Faculty, HOD, Management, and Proctor roles
- **User Profiles**: Detailed user profiles with photos and contact information
- **Permission System**: Role-based access control and permissions
- **Authentication**: Secure login with OTP verification and password reset

### 📚 Learning Management System (LMS)
- **Study Materials**: Upload and share documents, videos, and resources
- **Assignment System**: Create, submit, and grade assignments
- **Quiz System**: Online quizzes with auto-grading
- **Discussion Forums**: Interactive discussion boards for courses
- **Progress Tracking**: Monitor student progress and engagement

### 💼 Administrative Features
- **Admissions Management**: Complete admission workflow and tracking
- **Fee Management**: Fee structure, payment tracking, and receipts
- **Library Management**: Book catalog, issue tracking, and fine management
- **Hostel Management**: Room allocation and visitor management
- **Transport Management**: Route planning and student allocation
- **Event Management**: College events, participation tracking, and notifications

### 📊 Analytics & Reporting
- **Real-time Dashboards**: Interactive dashboards with key metrics
- **Custom Reports**: Flexible report builder with multiple export formats
- **Performance Analytics**: Student and faculty performance analysis
- **Financial Reports**: Fee collection and financial analytics
- **Attendance Analytics**: Detailed attendance reports and trends

### 🔧 Advanced Features
- **Real-time Chat**: Internal messaging system with WebSocket support
- **Mobile Responsive**: PWA-enabled mobile interface
- **API Integration**: RESTful API with JWT authentication
- **File Management**: Secure file upload and storage
- **Notification System**: Email, SMS, and in-app notifications
- **Backup & Recovery**: Automated backup and data recovery

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ (Recommended: 3.11+)
- PostgreSQL 12+ or SQLite 3.8+
- Redis 6+ (for caching)
- Node.js 16+ (for frontend assets)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/eduvision-college-management.git
   cd eduvision-college-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py loaddata fixtures/sample_data.json
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to access the application.

## 📖 Documentation

- **[Installation Guide](docs/INSTALLATION_GUIDE.md)**: Detailed installation instructions
- **[User Guide](docs/USER_GUIDE.md)**: Complete user manual for all roles
- **[Admin Guide](docs/ADMIN_GUIDE.md)**: Administrator configuration and management
- **[Developer Guide](docs/DEVELOPER_GUIDE.md)**: Development setup and contribution guide
- **[API Documentation](API_DOCUMENTATION.md)**: REST API reference and examples

## 🏗️ Architecture

### Technology Stack
- **Backend**: Django 5.2+, Python 3.11+
- **Database**: PostgreSQL 14+ with Redis caching
- **Frontend**: Django Templates, AdminLTE 3, Bootstrap 4
- **JavaScript**: jQuery, Chart.js, DataTables.js
- **API**: Django REST Framework with JWT authentication
- **Deployment**: Docker, Nginx, Gunicorn

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (AdminLTE)    │◄──►│   (Django)      │◄──►│   (PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CDN           │    │   Redis Cache   │    │   File Storage  │
│   (Static)      │    │   (Sessions)    │    │   (Media)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 User Roles

### 👨‍🎓 Student
- View academic records and attendance
- Access study materials and assignments
- Submit assignments and take quizzes
- Apply for leave and view results
- Access library and participate in events

### 👨‍🏫 Faculty
- Mark attendance and upload materials
- Grade assignments and create quizzes
- View student records and analytics
- Manage course content and discussions
- Access teaching tools and reports

### 👨‍💼 HOD/Admin
- Full system access and user management
- Academic configuration and approvals
- Analytics, reports, and system settings
- Course and subject management
- Staff and student oversight

### 🏢 Management
- Administrative operations and policies
- Financial management and reporting
- Staff coordination and HR functions
- Strategic planning and analytics

## 🔧 Configuration

### Environment Variables
```env
# Django Settings
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=yourdomain.com,localhost

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=eduvision
DB_USER=eduvision_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Redis
REDIS_URL=redis://localhost:6379/0
```

### Database Configuration
The system supports both PostgreSQL (production) and SQLite (development):
- **PostgreSQL**: Recommended for production with better performance
- **SQLite**: Suitable for development and small deployments

## 🚀 Deployment

### Docker Deployment
```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using deployment script
./scripts/deploy.sh
```

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Configure database
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Start with Gunicorn
gunicorn student_management_system.wsgi:application
```

### Production Checklist
- [ ] Configure production database
- [ ] Set up SSL certificates
- [ ] Configure email settings
- [ ] Set up monitoring and logging
- [ ] Configure backup system
- [ ] Set up CDN for static files
- [ ] Configure load balancing (if needed)

## 📊 Monitoring

### Built-in Monitoring
- **Performance Metrics**: Response times and resource usage
- **Error Tracking**: Application errors and exceptions
- **User Analytics**: User activity and engagement
- **System Health**: Database and cache performance

### External Monitoring
- **Prometheus**: Metrics collection and alerting
- **Grafana**: Visualization and dashboards
- **Sentry**: Error tracking and performance monitoring
- **Uptime Kuma**: Uptime monitoring and status pages

## 🔒 Security

### Security Features
- **Authentication**: JWT tokens with refresh mechanism
- **Authorization**: Role-based access control
- **Data Encryption**: Sensitive data encryption at rest
- **CSRF Protection**: Cross-site request forgery protection
- **XSS Protection**: Cross-site scripting prevention
- **SQL Injection**: Parameterized queries and ORM
- **File Upload Security**: File type and size validation
- **Audit Logging**: User action tracking and logging

### Security Best Practices
- Regular security updates and patches
- Strong password policies and enforcement
- Regular security audits and penetration testing
- Data backup and recovery procedures
- Access control and permission management

## 🧪 Testing

### Test Coverage
- **Unit Tests**: Model, view, and utility function tests
- **Integration Tests**: API and workflow testing
- **Performance Tests**: Load and stress testing
- **Security Tests**: Vulnerability and penetration testing

### Running Tests
```bash
# Run all tests
python manage.py test

# Run with coverage
coverage run --source='.' manage.py test
coverage report
coverage html

# Run specific test modules
python manage.py test main_app.tests.test_models
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](docs/DEVELOPER_GUIDE.md) for details.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

### Code Standards
- Follow PEP 8 for Python code
- Use type hints and docstrings
- Write comprehensive tests
- Update documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check our comprehensive guides
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions
- **Email**: support@eduvision.com

### Community
- **GitHub**: [Repository](https://github.com/yourusername/eduvision-college-management)
- **Discord**: [Community Server](https://discord.gg/eduvision)
- **Twitter**: [@EduVisionCMS](https://twitter.com/EduVisionCMS)

## 🗺️ Roadmap

### Upcoming Features
- [ ] Mobile app (React Native)
- [ ] Advanced analytics with AI/ML
- [ ] Integration with external LMS
- [ ] Multi-language support
- [ ] Advanced reporting with BI tools
- [ ] Blockchain-based certificate verification
- [ ] Video conferencing integration
- [ ] Advanced workflow automation

### Version History
- **v1.0.0**: Initial release with core features
- **v1.1.0**: Added LMS and analytics
- **v1.2.0**: Mobile responsiveness and PWA
- **v1.3.0**: API and integration features
- **v2.0.0**: Complete redesign and advanced features

## 🙏 Acknowledgments

- Django community for the excellent framework
- AdminLTE for the beautiful admin template
- Bootstrap for responsive design components
- Chart.js for data visualization
- All contributors and users who help improve the system

## 📞 Contact

- **Project Maintainer**: [Your Name](mailto:your.email@example.com)
- **Website**: [https://eduvision.com](https://eduvision.com)
- **Documentation**: [https://eduvision.com/docs](https://eduvision.com/docs)
- **Support**: [support@eduvision.com](mailto:support@eduvision.com)

---

**EduVision College Management System** - Empowering educational institutions with modern technology solutions.

⭐ **Star this repository** if you find it helpful!
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
