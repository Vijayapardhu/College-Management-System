from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Student, Staff, Course, Department, FeePayment, FeeStructure,
    Transport, TransportAllocation, Hostel, HostelAllocation,
    Library, LibraryIssue, Scholarship, ScholarshipApplication,
    Grievance, AttendanceReport, StudentResult, LeaveReportStudent, LeaveReportStaff,
    Subject, Session
)


@login_required(login_url='login')
def management_home(request):
    """Management home dashboard with comprehensive system statistics"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # System-wide statistics
    total_students = Student.objects.filter(student_status='active').count()
    total_staff = Staff.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    
    # Financial statistics
    total_fees_collected = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    pending_fees = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    # Operational statistics
    total_transport = Transport.objects.count()
    transport_utilization = TransportAllocation.objects.filter(is_active=True).count()
    
    total_hostels = Hostel.objects.count()
    hostel_occupancy = HostelAllocation.objects.filter(is_active=True).count()
    total_hostel_capacity = Hostel.objects.aggregate(total=Sum('total_rooms'))['total'] or 0
    
    total_library_books = Library.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    books_issued = LibraryIssue.objects.filter(return_date__isnull=True).count()
    
    # Scholarship statistics
    active_scholarships = Scholarship.objects.filter(is_active=True).count()
    pending_scholarship_apps = ScholarshipApplication.objects.filter(status='applied').count()
    
    # Grievance statistics
    pending_grievances = Grievance.objects.filter(status__in=['submitted', 'under_review']).count()
    
    # Recent activity
    recent_fee_payments = FeePayment.objects.select_related('student__admin').order_by('-payment_date')[:5]
    recent_grievances = Grievance.objects.select_related('submitted_by').order_by('-submitted_at')[:5]
    
    # Alerts
    fee_defaulters_count = Student.objects.filter(
        student_status='active',
        fee_payments__payment_status='pending'
    ).distinct().count()
    
    overdue_books = LibraryIssue.objects.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Management Dashboard',
        'total_students': total_students,
        'total_staff': total_staff,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_fees_collected': total_fees_collected,
        'pending_fees': pending_fees,
        'total_transport': total_transport,
        'transport_utilization': transport_utilization,
        'total_hostels': total_hostels,
        'hostel_occupancy': hostel_occupancy,
        'total_hostel_capacity': total_hostel_capacity,
        'total_library_books': total_library_books,
        'books_issued': books_issued,
        'active_scholarships': active_scholarships,
        'pending_scholarship_apps': pending_scholarship_apps,
        'pending_grievances': pending_grievances,
        'recent_fee_payments': recent_fee_payments,
        'recent_grievances': recent_grievances,
        'fee_defaulters_count': fee_defaulters_count,
        'overdue_books': overdue_books,
        'current_date': timezone.now(),
    }
    return render(request, 'management_template/home_content.html', context)


@login_required(login_url='login')
def management_view_profile(request):
    """Management view and edit profile"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Update user profile
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.email = request.POST.get('email')
            
            # Update password if provided
            new_password = request.POST.get('password')
            if new_password and len(new_password) > 0:
                request.user.set_password(new_password)
            
            # Handle profile picture upload
            if 'profile_pic' in request.FILES:
                request.user.profile_pic = request.FILES['profile_pic']
            
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'page_title': 'Management Profile',
        'user': request.user,
    }
    return render(request, 'management_template/view_profile.html', context)


# ==================== TRANSPORT MANAGEMENT ====================

@login_required(login_url='login')
def manage_transport(request):
    """Manage transport routes and buses"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all transport routes
    transports = Transport.objects.all().order_by('route_name')
    
    # Calculate statistics
    total_routes = transports.count()
    total_capacity = transports.aggregate(total=Sum('total_seats'))['total'] or 0
    total_occupied = transports.aggregate(total=Sum('occupied_seats'))['total'] or 0
    available_seats = total_capacity - total_occupied
    
    context = {
        'page_title': 'Manage Transport',
        'transports': transports,
        'total_routes': total_routes,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'available_seats': available_seats,
    }
    return render(request, 'management_template/manage_transport.html', context)


@login_required(login_url='login')
def add_transport(request):
    """Add new transport route"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            transport = Transport.objects.create(
                route_name=request.POST.get('route_name'),
                bus_number=request.POST.get('bus_number'),
                driver_name=request.POST.get('driver_name'),
                driver_contact=request.POST.get('driver_contact'),
                route_details=request.POST.get('route_details'),
                fee_per_semester=request.POST.get('fee_per_semester', 0),
                total_seats=request.POST.get('total_seats', 40),
                occupied_seats=0
            )
            messages.success(request, f'Transport route "{transport.route_name}" added successfully!')
            return redirect('management_transport')
        except Exception as e:
            messages.error(request, f'Error adding transport: {str(e)}')
    
    context = {'page_title': 'Add Transport Route'}
    return render(request, 'management_template/add_transport.html', context)


@login_required(login_url='login')
def edit_transport(request, transport_id):
    """Edit transport route"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    transport = get_object_or_404(Transport, id=transport_id)
    
    if request.method == 'POST':
        try:
            transport.route_name = request.POST.get('route_name')
            transport.bus_number = request.POST.get('bus_number')
            transport.driver_name = request.POST.get('driver_name')
            transport.driver_contact = request.POST.get('driver_contact')
            transport.route_details = request.POST.get('route_details')
            transport.fee_per_semester = request.POST.get('fee_per_semester')
            transport.total_seats = request.POST.get('total_seats')
            transport.save()
            
            messages.success(request, 'Transport route updated successfully!')
            return redirect('management_transport')
        except Exception as e:
            messages.error(request, f'Error updating transport: {str(e)}')
    
    context = {
        'page_title': 'Edit Transport Route',
        'transport': transport
    }
    return render(request, 'management_template/edit_transport.html', context)


@login_required(login_url='login')
def transport_allocations(request):
    """View all transport allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all allocations with related data
    allocations = TransportAllocation.objects.select_related(
        'student__admin', 'student__course', 'transport'
    ).filter(is_active=True).order_by('transport__route_name', 'student__admin__first_name')
    
    # Statistics
    total_allocations = allocations.count()
    routes_with_students = Transport.objects.filter(allocations__is_active=True).distinct().count()
    
    context = {
        'page_title': 'Transport Allocations',
        'allocations': allocations,
        'total_allocations': total_allocations,
        'routes_with_students': routes_with_students,
    }
    return render(request, 'management_template/transport_allocations.html', context)


