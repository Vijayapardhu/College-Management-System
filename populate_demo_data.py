#!/usr/bin/env python
"""
Demo Data Population Script for EduVision College Management System
This script populates the database with sample students, faculty, courses, and other data
"""

import os
import sys
import django
from datetime import datetime, date, timedelta
import random
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from main_app.models import (
    CustomUser, Course, Subject, Session, Department, Staff, Student,
    Attendance, FeeStructure, FeePayment, Exam, ExamSchedule, Timetable,
    Company, PlacementDrive, PlacementApplication, Hostel, HostelAllocation,
    Transport, TransportAllocation, Library, LibraryIssue, Grievance,
    Scholarship, ScholarshipApplication, Alumni, Internship, MedicalRecord,
    GatePass, DisciplinaryAction, SportsActivity, ActivityParticipation,
    Research, AntiRaggingCommittee, StudentCouncil, ParentGuardian,
    Classroom, ClassroomBooking, ClassroomMaintenance, Management
)

User = get_user_model()

# Sample data
FIRST_NAMES = [
    'Aarav', 'Aditi', 'Arjun', 'Ananya', 'Rohan', 'Priya', 'Vikram', 'Sneha',
    'Rahul', 'Kavya', 'Suresh', 'Deepika', 'Rajesh', 'Pooja', 'Amit', 'Shruti',
    'Vikash', 'Neha', 'Sandeep', 'Ritu', 'Manish', 'Anjali', 'Ravi', 'Sunita',
    'Kiran', 'Meera', 'Pradeep', 'Kavita', 'Naveen', 'Suman', 'Rakesh', 'Geeta',
    'Manoj', 'Rekha', 'Suresh', 'Lata', 'Vinod', 'Usha', 'Raj', 'Indira',
    'Kumar', 'Sarita', 'Ashok', 'Kamala', 'Suresh', 'Radha', 'Mohan', 'Leela'
]

LAST_NAMES = [
    'Sharma', 'Verma', 'Gupta', 'Singh', 'Kumar', 'Patel', 'Yadav', 'Jain',
    'Agarwal', 'Mishra', 'Pandey', 'Tiwari', 'Choudhary', 'Reddy', 'Nair',
    'Iyer', 'Menon', 'Pillai', 'Rao', 'Naidu', 'Gowda', 'Shetty', 'Joshi',
    'Desai', 'Mehta', 'Bhatt', 'Trivedi', 'Shukla', 'Dwivedi', 'Saxena',
    'Agarwal', 'Bansal', 'Goyal', 'Jindal', 'Khanna', 'Malhotra', 'Sethi',
    'Tandon', 'Vohra', 'Wadhwa', 'Zaveri', 'Ahuja', 'Bajaj', 'Chopra', 'Dua'
]

COURSES = [
    {'name': 'Computer Science Engineering', 'code': 'CSE', 'duration_years': 4},
    {'name': 'Electronics and Communication Engineering', 'code': 'ECE', 'duration_years': 4},
    {'name': 'Mechanical Engineering', 'code': 'ME', 'duration_years': 4},
    {'name': 'Civil Engineering', 'code': 'CE', 'duration_years': 4},
    {'name': 'Electrical Engineering', 'code': 'EE', 'duration_years': 4},
    {'name': 'Information Technology', 'code': 'IT', 'duration_years': 4},
    {'name': 'Aerospace Engineering', 'code': 'AE', 'duration_years': 4},
    {'name': 'Biotechnology', 'code': 'BT', 'duration_years': 4},
    {'name': 'Master of Computer Applications', 'code': 'MCA', 'duration_years': 3},
    {'name': 'Master of Business Administration', 'code': 'MBA', 'duration_years': 2},
]

