from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def management_home(request):
    """Management home dashboard"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Management Dashboard'}
    return render(request, 'management_template/management_home.html', context)


@login_required(login_url='login')
def management_view_profile(request):
    """Management view profile"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Management Profile'}
    return render(request, 'management_template/management_profile.html', context)


# Transport Management
@login_required(login_url='login')
def manage_transport(request):
    """Manage transport"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Transport'}
    return render(request, 'management_template/manage_transport.html', context)


@login_required(login_url='login')
def add_transport(request):
    """Add transport"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Transport'}
    return render(request, 'management_template/add_transport.html', context)


@login_required(login_url='login')
def edit_transport(request, transport_id):
    """Edit transport"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Transport', 'transport_id': transport_id}
    return render(request, 'management_template/edit_transport.html', context)


@login_required(login_url='login')
def transport_allocations(request):
    """Transport allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Transport Allocations'}
    return render(request, 'management_template/transport_allocations.html', context)


@login_required(login_url='login')
def allocate_transport(request):
    """Allocate transport"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Allocate Transport'}
    return render(request, 'management_template/allocate_transport.html', context)


# Hostel Management
@login_required(login_url='login')
def manage_hostels(request):
    """Manage hostels"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Hostels'}
    return render(request, 'management_template/manage_hostels.html', context)


@login_required(login_url='login')
def add_hostel(request):
    """Add hostel"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Hostel'}
    return render(request, 'management_template/add_hostel.html', context)


@login_required(login_url='login')
def hostel_allocations(request):
    """Hostel allocations"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Hostel Allocations'}
    return render(request, 'management_template/hostel_allocations.html', context)


@login_required(login_url='login')
def allocate_hostel(request):
    """Allocate hostel"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Allocate Hostel'}
    return render(request, 'management_template/allocate_hostel.html', context)


@login_required(login_url='login')
def hostel_visitor_logs(request):
    """Hostel visitor logs"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Hostel Visitor Logs'}
    return render(request, 'management_template/hostel_visitor_logs.html', context)


# Library Management
@login_required(login_url='login')
def manage_library(request):
    """Manage library"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Library'}
    return render(request, 'management_template/manage_library.html', context)


@login_required(login_url='login')
def add_library_book(request):
    """Add library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Library Book'}
    return render(request, 'management_template/add_library_book.html', context)


@login_required(login_url='login')
def edit_library_book(request, book_id):
    """Edit library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Library Book', 'book_id': book_id}
    return render(request, 'management_template/edit_library_book.html', context)


@login_required(login_url='login')
def library_issues(request):
    """Library issues"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Library Issues'}
    return render(request, 'management_template/library_issues.html', context)


@login_required(login_url='login')
def issue_library_book(request):
    """Issue library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Issue Library Book'}
    return render(request, 'management_template/issue_library_book.html', context)


@login_required(login_url='login')
def return_library_book(request, issue_id):
    """Return library book"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Return Library Book', 'issue_id': issue_id}
    return render(request, 'management_template/return_library_book.html', context)


# Fee Management
@login_required(login_url='login')
def manage_fee_structure(request):
    """Manage fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Fee Structure'}
    return render(request, 'management_template/manage_fee_structure.html', context)


@login_required(login_url='login')
def add_fee_structure(request):
    """Add fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Fee Structure'}
    return render(request, 'management_template/add_fee_structure.html', context)


@login_required(login_url='login')
def edit_fee_structure(request, structure_id):
    """Edit fee structure"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Edit Fee Structure', 'structure_id': structure_id}
    return render(request, 'management_template/edit_fee_structure.html', context)


@login_required(login_url='login')
def view_fee_payments(request):
    """View fee payments"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Fee Payments'}
    return render(request, 'management_template/view_fee_payments.html', context)


@login_required(login_url='login')
def record_fee_payment(request):
    """Record fee payment"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Record Fee Payment'}
    return render(request, 'management_template/record_fee_payment.html', context)


@login_required(login_url='login')
def fee_defaulters(request):
    """Fee defaulters"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Fee Defaulters'}
    return render(request, 'management_template/fee_defaulters.html', context)


# Scholarship Management
@login_required(login_url='login')
def manage_scholarships(request):
    """Manage scholarships"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Manage Scholarships'}
    return render(request, 'management_template/manage_scholarships.html', context)


@login_required(login_url='login')
def add_scholarship(request):
    """Add scholarship"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Add Scholarship'}
    return render(request, 'management_template/add_scholarship.html', context)


@login_required(login_url='login')
def scholarship_applications(request):
    """Scholarship applications"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Scholarship Applications'}
    return render(request, 'management_template/scholarship_applications.html', context)


@login_required(login_url='login')
def review_scholarship_application(request, app_id):
    """Review scholarship application"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Review Scholarship Application', 'app_id': app_id}
    return render(request, 'management_template/review_scholarship_application.html', context)


@login_required(login_url='login')
def disburse_scholarship(request, app_id):
    """Disburse scholarship"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Disburse Scholarship', 'app_id': app_id}
    return render(request, 'management_template/disburse_scholarship.html', context)


# Grievance Management
@login_required(login_url='login')
def view_grievances(request):
    """View grievances"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Grievances'}
    return render(request, 'management_template/view_grievances.html', context)


@login_required(login_url='login')
def assign_grievance(request, grievance_id):
    """Assign grievance"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Assign Grievance', 'grievance_id': grievance_id}
    return render(request, 'management_template/assign_grievance.html', context)


@login_required(login_url='login')
def resolve_grievance(request, grievance_id):
    """Resolve grievance"""
    if request.user.user_type != '4':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Resolve Grievance', 'grievance_id': grievance_id}
    return render(request, 'management_template/resolve_grievance.html', context)