@login_required(login_url='login')
def allocate_transport(request):
    """Allocate transport to students"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            transport_id = request.POST.get('transport')
            pickup_point = request.POST.get('pickup_point')
            
            student = get_object_or_404(Student, id=student_id)
            transport = get_object_or_404(Transport, id=transport_id)
            
            # Check if transport has available seats
            if transport.available_seats <= 0:
                messages.error(request, 'No seats available on this route')
                return redirect('management_allocate_transport')
            
            # Check if student already has allocation
            if TransportAllocation.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student already has an active transport allocation')
                return redirect('management_allocate_transport')
            
            # Create allocation
            allocation = TransportAllocation.objects.create(
                student=student,
                transport=transport,
                pickup_point=pickup_point,
                is_active=True
            )
            
            # Update occupied seats
            transport.occupied_seats += 1
            transport.save()
            
            messages.success(request, f'Transport allocated to {student.admin.first_name} {student.admin.last_name} successfully!')
            return redirect('management_transport_allocations')
        except Exception as e:
            messages.error(request, f'Error allocating transport: {str(e)}')
    
    # Get students who need transport
    students = Student.objects.filter(
        transport_required=True,
        student_status='active'
    ).exclude(
        transport_allocation__is_active=True
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    # Get available transport routes
    transports = Transport.objects.all().order_by('route_name')
    
    context = {
        'page_title': 'Allocate Transport',
        'students': students,
        'transports': transports,
    }
    return render(request, 'management_template/allocate_transport.html', context)


# ==================== HOSTEL MANAGEMENT ====================

@login_required(login_url='login')
def manage_hostels(request):
    """Manage hostels and view occupancy"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all hostels
    hostels = Hostel.objects.annotate(
        current_occupancy=Count('allocations', filter=Q(allocations__is_active=True))
    ).order_by('name')
    
    # Calculate statistics
    total_hostels = hostels.count()
    total_capacity = hostels.aggregate(total=Sum('total_rooms'))['total'] or 0
    total_occupied = HostelAllocation.objects.filter(is_active=True).count()
    available_rooms = total_capacity - total_occupied
    occupancy_rate = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
    
    context = {
        'page_title': 'Manage Hostels',
        'hostels': hostels,
        'total_hostels': total_hostels,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    return render(request, 'management_template/manage_hostels.html', context)


@login_required(login_url='login')
def add_hostel(request):
    """Add new hostel"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            hostel = Hostel.objects.create(
                name=request.POST.get('name'),
                hostel_type=request.POST.get('hostel_type'),
                warden_name=request.POST.get('warden_name'),
                warden_contact=request.POST.get('warden_contact'),
                total_rooms=request.POST.get('total_rooms'),
                occupied_rooms=0,
                address=request.POST.get('address')
            )
            messages.success(request, f'Hostel "{hostel.name}" added successfully!')
            return redirect('management_hostels')
        except Exception as e:
            messages.error(request, f'Error adding hostel: {str(e)}')
    
    context = {'page_title': 'Add Hostel'}
    return render(request, 'management_template/add_hostel.html', context)


@login_required(login_url='login')
def hostel_allocations(request):
    """View all hostel room allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all allocations
    allocations = HostelAllocation.objects.select_related(
        'student__admin', 'student__course', 'hostel'
    ).filter(is_active=True).order_by('hostel__name', 'room_number')
    
    # Filter by hostel if specified
    hostel_filter = request.GET.get('hostel')
    if hostel_filter:
        allocations = allocations.filter(hostel_id=hostel_filter)
    
    # Statistics
    total_allocations = allocations.count()
    hostels_list = Hostel.objects.all().order_by('name')
    
    context = {
        'page_title': 'Hostel Room Allocations',
        'allocations': allocations,
        'total_allocations': total_allocations,
        'hostels_list': hostels_list,
        'hostel_filter': hostel_filter,
    }
    return render(request, 'management_template/hostel_allocations.html', context)


@login_required(login_url='login')
def allocate_hostel(request):
    """Allocate hostel room to student"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            hostel_id = request.POST.get('hostel')
            room_number = request.POST.get('room_number')
            rent_per_semester = request.POST.get('rent_per_semester', 0)
            
            student = get_object_or_404(Student, id=student_id)
            hostel = get_object_or_404(Hostel, id=hostel_id)
            
            # Check if hostel has available rooms
            if hostel.available_rooms <= 0:
                messages.error(request, 'No rooms available in this hostel')
                return redirect('management_allocate_hostel')
            
            # Check if student already has allocation
            if HostelAllocation.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student already has an active hostel allocation')
                return redirect('management_allocate_hostel')
            
            # Check if room is already occupied
            if HostelAllocation.objects.filter(
                hostel=hostel, room_number=room_number, is_active=True
            ).exists():
                messages.error(request, f'Room {room_number} is already occupied')
                return redirect('management_allocate_hostel')
            
            # Create allocation
            allocation = HostelAllocation.objects.create(
                student=student,
                hostel=hostel,
                room_number=room_number,
                rent_per_semester=rent_per_semester,
                is_active=True
            )
            
            # Update occupied rooms
            hostel.occupied_rooms += 1
            hostel.save()
            
            messages.success(request, f'Room {room_number} allocated to {student.admin.first_name} {student.admin.last_name} successfully!')
            return redirect('management_hostel_allocations')
        except Exception as e:
            messages.error(request, f'Error allocating hostel: {str(e)}')
    
    # Get students who need hostel
    students = Student.objects.filter(
        hostel_required=True,
        student_status='active'
    ).exclude(
        hostel_allocation__is_active=True
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    # Get available hostels
    hostels = Hostel.objects.all().order_by('name')
    
    context = {
        'page_title': 'Allocate Hostel Room',
        'students': students,
        'hostels': hostels,
    }
    return render(request, 'management_template/allocate_hostel.html', context)


@login_required(login_url='login')
def hostel_visitor_logs(request):
    """View hostel visitor logs"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    from .models import HostelVisitorLog
    
    # Get visitor logs
    logs = HostelVisitorLog.objects.select_related(
        'hostel', 'student__admin'
    ).order_by('-entry_time')
    
    # Filter by date if specified
    date_filter = request.GET.get('date')
    if date_filter:
        logs = logs.filter(entry_time__date=date_filter)
    
    # Filter by hostel if specified
    hostel_filter = request.GET.get('hostel')
    if hostel_filter:
        logs = logs.filter(hostel_id=hostel_filter)
    
    # Get hostels for filter
    hostels = Hostel.objects.all().order_by('name')
    
    # Statistics
    total_visitors_today = HostelVisitorLog.objects.filter(
        entry_time__date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Hostel Visitor Logs',
        'logs': logs[:100],  # Limit to recent 100
        'hostels': hostels,
        'total_visitors_today': total_visitors_today,
        'date_filter': date_filter,
        'hostel_filter': hostel_filter,
    }
    return render(request, 'management_template/hostel_visitor_logs.html', context)


# ==================== LIBRARY MANAGEMENT ====================

@login_required(login_url='login')
def manage_library(request):
    """Manage library books and inventory"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all books
    books = Library.objects.select_related('subject').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        books = books.filter(category=category_filter)
    
    books = books.order_by('title')
    
    # Statistics
    total_books = Library.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    available_books = Library.objects.aggregate(total=Sum('available_copies'))['total'] or 0
    issued_books = total_books - available_books
    total_unique_titles = Library.objects.count()
    
    context = {
        'page_title': 'Library Management',
        'books': books,
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_unique_titles': total_unique_titles,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/manage_library.html', context)


@login_required(login_url='login')
def add_library_book(request):
    """Add new library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Handle file upload
            cover_image = request.FILES.get('cover_image')
            
            book = Library.objects.create(
                title=request.POST.get('title'),
                author=request.POST.get('author'),
                isbn=request.POST.get('isbn') or None,
                publisher=request.POST.get('publisher'),
                published_year=request.POST.get('published_year'),
                category=request.POST.get('category'),
                subject_id=request.POST.get('subject') if request.POST.get('subject') else None,
                total_copies=request.POST.get('total_copies', 1),
                available_copies=request.POST.get('total_copies', 1),
                shelf_number=request.POST.get('shelf_number', ''),
                description=request.POST.get('description', ''),
                cover_image=cover_image
            )
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('management_library')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')
    
    # Get subjects for dropdown
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'page_title': 'Add Library Book',
        'subjects': subjects,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/add_library_book.html', context)


@login_required(login_url='login')
def edit_library_book(request, book_id):
    """Edit library book details"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    book = get_object_or_404(Library, id=book_id)
    
    if request.method == 'POST':
        try:
            book.title = request.POST.get('title')
            book.author = request.POST.get('author')
            book.isbn = request.POST.get('isbn') or None
            book.publisher = request.POST.get('publisher')
            book.published_year = request.POST.get('published_year')
            book.category = request.POST.get('category')
            book.subject_id = request.POST.get('subject') if request.POST.get('subject') else None
            
            # Update copies if changed
            new_total = int(request.POST.get('total_copies', book.total_copies))
            difference = new_total - book.total_copies
            book.total_copies = new_total
            book.available_copies += difference
            
            book.shelf_number = request.POST.get('shelf_number', '')
            book.description = request.POST.get('description', '')
            
            # Handle cover image upload
            if 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']
            
            book.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('management_library')
        except Exception as e:
            messages.error(request, f'Error updating book: {str(e)}')
    
    # Get subjects for dropdown
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'page_title': 'Edit Library Book',
        'book': book,
        'subjects': subjects,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/edit_library_book.html', context)


@login_required(login_url='login')
def library_issues(request):
    """View all library book issues and returns"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all issues
    issues = LibraryIssue.objects.select_related(
        'book', 'student__admin', 'issued_by'
    ).order_by('-issue_date')
    
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        issues = issues.filter(return_date__isnull=True)
    elif status_filter == 'returned':
        issues = issues.filter(return_date__isnull=False)
    elif status_filter == 'overdue':
        issues = issues.filter(return_date__isnull=True, due_date__lt=timezone.now().date())
    
    # Statistics
    active_issues = LibraryIssue.objects.filter(return_date__isnull=True).count()
    overdue_issues = LibraryIssue.objects.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).count()
    returned_today = LibraryIssue.objects.filter(
        return_date__date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Library Issues & Returns',
        'issues': issues[:100],  # Limit to 100 for performance
        'active_issues': active_issues,
        'overdue_issues': overdue_issues,
        'returned_today': returned_today,
        'status_filter': status_filter,
    }
    return render(request, 'management_template/library_issues.html', context)


@login_required(login_url='login')
def issue_library_book(request):
    """Issue library book to student"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            book_id = request.POST.get('book')
            student_id = request.POST.get('student')
            due_days = int(request.POST.get('due_days', 14))
            
            book = get_object_or_404(Library, id=book_id)
            student = get_object_or_404(Student, id=student_id)
            
            # Check if book is available
            if book.available_copies <= 0:
                messages.error(request, f'No copies of "{book.title}" are currently available')
                return redirect('management_issue_library_book')
            
            # Check if student already has this book
            if LibraryIssue.objects.filter(
                book=book, student=student, return_date__isnull=True
            ).exists():
                messages.error(request, 'Student already has this book issued')
                return redirect('management_issue_library_book')
            
            # Create issue record
            issue = LibraryIssue.objects.create(
                book=book,
                student=student,
                issued_by=request.user.staff if hasattr(request.user, 'staff') else None,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=due_days)
            )
            
            # Update available copies
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f'Book "{book.title}" issued to {student.admin.first_name} {student.admin.last_name}!')
            return redirect('management_library_issues')
        except Exception as e:
            messages.error(request, f'Error issuing book: {str(e)}')
    
    # Get available books
    books = Library.objects.filter(available_copies__gt=0).order_by('title')
    
    # Get active students
    students = Student.objects.filter(
        student_status='active'
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    context = {
        'page_title': 'Issue Library Book',
        'books': books,
        'students': students,
    }
    return render(request, 'management_template/issue_library_book.html', context)


@login_required(login_url='login')
def return_library_book(request, issue_id):
    """Process book return"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    issue = get_object_or_404(LibraryIssue, id=issue_id)
    
    if request.method == 'POST':
        try:
            # Mark as returned
            issue.return_date = timezone.now().date()
            
            # Calculate fine if overdue
            if issue.due_date < issue.return_date:
                days_overdue = (issue.return_date - issue.due_date).days
                fine_per_day = 5  # Rs. 5 per day
                issue.fine_amount = days_overdue * fine_per_day
            else:
                issue.fine_amount = 0
            
            issue.save()
            
            # Update available copies
            book = issue.book
            book.available_copies += 1
            book.save()
            
            if issue.fine_amount > 0:
                messages.warning(request, f'Book returned with fine of ₹{issue.fine_amount}')
            else:
                messages.success(request, 'Book returned successfully!')
            
            return redirect('management_library_issues')
        except Exception as e:
            messages.error(request, f'Error processing return: {str(e)}')
    
    # Calculate potential fine
    potential_fine = 0
    if issue.due_date < timezone.now().date():
        days_overdue = (timezone.now().date() - issue.due_date).days
        potential_fine = days_overdue * 5
    
    context = {
        'page_title': 'Return Library Book',
        'issue': issue,
        'potential_fine': potential_fine,
    }
    return render(request, 'management_template/return_library_book.html', context)


# ==================== FEE MANAGEMENT ====================