SUBJECTS = [
    # CSE Subjects
    {'name': 'Programming in C', 'code': 'CS101', 'credits': 4},
    {'name': 'Data Structures', 'code': 'CS102', 'credits': 4},
    {'name': 'Computer Networks', 'code': 'CS201', 'credits': 3},
    {'name': 'Database Management Systems', 'code': 'CS202', 'credits': 4},
    {'name': 'Operating Systems', 'code': 'CS301', 'credits': 4},
    {'name': 'Software Engineering', 'code': 'CS302', 'credits': 3},
    {'name': 'Machine Learning', 'code': 'CS401', 'credits': 3},
    {'name': 'Artificial Intelligence', 'code': 'CS402', 'credits': 3},
    
    # ECE Subjects
    {'name': 'Digital Electronics', 'code': 'EC101', 'credits': 4},
    {'name': 'Analog Electronics', 'code': 'EC102', 'credits': 4},
    {'name': 'Communication Systems', 'code': 'EC201', 'credits': 4},
    {'name': 'Microprocessors', 'code': 'EC202', 'credits': 3},
    {'name': 'VLSI Design', 'code': 'EC301', 'credits': 3},
    {'name': 'Signal Processing', 'code': 'EC302', 'credits': 4},
    
    # ME Subjects
    {'name': 'Thermodynamics', 'code': 'ME101', 'credits': 4},
    {'name': 'Fluid Mechanics', 'code': 'ME102', 'credits': 4},
    {'name': 'Machine Design', 'code': 'ME201', 'credits': 4},
    {'name': 'Heat Transfer', 'code': 'ME202', 'credits': 3},
    {'name': 'Manufacturing Technology', 'code': 'ME301', 'credits': 4},
    {'name': 'Automobile Engineering', 'code': 'ME302', 'credits': 3},
]

DEPARTMENTS = [
    'Computer Science and Engineering',
    'Electronics and Communication Engineering',
    'Mechanical Engineering',
    'Civil Engineering',
    'Electrical Engineering',
    'Information Technology',
    'Aerospace Engineering',
    'Biotechnology',
    'Management Studies',
    'Mathematics',
    'Physics',
    'Chemistry',
    'English',
    'Physical Education'
]

COMPANIES = [
    {'name': 'TechCorp Solutions', 'industry': 'Technology', 'website': 'https://techcorp.com'},
    {'name': 'DataSoft Technologies', 'industry': 'Software', 'website': 'https://datasoft.com'},
    {'name': 'InnovateTech', 'industry': 'Innovation', 'website': 'https://innovatetech.com'},
    {'name': 'CloudSystems Inc', 'industry': 'Cloud Computing', 'website': 'https://cloudsystems.com'},
    {'name': 'AI Dynamics', 'industry': 'Artificial Intelligence', 'website': 'https://aidynamics.com'},
    {'name': 'CyberGuard', 'industry': 'Cybersecurity', 'website': 'https://cyberguard.com'},
    {'name': 'MobileFirst', 'industry': 'Mobile Development', 'website': 'https://mobilefirst.com'},
    {'name': 'WebCraft', 'industry': 'Web Development', 'website': 'https://webcraft.com'},
    {'name': 'DataAnalytics Pro', 'industry': 'Data Science', 'website': 'https://dataanalytics.com'},
    {'name': 'BlockChain Solutions', 'industry': 'Blockchain', 'website': 'https://blockchainsolutions.com'},
]

def create_departments():
    """Create departments"""
    print("Creating departments...")
    for i, dept_name in enumerate(DEPARTMENTS):
        dept_code = f"DEPT{i+1:03d}"
        dept, created = Department.objects.get_or_create(
            name=dept_name,
            defaults={'code': dept_code}
        )
        if created:
            print(f"  Created department: {dept_name}")

def create_courses():
    """Create courses"""
    print("Creating courses...")
    for course_data in COURSES:
        course, created = Course.objects.get_or_create(
            name=course_data['name']
        )
        if created:
            print(f"  Created course: {course_data['name']}")

def create_sessions():
    """Create academic sessions"""
    print("Creating sessions...")
    current_year = datetime.now().year
    
    for i in range(5):  # Create 5 sessions
        start_year = current_year - 2 + i
        end_year = start_year + 1
        
        start_date = date(start_year, 7, 1)  # July 1st
        end_date = date(end_year, 6, 30)     # June 30th
        
        session, created = Session.objects.get_or_create(
            start_year=start_date,
            end_year=end_date
        )
        if created:
            print(f"  Created session: {start_year}-{end_year}")

def create_subjects():
    """Create subjects and assign to courses"""
    print("Creating subjects...")
    
    # Get courses and staff
    courses = Course.objects.all()
    staff_members = Staff.objects.all()
    
    if not staff_members.exists():
        print("  No staff members found. Creating subjects without staff assignment.")
        return
    
    for subject_data in SUBJECTS:
        # Assign subjects to appropriate courses based on name
        course = None
        if 'Computer' in subject_data['name'] or 'Programming' in subject_data['name'] or 'Software' in subject_data['name']:
            course = courses.filter(name__icontains='Computer').first()
        elif 'Electronics' in subject_data['name'] or 'Communication' in subject_data['name']:
            course = courses.filter(name__icontains='Electronics').first()
        elif 'Mechanical' in subject_data['name'] or 'Thermodynamics' in subject_data['name']:
            course = courses.filter(name__icontains='Mechanical').first()
        
        if not course:
            course = courses.first()  # Default to first course
        
        # Assign to a random staff member
        staff = random.choice(staff_members)
        
        subject, created = Subject.objects.get_or_create(
            name=subject_data['name'],
            course=course,
            defaults={
                'staff': staff
            }
        )
        if created:
            print(f"  Created subject: {subject_data['name']}")

