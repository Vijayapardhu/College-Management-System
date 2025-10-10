"""
EduVision - Complete ERP Demo Data Population Script
Populates all ERP features with realistic data
"""

import os
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import *

def populate_departments():
    """Create university departments"""
    print("[START] Creating Departments...")
    
    departments_data = [
        {'name': 'Computer Science & Engineering', 'code': 'CSE', 'contact_email': 'cse@eduvision.edu', 'contact_number': '0123456780', 'established_year': 2005},
        {'name': 'Electronics & Communication Engineering', 'code': 'ECE', 'contact_email': 'ece@eduvision.edu', 'contact_number': '0123456781', 'established_year': 2006},
        {'name': 'Mechanical Engineering', 'code': 'MECH', 'contact_email': 'mech@eduvision.edu', 'contact_number': '0123456782', 'established_year': 2007},
        {'name': 'Civil Engineering', 'code': 'CIVIL', 'contact_email': 'civil@eduvision.edu', 'contact_number': '0123456783', 'established_year': 2008},
        {'name': 'Electrical & Electronics Engineering', 'code': 'EEE', 'contact_email': 'eee@eduvision.edu', 'contact_number': '0123456784', 'established_year': 2009},
    ]
    
    created = 0
    for data in departments_data:
        dept, created_flag = Department.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} departments (Total: {Department.objects.count()})")
    return Department.objects.all()


