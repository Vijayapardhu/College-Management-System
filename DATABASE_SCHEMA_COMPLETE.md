# 🗄️ EduVision - Complete Database Schema

## Overview
This document provides the complete database structure for the EduVision University ERP System with all 50+ tables.

---

## 📋 TABLE OF CONTENTS

1. [Core Authentication](#core-authentication)
2. [Academic Structure](#academic-structure)
3. [Student Management](#student-management)
4. [Staff Management](#staff-management)
5. [Examination System](#examination-system)
6. [Attendance & Leave](#attendance--leave)
7. [Financial Management](#financial-management)
8. [Scholarship System](#scholarship-system)
9. [Hostel Management](#hostel-management)
10. [Transport Management](#transport-management)
11. [Library Management](#library-management)
12. [Placement Cell](#placement-cell)
13. [Communication](#communication)
14. [Academic Resources](#academic-resources)
15. [Events & Activities](#events--activities)
16. [Grievance System](#grievance-system)
17. [Activity Logs](#activity-logs)

---

## 1. CORE AUTHENTICATION

### `auth_user` (Django Built-in)
```sql
- id (PK, Auto-increment)
- username (Unique, VARCHAR)
- password (Hash, VARCHAR)
- email (VARCHAR)
- first_name (VARCHAR)
- last_name (VARCHAR)
- is_staff (BOOLEAN)
- is_active (BOOLEAN)
- is_superuser (BOOLEAN)
- date_joined (DATETIME)
- last_login (DATETIME)
```

### `main_app_customuser`
```sql
- id (PK, Auto-increment)
- user_ptr_id (FK -> auth_user, OneToOne)
- user_type (ENUM: 1=HOD, 2=Staff, 3=Student)
- gender (ENUM: M/F/O)
- profile_pic (ImageField)
- address (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_admin`
```sql
- id (PK, Auto-increment)
- admin_id (FK -> main_app_customuser, OneToOne)
```

---

## 2. ACADEMIC STRUCTURE

### `main_app_department`
```sql
- id (PK, Auto-increment)
- name (VARCHAR, Unique)
- code (VARCHAR, Unique)
- hod_id (FK -> main_app_staff, Nullable)
- contact_email (VARCHAR)
- contact_number (VARCHAR)
- description (TEXT)
- established_year (INTEGER)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_program`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- code (VARCHAR, Unique)
- program_type (ENUM: diploma/btech/mtech/phd/mca/mba)
- department_id (FK -> main_app_department)
- duration_years (INTEGER)
- total_semesters (INTEGER)
- total_credits (INTEGER)
- eligibility_criteria (TEXT)
- syllabus_document (FileField)
- is_active (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
- UNIQUE (name, program_type, department_id)
```

### `main_app_course` (Legacy)
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_session`
```sql
- id (PK, Auto-increment)
- start_year (DATE)
- end_year (DATE)
```

### `main_app_subject`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- staff_id (FK -> main_app_staff)
- course_id (FK -> main_app_course)
- created_at (DATETIME)
- updated_at (DATETIME)
```

---

## 3. STUDENT MANAGEMENT

### `main_app_student` (80+ Fields)
```sql
-- Primary Key
- id (PK, Auto-increment)
- admin_id (FK -> main_app_customuser, OneToOne)

-- Academic Information
- course_id (FK -> main_app_course)
- session_id (FK -> main_app_session)
- course_type (ENUM: diploma/btech/mtech/phd)
- admission_year (INTEGER)
- roll_number (VARCHAR, Unique)
- admission_number (VARCHAR, Unique)
- current_semester (INTEGER)

-- Personal Details
- date_of_birth (DATE)
- nationality (VARCHAR)
- religion (VARCHAR)
- blood_group (VARCHAR)
- mobile_number (VARCHAR)
- alternate_mobile (VARCHAR)
- aadhaar_number (VARCHAR, Unique)

-- Category & Scholarship
- caste_category (ENUM: general/obc/sc/st/ews)
- income_certificate_number (VARCHAR)
- annual_family_income (DECIMAL)
- is_disabled (BOOLEAN)
- disability_percentage (DECIMAL)

-- Address
- permanent_address (TEXT)
- permanent_city (VARCHAR)
- permanent_state (VARCHAR)
- permanent_pincode (VARCHAR)
- current_address (TEXT)
- current_city (VARCHAR)
- current_state (VARCHAR)
- current_pincode (VARCHAR)

-- Guardian Information
- father_name (VARCHAR)
- father_occupation (VARCHAR)
- father_mobile (VARCHAR)
- mother_name (VARCHAR)
- mother_occupation (VARCHAR)
- mother_mobile (VARCHAR)
- guardian_name (VARCHAR)
- guardian_relation (VARCHAR)
- guardian_mobile (VARCHAR)

-- Academic Background - 10th
- tenth_board (VARCHAR)
- tenth_school (VARCHAR)
- tenth_year (INTEGER)
- tenth_marks_total (DECIMAL)
- tenth_marks_obtained (DECIMAL)
- tenth_percentage (DECIMAL)
- tenth_cgpa (DECIMAL)

-- Academic Background - 12th
- twelfth_board (VARCHAR)
- twelfth_school (VARCHAR)
- twelfth_year (INTEGER)
- twelfth_marks_total (DECIMAL)
- twelfth_marks_obtained (DECIMAL)
- twelfth_percentage (DECIMAL)
- twelfth_cgpa (DECIMAL)

-- Diploma Details
- diploma_college (VARCHAR)
- diploma_branch (VARCHAR)
- diploma_year (INTEGER)
- diploma_percentage (DECIMAL)
- diploma_cgpa (DECIMAL)

-- Entrance Exam
- entrance_exam_name (VARCHAR)
- entrance_exam_year (INTEGER)
- entrance_exam_rank (INTEGER)
- entrance_exam_score (DECIMAL)
- entrance_category_rank (INTEGER)

-- Documents
- photo (ImageField)
- signature (ImageField)
- tenth_certificate (FileField)
- twelfth_certificate (FileField)
- diploma_certificate (FileField)
- transfer_certificate (FileField)
- migration_certificate (FileField)
- character_certificate (FileField)
- caste_certificate (FileField)
- income_certificate (FileField)
- disability_certificate (FileField)

-- Status & Graduation
- student_status (ENUM: active/graduated/suspended/dropped/transferred)
- date_of_graduation (DATE)
- graduation_cgpa (DECIMAL)

-- Additional Info
- hostel_required (BOOLEAN)
- transport_required (BOOLEAN)
- scholarship_applied (BOOLEAN)
- scholarship_name (VARCHAR)
- bank_account_number (VARCHAR)
- bank_ifsc_code (VARCHAR)
- bank_name (VARCHAR)

-- Emergency Contact
- emergency_contact_name (VARCHAR)
- emergency_contact_relation (VARCHAR)
- emergency_contact_mobile (VARCHAR)

-- Remarks
- remarks (TEXT)
```

---

## 4. STAFF MANAGEMENT

### `main_app_staff` (30+ Fields)
```sql
- id (PK, Auto-increment)
- admin_id (FK -> main_app_customuser, OneToOne)

-- Legacy
- course_id (FK -> main_app_course, Nullable)

-- New Structure
- department_id (FK -> main_app_department, Nullable)

-- Professional Information
- designation (ENUM: professor/associate_professor/assistant_professor/lecturer/hod/dean/principal/librarian/accountant/admin_staff)
- employee_id (VARCHAR, Unique)
- qualification (VARCHAR)
- specialization (VARCHAR)
- experience_years (INTEGER)

-- Contact
- mobile_number (VARCHAR)
- alternate_mobile (VARCHAR)
- emergency_contact (VARCHAR)

-- Date Information
- date_of_birth (DATE)
- date_of_joining (DATE)
- date_of_retirement (DATE)

-- Status
- status (ENUM: active/on_leave/retired/resigned/terminated)

-- Documents
- photo (ImageField)
- resume (FileField)

-- Permissions
- is_proctor (BOOLEAN)
- can_approve_events (BOOLEAN)
- can_manage_library (BOOLEAN)
- can_manage_exam (BOOLEAN)
- can_manage_placement (BOOLEAN)

-- Additional Info
- blood_group (VARCHAR)
- aadhaar_number (VARCHAR, Unique)
- pan_number (VARCHAR)

-- Banking
- bank_account_number (VARCHAR)
- bank_ifsc_code (VARCHAR)
- bank_name (VARCHAR)

- remarks (TEXT)
```

---

## 5. EXAMINATION SYSTEM

### `main_app_exam`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- exam_type (ENUM: mid_term/end_term/internal/practical/viva/quiz)
- session_id (FK -> main_app_session)
- semester (INTEGER)
- start_date (DATE)
- end_date (DATE)
- created_by_id (FK -> main_app_staff, Nullable)
- is_published (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_examschedule`
```sql
- id (PK, Auto-increment)
- exam_id (FK -> main_app_exam)
- subject_id (FK -> main_app_subject)
- exam_date (DATE)
- start_time (TIME)
- end_time (TIME)
- room_number (VARCHAR)
- max_marks (INTEGER)
- question_paper (FileField)
- answer_key (FileField)
- created_at (DATETIME)
- UNIQUE (exam_id, subject_id)
```

### `main_app_invigilator`
```sql
- id (PK, Auto-increment)
- exam_schedule_id (FK -> main_app_examschedule)
- staff_id (FK -> main_app_staff)
- duty_type (ENUM: chief/assistant)
- created_at (DATETIME)
- UNIQUE (exam_schedule_id, staff_id)
```

### `main_app_admitcard`
```sql
- id (PK, Auto-increment)
- exam_id (FK -> main_app_exam)
- student_id (FK -> main_app_student)
- admit_card_number (VARCHAR, Unique)
- is_generated (BOOLEAN)
- is_downloaded (BOOLEAN)
- downloaded_at (DATETIME)
- remarks (TEXT)
- created_at (DATETIME)
- UNIQUE (exam_id, student_id)
```

### `main_app_semesterresult`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- session_id (FK -> main_app_session)
- semester (INTEGER)
- total_credits (INTEGER)
- credits_earned (INTEGER)
- sgpa (DECIMAL)
- cgpa (DECIMAL)
- total_marks (DECIMAL)
- marks_obtained (DECIMAL)
- percentage (DECIMAL)
- has_backlogs (BOOLEAN)
- number_of_backlogs (INTEGER)
- is_published (BOOLEAN)
- published_date (DATETIME)
- remarks (TEXT)
- UNIQUE (student_id, session_id, semester)
```

### `main_app_subjectresult`
```sql
- id (PK, Auto-increment)
- semester_result_id (FK -> main_app_semesterresult)
- subject_id (FK -> main_app_subject)
- internal_marks (DECIMAL)
- external_marks (DECIMAL)
- total_marks (DECIMAL)
- max_marks (DECIMAL)
- grade (ENUM: O/A+/A/B+/B/C/P/F/AB)
- credits (INTEGER)
- is_pass (BOOLEAN)
- UNIQUE (semester_result_id, subject_id)
```

### `main_app_timetable`
```sql
- id (PK, Auto-increment)
- session_id (FK -> main_app_session)
- course_id (FK -> main_app_course)
- semester (INTEGER)
- weekday (ENUM: monday/tuesday/wednesday/thursday/friday/saturday)
- period (ENUM: 1-8)
- start_time (TIME)
- end_time (TIME)
- subject_id (FK -> main_app_subject)
- staff_id (FK -> main_app_staff)
- room_number (VARCHAR)
- is_lab (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
- UNIQUE (session_id, course_id, semester, weekday, period)
```

---

## 6. ATTENDANCE & LEAVE

### `main_app_attendance`
```sql
- id (PK, Auto-increment)
- session_id (FK -> main_app_session)
- subject_id (FK -> main_app_subject)
- date (DATE)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_attendancereport`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- attendance_id (FK -> main_app_attendance)
- status (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_leavereportstudent`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- date (VARCHAR)
- message (TEXT)
- status (INTEGER: 0=Pending, 1=Approved, 2=Rejected)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_leavereportstaff`
```sql
- id (PK, Auto-increment)
- staff_id (FK -> main_app_staff)
- date (VARCHAR)
- message (TEXT)
- status (INTEGER: 0=Pending, 1=Approved, 2=Rejected)
- created_at (DATETIME)
- updated_at (DATETIME)
```

---

## 7. FINANCIAL MANAGEMENT

### `main_app_feestructure`
```sql
- id (PK, Auto-increment)
- course_id (FK -> main_app_course)
- course_type (ENUM: diploma/btech/mtech/phd)
- semester (INTEGER)
- session_id (FK -> main_app_session)
- tuition_fee (DECIMAL)
- development_fee (DECIMAL)
- lab_fee (DECIMAL)
- library_fee (DECIMAL)
- exam_fee (DECIMAL)
- other_fee (DECIMAL)
- UNIQUE (course_id, course_type, semester, session_id)
```

### `main_app_feepayment`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- fee_structure_id (FK -> main_app_feestructure)
- amount_paid (DECIMAL)
- payment_date (DATE)
- payment_method (ENUM: cash/cheque/dd/online/card)
- transaction_id (VARCHAR)
- receipt_number (VARCHAR, Unique)
- status (ENUM: pending/partial/paid/overdue)
- remarks (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

---

## 8. SCHOLARSHIP SYSTEM

### `main_app_scholarship`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- scholarship_type (ENUM: merit/need/sports/minority/govt/private)
- description (TEXT)
- eligibility_criteria (TEXT)
- amount (DECIMAL)
- max_recipients (INTEGER)
- application_deadline (DATE)
- is_active (BOOLEAN)
```

### `main_app_scholarshipapplication`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- scholarship_id (FK -> main_app_scholarship)
- application_date (DATE)
- reason (TEXT)
- supporting_documents (FileField)
- status (ENUM: applied/under_review/approved/rejected/disbursed)
- reviewed_by_id (FK -> main_app_staff, Nullable)
- review_remarks (TEXT)
- reviewed_at (DATETIME)
- disbursement_date (DATE)
- disbursement_amount (DECIMAL)
```

---

## 9. HOSTEL MANAGEMENT

### `main_app_hostel`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- hostel_type (ENUM: boys/girls)
- warden_name (VARCHAR)
- warden_contact (VARCHAR)
- total_rooms (INTEGER)
- occupied_rooms (INTEGER)
- address (TEXT)
```

### `main_app_hostelallocation`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student, OneToOne)
- hostel_id (FK -> main_app_hostel)
- room_number (VARCHAR)
- allocated_date (DATE)
- rent_per_semester (DECIMAL)
- is_active (BOOLEAN)
```

### `main_app_hostelvisitorlog`
```sql
- id (PK, Auto-increment)
- hostel_id (FK -> main_app_hostel)
- student_id (FK -> main_app_student)
- visitor_name (VARCHAR)
- visitor_relation (VARCHAR)
- visitor_contact (VARCHAR)
- visitor_id_proof (VARCHAR)
- entry_time (DATETIME)
- exit_time (DATETIME, Nullable)
- purpose (TEXT)
- approved_by_id (FK -> main_app_staff, Nullable)
```

---

## 10. TRANSPORT MANAGEMENT

### `main_app_transport`
```sql
- id (PK, Auto-increment)
- route_name (VARCHAR)
- bus_number (VARCHAR)
- driver_name (VARCHAR)
- driver_contact (VARCHAR)
- route_details (TEXT)
- fee_per_semester (DECIMAL)
- total_seats (INTEGER)
- occupied_seats (INTEGER)
```

### `main_app_transportallocation`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- transport_id (FK -> main_app_transport)
- pickup_point (VARCHAR)
- registered_date (DATE)
- is_active (BOOLEAN)
- UNIQUE (student_id, transport_id)
```

---

## 11. LIBRARY MANAGEMENT

### `main_app_library`
```sql
- id (PK, Auto-increment)
- title (VARCHAR)
- author (VARCHAR)
- isbn (VARCHAR, Unique)
- publisher (VARCHAR)
- published_year (INTEGER)
- category (ENUM: textbook/reference/journal/magazine/ebook)
- subject_id (FK -> main_app_subject, Nullable)
- total_copies (INTEGER)
- available_copies (INTEGER)
- shelf_number (VARCHAR)
- description (TEXT)
- cover_image (ImageField)
```

### `main_app_libraryissue`
```sql
- id (PK, Auto-increment)
- book_id (FK -> main_app_library)
- student_id (FK -> main_app_student)
- issue_date (DATE)
- due_date (DATE)
- return_date (DATE, Nullable)
- status (ENUM: issued/returned/overdue/lost)
- fine_amount (DECIMAL)
- remarks (TEXT)
- issued_by_id (FK -> main_app_staff, Nullable)
```

---

## 12. PLACEMENT CELL

### `main_app_company`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- company_type (ENUM: product/service/startup/mnc/psu/government)
- website (URL)
- description (TEXT)
- hr_name (VARCHAR)
- hr_email (VARCHAR)
- hr_contact (VARCHAR)
- address (TEXT)
- logo (ImageField)
- is_active (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_placementdrive`
```sql
- id (PK, Auto-increment)
- company_id (FK -> main_app_company)
- session_id (FK -> main_app_session)
- drive_type (ENUM: campus/off_campus/pool/virtual)
- job_title (VARCHAR)
- job_description (TEXT)
- min_cgpa (DECIMAL)
- allowed_backlogs (INTEGER)
- salary_package (DECIMAL)
- bond_years (INTEGER)
- registration_deadline (DATETIME)
- aptitude_test_date (DATETIME)
- interview_date (DATETIME)
- selection_process (TEXT)
- number_of_openings (INTEGER)
- jd_document (FileField)
- is_active (BOOLEAN)
- coordinator_id (FK -> main_app_staff, Nullable)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_placementdrive_eligible_courses` (Many-to-Many)
```sql
- id (PK, Auto-increment)
- placementdrive_id (FK -> main_app_placementdrive)
- course_id (FK -> main_app_course)
```

### `main_app_placementapplication`
```sql
- id (PK, Auto-increment)
- placement_drive_id (FK -> main_app_placementdrive)
- student_id (FK -> main_app_student)
- applied_at (DATETIME)
- status (ENUM: registered/shortlisted/aptitude_cleared/technical_cleared/hr_cleared/selected/rejected/offer_accepted/offer_declined)
- resume (FileField)
- cover_letter (TEXT)
- aptitude_score (DECIMAL)
- technical_score (DECIMAL)
- hr_score (DECIMAL)
- offer_letter (FileField)
- offered_package (DECIMAL)
- joining_date (DATE)
- remarks (TEXT)
- updated_at (DATETIME)
- UNIQUE (placement_drive_id, student_id)
```

---

## 13. COMMUNICATION

### `main_app_message`
```sql
- id (PK, Auto-increment)
- sender_id (FK -> main_app_customuser)
- recipient_id (FK -> main_app_customuser)
- subject (VARCHAR)
- message (TEXT)
- is_read (BOOLEAN)
- parent_message_id (FK -> main_app_message, Nullable)
- sent_at (DATETIME)
- read_at (DATETIME, Nullable)
```

### `main_app_announcement`
```sql
- id (PK, Auto-increment)
- title (VARCHAR)
- message (TEXT)
- priority (ENUM: low/medium/high/urgent)
- target_audience (ENUM: all/staff/students/course)
- course_id (FK -> main_app_course, Nullable)
- posted_by_id (FK -> main_app_customuser)
- attachment (FileField)
- is_active (BOOLEAN)
- expires_at (DATETIME)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_notificationstudent`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- message (TEXT)
- created_at (DATETIME)
```

### `main_app_notificationstaff`
```sql
- id (PK, Auto-increment)
- staff_id (FK -> main_app_staff)
- message (TEXT)
- created_at (DATETIME)
```

---

## 14. ACADEMIC RESOURCES

### `main_app_studymaterial`
```sql
- id (PK, Auto-increment)
- title (VARCHAR)
- description (TEXT)
- material_type (ENUM: document/link/video)
- file (FileField)
- external_url (URL)
- subject_id (FK -> main_app_subject)
- course_id (FK -> main_app_course)
- uploaded_by_id (FK -> main_app_staff)
- is_archived (BOOLEAN)
- version (INTEGER)
- uploaded_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_resourcerating`
```sql
- id (PK, Auto-increment)
- material_id (FK -> main_app_studymaterial)
- student_id (FK -> main_app_student)
- rating (INTEGER: 1-5)
- review (TEXT)
- created_at (DATETIME)
- UNIQUE (material_id, student_id)
```

### `main_app_resourcebookmark`
```sql
- id (PK, Auto-increment)
- material_id (FK -> main_app_studymaterial)
- student_id (FK -> main_app_student)
- created_at (DATETIME)
- UNIQUE (material_id, student_id)
```

### `main_app_resourcedownloadlog`
```sql
- id (PK, Auto-increment)
- material_id (FK -> main_app_studymaterial)
- student_id (FK -> main_app_student)
- downloaded_at (DATETIME)
```

### `main_app_assignment`
```sql
- id (PK, Auto-increment)
- title (VARCHAR)
- description (TEXT)
- subject_id (FK -> main_app_subject)
- course_id (FK -> main_app_course)
- created_by_id (FK -> main_app_staff)
- due_date (DATETIME)
- max_marks (INTEGER)
- attachment (FileField)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_assignmentsubmission`
```sql
- id (PK, Auto-increment)
- assignment_id (FK -> main_app_assignment)
- student_id (FK -> main_app_student)
- submission_file (FileField)
- remarks (TEXT)
- status (ENUM: pending/submitted/graded/late)
- marks_obtained (FLOAT)
- feedback (TEXT)
- graded_by_id (FK -> main_app_staff, Nullable)
- graded_at (DATETIME)
- submitted_at (DATETIME)
- updated_at (DATETIME)
- UNIQUE (assignment_id, student_id)
```

### `main_app_discussion`
```sql
- id (PK, Auto-increment)
- title (VARCHAR)
- content (TEXT)
- material_id (FK -> main_app_studymaterial, Nullable)
- subject_id (FK -> main_app_subject)
- created_by_id (FK -> main_app_customuser)
- is_pinned (BOOLEAN)
- is_locked (BOOLEAN)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_discussionreply`
```sql
- id (PK, Auto-increment)
- discussion_id (FK -> main_app_discussion)
- content (TEXT)
- created_by_id (FK -> main_app_customuser)
- created_at (DATETIME)
- updated_at (DATETIME)
```

---

## 15. EVENTS & ACTIVITIES

### `main_app_event`
```sql
- id (PK, Auto-increment)
- name (VARCHAR)
- description (TEXT)
- event_type (ENUM: academic/cultural/sports/technical/other)
- start_date (DATETIME)
- end_date (DATETIME)
- venue (VARCHAR)
- max_participants (INTEGER)
- registration_deadline (DATETIME)
- created_by_id (FK -> main_app_staff)
- status (ENUM: pending/approved/rejected/completed)
- approved_by_id (FK -> main_app_staff, Nullable)
- poster (ImageField)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_eventparticipation`
```sql
- id (PK, Auto-increment)
- event_id (FK -> main_app_event)
- student_id (FK -> main_app_student)
- registered_at (DATETIME)
- attended (BOOLEAN)
- certificate_issued (BOOLEAN)
- UNIQUE (event_id, student_id)
```

---

## 16. GRIEVANCE SYSTEM

### `main_app_grievance`
```sql
- id (PK, Auto-increment)
- grievance_number (VARCHAR, Unique)
- submitted_by_id (FK -> main_app_customuser)
- grievance_type (ENUM: academic/administrative/hostel/library/transport/ragging/fee/other)
- subject (VARCHAR)
- description (TEXT)
- priority (ENUM: low/medium/high/urgent)
- attachment (FileField)
- status (ENUM: submitted/under_review/in_progress/resolved/closed/rejected)
- assigned_to_id (FK -> main_app_staff, Nullable)
- resolution (TEXT)
- resolved_at (DATETIME)
- submitted_at (DATETIME)
- updated_at (DATETIME)
```

---

## 17. ACTIVITY LOGS

### `main_app_activitylog`
```sql
- id (PK, Auto-increment)
- user_id (FK -> main_app_customuser, Nullable)
- action (ENUM: create/update/delete/login/logout/view/download/upload)
- model_name (VARCHAR)
- object_id (INTEGER)
- description (TEXT)
- ip_address (IP Address)
- user_agent (TEXT)
- timestamp (DATETIME)
- INDEX (timestamp DESC)
- INDEX (user_id, timestamp DESC)
```

---

## 18. PROCTOR SYSTEM

### `main_app_proctorassignment`
```sql
- id (PK, Auto-increment)
- staff_id (FK -> main_app_staff, limit_choices_to: is_proctor=True)
- student_id (FK -> main_app_student)
- assigned_date (DATETIME)
- is_active (BOOLEAN)
- UNIQUE (staff_id, student_id)
```

---

## 19. FEEDBACK SYSTEM

### `main_app_feedbackstudent`
```sql
- id (PK, Auto-increment)
- student_id (FK -> main_app_student)
- feedback (TEXT)
- reply (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

### `main_app_feedbackstaff`
```sql
- id (PK, Auto-increment)
- staff_id (FK -> main_app_staff)
- feedback (TEXT)
- reply (TEXT)
- created_at (DATETIME)
- updated_at (DATETIME)
```

---

## 🔗 KEY RELATIONSHIPS SUMMARY

### One-to-One
- CustomUser ↔ Admin/Staff/Student
- Student ↔ HostelAllocation

### One-to-Many
- Department → Programs
- Program → Students (through Course)
- Session → Exams, Timetables, Results
- Staff → Created Exams, Assignments, Events
- Student → SemesterResults, Assignments, Placements
- Course → Subjects, Students, Timetables
- Exam → ExamSchedules, AdmitCards
- Library → LibraryIssues
- Company → PlacementDrives
- PlacementDrive → Applications

### Many-to-Many
- PlacementDrive ↔ Courses (eligible courses)
- Staff ↔ ExamSchedules (via Invigilator)

---

## 📊 TABLE COUNT & SIZE ESTIMATES

### Total Tables: 50+

### Expected Record Volumes (for a mid-sized university):
- **Students**: 5,000 - 10,000
- **Staff**: 200 - 500
- **Subjects**: 500 - 1,000
- **Exams**: 100 - 200 per year
- **Attendance Records**: 1M+ per year
- **Fee Payments**: 50K+ per year
- **Library Issues**: 10K+ per year
- **Activity Logs**: Unlimited (millions over time)

---

## 🔒 INDEXES & OPTIMIZATIONS

### Recommended Indexes (already implemented):
```sql
-- Activity Logs
CREATE INDEX idx_activitylog_timestamp ON main_app_activitylog(timestamp DESC);
CREATE INDEX idx_activitylog_user_time ON main_app_activitylog(user_id, timestamp DESC);

-- Unique Constraints
UNIQUE (exam_id, student_id) ON main_app_admitcard
UNIQUE (assignment_id, student_id) ON main_app_assignmentsubmission
UNIQUE (material_id, student_id) ON main_app_resourcerating
UNIQUE (material_id, student_id) ON main_app_resourcebookmark
UNIQUE (event_id, student_id) ON main_app_eventparticipation
```

---

## 🚀 PERFORMANCE CONSIDERATIONS

1. **Partitioning** (for large datasets):
   - Consider partitioning ActivityLog by month/year
   - Partition Attendance by session

2. **Archival**:
   - Move graduated students to archive tables
   - Archive old activity logs

3. **Caching**:
   - Cache frequently accessed data (departments, courses)
   - Use Redis for session management

4. **Query Optimization**:
   - Use select_related() for Foreign Keys
   - Use prefetch_related() for Many-to-Many
   - Index commonly filtered fields

---

## 📝 MIGRATION HISTORY

```
0001_initial.py - Core models
0002_auto_*.py - Attendance, Leave, Feedback
0003_auto_*.py - Events, Messages, Resources
0004_auto_*.py - Student comprehensive fields, Hostel, Transport, Library, Results
0005_auto_*.py - Department, Program, Staff enhancements, Exams, Placement, Grievance, Timetable
```

---

## ✅ CONCLUSION

This database schema supports a **complete university ERP system** with:
- ✅ **50+ interconnected tables**
- ✅ **Comprehensive student records** (80+ fields)
- ✅ **Complete academic lifecycle** (admission to graduation)
- ✅ **Financial management** (fees, scholarships)
- ✅ **Facility management** (hostel, transport, library)
- ✅ **Examination system** (scheduling, grading, results)
- ✅ **Placement services** (companies, drives, applications)
- ✅ **Communication hub** (messages, announcements)
- ✅ **Activity tracking** (audit logs)
- ✅ **Scalable architecture** (10,000+ students)

**The schema is normalized, indexed, and production-ready!**

---

**Database Engine**: SQLite (development) / MySQL/PostgreSQL (production)  
**ORM**: Django 3.2.25  
**Version**: 3.0.0  
**Last Updated**: October 2025