def create_faculty():
    """Create faculty members"""
    print("Creating faculty...")
    
    departments = Department.objects.all()
    courses = Course.objects.all()
    
    # Check existing staff count
    existing_count = Staff.objects.count()
    if existing_count >= 10:
        print(f"  {existing_count} faculty members already exist. Skipping faculty creation.")
        return
    
    for i in range(30):  # Create 30 faculty members
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"faculty{i+1}@college.edu"
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            continue
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                email=email,
                password='faculty123',
                user_type=2,  # Staff
                first_name=first_name,
                last_name=last_name
            )
            
            # Create staff profile
            staff = Staff.objects.create(
                admin=user,
                employee_id=f"EMP{i+1:04d}",
                department=random.choice(departments),
                date_of_joining=date.today() - timedelta(days=random.randint(30, 1000)),
                designation=random.choice(['professor', 'associate_professor', 'assistant_professor', 'lecturer']),
                qualification=random.choice(['Ph.D', 'M.Tech', 'M.E', 'M.Sc', 'M.C.A']),
                experience_years=random.randint(1, 20),
                mobile_number=f"9{random.randint(100000000, 999999999)}",
                specialization=random.choice(['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Electrical']),
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                aadhaar_number=f"{random.randint(100000000000, 999999999999)}"
            )
            
            # Assign subjects to staff
            subjects = Subject.objects.filter(course__department=staff.department)[:3]
            staff.subjects.set(subjects)
            
            print(f"  Created faculty: {first_name} {last_name}")
            
        except Exception as e:
            print(f"  Error creating faculty {i+1}: {str(e)}")
            continue

def create_students():
    """Create students"""
    print("Creating students...")
    
    courses = Course.objects.all()
    sessions = Session.objects.all()
    
    # Check existing student count
    existing_count = Student.objects.count()
    if existing_count >= 50:
        print(f"  {existing_count} students already exist. Skipping student creation.")
        return
    
    for i in range(100):  # Create 100 students
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"student{i+1}@college.edu"
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            continue
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                email=email,
                password='student123',
                user_type=3,  # Student
                first_name=first_name,
                last_name=last_name,
                gender=random.choice(['M', 'F']),
                address=f"Student Address {i+1}"
            )
            
            # Create student profile
            course = random.choice(courses)
            session = random.choice(sessions)
            
            student = Student.objects.create(
                admin=user,
                roll_number=f"STU{i+1:04d}",
                admission_number=f"ADM{i+1:06d}",
                course=course,
                session=session,
                permanent_address=f"Student Address {i+1}",
                permanent_city=random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']),
                permanent_state=random.choice(['Maharashtra', 'Delhi', 'Karnataka', 'Tamil Nadu', 'West Bengal', 'Telangana', 'Gujarat']),
                permanent_pincode=f"{random.randint(100000, 999999)}",
                father_name=f"Father of {first_name}",
                mother_name=f"Mother of {first_name}",
                father_occupation=random.choice(['Business', 'Service', 'Farmer', 'Teacher', 'Engineer', 'Doctor']),
                mother_occupation=random.choice(['Housewife', 'Teacher', 'Nurse', 'Business', 'Service']),
                father_mobile=f"9{random.randint(100000000, 999999999)}",
                mother_mobile=f"9{random.randint(100000000, 999999999)}",
                caste_category=random.choice(['general', 'obc', 'sc', 'st', 'ews']),
                annual_family_income=random.randint(100000, 2000000),
                blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']),
                nationality='Indian',
                religion=random.choice(['Hindu', 'Muslim', 'Christian', 'Sikh', 'Buddhist', 'Jain'])
            )
            
            print(f"  Created student: {first_name} {last_name} - {course.name}")
            
        except Exception as e:
            print(f"  Error creating student {i+1}: {str(e)}")
            continue