def populate_programs(departments):
    """Create degree programs"""
    print("[START] Creating Programs...")
    
    programs_data = []
    
    for dept in departments:
        programs_data.extend([
            {
                'name': f'{dept.name}',
                'code': f'BTECH-{dept.code}',
                'program_type': 'btech',
                'department': dept,
                'duration_years': 4,
                'total_semesters': 8,
                'total_credits': 160,
                'eligibility_criteria': '10+2 with Physics, Chemistry, Maths. Min 75% or JEE Main qualified.',
                'is_active': True
            },
            {
                'name': f'{dept.name} (M.Tech)',
                'code': f'MTECH-{dept.code}',
                'program_type': 'mtech',
                'department': dept,
                'duration_years': 2,
                'total_semesters': 4,
                'total_credits': 64,
                'eligibility_criteria': 'B.Tech in related field with 60% or GATE qualified.',
                'is_active': True
            },
        ])
    
    created = 0
    for data in programs_data:
        prog, created_flag = Program.objects.get_or_create(
            code=data['code'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} programs (Total: {Program.objects.count()})")


def populate_transport():
    """Create transport routes"""
    print("[START] Creating Transport Routes...")
    
    routes_data = [
        {
            'route_name': 'City Center - Campus',
            'bus_number': 'EV-BUS-001',
            'driver_name': 'Rajesh Kumar',
            'driver_contact': '9876543210',
            'route_details': '''Route Stops & Timings:
1. City Center Bus Stand - 7:00 AM
2. Railway Station - 7:15 AM
3. Gandhi Chowk - 7:30 AM
4. University Gate - 7:45 AM

Return Journey:
1. University Gate - 5:00 PM
2. Gandhi Chowk - 5:15 PM
3. Railway Station - 5:30 PM
4. City Center - 5:45 PM''',
            'fee_per_semester': Decimal('5000.00'),
            'total_seats': 50,
            'occupied_seats': 35
        },
        {
            'route_name': 'Airport Road - Campus',
            'bus_number': 'EV-BUS-002',
            'driver_name': 'Suresh Singh',
            'driver_contact': '9876543211',
            'route_details': '''Route Stops & Timings:
1. Airport Road - 7:10 AM
2. Tech Park - 7:25 AM
3. Shopping Mall - 7:40 AM
4. University Gate - 7:55 AM''',
            'fee_per_semester': Decimal('4500.00'),
            'total_seats': 45,
            'occupied_seats': 28
        },
        {
            'route_name': 'Old City - Campus',
            'bus_number': 'EV-BUS-003',
            'driver_name': 'Mohammad Ali',
            'driver_contact': '9876543212',
            'route_details': '''Route Stops & Timings:
1. Old City Gate - 6:50 AM
2. Market Square - 7:05 AM
3. Hospital Junction - 7:20 AM
4. University Gate - 7:35 AM''',
            'fee_per_semester': Decimal('4000.00'),
            'total_seats': 40,
            'occupied_seats': 32
        },
        {
            'route_name': 'Residential Area - Campus',
            'bus_number': 'EV-BUS-004',
            'driver_name': 'Prakash Sharma',
            'driver_contact': '9876543213',
            'route_details': '''Route Stops & Timings:
1. Green Park - 7:05 AM
2. Blue Heights - 7:20 AM
3. Silver Apartments - 7:35 AM
4. University Gate - 7:50 AM''',
            'fee_per_semester': Decimal('5500.00'),
            'total_seats': 50,
            'occupied_seats': 40
        },
    ]
    
    created = 0
    for data in routes_data:
        route, created_flag = Transport.objects.get_or_create(
            bus_number=data['bus_number'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} transport routes (Total: {Transport.objects.count()})")


def populate_hostels():
    """Create hostels"""
    print("[START] Creating Hostels...")
    
    hostels_data = [
        {
            'name': 'Krishna Boys Hostel',
            'hostel_type': 'boys',
            'warden_name': 'Dr. Ramesh Rao',
            'warden_contact': '9876540001',
            'total_rooms': 100,
            'occupied_rooms': 85,
            'address': 'Near Main Gate, EduVision Campus, City - 500001'
        },
        {
            'name': 'Saraswati Girls Hostel',
            'hostel_type': 'girls',
            'warden_name': 'Dr. Lakshmi Devi',
            'warden_contact': '9876540002',
            'total_rooms': 80,
            'occupied_rooms': 65,
            'address': 'Behind Library Block, EduVision Campus, City - 500001'
        },
        {
            'name': 'Vivekananda Boys Hostel',
            'hostel_type': 'boys',
            'warden_name': 'Prof. Vijay Kumar',
            'warden_contact': '9876540003',
            'total_rooms': 120,
            'occupied_rooms': 100,
            'address': 'Near Sports Complex, EduVision Campus, City - 500001'
        },
        {
            'name': 'Radha Girls Hostel',
            'hostel_type': 'girls',
            'warden_name': 'Dr. Sita Reddy',
            'warden_contact': '9876540004',
            'total_rooms': 90,
            'occupied_rooms': 70,
            'address': 'Near Medical Center, EduVision Campus, City - 500001'
        },
    ]
    
    created = 0
    for data in hostels_data:
        hostel, created_flag = Hostel.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} hostels (Total: {Hostel.objects.count()})")


def populate_library():
    """Populate library with books"""
    print("[START] Adding Library Books...")
    
    books_data = [
        # Computer Science Books
        {'title': 'Introduction to Algorithms', 'author': 'Cormen, Leiserson, Rivest', 'isbn': '9780262033848', 'publisher': 'MIT Press', 'published_year': 2009, 'category': 'textbook', 'total_copies': 10, 'available_copies': 7, 'shelf_number': 'CS-A-01'},
        {'title': 'Operating System Concepts', 'author': 'Silberschatz, Galvin', 'isbn': '9781118063330', 'publisher': 'Wiley', 'published_year': 2012, 'category': 'textbook', 'total_copies': 15, 'available_copies': 10, 'shelf_number': 'CS-A-02'},
        {'title': 'Database System Concepts', 'author': 'Korth, Silberschatz', 'isbn': '9780073523323', 'publisher': 'McGraw-Hill', 'published_year': 2011, 'category': 'textbook', 'total_copies': 12, 'available_copies': 8, 'shelf_number': 'CS-A-03'},
        {'title': 'Computer Networks', 'author': 'Andrew S. Tanenbaum', 'isbn': '9780132126953', 'publisher': 'Pearson', 'published_year': 2010, 'category': 'textbook', 'total_copies': 10, 'available_copies': 6, 'shelf_number': 'CS-A-04'},
        {'title': 'Data Structures and Algorithms in Python', 'author': 'Goodrich, Tamassia', 'isbn': '9781118290279', 'publisher': 'Wiley', 'published_year': 2013, 'category': 'textbook', 'total_copies': 8, 'available_copies': 5, 'shelf_number': 'CS-A-05'},
        
        # Electronics Books
        {'title': 'Electronic Devices and Circuits', 'author': 'Boylestad, Nashelsky', 'isbn': '9780132622264', 'publisher': 'Pearson', 'published_year': 2012, 'category': 'textbook', 'total_copies': 12, 'available_copies': 9, 'shelf_number': 'EC-A-01'},
        {'title': 'Digital Electronics', 'author': 'R.P. Jain', 'isbn': '9780070151703', 'publisher': 'McGraw-Hill', 'published_year': 2009, 'category': 'textbook', 'total_copies': 10, 'available_copies': 7, 'shelf_number': 'EC-A-02'},
        {'title': 'Signals and Systems', 'author': 'Alan V. Oppenheim', 'isbn': '9780138147570', 'publisher': 'Pearson', 'published_year': 1996, 'category': 'textbook', 'total_copies': 8, 'available_copies': 5, 'shelf_number': 'EC-A-03'},
        
        # Mechanical Books
        {'title': 'Engineering Mechanics', 'author': 'R.S. Khurmi', 'isbn': '9788121925785', 'publisher': 'S.Chand', 'published_year': 2013, 'category': 'textbook', 'total_copies': 15, 'available_copies': 11, 'shelf_number': 'ME-A-01'},
        {'title': 'Thermodynamics', 'author': 'P.K. Nag', 'isbn': '9780070648722', 'publisher': 'McGraw-Hill', 'published_year': 2012, 'category': 'textbook', 'total_copies': 10, 'available_copies': 6, 'shelf_number': 'ME-A-02'},
        
        # Journals & Reference
        {'title': 'IEEE Computer Society Magazine', 'author': 'IEEE', 'isbn': '', 'publisher': 'IEEE', 'published_year': 2024, 'category': 'journal', 'total_copies': 5, 'available_copies': 4, 'shelf_number': 'J-001'},
        {'title': 'ACM Computing Surveys', 'author': 'ACM', 'isbn': '', 'publisher': 'ACM', 'published_year': 2024, 'category': 'journal', 'total_copies': 3, 'available_copies': 3, 'shelf_number': 'J-002'},
    ]
    
    created = 0
    for data in books_data:
        isbn = data.get('isbn') or None
        try:
            if isbn and isbn.strip():
                book, created_flag = Library.objects.get_or_create(
                    isbn=isbn,
                    defaults=data
                )
            else:
                # For books without ISBN, check by title and author
                book, created_flag = Library.objects.get_or_create(
                    title=data['title'],
                    author=data['author'],
                    defaults=data
                )
            
            if created_flag:
                created += 1
        except Exception as e:
            print(f"[SKIP] Book '{data['title']}' already exists or error: {str(e)}")
            continue
    
    print(f"[OK] Added {created} library books (Total: {Library.objects.count()})")


def populate_scholarships():
    """Create scholarship programs"""
    print("[START] Creating Scholarship Programs...")
    
    today = date.today()
    deadline = today + timedelta(days=60)
    
    scholarships_data = [
        {
            'name': 'Merit Scholarship for Excellence',
            'scholarship_type': 'merit',
            'description': 'For students with CGPA above 9.0',
            'eligibility_criteria': 'CGPA >= 9.0, No backlogs, Attendance >= 85%',
            'amount': Decimal('50000.00'),
            'max_recipients': 20,
            'application_deadline': deadline,
            'is_active': True
        },
        {
            'name': 'SC/ST Scholarship',
            'scholarship_type': 'govt',
            'description': 'Government scholarship for SC/ST students',
            'eligibility_criteria': 'Valid SC/ST certificate, Family income < 2.5 LPA',
            'amount': Decimal('25000.00'),
            'max_recipients': 100,
            'application_deadline': deadline,
            'is_active': True
        },
        {
            'name': 'Sports Excellence Scholarship',
            'scholarship_type': 'sports',
            'description': 'For students with state/national level sports achievements',
            'eligibility_criteria': 'State level or higher sports certificate',
            'amount': Decimal('30000.00'),
            'max_recipients': 15,
            'application_deadline': deadline,
            'is_active': True
        },
        {
            'name': 'Need-Based Financial Aid',
            'scholarship_type': 'need',
            'description': 'For economically disadvantaged students',
            'eligibility_criteria': 'Family income < 1 LPA, Valid income certificate',
            'amount': Decimal('40000.00'),
            'max_recipients': 50,
            'application_deadline': deadline,
            'is_active': True
        },
        {
            'name': 'Minority Scholarship',
            'scholarship_type': 'minority',
            'description': 'For minority community students',
            'eligibility_criteria': 'Valid minority certificate, CGPA >= 6.0',
            'amount': Decimal('20000.00'),
            'max_recipients': 40,
            'application_deadline': deadline,
            'is_active': True
        },
    ]
    
    created = 0
    for data in scholarships_data:
        scholarship, created_flag = Scholarship.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} scholarships (Total: {Scholarship.objects.count()})")