@login_required(login_url='login')
def manage_fee_structure(request):
    """Manage fee structures for all courses"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all fee structures
    fee_structures = FeeStructure.objects.select_related(
        'course', 'session'
    ).order_by('course__name', 'semester')
    
    # Filter by course if specified
    course_filter = request.GET.get('course')
    if course_filter:
        fee_structures = fee_structures.filter(course_id=course_filter)
    
    # Get courses for filter
    courses = Course.objects.all().order_by('name')
    
    context = {
        'page_title': 'Fee Structure Management',
        'fee_structures': fee_structures,
        'courses': courses,
        'course_filter': course_filter,
    }
    return render(request, 'management_template/manage_fee_structure.html', context)


@login_required(login_url='login')
def add_fee_structure(request):
    """Create new fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            course_type = request.POST.get('course_type')
            semester = request.POST.get('semester')
            session_id = request.POST.get('session')
            
            # Check if fee structure already exists
            if FeeStructure.objects.filter(
                course_id=course_id,
                course_type=course_type,
                semester=semester,
                session_id=session_id
            ).exists():
                messages.error(request, 'Fee structure already exists for this combination')
                return redirect('management_add_fee_structure')
            
            fee_structure = FeeStructure.objects.create(
                course_id=course_id,
                course_type=course_type,
                semester=semester,
                session_id=session_id,
                tuition_fee=request.POST.get('tuition_fee', 0),
                development_fee=request.POST.get('development_fee', 0),
                lab_fee=request.POST.get('lab_fee', 0),
                library_fee=request.POST.get('library_fee', 0),
                exam_fee=request.POST.get('exam_fee', 0),
                other_fee=request.POST.get('other_fee', 0)
            )
            messages.success(request, f'Fee structure created successfully! Total: ₹{fee_structure.total_fee}')
            return redirect('management_fee_structure')
        except Exception as e:
            messages.error(request, f'Error creating fee structure: {str(e)}')
    
    # Get courses and sessions
    courses = Course.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-session_start_year')
    
    context = {
        'page_title': 'Add Fee Structure',
        'courses': courses,
        'sessions': sessions,
        'course_types': Student.COURSE_TYPE_CHOICES,
    }
    return render(request, 'management_template/add_fee_structure.html', context)


@login_required(login_url='login')
def edit_fee_structure(request, structure_id):
    """Edit existing fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    fee_structure = get_object_or_404(FeeStructure, id=structure_id)
    
    if request.method == 'POST':
        try:
            fee_structure.tuition_fee = request.POST.get('tuition_fee')
            fee_structure.development_fee = request.POST.get('development_fee')
            fee_structure.lab_fee = request.POST.get('lab_fee')
            fee_structure.library_fee = request.POST.get('library_fee')
            fee_structure.exam_fee = request.POST.get('exam_fee')
            fee_structure.other_fee = request.POST.get('other_fee')
            fee_structure.save()
            
            messages.success(request, f'Fee structure updated! New total: ₹{fee_structure.total_fee}')
            return redirect('management_fee_structure')
        except Exception as e:
            messages.error(request, f'Error updating fee structure: {str(e)}')
    
    context = {
        'page_title': 'Edit Fee Structure',
        'fee_structure': fee_structure,
    }
    return render(request, 'management_template/edit_fee_structure.html', context)


@login_required(login_url='login')
def view_fee_payments(request):
    """View all fee payment records"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all payments
    payments = FeePayment.objects.select_related(
        'student__admin', 'student__course', 'fee_structure'
    ).order_by('-payment_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    # Statistics
    total_collected = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    pending_amount = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    payments_today = FeePayment.objects.filter(
        payment_date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Fee Payments',
        'payments': payments[:100],  # Limit for performance
        'total_collected': total_collected,
        'pending_amount': pending_amount,
        'payments_today': payments_today,
        'status_filter': status_filter,
    }
    return render(request, 'management_template/view_fee_payments.html', context)


@login_required(login_url='login')
def record_fee_payment(request):
    """Record new fee payment"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            fee_structure_id = request.POST.get('fee_structure')
            amount_paid = float(request.POST.get('amount_paid', 0))
            payment_mode = request.POST.get('payment_mode')
            transaction_id = request.POST.get('transaction_id', '')
            remarks = request.POST.get('remarks', '')
            
            student = get_object_or_404(Student, id=student_id)
            fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)
            
            # Calculate amounts
            total_fee = fee_structure.total_fee
            amount_pending = total_fee - amount_paid
            
            # Determine payment status
            if amount_paid >= total_fee:
                payment_status = 'paid'
                amount_pending = 0
            elif amount_paid > 0:
                payment_status = 'partial'
            else:
                payment_status = 'pending'
            
            payment = FeePayment.objects.create(
                student=student,
                fee_structure=fee_structure,
                amount_paid=amount_paid,
                amount_pending=amount_pending,
                payment_date=timezone.now().date(),
                payment_mode=payment_mode,
                transaction_id=transaction_id,
                payment_status=payment_status,
                remarks=remarks
            )
            
            messages.success(request, f'Payment of ₹{amount_paid} recorded for {student.admin.first_name} {student.admin.last_name}!')
            return redirect('management_fee_payments')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    # Get students and fee structures
    students = Student.objects.filter(
        student_status='active'
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    fee_structures = FeeStructure.objects.select_related('course', 'session').all()
    
    context = {
        'page_title': 'Record Fee Payment',
        'students': students,
        'fee_structures': fee_structures,
        'payment_modes': FeePayment.PAYMENT_MODE,
    }
    return render(request, 'management_template/record_fee_payment.html', context)


@login_required(login_url='login')
def fee_defaulters(request):
    """View students with pending fee payments"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get students with pending fees
    defaulters = Student.objects.filter(
        student_status='active',
        fee_payments__payment_status='pending'
    ).select_related('admin', 'course').annotate(
        total_pending=Sum('fee_payments__amount_pending', filter=Q(fee_payments__payment_status='pending'))
    ).distinct().order_by('-total_pending')
    
    # Calculate total pending amount
    total_pending_amount = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    context = {
        'page_title': 'Fee Defaulters',
        'defaulters': defaulters,
        'total_defaulters': defaulters.count(),
        'total_pending_amount': total_pending_amount,
    }
    return render(request, 'management_template/fee_defaulters.html', context)


# ==================== SCHOLARSHIP MANAGEMENT ====================

@login_required(login_url='login')
def manage_scholarships(request):
    """Manage scholarship programs"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all scholarships
    scholarships = Scholarship.objects.annotate(
        application_count=Count('applications'),
        approved_count=Count('applications', filter=Q(applications__status='approved')),
        disbursed_count=Count('applications', filter=Q(applications__status='disbursed'))
    ).order_by('-is_active', 'name')
    
    # Statistics
    total_scholarships = scholarships.count()
    active_scholarships = scholarships.filter(is_active=True).count()
    total_amount_allocated = scholarships.filter(is_active=True).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'page_title': 'Manage Scholarships',
        'scholarships': scholarships,
        'total_scholarships': total_scholarships,
        'active_scholarships': active_scholarships,
        'total_amount_allocated': total_amount_allocated,
    }
    return render(request, 'management_template/manage_scholarships.html', context)


@login_required(login_url='login')
def add_scholarship(request):
    """Create new scholarship program"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            scholarship = Scholarship.objects.create(
                name=request.POST.get('name'),
                scholarship_type=request.POST.get('scholarship_type'),
                description=request.POST.get('description'),
                eligibility_criteria=request.POST.get('eligibility_criteria'),
                amount=request.POST.get('amount'),
                max_recipients=request.POST.get('max_recipients'),
                application_deadline=request.POST.get('application_deadline'),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f'Scholarship "{scholarship.name}" created successfully!')
            return redirect('management_scholarships')
        except Exception as e:
            messages.error(request, f'Error creating scholarship: {str(e)}')
    
    context = {
        'page_title': 'Add Scholarship Program',
        'scholarship_types': Scholarship.SCHOLARSHIP_TYPE,
    }
    return render(request, 'management_template/add_scholarship.html', context)


@login_required(login_url='login')
def scholarship_applications(request):
    """View all scholarship applications"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all applications
    applications = ScholarshipApplication.objects.select_related(
        'student__admin', 'student__course', 'scholarship', 'reviewed_by'
    ).order_by('-application_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Statistics
    total_applications = applications.count()
    pending_review = applications.filter(status='applied').count()
    approved = applications.filter(status='approved').count()
    disbursed = applications.filter(status='disbursed').count()
    
    context = {
        'page_title': 'Scholarship Applications',
        'applications': applications,
        'total_applications': total_applications,
        'pending_review': pending_review,
        'approved': approved,
        'disbursed': disbursed,
        'status_filter': status_filter,
        'statuses': ScholarshipApplication.APPLICATION_STATUS,
    }
    return render(request, 'management_template/scholarship_applications.html', context)


@login_required(login_url='login')
def review_scholarship_application(request, app_id):
    """Review and approve/reject scholarship application"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    application = get_object_or_404(ScholarshipApplication, id=app_id)
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            review_remarks = request.POST.get('review_remarks', '')
            
            if action == 'approve':
                application.status = 'approved'
                application.review_remarks = review_remarks
                application.reviewed_at = timezone.now()
                application.save()
                messages.success(request, f'Scholarship application approved for {application.student.admin.first_name}!')
            elif action == 'reject':
                application.status = 'rejected'
                application.review_remarks = review_remarks
                application.reviewed_at = timezone.now()
                application.save()
                messages.warning(request, 'Scholarship application rejected')
            
            return redirect('management_scholarship_applications')
        except Exception as e:
            messages.error(request, f'Error reviewing application: {str(e)}')
    
    context = {
        'page_title': 'Review Scholarship Application',
        'application': application,
    }
    return render(request, 'management_template/review_scholarship_application.html', context)