def create_attendance():
    """Create attendance records"""
    print("Creating attendance records...")
    
    students = Student.objects.all()
    subjects = Subject.objects.all()
    
    # Create attendance for last 30 days
    for i in range(30):
        attendance_date = date.today() - timedelta(days=i)
        
        for student in students[:50]:  # Only for first 50 students
            for subject in subjects[:3]:  # Only for first 3 subjects
                Attendance.objects.get_or_create(
                    student=student,
                    subject=subject,
                    session=student.session,
                    date=attendance_date,
                    defaults={
                        'status': random.choice([True, True, True, False]),  # 75% attendance
                        'marked_by': Staff.objects.first()
                    }
                )
    
    print(f"  Created attendance records for {students.count()} students")

def create_fee_structures():
    """Create fee structures"""
    print("Creating fee structures...")
    
    courses = Course.objects.all()
    
    for course in courses:
        FeeStructure.objects.get_or_create(
            course=course,
            session=Session.objects.first(),
            defaults={
                'tuition_fee': random.randint(50000, 200000),
                'hostel_fee': random.randint(20000, 50000),
                'transport_fee': random.randint(10000, 25000),
                'library_fee': random.randint(2000, 5000),
                'exam_fee': random.randint(5000, 10000),
                'misc_fee': random.randint(5000, 15000),
                'total_fee': 0  # Will be calculated
            }
        )
    
    print("  Created fee structures")

def create_companies():
    """Create companies for placement"""
    print("Creating companies...")
    
    for company_data in COMPANIES:
        company, created = Company.objects.get_or_create(
            name=company_data['name'],
            defaults={
                'industry': company_data['industry'],
                'website': company_data['website'],
                'description': f"Leading company in {company_data['industry']}",
                'contact_person': f"HR Manager - {company_data['name']}",
                'contact_email': f"hr@{company_data['name'].lower().replace(' ', '')}.com",
                'contact_phone': f"9{random.randint(100000000, 999999999)}",
                'address': f"Corporate Office, {company_data['name']}",
                'is_active': True
            }
        )
        if created:
            print(f"  Created company: {company_data['name']}")

def create_placement_drives():
    """Create placement drives"""
    print("Creating placement drives...")
    
    companies = Company.objects.all()
    sessions = Session.objects.all()
    courses = Course.objects.all()
    
    for i in range(10):  # Create 10 placement drives
        company = random.choice(companies)
        session = random.choice(sessions)
        
        drive, created = PlacementDrive.objects.get_or_create(
            company=company,
            session=session,
            job_title=f"Software Engineer - {company.name}",
            defaults={
                'drive_type': random.choice(['campus', 'off_campus', 'walk_in']),
                'job_description': f"Exciting opportunity to work with {company.name}",
                'eligible_courses': courses[:3],
                'min_cgpa': round(random.uniform(6.0, 8.5), 2),
                'allowed_backlogs': random.randint(0, 3),
                'salary_package': random.randint(300000, 1500000),
                'bond_years': random.randint(0, 2),
                'registration_deadline': datetime.now() + timedelta(days=random.randint(7, 30)),
                'aptitude_test_date': datetime.now() + timedelta(days=random.randint(10, 40)),
                'interview_date': datetime.now() + timedelta(days=random.randint(15, 45)),
                'selection_process': 'Online Test -> Technical Interview -> HR Interview',
                'number_of_openings': random.randint(5, 50),
                'coordinator': Staff.objects.first(),
                'is_active': True
            }
        )
        if created:
            print(f"  Created placement drive: {company.name}")

