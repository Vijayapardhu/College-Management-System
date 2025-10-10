# EduVision – College Management Application

## 📋 Abstract

This project introduces **EduVision**, a centralized college management platform designed to simplify and digitalize core academic operations. The system integrates features such as attendance tracking, marks entry, event management, student–faculty communication, and real-time academic reporting. 

Unlike existing systems such as ECAP, EduVision provides a modern, mobile-friendly, and secure solution with role-based access for students, faculty, HODs, and proctors. Its intuitive interface and real-time synchronization aim to improve transparency, reduce inefficiencies, and enhance decision-making in academic environments.

---

## 🔍 System Comparison

### ❌ Existing System (ECAP)
- ECAP is widely used for managing attendance, marks, and timetables
- Updates are often delayed, leading to inaccurate or outdated information
- UI is outdated, cluttered, and not optimized for mobile devices
- No real-time monitoring of attendance or events
- Limited communication features for students and faculty
- Lacks advanced analytics and strong data security

### ✅ Proposed System (EduVision)
- Modern, mobile-first application with clean UI
- Real-time synchronization using Supabase
- Secure role-based access for Students, Faculty, HODs, and Proctors
- Attendance and marks entry with instant updates
- Event creation, approval, and participation tracking
- Feedback, request submission, and direct communication channels
- Analytics dashboards for class-wise and department-level performance monitoring
- Proctor-specific tools for absentee list generation and student history review

---

## ✨ Core Features

### 👨‍💼 HOD/Admin Users Can
1. **Dashboard Analytics** - View comprehensive charts of student performance, staff performance, courses, subjects, and leave statistics
2. **Staff Management** - Add, update, and delete staff members with role-based permissions
3. **Student Management** - Complete CRUD operations for student records
4. **Course Management** - Manage courses and academic programs
5. **Subject Management** - Add, update, and delete subjects across departments
6. **Session Management** - Configure and manage academic sessions/semesters
7. **Attendance Monitoring** - Real-time attendance tracking with class-wise and department-level reports
8. **Feedback System** - Review and respond to feedback from students and staff
9. **Leave Management** - Approve or reject leave applications from students and faculty
10. **Event Approval** - Review and approve event creation requests
11. **Performance Analytics** - Access department-level performance monitoring dashboards

### 👨‍🏫 Faculty/Staff Users Can
1. **Performance Dashboard** - View summary charts related to their students, subjects, and leave status
2. **Attendance Management** - Take and update student attendance with instant synchronization
3. **Marks Entry** - Add and update student results/marks in real-time
4. **Leave Application** - Submit leave requests with instant notification to HOD
5. **Feedback Submission** - Send feedback and suggestions to HOD
6. **Event Management** - Create event proposals for approval
7. **Student Communication** - Direct communication channels with students
8. **Class Analytics** - Monitor class-wise performance and attendance trends

### 🎓 Students Can
1. **Personal Dashboard** - View comprehensive summary of attendance, marks, and academic progress
2. **Real-time Attendance** - Check attendance status with instant updates
3. **Results Access** - View marks and academic performance across subjects
4. **Leave Application** - Apply for leave with tracking and approval status
5. **Feedback System** - Submit feedback and requests to faculty and HOD
6. **Event Participation** - View and participate in college events
7. **Academic History** - Access complete academic record and progress reports
8. **Communication** - Direct communication with faculty and proctors

### 🎯 Proctor-Specific Features
1. **Absentee Tracking** - Generate absentee lists for assigned students
2. **Student History** - Review complete academic and attendance history of mentees
3. **Performance Monitoring** - Track individual student progress and identify at-risk students
4. **Communication Tools** - Direct channels for student guidance and support


---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 3.2.25
- **Database:** SQLite (Development) / PostgreSQL or MySQL (Production)
- **Authentication:** Django Auth with Email-based login
- **Real-time Sync:** Supabase integration support

### Frontend
- **Template Engine:** Django Templates
- **UI Framework:** AdminLTE 3.0
- **CSS Framework:** Bootstrap 4
- **Icons:** Font Awesome, Ionicons
- **Charts:** Chart.js
- **JavaScript Libraries:** jQuery, Moment.js