@login_required(login_url='login')
def disburse_scholarship(request, app_id):
    """Disburse approved scholarship"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    application = get_object_or_404(ScholarshipApplication, id=app_id)
    
    if application.status != 'approved':
        messages.error(request, 'Only approved applications can be disbursed')
        return redirect('management_scholarship_applications')
    
    if request.method == 'POST':
        try:
            application.status = 'disbursed'
            application.disbursement_date = timezone.now().date()
            application.save()
            
            messages.success(request, f'Scholarship of ₹{application.scholarship.amount} disbursed to {application.student.admin.first_name}!')
            return redirect('management_scholarship_applications')
        except Exception as e:
            messages.error(request, f'Error disbursing scholarship: {str(e)}')
    
    context = {
        'page_title': 'Disburse Scholarship',
        'application': application,
    }
    return render(request, 'management_template/disburse_scholarship.html', context)


# ==================== GRIEVANCE MANAGEMENT ====================

@login_required(login_url='login')
def view_grievances(request):
    """View all student/staff grievances"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all grievances
    grievances = Grievance.objects.select_related(
        'submitted_by', 'assigned_to'
    ).order_by('-submitted_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        grievances = grievances.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        grievances = grievances.filter(grievance_type=type_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        grievances = grievances.filter(priority=priority_filter)
    
    # Statistics
    total_grievances = Grievance.objects.count()
    pending = Grievance.objects.filter(status__in=['submitted', 'under_review']).count()
    in_progress = Grievance.objects.filter(status='in_progress').count()
    resolved = Grievance.objects.filter(status='resolved').count()
    urgent_count = Grievance.objects.filter(priority='urgent', status__in=['submitted', 'under_review']).count()
    
    context = {
        'page_title': 'Grievance Management',
        'grievances': grievances,
        'total_grievances': total_grievances,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'urgent_count': urgent_count,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'statuses': Grievance.STATUS_CHOICES,
        'types': Grievance.GRIEVANCE_TYPE_CHOICES,
        'priorities': Grievance.PRIORITY_CHOICES,
    }
    return render(request, 'management_template/view_grievances.html', context)


@login_required(login_url='login')
def assign_grievance(request, grievance_id):
    """Assign grievance to staff member"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        try:
            staff_id = request.POST.get('staff')
            staff = get_object_or_404(Staff, id=staff_id)
            
            grievance.assigned_to = staff
            grievance.status = 'in_progress'
            grievance.save()
            
            messages.success(request, f'Grievance assigned to {staff.admin.first_name} {staff.admin.last_name}')
            return redirect('management_grievances')
        except Exception as e:
            messages.error(request, f'Error assigning grievance: {str(e)}')
    
    # Get all staff members
    staff_members = Staff.objects.select_related('admin', 'department').order_by('admin__first_name')
    
    context = {
        'page_title': 'Assign Grievance',
        'grievance': grievance,
        'staff_members': staff_members,
    }
    return render(request, 'management_template/assign_grievance.html', context)


@login_required(login_url='login')
def resolve_grievance(request, grievance_id):
    """Mark grievance as resolved"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        try:
            resolution = request.POST.get('resolution')
            action = request.POST.get('action')
            
            if action == 'resolve':
                grievance.resolution = resolution
                grievance.status = 'resolved'
                grievance.resolved_at = timezone.now()
                grievance.save()
                messages.success(request, 'Grievance marked as resolved!')
            elif action == 'close':
                grievance.status = 'closed'
                grievance.save()
                messages.success(request, 'Grievance closed')
            
            return redirect('management_grievances')
        except Exception as e:
            messages.error(request, f'Error resolving grievance: {str(e)}')
    
    context = {
        'page_title': 'Resolve Grievance',
        'grievance': grievance,
    }
    return render(request, 'management_template/resolve_grievance.html', context)
















from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Student, Staff, Course, Department, FeePayment, FeeStructure,
    Transport, TransportAllocation, Hostel, HostelAllocation,
    Library, LibraryIssue, Scholarship, ScholarshipApplication,
    Grievance, AttendanceReport, StudentResult, LeaveReportStudent, LeaveReportStaff,
    Subject, Session
)


@login_required(login_url='login')
def management_home(request):
    """Management home dashboard with comprehensive system statistics"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # System-wide statistics
    total_students = Student.objects.filter(student_status='active').count()
    total_staff = Staff.objects.count()
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    
    # Financial statistics
    total_fees_collected = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    pending_fees = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    # Operational statistics
    total_transport = Transport.objects.count()
    transport_utilization = TransportAllocation.objects.filter(is_active=True).count()
    
    total_hostels = Hostel.objects.count()
    hostel_occupancy = HostelAllocation.objects.filter(is_active=True).count()
    total_hostel_capacity = Hostel.objects.aggregate(total=Sum('total_rooms'))['total'] or 0
    
    total_library_books = Library.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    books_issued = LibraryIssue.objects.filter(return_date__isnull=True).count()
    
    # Scholarship statistics
    active_scholarships = Scholarship.objects.filter(is_active=True).count()
    pending_scholarship_apps = ScholarshipApplication.objects.filter(status='applied').count()
    
    # Grievance statistics
    pending_grievances = Grievance.objects.filter(status__in=['submitted', 'under_review']).count()
    
    # Recent activity
    recent_fee_payments = FeePayment.objects.select_related('student__admin').order_by('-payment_date')[:5]
    recent_grievances = Grievance.objects.select_related('submitted_by').order_by('-submitted_at')[:5]
    
    # Alerts
    fee_defaulters_count = Student.objects.filter(
        student_status='active',
        fee_payments__payment_status='pending'
    ).distinct().count()
    
    overdue_books = LibraryIssue.objects.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Management Dashboard',
        'total_students': total_students,
        'total_staff': total_staff,
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_fees_collected': total_fees_collected,
        'pending_fees': pending_fees,
        'total_transport': total_transport,
        'transport_utilization': transport_utilization,
        'total_hostels': total_hostels,
        'hostel_occupancy': hostel_occupancy,
        'total_hostel_capacity': total_hostel_capacity,
        'total_library_books': total_library_books,
        'books_issued': books_issued,
        'active_scholarships': active_scholarships,
        'pending_scholarship_apps': pending_scholarship_apps,
        'pending_grievances': pending_grievances,
        'recent_fee_payments': recent_fee_payments,
        'recent_grievances': recent_grievances,
        'fee_defaulters_count': fee_defaulters_count,
        'overdue_books': overdue_books,
        'current_date': timezone.now(),
    }
    return render(request, 'management_template/home_content.html', context)


@login_required(login_url='login')
def management_view_profile(request):
    """Management view and edit profile"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Update user profile
            request.user.first_name = request.POST.get('first_name')
            request.user.last_name = request.POST.get('last_name')
            request.user.email = request.POST.get('email')
            
            # Update password if provided
            new_password = request.POST.get('password')
            if new_password and len(new_password) > 0:
                request.user.set_password(new_password)
            
            # Handle profile picture upload
            if 'profile_pic' in request.FILES:
                request.user.profile_pic = request.FILES['profile_pic']
            
            request.user.save()
            messages.success(request, 'Profile updated successfully!')
            
        except Exception as e:
            messages.error(request, f'Error updating profile: {str(e)}')
    
    context = {
        'page_title': 'Management Profile',
        'user': request.user,
    }
    return render(request, 'management_template/view_profile.html', context)


# ==================== TRANSPORT MANAGEMENT ====================

@login_required(login_url='login')
def manage_transport(request):
    """Manage transport routes and buses"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all transport routes
    transports = Transport.objects.all().order_by('route_name')
    
    # Calculate statistics
    total_routes = transports.count()
    total_capacity = transports.aggregate(total=Sum('total_seats'))['total'] or 0
    total_occupied = transports.aggregate(total=Sum('occupied_seats'))['total'] or 0
    available_seats = total_capacity - total_occupied
    
    context = {
        'page_title': 'Manage Transport',
        'transports': transports,
        'total_routes': total_routes,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'available_seats': available_seats,
    }
    return render(request, 'management_template/manage_transport.html', context)


@login_required(login_url='login')
def add_transport(request):
    """Add new transport route"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            transport = Transport.objects.create(
                route_name=request.POST.get('route_name'),
                bus_number=request.POST.get('bus_number'),
                driver_name=request.POST.get('driver_name'),
                driver_contact=request.POST.get('driver_contact'),
                route_details=request.POST.get('route_details'),
                fee_per_semester=request.POST.get('fee_per_semester', 0),
                total_seats=request.POST.get('total_seats', 40),
                occupied_seats=0
            )
            messages.success(request, f'Transport route "{transport.route_name}" added successfully!')
            return redirect('management_transport')
        except Exception as e:
            messages.error(request, f'Error adding transport: {str(e)}')
    
    context = {'page_title': 'Add Transport Route'}
    return render(request, 'management_template/add_transport.html', context)


@login_required(login_url='login')
def edit_transport(request, transport_id):
    """Edit transport route"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    transport = get_object_or_404(Transport, id=transport_id)
    
    if request.method == 'POST':
        try:
            transport.route_name = request.POST.get('route_name')
            transport.bus_number = request.POST.get('bus_number')
            transport.driver_name = request.POST.get('driver_name')
            transport.driver_contact = request.POST.get('driver_contact')
            transport.route_details = request.POST.get('route_details')
            transport.fee_per_semester = request.POST.get('fee_per_semester')
            transport.total_seats = request.POST.get('total_seats')
            transport.save()
            
            messages.success(request, 'Transport route updated successfully!')
            return redirect('management_transport')
        except Exception as e:
            messages.error(request, f'Error updating transport: {str(e)}')
    
    context = {
        'page_title': 'Edit Transport Route',
        'transport': transport
    }
    return render(request, 'management_template/edit_transport.html', context)


@login_required(login_url='login')
def transport_allocations(request):
    """View all transport allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all allocations with related data
    allocations = TransportAllocation.objects.select_related(
        'student__admin', 'student__course', 'transport'
    ).filter(is_active=True).order_by('transport__route_name', 'student__admin__first_name')
    
    # Statistics
    total_allocations = allocations.count()
    routes_with_students = Transport.objects.filter(allocations__is_active=True).distinct().count()
    
    context = {
        'page_title': 'Transport Allocations',
        'allocations': allocations,
        'total_allocations': total_allocations,
        'routes_with_students': routes_with_students,
    }
    return render(request, 'management_template/transport_allocations.html', context)