def populate_companies():
    """Create placement companies"""
    print("[START] Adding Placement Companies...")
    
    companies_data = [
        {'name': 'Tata Consultancy Services (TCS)', 'company_type': 'service', 'website': 'https://www.tcs.com', 'hr_name': 'Priya Sharma', 'hr_email': 'priya.sharma@tcs.com', 'hr_contact': '9800000001', 'description': 'Leading IT services company'},
        {'name': 'Infosys Limited', 'company_type': 'service', 'website': 'https://www.infosys.com', 'hr_name': 'Rahul Verma', 'hr_email': 'rahul.verma@infosys.com', 'hr_contact': '9800000002', 'description': 'Global leader in consulting and technology'},
        {'name': 'Google India', 'company_type': 'product', 'website': 'https://www.google.com', 'hr_name': 'Sneha Gupta', 'hr_email': 'sneha.gupta@google.com', 'hr_contact': '9800000003', 'description': 'Technology giant - Search, Cloud, AI'},
        {'name': 'Amazon Development Center', 'company_type': 'product', 'website': 'https://www.amazon.com', 'hr_name': 'Amit Patel', 'hr_email': 'amit.patel@amazon.com', 'hr_contact': '9800000004', 'description': 'E-commerce and cloud computing leader'},
        {'name': 'Microsoft India', 'company_type': 'product', 'website': 'https://www.microsoft.com', 'hr_name': 'Neha Singh', 'hr_email': 'neha.singh@microsoft.com', 'hr_contact': '9800000005', 'description': 'Software and cloud services'},
        {'name': 'Wipro Technologies', 'company_type': 'service', 'website': 'https://www.wipro.com', 'hr_name': 'Karthik Reddy', 'hr_email': 'karthik.reddy@wipro.com', 'hr_contact': '9800000006', 'description': 'IT services and consulting'},
        {'name': 'Tech Mahindra', 'company_type': 'service', 'website': 'https://www.techmahindra.com', 'hr_name': 'Divya Krishnan', 'hr_email': 'divya.k@techmahindra.com', 'hr_contact': '9800000007', 'description': 'Digital transformation services'},
        {'name': 'Cognizant Technology Solutions', 'company_type': 'service', 'website': 'https://www.cognizant.com', 'hr_name': 'Arjun Mehta', 'hr_email': 'arjun.mehta@cognizant.com', 'hr_contact': '9800000008', 'description': 'Professional services company'},
    ]
    
    created = 0
    for data in companies_data:
        company, created_flag = Company.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created_flag:
            created += 1
    
    print(f"[OK] Created {created} companies (Total: {Company.objects.count()})")