### Key Features
- **Role-based Access Control** - Separate dashboards for HOD, Faculty, Students, and Proctors
- **Responsive Design** - Mobile-first approach for accessibility on all devices
- **Real-time Updates** - Instant synchronization of attendance and marks
- **Secure Authentication** - Email-based login with password encryption
- **Data Validation** - Comprehensive form validation and error handling
- **File Management** - Profile picture uploads with Django FileSystemStorage

---

## 📸 ScreenShots

<img src="ss/1.png"/>
<img src="ss/2.png"/>
<img src="ss/3.png"/>
<img src="ss/4.png"/>
<img src="ss/5.png"/>

| Admin| Staff| Student |
|------|-------|---------|
|<img src="ss/admin5.png" width="400">|<img src="ss/staff1.png" width="400">|<img src="ss/student1.png" width="400">|

|<img src="ss/admin2.png" width="400">|<img src="ss/staff2.png" width="400">|<img src="ss/student2.png" width="400">|

|<img src="ss/admin3.png" width="400">|<img src="ss/staff3.png" width="400">|<img src="ss/student3.png" width="400">|

|<img src="ss/admin4.png" width="400">|<img src="ss/staff4.png" width="400">|<img src="ss/student4.png" width="400">|

|<img src="ss/admin1.png" width="400">|<img src="ss/staff5.png" width="400">|<img src="ss/student5.png" width="400">|

|<img src="ss/admin6.png" width="400">|<img src="ss/staff6.png" width="400">|<img src="ss/student6.png" width="400">|

---

## 🚀 Installation & Setup

### Prerequisites
Before you begin, ensure you have the following installed:

1. **Git** - Version Control System
   - Download: [https://git-scm.com/](https://git-scm.com/)

2. **Python 3.8+** - Programming Language
   - Download: [https://www.python.org/downloads/](https://www.python.org/downloads/)

3. **pip** - Python Package Manager (comes with Python)
   - Verify: `pip --version`

---

### Step-by-Step Installation

#### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/EduVision.git
cd EduVision
```

#### 2️⃣ Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4️⃣ Configure Database
Run migrations to set up the database:
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5️⃣ Create Superuser (HOD/Admin)
```bash
python manage.py createsuperuser
```
- Enter your email address
- Set a secure password
- Confirm password

#### 6️⃣ Run Development Server
```bash
python manage.py runserver
```

#### 7️⃣ Access the Application
Open your browser and navigate to:
- **Application:** [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Admin Panel:** [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## 🔐 Default Login Credentials

### HOD/Admin
- **Email:** `admin@admin.com`
- **Password:** `admin123`

### Faculty/Staff
- **Email:** `staff@staff.com`
- **Password:** `staff`
- *(Create via admin panel)*

### Student
- **Email:** `student@student.com`
- **Password:** `student`
- *(Create via admin panel)*

> **Note:** For security, change these default credentials in production environments.

---

## 📝 Configuration

### Environment Variables (Optional)
Create a `.env` file in the root directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Email Configuration
For email notifications, update `settings.py`:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
```

---

## 🎨 UI/UX Credits
- **Admin Template:** [AdminLTE 3.0](https://adminlte.io/)
- **Stock Images:** [Unsplash](https://unsplash.com)

---

## 🚧 Future Enhancements

- [ ] Mobile Application (iOS & Android)
- [ ] Advanced Analytics Dashboard with AI-powered insights
- [ ] Automated Report Generation (PDF/Excel)
- [ ] Parent Portal for student progress monitoring
- [ ] Integration with Learning Management Systems (LMS)
- [ ] SMS and Push Notification support
- [ ] Biometric Attendance Integration
- [ ] Online Exam/Quiz Module
- [ ] Library Management System
- [ ] Fee Management & Payment Gateway Integration
- [ ] Alumni Tracking System
- [ ] Placement Cell Management

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -m 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Authors & Contributors

- **Project Lead:** Your Name
- **Contributors:** List of contributors

---

## 📞 Support & Contact

For issues, questions, or suggestions:
- **Email:** support@eduvision.com
- **GitHub Issues:** [Create an issue](https://github.com/yourusername/EduVision/issues)
- **Documentation:** [Wiki](https://github.com/yourusername/EduVision/wiki)

---

## ⭐ Show Your Support

If you find this project helpful, please give it a ⭐ on GitHub!

---

**Built with ❤️ for better education management**