@login_required(login_url='login')
def allocate_transport(request):
    """Allocate transport to students"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            transport_id = request.POST.get('transport')
            pickup_point = request.POST.get('pickup_point')
            
            student = get_object_or_404(Student, id=student_id)
            transport = get_object_or_404(Transport, id=transport_id)
            
            # Check if transport has available seats
            if transport.available_seats <= 0:
                messages.error(request, 'No seats available on this route')
                return redirect('management_allocate_transport')
            
            # Check if student already has allocation
            if TransportAllocation.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student already has an active transport allocation')
                return redirect('management_allocate_transport')
            
            # Create allocation
            allocation = TransportAllocation.objects.create(
                student=student,
                transport=transport,
                pickup_point=pickup_point,
                is_active=True
            )
            
            # Update occupied seats
            transport.occupied_seats += 1
            transport.save()
            
            messages.success(request, f'Transport allocated to {student.admin.first_name} {student.admin.last_name} successfully!')
            return redirect('management_transport_allocations')
        except Exception as e:
            messages.error(request, f'Error allocating transport: {str(e)}')
    
    # Get students who need transport
    students = Student.objects.filter(
        transport_required=True,
        student_status='active'
    ).exclude(
        transport_allocation__is_active=True
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    # Get available transport routes
    transports = Transport.objects.all().order_by('route_name')
    
    context = {
        'page_title': 'Allocate Transport',
        'students': students,
        'transports': transports,
    }
    return render(request, 'management_template/allocate_transport.html', context)


# ==================== HOSTEL MANAGEMENT ====================

@login_required(login_url='login')
def manage_hostels(request):
    """Manage hostels and view occupancy"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all hostels
    hostels = Hostel.objects.annotate(
        current_occupancy=Count('allocations', filter=Q(allocations__is_active=True))
    ).order_by('name')
    
    # Calculate statistics
    total_hostels = hostels.count()
    total_capacity = hostels.aggregate(total=Sum('total_rooms'))['total'] or 0
    total_occupied = HostelAllocation.objects.filter(is_active=True).count()
    available_rooms = total_capacity - total_occupied
    occupancy_rate = (total_occupied / total_capacity * 100) if total_capacity > 0 else 0
    
    context = {
        'page_title': 'Manage Hostels',
        'hostels': hostels,
        'total_hostels': total_hostels,
        'total_capacity': total_capacity,
        'total_occupied': total_occupied,
        'available_rooms': available_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
    }
    return render(request, 'management_template/manage_hostels.html', context)


@login_required(login_url='login')
def add_hostel(request):
    """Add new hostel"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            hostel = Hostel.objects.create(
                name=request.POST.get('name'),
                hostel_type=request.POST.get('hostel_type'),
                warden_name=request.POST.get('warden_name'),
                warden_contact=request.POST.get('warden_contact'),
                total_rooms=request.POST.get('total_rooms'),
                occupied_rooms=0,
                address=request.POST.get('address')
            )
            messages.success(request, f'Hostel "{hostel.name}" added successfully!')
            return redirect('management_hostels')
        except Exception as e:
            messages.error(request, f'Error adding hostel: {str(e)}')
    
    context = {'page_title': 'Add Hostel'}
    return render(request, 'management_template/add_hostel.html', context)


@login_required(login_url='login')
def hostel_allocations(request):
    """View all hostel room allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all allocations
    allocations = HostelAllocation.objects.select_related(
        'student__admin', 'student__course', 'hostel'
    ).filter(is_active=True).order_by('hostel__name', 'room_number')
    
    # Filter by hostel if specified
    hostel_filter = request.GET.get('hostel')
    if hostel_filter:
        allocations = allocations.filter(hostel_id=hostel_filter)
    
    # Statistics
    total_allocations = allocations.count()
    hostels_list = Hostel.objects.all().order_by('name')
    
    context = {
        'page_title': 'Hostel Room Allocations',
        'allocations': allocations,
        'total_allocations': total_allocations,
        'hostels_list': hostels_list,
        'hostel_filter': hostel_filter,
    }
    return render(request, 'management_template/hostel_allocations.html', context)


@login_required(login_url='login')
def allocate_hostel(request):
    """Allocate hostel room to student"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            hostel_id = request.POST.get('hostel')
            room_number = request.POST.get('room_number')
            rent_per_semester = request.POST.get('rent_per_semester', 0)
            
            student = get_object_or_404(Student, id=student_id)
            hostel = get_object_or_404(Hostel, id=hostel_id)
            
            # Check if hostel has available rooms
            if hostel.available_rooms <= 0:
                messages.error(request, 'No rooms available in this hostel')
                return redirect('management_allocate_hostel')
            
            # Check if student already has allocation
            if HostelAllocation.objects.filter(student=student, is_active=True).exists():
                messages.error(request, 'Student already has an active hostel allocation')
                return redirect('management_allocate_hostel')
            
            # Check if room is already occupied
            if HostelAllocation.objects.filter(
                hostel=hostel, room_number=room_number, is_active=True
            ).exists():
                messages.error(request, f'Room {room_number} is already occupied')
                return redirect('management_allocate_hostel')
            
            # Create allocation
            allocation = HostelAllocation.objects.create(
                student=student,
                hostel=hostel,
                room_number=room_number,
                rent_per_semester=rent_per_semester,
                is_active=True
            )
            
            # Update occupied rooms
            hostel.occupied_rooms += 1
            hostel.save()
            
            messages.success(request, f'Room {room_number} allocated to {student.admin.first_name} {student.admin.last_name} successfully!')
            return redirect('management_hostel_allocations')
        except Exception as e:
            messages.error(request, f'Error allocating hostel: {str(e)}')
    
    # Get students who need hostel
    students = Student.objects.filter(
        hostel_required=True,
        student_status='active'
    ).exclude(
        hostel_allocation__is_active=True
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    # Get available hostels
    hostels = Hostel.objects.all().order_by('name')
    
    context = {
        'page_title': 'Allocate Hostel Room',
        'students': students,
        'hostels': hostels,
    }
    return render(request, 'management_template/allocate_hostel.html', context)


@login_required(login_url='login')
def hostel_visitor_logs(request):
    """View hostel visitor logs"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    from .models import HostelVisitorLog
    
    # Get visitor logs
    logs = HostelVisitorLog.objects.select_related(
        'hostel', 'student__admin'
    ).order_by('-entry_time')
    
    # Filter by date if specified
    date_filter = request.GET.get('date')
    if date_filter:
        logs = logs.filter(entry_time__date=date_filter)
    
    # Filter by hostel if specified
    hostel_filter = request.GET.get('hostel')
    if hostel_filter:
        logs = logs.filter(hostel_id=hostel_filter)
    
    # Get hostels for filter
    hostels = Hostel.objects.all().order_by('name')
    
    # Statistics
    total_visitors_today = HostelVisitorLog.objects.filter(
        entry_time__date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Hostel Visitor Logs',
        'logs': logs[:100],  # Limit to recent 100
        'hostels': hostels,
        'total_visitors_today': total_visitors_today,
        'date_filter': date_filter,
        'hostel_filter': hostel_filter,
    }
    return render(request, 'management_template/hostel_visitor_logs.html', context)


# ==================== LIBRARY MANAGEMENT ====================

@login_required(login_url='login')
def manage_library(request):
    """Manage library books and inventory"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all books
    books = Library.objects.select_related('subject').all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        books = books.filter(
            Q(title__icontains=search_query) |
            Q(author__icontains=search_query) |
            Q(isbn__icontains=search_query)
        )
    
    # Category filter
    category_filter = request.GET.get('category')
    if category_filter:
        books = books.filter(category=category_filter)
    
    books = books.order_by('title')
    
    # Statistics
    total_books = Library.objects.aggregate(total=Sum('total_copies'))['total'] or 0
    available_books = Library.objects.aggregate(total=Sum('available_copies'))['total'] or 0
    issued_books = total_books - available_books
    total_unique_titles = Library.objects.count()
    
    context = {
        'page_title': 'Library Management',
        'books': books,
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_unique_titles': total_unique_titles,
        'search_query': search_query,
        'category_filter': category_filter,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/manage_library.html', context)


@login_required(login_url='login')
def add_library_book(request):
    """Add new library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            # Handle file upload
            cover_image = request.FILES.get('cover_image')
            
            book = Library.objects.create(
                title=request.POST.get('title'),
                author=request.POST.get('author'),
                isbn=request.POST.get('isbn') or None,
                publisher=request.POST.get('publisher'),
                published_year=request.POST.get('published_year'),
                category=request.POST.get('category'),
                subject_id=request.POST.get('subject') if request.POST.get('subject') else None,
                total_copies=request.POST.get('total_copies', 1),
                available_copies=request.POST.get('total_copies', 1),
                shelf_number=request.POST.get('shelf_number', ''),
                description=request.POST.get('description', ''),
                cover_image=cover_image
            )
            messages.success(request, f'Book "{book.title}" added successfully!')
            return redirect('management_library')
        except Exception as e:
            messages.error(request, f'Error adding book: {str(e)}')
    
    # Get subjects for dropdown
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'page_title': 'Add Library Book',
        'subjects': subjects,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/add_library_book.html', context)


@login_required(login_url='login')
def edit_library_book(request, book_id):
    """Edit library book details"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    book = get_object_or_404(Library, id=book_id)
    
    if request.method == 'POST':
        try:
            book.title = request.POST.get('title')
            book.author = request.POST.get('author')
            book.isbn = request.POST.get('isbn') or None
            book.publisher = request.POST.get('publisher')
            book.published_year = request.POST.get('published_year')
            book.category = request.POST.get('category')
            book.subject_id = request.POST.get('subject') if request.POST.get('subject') else None
            
            # Update copies if changed
            new_total = int(request.POST.get('total_copies', book.total_copies))
            difference = new_total - book.total_copies
            book.total_copies = new_total
            book.available_copies += difference
            
            book.shelf_number = request.POST.get('shelf_number', '')
            book.description = request.POST.get('description', '')
            
            # Handle cover image upload
            if 'cover_image' in request.FILES:
                book.cover_image = request.FILES['cover_image']
            
            book.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('management_library')
        except Exception as e:
            messages.error(request, f'Error updating book: {str(e)}')
    
    # Get subjects for dropdown
    subjects = Subject.objects.all().order_by('name')
    
    context = {
        'page_title': 'Edit Library Book',
        'book': book,
        'subjects': subjects,
        'categories': Library.BOOK_CATEGORY,
    }
    return render(request, 'management_template/edit_library_book.html', context)


@login_required(login_url='login')
def library_issues(request):
    """View all library book issues and returns"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all issues
    issues = LibraryIssue.objects.select_related(
        'book', 'student__admin', 'issued_by'
    ).order_by('-issue_date')
    
    # Filter by status
    status_filter = request.GET.get('status', 'active')
    if status_filter == 'active':
        issues = issues.filter(return_date__isnull=True)
    elif status_filter == 'returned':
        issues = issues.filter(return_date__isnull=False)
    elif status_filter == 'overdue':
        issues = issues.filter(return_date__isnull=True, due_date__lt=timezone.now().date())
    
    # Statistics
    active_issues = LibraryIssue.objects.filter(return_date__isnull=True).count()
    overdue_issues = LibraryIssue.objects.filter(
        return_date__isnull=True,
        due_date__lt=timezone.now().date()
    ).count()
    returned_today = LibraryIssue.objects.filter(
        return_date__date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Library Issues & Returns',
        'issues': issues[:100],  # Limit to 100 for performance
        'active_issues': active_issues,
        'overdue_issues': overdue_issues,
        'returned_today': returned_today,
        'status_filter': status_filter,
    }
    return render(request, 'management_template/library_issues.html', context)