def populate_exams():
    """Create exam instances"""
    print("[START] Creating Exams...")
    
    session = Session.objects.first()
    if not session:
        print("[SKIP] No session found. Please create a session first.")
        return
    
    # Create exams for different semesters
    for semester in [1, 2, 3, 4]:
        # Mid-term
        exam1, created1 = Exam.objects.get_or_create(
            name=f'Mid Term Examination - Semester {semester}',
            exam_type='mid_term',
            session=session,
            semester=semester,
            defaults={
                'start_date': date.today() + timedelta(days=30 + (semester * 7)),
                'end_date': date.today() + timedelta(days=40 + (semester * 7)),
                'is_published': False
            }
        )
        
        # End-term
        exam2, created2 = Exam.objects.get_or_create(
            name=f'End Term Examination - Semester {semester}',
            exam_type='end_term',
            session=session,
            semester=semester,
            defaults={
                'start_date': date.today() + timedelta(days=90 + (semester * 7)),
                'end_date': date.today() + timedelta(days=100 + (semester * 7)),
                'is_published': False
            }
        )
    
    print(f"[OK] Created exams (Total: {Exam.objects.count()})")


def populate_placement_drives():
    """Create placement drives"""
    print("[START] Creating Placement Drives...")
    
    companies = Company.objects.all()[:5]  # Get first 5 companies
    session = Session.objects.first()
    courses = list(Course.objects.all()[:3])  # Get first 3 courses
    
    if not companies or not session or not courses:
        print("[SKIP] Need companies, session, and courses to create drives")
        return
    
    from django.utils import timezone
    now = timezone.now()
    
    drives_data = [
        {
            'company': companies[0],
            'job_title': 'Software Engineer',
            'job_description': 'Develop and maintain enterprise applications. Work on cutting-edge technologies.',
            'min_cgpa': Decimal('7.0'),
            'allowed_backlogs': 0,
            'salary_package': Decimal('6.5'),
            'bond_years': 2,
            'selection_process': 'Aptitude Test → Technical Round → HR Round',
            'number_of_openings': 50,
            'drive_type': 'campus'
        },
        {
            'company': companies[1],
            'job_title': 'Systems Engineer',
            'job_description': 'Design and implement software solutions for global clients.',
            'min_cgpa': Decimal('6.5'),
            'allowed_backlogs': 1,
            'salary_package': Decimal('7.0'),
            'bond_years': 2,
            'selection_process': 'Online Test → Technical Interview → Managerial Round',
            'number_of_openings': 60,
            'drive_type': 'campus'
        },
        {
            'company': companies[2],
            'job_title': 'Software Development Engineer',
            'job_description': 'Build scalable distributed systems. Work on cloud technologies.',
            'min_cgpa': Decimal('8.0'),
            'allowed_backlogs': 0,
            'salary_package': Decimal('15.0'),
            'bond_years': 0,
            'selection_process': 'Coding Test → Technical Rounds (2) → Hiring Manager Round',
            'number_of_openings': 10,
            'drive_type': 'campus'
        },
    ]
    
    created = 0
    for i, data in enumerate(drives_data):
        drive, created_flag = PlacementDrive.objects.get_or_create(
            company=data['company'],
            session=session,
            job_title=data['job_title'],
            defaults={
                **data,
                'registration_deadline': now + timedelta(days=15 + i*3),
                'aptitude_test_date': now + timedelta(days=20 + i*3),
                'interview_date': now + timedelta(days=25 + i*3),
            }
        )
        
        if created_flag:
            # Add eligible courses
            drive.eligible_courses.set(courses)
            created += 1
    
    print(f"[OK] Created {created} placement drives (Total: {PlacementDrive.objects.count()})")