def create_alumni():
    """Create alumni records"""
    print("Creating alumni...")
    
    # Get existing students to convert to alumni
    students = Student.objects.all()
    
    # Check existing alumni count
    existing_count = Alumni.objects.count()
    if existing_count >= 10:
        print(f"  {existing_count} alumni already exist. Skipping alumni creation.")
        return
    
    for i, student in enumerate(students[:20]):  # Convert first 20 students to alumni
        # Check if alumni already exists for this student
        if Alumni.objects.filter(student=student).exists():
            continue
        
        try:
            # Create alumni profile
            alumni = Alumni.objects.create(
                student=student,
                passout_year=student.session.end_year.year,
                final_cgpa=round(random.uniform(6.0, 9.5), 2),
                current_company=random.choice(COMPANIES)['name'],
                current_designation=random.choice(['Software Engineer', 'Senior Software Engineer', 'Tech Lead', 'Manager', 'Director']),
                current_location=random.choice(['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad']),
                current_salary_package=random.randint(300000, 2000000),
                industry=random.choice(['Technology', 'Finance', 'Healthcare', 'Education', 'Manufacturing']),
                work_experience_years=random.randint(1, 15),
                job_function=random.choice(['Software Development', 'Data Science', 'Product Management', 'Consulting', 'Research']),
                company_size=random.choice(['startup', 'small', 'medium', 'large', 'mnc']),
                current_email=student.admin.email,
                current_mobile=f"9{random.randint(100000000, 999999999)}",
                linkedin_profile=f"https://linkedin.com/in/{student.admin.first_name.lower()}-{student.admin.last_name.lower()}-{i+1}",
                is_willing_to_mentor=random.choice([True, False]),
                is_available_for_placement_talks=random.choice([True, False]),
                is_recruiter=random.choice([True, False]),
                mentorship_areas=['Career Guidance', 'Technical Skills', 'Interview Preparation'],
                mentorship_availability=random.choice(['available', 'limited', 'unavailable']),
                max_mentees=random.randint(1, 5),
                achievements=f"Successfully completed {student.course.name} with distinction",
                profile_completion_percentage=random.randint(60, 100),
                is_profile_verified=random.choice([True, False])
            )
            
            print(f"  Created alumni: {student.admin.first_name} {student.admin.last_name} - {student.course.name}")
            
        except Exception as e:
            print(f"  Error creating alumni {i+1}: {str(e)}")
            continue

def create_management():
    """Create management staff"""
    print("Creating management staff...")
    
    # Check existing management count
    existing_count = Management.objects.count()
    if existing_count >= 5:
        print(f"  {existing_count} management staff already exist. Skipping management creation.")
        return
    
    for i in range(5):  # Create 5 management staff
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        email = f"management{i+1}@college.edu"
        
        # Check if user already exists
        if CustomUser.objects.filter(email=email).exists():
            continue
        
        try:
            # Create user
            user = CustomUser.objects.create_user(
                email=email,
                password='management123',
                user_type=4,  # Management
                first_name=first_name,
                last_name=last_name,
                gender=random.choice(['M', 'F']),
                address=f"Management Address {i+1}"
            )
            
            # Create management profile
            management = Management.objects.create(
                admin=user,
                employee_id=f"MGT{i+1:04d}",
                department=random.choice(['Finance', 'Administration', 'Facilities', 'HR', 'IT']),
                designation=random.choice(['Registrar', 'Deputy Registrar', 'Administrative Officer', 'Finance Officer', 'HR Manager']),
                mobile_number=f"9{random.randint(100000000, 999999999)}"
            )
            
            print(f"  Created management: {first_name} {last_name}")
            
        except Exception as e:
            print(f"  Error creating management {i+1}: {str(e)}")
            continue

def main():
    """Main function to populate all data"""
    print("Starting data population...")
    print("=" * 50)
    
    try:
        # Create basic data
        create_departments()
        create_courses()
        create_sessions()
        create_subjects()
        
        # Create users
        create_faculty()
        create_students()
        create_alumni()
        create_management()
        
        # Create related data
        create_attendance()
        create_fee_structures()
        create_companies()
        create_placement_drives()
        
        print("=" * 50)
        print("Data population completed successfully!")
        print("\nSummary:")
        print(f"  Departments: {Department.objects.count()}")
        print(f"  Courses: {Course.objects.count()}")
        print(f"  Subjects: {Subject.objects.count()}")
        print(f"  Sessions: {Session.objects.count()}")
        print(f"  Faculty: {Staff.objects.count()}")
        print(f"  Students: {Student.objects.count()}")
        print(f"  Alumni: {Alumni.objects.count()}")
        print(f"  Management: {Management.objects.count()}")
        print(f"  Companies: {Company.objects.count()}")
        print(f"  Placement Drives: {PlacementDrive.objects.count()}")
        print(f"  Attendance Records: {Attendance.objects.count()}")
        print(f"  Fee Structures: {FeeStructure.objects.count()}")
        
        print("\nDefault Login Credentials:")
        print("  HOD/Admin: admin@college.edu / admin123")
        print("  Faculty: faculty1@college.edu / faculty123")
        print("  Student: student1@college.edu / student123")
        print("  Alumni: alumni1@college.edu / alumni123")
        print("  Management: management1@college.edu / management123")
        
    except Exception as e:
        print(f"Error during data population: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()