@login_required(login_url='login')
def issue_library_book(request):
    """Issue library book to student"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            book_id = request.POST.get('book')
            student_id = request.POST.get('student')
            due_days = int(request.POST.get('due_days', 14))
            
            book = get_object_or_404(Library, id=book_id)
            student = get_object_or_404(Student, id=student_id)
            
            # Check if book is available
            if book.available_copies <= 0:
                messages.error(request, f'No copies of "{book.title}" are currently available')
                return redirect('management_issue_library_book')
            
            # Check if student already has this book
            if LibraryIssue.objects.filter(
                book=book, student=student, return_date__isnull=True
            ).exists():
                messages.error(request, 'Student already has this book issued')
                return redirect('management_issue_library_book')
            
            # Create issue record
            issue = LibraryIssue.objects.create(
                book=book,
                student=student,
                issued_by=request.user.staff if hasattr(request.user, 'staff') else None,
                issue_date=timezone.now().date(),
                due_date=timezone.now().date() + timedelta(days=due_days)
            )
            
            # Update available copies
            book.available_copies -= 1
            book.save()
            
            messages.success(request, f'Book "{book.title}" issued to {student.admin.first_name} {student.admin.last_name}!')
            return redirect('management_library_issues')
        except Exception as e:
            messages.error(request, f'Error issuing book: {str(e)}')
    
    # Get available books
    books = Library.objects.filter(available_copies__gt=0).order_by('title')
    
    # Get active students
    students = Student.objects.filter(
        student_status='active'
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    context = {
        'page_title': 'Issue Library Book',
        'books': books,
        'students': students,
    }
    return render(request, 'management_template/issue_library_book.html', context)


@login_required(login_url='login')
def return_library_book(request, issue_id):
    """Process book return"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    issue = get_object_or_404(LibraryIssue, id=issue_id)
    
    if request.method == 'POST':
        try:
            # Mark as returned
            issue.return_date = timezone.now().date()
            
            # Calculate fine if overdue
            if issue.due_date < issue.return_date:
                days_overdue = (issue.return_date - issue.due_date).days
                fine_per_day = 5  # Rs. 5 per day
                issue.fine_amount = days_overdue * fine_per_day
            else:
                issue.fine_amount = 0
            
            issue.save()
            
            # Update available copies
            book = issue.book
            book.available_copies += 1
            book.save()
            
            if issue.fine_amount > 0:
                messages.warning(request, f'Book returned with fine of ₹{issue.fine_amount}')
            else:
                messages.success(request, 'Book returned successfully!')
            
            return redirect('management_library_issues')
        except Exception as e:
            messages.error(request, f'Error processing return: {str(e)}')
    
    # Calculate potential fine
    potential_fine = 0
    if issue.due_date < timezone.now().date():
        days_overdue = (timezone.now().date() - issue.due_date).days
        potential_fine = days_overdue * 5
    
    context = {
        'page_title': 'Return Library Book',
        'issue': issue,
        'potential_fine': potential_fine,
    }
    return render(request, 'management_template/return_library_book.html', context)


# ==================== FEE MANAGEMENT ====================

@login_required(login_url='login')
def manage_fee_structure(request):
    """Manage fee structures for all courses"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all fee structures
    fee_structures = FeeStructure.objects.select_related(
        'course', 'session'
    ).order_by('course__name', 'semester')
    
    # Filter by course if specified
    course_filter = request.GET.get('course')
    if course_filter:
        fee_structures = fee_structures.filter(course_id=course_filter)
    
    # Get courses for filter
    courses = Course.objects.all().order_by('name')
    
    context = {
        'page_title': 'Fee Structure Management',
        'fee_structures': fee_structures,
        'courses': courses,
        'course_filter': course_filter,
    }
    return render(request, 'management_template/manage_fee_structure.html', context)


@login_required(login_url='login')
def add_fee_structure(request):
    """Create new fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            course_id = request.POST.get('course')
            course_type = request.POST.get('course_type')
            semester = request.POST.get('semester')
            session_id = request.POST.get('session')
            
            # Check if fee structure already exists
            if FeeStructure.objects.filter(
                course_id=course_id,
                course_type=course_type,
                semester=semester,
                session_id=session_id
            ).exists():
                messages.error(request, 'Fee structure already exists for this combination')
                return redirect('management_add_fee_structure')
            
            fee_structure = FeeStructure.objects.create(
                course_id=course_id,
                course_type=course_type,
                semester=semester,
                session_id=session_id,
                tuition_fee=request.POST.get('tuition_fee', 0),
                development_fee=request.POST.get('development_fee', 0),
                lab_fee=request.POST.get('lab_fee', 0),
                library_fee=request.POST.get('library_fee', 0),
                exam_fee=request.POST.get('exam_fee', 0),
                other_fee=request.POST.get('other_fee', 0)
            )
            messages.success(request, f'Fee structure created successfully! Total: ₹{fee_structure.total_fee}')
            return redirect('management_fee_structure')
        except Exception as e:
            messages.error(request, f'Error creating fee structure: {str(e)}')
    
    # Get courses and sessions
    courses = Course.objects.all().order_by('name')
    sessions = Session.objects.all().order_by('-session_start_year')
    
    context = {
        'page_title': 'Add Fee Structure',
        'courses': courses,
        'sessions': sessions,
        'course_types': Student.COURSE_TYPE_CHOICES,
    }
    return render(request, 'management_template/add_fee_structure.html', context)