def populate_timetable():
    """Create sample timetable"""
    print("[START] Creating Timetable Entries...")
    
    session = Session.objects.first()
    courses = Course.objects.all()[:2]  # First 2 courses
    
    if not session or not courses:
        print("[SKIP] Need session and courses to create timetable")
        return
    
    created = 0
    
    for course in courses:
        subjects = Subject.objects.filter(course=course)[:5]  # Get 5 subjects per course
        
        if not subjects:
            continue
        
        # Create timetable for semester 1
        weekdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        periods = ['1', '2', '3', '4', '5', '6']
        
        for day_idx, weekday in enumerate(weekdays):
            for period_idx, period in enumerate(periods):
                subject = subjects[period_idx % len(subjects)]
                
                # Skip lunch break (period 4)
                if period == '4':
                    continue
                
                start_hour = 9 + (period_idx if period_idx < 3 else period_idx + 1)
                end_hour = start_hour + 1
                
                tt, created_flag = Timetable.objects.get_or_create(
                    session=session,
                    course=course,
                    semester=1,
                    weekday=weekday,
                    period=period,
                    defaults={
                        'start_time': f'{start_hour}:00:00',
                        'end_time': f'{end_hour}:00:00',
                        'subject': subject,
                        'staff': subject.staff,
                        'room_number': f'R{100 + period_idx}',
                        'is_lab': period in ['5', '6']
                    }
                )
                
                if created_flag:
                    created += 1
    
    print(f"[OK] Created {created} timetable entries (Total: {Timetable.objects.count()})")


def main():
    """Main execution"""
    print("\n" + "="*60)
    print("EduVision - Complete ERP Data Population")
    print("="*60 + "\n")
    
    try:
        # Populate all data
        departments = populate_departments()
        populate_programs(departments)
        populate_transport()
        populate_hostels()
        populate_library()
        populate_scholarships()
        populate_companies()
        populate_exams()
        populate_placement_drives()
        populate_timetable()
        
        print("\n" + "="*60)
        print("DATA POPULATION COMPLETE!")
        print("="*60)
        print("\nSummary:")
        print(f"  - Departments: {Department.objects.count()}")
        print(f"  - Programs: {Program.objects.count()}")
        print(f"  - Transport Routes: {Transport.objects.count()}")
        print(f"  - Hostels: {Hostel.objects.count()}")
        print(f"  - Library Books: {Library.objects.count()}")
        print(f"  - Scholarships: {Scholarship.objects.count()}")
        print(f"  - Companies: {Company.objects.count()}")
        print(f"  - Placement Drives: {PlacementDrive.objects.count()}")
        print(f"  - Exams: {Exam.objects.count()}")
        print(f"  - Timetable Entries: {Timetable.objects.count()}")
        print("\n[OK] All ERP features populated with demo data!")
        print("\nYou can now test all features at: http://localhost:8000\n")
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()