@login_required(login_url='login')
def edit_fee_structure(request, structure_id):
    """Edit existing fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    fee_structure = get_object_or_404(FeeStructure, id=structure_id)
    
    if request.method == 'POST':
        try:
            fee_structure.tuition_fee = request.POST.get('tuition_fee')
            fee_structure.development_fee = request.POST.get('development_fee')
            fee_structure.lab_fee = request.POST.get('lab_fee')
            fee_structure.library_fee = request.POST.get('library_fee')
            fee_structure.exam_fee = request.POST.get('exam_fee')
            fee_structure.other_fee = request.POST.get('other_fee')
            fee_structure.save()
            
            messages.success(request, f'Fee structure updated! New total: ₹{fee_structure.total_fee}')
            return redirect('management_fee_structure')
        except Exception as e:
            messages.error(request, f'Error updating fee structure: {str(e)}')
    
    context = {
        'page_title': 'Edit Fee Structure',
        'fee_structure': fee_structure,
    }
    return render(request, 'management_template/edit_fee_structure.html', context)


@login_required(login_url='login')
def view_fee_payments(request):
    """View all fee payment records"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all payments
    payments = FeePayment.objects.select_related(
        'student__admin', 'student__course', 'fee_structure'
    ).order_by('-payment_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        payments = payments.filter(payment_status=status_filter)
    
    # Filter by date range
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        payments = payments.filter(payment_date__range=[start_date, end_date])
    
    # Statistics
    total_collected = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(total=Sum('amount_paid'))['total'] or 0
    
    pending_amount = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    payments_today = FeePayment.objects.filter(
        payment_date=timezone.now().date()
    ).count()
    
    context = {
        'page_title': 'Fee Payments',
        'payments': payments[:100],  # Limit for performance
        'total_collected': total_collected,
        'pending_amount': pending_amount,
        'payments_today': payments_today,
        'status_filter': status_filter,
    }
    return render(request, 'management_template/view_fee_payments.html', context)


@login_required(login_url='login')
def record_fee_payment(request):
    """Record new fee payment"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            student_id = request.POST.get('student')
            fee_structure_id = request.POST.get('fee_structure')
            amount_paid = float(request.POST.get('amount_paid', 0))
            payment_mode = request.POST.get('payment_mode')
            transaction_id = request.POST.get('transaction_id', '')
            remarks = request.POST.get('remarks', '')
            
            student = get_object_or_404(Student, id=student_id)
            fee_structure = get_object_or_404(FeeStructure, id=fee_structure_id)
            
            # Calculate amounts
            total_fee = fee_structure.total_fee
            amount_pending = total_fee - amount_paid
            
            # Determine payment status
            if amount_paid >= total_fee:
                payment_status = 'paid'
                amount_pending = 0
            elif amount_paid > 0:
                payment_status = 'partial'
            else:
                payment_status = 'pending'
            
            payment = FeePayment.objects.create(
                student=student,
                fee_structure=fee_structure,
                amount_paid=amount_paid,
                amount_pending=amount_pending,
                payment_date=timezone.now().date(),
                payment_mode=payment_mode,
                transaction_id=transaction_id,
                payment_status=payment_status,
                remarks=remarks
            )
            
            messages.success(request, f'Payment of ₹{amount_paid} recorded for {student.admin.first_name} {student.admin.last_name}!')
            return redirect('management_fee_payments')
        except Exception as e:
            messages.error(request, f'Error recording payment: {str(e)}')
    
    # Get students and fee structures
    students = Student.objects.filter(
        student_status='active'
    ).select_related('admin', 'course').order_by('admin__first_name')
    
    fee_structures = FeeStructure.objects.select_related('course', 'session').all()
    
    context = {
        'page_title': 'Record Fee Payment',
        'students': students,
        'fee_structures': fee_structures,
        'payment_modes': FeePayment.PAYMENT_MODE,
    }
    return render(request, 'management_template/record_fee_payment.html', context)


@login_required(login_url='login')
def fee_defaulters(request):
    """View students with pending fee payments"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get students with pending fees
    defaulters = Student.objects.filter(
        student_status='active',
        fee_payments__payment_status='pending'
    ).select_related('admin', 'course').annotate(
        total_pending=Sum('fee_payments__amount_pending', filter=Q(fee_payments__payment_status='pending'))
    ).distinct().order_by('-total_pending')
    
    # Calculate total pending amount
    total_pending_amount = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(total=Sum('amount_pending'))['total'] or 0
    
    context = {
        'page_title': 'Fee Defaulters',
        'defaulters': defaulters,
        'total_defaulters': defaulters.count(),
        'total_pending_amount': total_pending_amount,
    }
    return render(request, 'management_template/fee_defaulters.html', context)


# ==================== SCHOLARSHIP MANAGEMENT ====================

@login_required(login_url='login')
def manage_scholarships(request):
    """Manage scholarship programs"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all scholarships
    scholarships = Scholarship.objects.annotate(
        application_count=Count('applications'),
        approved_count=Count('applications', filter=Q(applications__status='approved')),
        disbursed_count=Count('applications', filter=Q(applications__status='disbursed'))
    ).order_by('-is_active', 'name')
    
    # Statistics
    total_scholarships = scholarships.count()
    active_scholarships = scholarships.filter(is_active=True).count()
    total_amount_allocated = scholarships.filter(is_active=True).aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'page_title': 'Manage Scholarships',
        'scholarships': scholarships,
        'total_scholarships': total_scholarships,
        'active_scholarships': active_scholarships,
        'total_amount_allocated': total_amount_allocated,
    }
    return render(request, 'management_template/manage_scholarships.html', context)


@login_required(login_url='login')
def add_scholarship(request):
    """Create new scholarship program"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    if request.method == 'POST':
        try:
            scholarship = Scholarship.objects.create(
                name=request.POST.get('name'),
                scholarship_type=request.POST.get('scholarship_type'),
                description=request.POST.get('description'),
                eligibility_criteria=request.POST.get('eligibility_criteria'),
                amount=request.POST.get('amount'),
                max_recipients=request.POST.get('max_recipients'),
                application_deadline=request.POST.get('application_deadline'),
                is_active=request.POST.get('is_active') == 'on'
            )
            messages.success(request, f'Scholarship "{scholarship.name}" created successfully!')
            return redirect('management_scholarships')
        except Exception as e:
            messages.error(request, f'Error creating scholarship: {str(e)}')
    
    context = {
        'page_title': 'Add Scholarship Program',
        'scholarship_types': Scholarship.SCHOLARSHIP_TYPE,
    }
    return render(request, 'management_template/add_scholarship.html', context)


@login_required(login_url='login')
def scholarship_applications(request):
    """View all scholarship applications"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all applications
    applications = ScholarshipApplication.objects.select_related(
        'student__admin', 'student__course', 'scholarship', 'reviewed_by'
    ).order_by('-application_date')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    # Statistics
    total_applications = applications.count()
    pending_review = applications.filter(status='applied').count()
    approved = applications.filter(status='approved').count()
    disbursed = applications.filter(status='disbursed').count()
    
    context = {
        'page_title': 'Scholarship Applications',
        'applications': applications,
        'total_applications': total_applications,
        'pending_review': pending_review,
        'approved': approved,
        'disbursed': disbursed,
        'status_filter': status_filter,
        'statuses': ScholarshipApplication.APPLICATION_STATUS,
    }
    return render(request, 'management_template/scholarship_applications.html', context)


@login_required(login_url='login')
def review_scholarship_application(request, app_id):
    """Review and approve/reject scholarship application"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    application = get_object_or_404(ScholarshipApplication, id=app_id)
    
    if request.method == 'POST':
        try:
            action = request.POST.get('action')
            review_remarks = request.POST.get('review_remarks', '')
            
            if action == 'approve':
                application.status = 'approved'
                application.review_remarks = review_remarks
                application.reviewed_at = timezone.now()
                application.save()
                messages.success(request, f'Scholarship application approved for {application.student.admin.first_name}!')
            elif action == 'reject':
                application.status = 'rejected'
                application.review_remarks = review_remarks
                application.reviewed_at = timezone.now()
                application.save()
                messages.warning(request, 'Scholarship application rejected')
            
            return redirect('management_scholarship_applications')
        except Exception as e:
            messages.error(request, f'Error reviewing application: {str(e)}')
    
    context = {
        'page_title': 'Review Scholarship Application',
        'application': application,
    }
    return render(request, 'management_template/review_scholarship_application.html', context)


@login_required(login_url='login')
def disburse_scholarship(request, app_id):
    """Disburse approved scholarship"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    application = get_object_or_404(ScholarshipApplication, id=app_id)
    
    if application.status != 'approved':
        messages.error(request, 'Only approved applications can be disbursed')
        return redirect('management_scholarship_applications')
    
    if request.method == 'POST':
        try:
            application.status = 'disbursed'
            application.disbursement_date = timezone.now().date()
            application.save()
            
            messages.success(request, f'Scholarship of ₹{application.scholarship.amount} disbursed to {application.student.admin.first_name}!')
            return redirect('management_scholarship_applications')
        except Exception as e:
            messages.error(request, f'Error disbursing scholarship: {str(e)}')
    
    context = {
        'page_title': 'Disburse Scholarship',
        'application': application,
    }
    return render(request, 'management_template/disburse_scholarship.html', context)


# ==================== GRIEVANCE MANAGEMENT ====================

@login_required(login_url='login')
def view_grievances(request):
    """View all student/staff grievances"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Get all grievances
    grievances = Grievance.objects.select_related(
        'submitted_by', 'assigned_to'
    ).order_by('-submitted_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        grievances = grievances.filter(status=status_filter)
    
    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        grievances = grievances.filter(grievance_type=type_filter)
    
    # Filter by priority
    priority_filter = request.GET.get('priority')
    if priority_filter:
        grievances = grievances.filter(priority=priority_filter)
    
    # Statistics
    total_grievances = Grievance.objects.count()
    pending = Grievance.objects.filter(status__in=['submitted', 'under_review']).count()
    in_progress = Grievance.objects.filter(status='in_progress').count()
    resolved = Grievance.objects.filter(status='resolved').count()
    urgent_count = Grievance.objects.filter(priority='urgent', status__in=['submitted', 'under_review']).count()
    
    context = {
        'page_title': 'Grievance Management',
        'grievances': grievances,
        'total_grievances': total_grievances,
        'pending': pending,
        'in_progress': in_progress,
        'resolved': resolved,
        'urgent_count': urgent_count,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'priority_filter': priority_filter,
        'statuses': Grievance.STATUS_CHOICES,
        'types': Grievance.GRIEVANCE_TYPE_CHOICES,
        'priorities': Grievance.PRIORITY_CHOICES,
    }
    return render(request, 'management_template/view_grievances.html', context)


@login_required(login_url='login')
def assign_grievance(request, grievance_id):
    """Assign grievance to staff member"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        try:
            staff_id = request.POST.get('staff')
            staff = get_object_or_404(Staff, id=staff_id)
            
            grievance.assigned_to = staff
            grievance.status = 'in_progress'
            grievance.save()
            
            messages.success(request, f'Grievance assigned to {staff.admin.first_name} {staff.admin.last_name}')
            return redirect('management_grievances')
        except Exception as e:
            messages.error(request, f'Error assigning grievance: {str(e)}')
    
    # Get all staff members
    staff_members = Staff.objects.select_related('admin', 'department').order_by('admin__first_name')
    
    context = {
        'page_title': 'Assign Grievance',
        'grievance': grievance,
        'staff_members': staff_members,
    }
    return render(request, 'management_template/assign_grievance.html', context)


@login_required(login_url='login')
def resolve_grievance(request, grievance_id):
    """Mark grievance as resolved"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    grievance = get_object_or_404(Grievance, id=grievance_id)
    
    if request.method == 'POST':
        try:
            resolution = request.POST.get('resolution')
            action = request.POST.get('action')
            
            if action == 'resolve':
                grievance.resolution = resolution
                grievance.status = 'resolved'
                grievance.resolved_at = timezone.now()
                grievance.save()
                messages.success(request, 'Grievance marked as resolved!')
            elif action == 'close':
                grievance.status = 'closed'
                grievance.save()
                messages.success(request, 'Grievance closed')
            
            return redirect('management_grievances')
        except Exception as e:
            messages.error(request, f'Error resolving grievance: {str(e)}')
    
    context = {
        'page_title': 'Resolve Grievance',
        'grievance': grievance,
    }
    return render(request, 'management_template/resolve_grievance.html', context)

























# ==================== PHASE 10: MANAGEMENT REPORTING ====================


@login_required(login_url='login')
def financial_reports(request):
    """Comprehensive financial reporting for management"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Revenue Statistics
    total_revenue = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    pending_revenue = FeePayment.objects.filter(
        payment_status__in=['pending', 'partial']
    ).aggregate(Sum('amount_pending'))['amount_pending__sum'] or 0
    
    expected_revenue = total_revenue + pending_revenue
    collection_efficiency = round((total_revenue / expected_revenue) * 100, 2) if expected_revenue > 0 else 0
    
    # Monthly Revenue Trend (Last 12 months)
    import json
    monthly_data = []
    today = timezone.now()
    for i in range(11, -1, -1):
        month_start = (today - timedelta(days=30*i)).replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        month_revenue = FeePayment.objects.filter(
            payment_date__range=[month_start, month_end],
            payment_status__in=['paid', 'partial']
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        monthly_data.append({
            'month': month_start.strftime('%b %Y'),
            'revenue': float(month_revenue)
        })
    
    # Scholarship Expenses
    total_scholarships = ScholarshipApplication.objects.filter(status='disbursed').count()
    scholarship_expense = 0
    for app in ScholarshipApplication.objects.filter(status='disbursed'):
        scholarship_expense += app.scholarship.amount
    
    # Department-wise Revenue
    dept_revenue = []
    for dept in Department.objects.all():
        students = Student.objects.filter(course__department=dept)
        student_ids = students.values_list('id', flat=True)
        
        dept_collected = FeePayment.objects.filter(
            student_id__in=student_ids,
            payment_status__in=['paid', 'partial']
        ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
        
        dept_revenue.append({
            'department': dept.name,
            'revenue': float(dept_collected),
            'student_count': students.count()
        })
    
    # Fee Defaulters
    defaulters = FeePayment.objects.filter(
        payment_status='pending',
        amount_pending__gt=0
    ).select_related('student').order_by('-amount_pending')[:20]
    
    context = {
        'page_title': 'Financial Reports',
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'expected_revenue': expected_revenue,
        'collection_efficiency': collection_efficiency,
        'monthly_data': monthly_data,
        'monthly_data_json': json.dumps(monthly_data),
        'total_scholarships': total_scholarships,
        'scholarship_expense': scholarship_expense,
        'dept_revenue': dept_revenue,
        'defaulters': defaulters
    }
    return render(request, 'management_template/financial_reports.html', context)


@login_required(login_url='login')
def operational_reports(request):
    """Operational metrics: hostel, transport, library"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Hostel Operations
    total_hostel_rooms = Hostel.objects.aggregate(Sum('total_rooms'))['total_rooms__sum'] or 0
    occupied_rooms = HostelAllocation.objects.filter(is_active=True).count()
    hostel_occupancy_rate = round((occupied_rooms / total_hostel_rooms) * 100, 2) if total_hostel_rooms > 0 else 0
    
    hostel_stats = []
    for hostel in Hostel.objects.all():
        occupied = HostelAllocation.objects.filter(hostel=hostel, is_active=True).count()
        occupancy = round((occupied / hostel.total_rooms) * 100, 2) if hostel.total_rooms > 0 else 0
        
        hostel_stats.append({
            'name': hostel.hostel_name,
            'total_rooms': hostel.total_rooms,
            'occupied': occupied,
            'available': hostel.total_rooms - occupied,
            'occupancy': occupancy
        })
    
    # Transport Operations
    total_transport_seats = Transport.objects.aggregate(Sum('total_seats'))['total_seats__sum'] or 0
    occupied_seats = TransportAllocation.objects.filter(is_active=True).count()
    transport_utilization = round((occupied_seats / total_transport_seats) * 100, 2) if total_transport_seats > 0 else 0
    
    transport_stats = []
    for transport in Transport.objects.all():
        allocated = TransportAllocation.objects.filter(transport=transport, is_active=True).count()
        utilization = round((allocated / transport.total_seats) * 100, 2) if transport.total_seats > 0 else 0
        
        transport_stats.append({
            'route': transport.route_name,
            'total_seats': transport.total_seats,
            'occupied': allocated,
            'available': transport.total_seats - allocated,
            'utilization': utilization
        })
    
    # Library Operations
    total_books = Library.objects.aggregate(Sum('total_copies'))['total_copies__sum'] or 0
    books_issued = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).count()
    library_circulation = round((books_issued / total_books) * 100, 2) if total_books > 0 else 0
    
    overdue_books = LibraryIssue.objects.filter(status='overdue').count()
    total_fines = LibraryIssue.objects.filter(fine_amount__gt=0).aggregate(Sum('fine_amount'))['fine_amount__sum'] or 0
    
    context = {
        'page_title': 'Operational Reports',
        'hostel_occupancy_rate': hostel_occupancy_rate,
        'total_hostel_rooms': total_hostel_rooms,
        'occupied_rooms': occupied_rooms,
        'hostel_stats': hostel_stats,
        'transport_utilization': transport_utilization,
        'total_transport_seats': total_transport_seats,
        'occupied_seats': occupied_seats,
        'transport_stats': transport_stats,
        'library_circulation': library_circulation,
        'total_books': total_books,
        'books_issued': books_issued,
        'overdue_books': overdue_books,
        'total_fines': total_fines
    }
    return render(request, 'management_template/operational_reports.html', context)


@login_required(login_url='login')
def academic_oversight(request):
    """Academic oversight: cross-department comparison, faculty workload, retention"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Department Comparison
    dept_comparison = []
    for dept in Department.objects.all():
        students = Student.objects.filter(course__department=dept)
        student_ids = students.values_list('id', flat=True)
        faculty = Staff.objects.filter(department=dept)
        
        # Calculate average attendance
        dept_attendance = AttendanceReport.objects.filter(student_id__in=student_ids)
        if dept_attendance.exists():
            present = dept_attendance.filter(status=True).count()
            total = dept_attendance.count()
            avg_attendance = round((present / total) * 100, 2) if total > 0 else 0
        else:
            avg_attendance = 0
        
        # Calculate average performance
        dept_results = StudentResult.objects.filter(student_id__in=student_ids)
        avg_performance = round(dept_results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
        
        # Student-Faculty Ratio
        student_faculty_ratio = round(students.count() / faculty.count(), 1) if faculty.count() > 0 else 0
        
        dept_comparison.append({
            'department': dept.name,
            'students': students.count(),
            'faculty': faculty.count(),
            'ratio': student_faculty_ratio,
            'attendance': avg_attendance,
            'performance': avg_performance
        })
    
    # Faculty Workload
    faculty_workload = []
    for staff in Staff.objects.all()[:20]:
        subjects = Subject.objects.filter(staff=staff)
        total_students = 0
        for subject in subjects:
            total_students += Student.objects.filter(course=subject.course).count()
        
        faculty_workload.append({
            'name': f"{staff.admin.first_name} {staff.admin.last_name}",
            'department': staff.department.name if staff.department else 'N/A',
            'subjects': subjects.count(),
            'students': total_students
        })
    
    # Student Retention
    current_year = timezone.now().year
    retention_data = []
    for i in range(4):
        year = current_year - i
        enrolled = Student.objects.filter(admission_year=year).count()
        active = Student.objects.filter(admission_year=year, student_status='active').count()
        retention_rate = round((active / enrolled) * 100, 2) if enrolled > 0 else 0
        
        retention_data.append({
            'year': year,
            'enrolled': enrolled,
            'active': active,
            'retention': retention_rate
        })
    
    context = {
        'page_title': 'Academic Oversight',
        'dept_comparison': dept_comparison,
        'faculty_workload': faculty_workload,
        'retention_data': retention_data
    }
    return render(request, 'management_template/academic_oversight.html', context)


@login_required(login_url='login')
def institutional_kpis(request):
    """Overall institutional KPIs dashboard"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    # Academic KPIs
    total_students = Student.objects.filter(student_status='active').count()
    total_faculty = Staff.objects.count()
    student_faculty_ratio = round(total_students / total_faculty, 1) if total_faculty > 0 else 0
    
    # Overall Attendance Rate
    attendance_records = AttendanceReport.objects.all()
    if attendance_records.exists():
        present = attendance_records.filter(status=True).count()
        overall_attendance = round((present / attendance_records.count()) * 100, 2)
    else:
        overall_attendance = 0
    
    # Overall Performance
    results = StudentResult.objects.all()
    overall_performance = round(results.aggregate(Avg('marks'))['marks__avg'] or 0, 2)
    pass_rate = round((results.filter(marks__gte=40).count() / results.count()) * 100, 2) if results.count() > 0 else 0
    
    # Financial KPIs
    total_revenue = FeePayment.objects.filter(
        payment_status__in=['paid', 'partial']
    ).aggregate(Sum('amount_paid'))['amount_paid__sum'] or 0
    
    pending_revenue = FeePayment.objects.filter(
        payment_status='pending'
    ).aggregate(Sum('amount_pending'))['amount_pending__sum'] or 0
    
    revenue_collection = round((total_revenue / (total_revenue + pending_revenue)) * 100, 2) if (total_revenue + pending_revenue) > 0 else 0
    
    # Operational KPIs
    hostel_occupancy = HostelAllocation.objects.filter(is_active=True).count()
    total_hostel_capacity = Hostel.objects.aggregate(Sum('total_rooms'))['total_rooms__sum'] or 0
    hostel_utilization = round((hostel_occupancy / total_hostel_capacity) * 100, 2) if total_hostel_capacity > 0 else 0
    
    transport_allocated = TransportAllocation.objects.filter(is_active=True).count()
    total_transport_seats = Transport.objects.aggregate(Sum('total_seats'))['total_seats__sum'] or 0
    transport_utilization = round((transport_allocated / total_transport_seats) * 100, 2) if total_transport_seats > 0 else 0
    
    library_issued = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).count()
    total_books = Library.objects.aggregate(Sum('total_copies'))['total_copies__sum'] or 0
    library_circulation = round((library_issued / total_books) * 100, 2) if total_books > 0 else 0
    
    # Service KPIs
    active_grievances = Grievance.objects.filter(status='pending').count()
    resolved_grievances = Grievance.objects.filter(status='resolved').count()
    total_grievances = Grievance.objects.count()
    grievance_resolution_rate = round((resolved_grievances / total_grievances) * 100, 2) if total_grievances > 0 else 0
    
    active_scholarships = ScholarshipApplication.objects.filter(status='approved').count()
    disbursed_scholarships = ScholarshipApplication.objects.filter(status='disbursed').count()
    
    context = {
        'page_title': 'Institutional KPIs',
        'total_students': total_students,
        'total_faculty': total_faculty,
        'student_faculty_ratio': student_faculty_ratio,
        'overall_attendance': overall_attendance,
        'overall_performance': overall_performance,
        'pass_rate': pass_rate,
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        'revenue_collection': revenue_collection,
        'hostel_utilization': hostel_utilization,
        'transport_utilization': transport_utilization,
        'library_circulation': library_circulation,
        'active_grievances': active_grievances,
        'grievance_resolution_rate': grievance_resolution_rate,
        'active_scholarships': active_scholarships,
        'disbursed_scholarships': disbursed_scholarships
    }
    return render(request, 'management_template/institutional_kpis.html', context)

