"""
Management Panel Views - Administrative Operations
Handles: Hostel, Transport, Library, Fees, Scholarships, Facilities
"""

import json
from datetime import datetime, date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render)
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum, Q

from .forms import *
from .models import *


def management_home(request):
    """Management dashboard"""
    management = get_object_or_404(Management, admin=request.user)
    
    # Statistics
    total_students = Student.objects.filter(student_status='active').count()
    total_staff = Staff.objects.filter(status='active').count()
    
    # Transport stats
    total_buses = Transport.objects.count()
    occupied_seats = sum([t.occupied_seats for t in Transport.objects.all()])
    total_seats = sum([t.total_seats for t in Transport.objects.all()])
    
    # Hostel stats
    total_hostels = Hostel.objects.count()
    occupied_rooms = sum([h.occupied_rooms for h in Hostel.objects.all()])
    total_rooms = sum([h.total_rooms for h in Hostel.objects.all()])
    
    # Library stats
    total_books = Library.objects.count()
    active_issues = LibraryIssue.objects.filter(status__in=['issued', 'overdue']).count()
    overdue_books = LibraryIssue.objects.filter(status='overdue').count()
    
    # Fee stats
    total_collected = sum([p.amount_paid for p in FeePayment.objects.filter(status='paid')])
    defaulters_count = Student.objects.filter(
        fee_payments__status__in=['pending', 'partial', 'overdue']
    ).distinct().count()
    
    # Scholarship stats
    active_scholarships = Scholarship.objects.filter(is_active=True).count()
    pending_applications = ScholarshipApplication.objects.filter(status='applied').count()
    
    # Grievance stats
    pending_grievances = Grievance.objects.filter(status__in=['submitted', 'in_progress']).count()
    
    context = {
        'page_title': 'Management Dashboard',
        'management': management,
        'total_students': total_students,
        'total_staff': total_staff,
        'total_buses': total_buses,
        'occupied_seats': occupied_seats,
        'total_seats': total_seats,
        'total_hostels': total_hostels,
        'occupied_rooms': occupied_rooms,
        'total_rooms': total_rooms,
        'total_books': total_books,
        'active_issues': active_issues,
        'overdue_books': overdue_books,
        'total_collected': total_collected,
        'defaulters_count': defaulters_count,
        'active_scholarships': active_scholarships,
        'pending_applications': pending_applications,
        'pending_grievances': pending_grievances,
    }
    return render(request, 'management_template/home_content.html', context)


def management_view_profile(request):
    """View/Edit management profile"""
    management = get_object_or_404(Management, admin=request.user)
    
    context = {
        'page_title': 'My Profile',
        'management': management
    }
    return render(request, 'management_template/view_profile.html', context)


# Import all views from hod_views for facilities management
from . import hod_views

# Re-use HOD views for administrative tasks
# Transport Management
manage_transport = hod_views.manage_transport
add_transport = hod_views.add_transport
edit_transport = hod_views.edit_transport
transport_allocations = hod_views.transport_allocations
allocate_transport = hod_views.allocate_transport

# Hostel Management
manage_hostels = hod_views.manage_hostels
add_hostel = hod_views.add_hostel
hostel_allocations = hod_views.hostel_allocations
allocate_hostel = hod_views.allocate_hostel
hostel_visitor_logs = hod_views.hostel_visitor_logs

# Library Management
manage_library = hod_views.manage_library
add_library_book = hod_views.add_library_book
edit_library_book = hod_views.edit_library_book
library_issues = hod_views.library_issues
issue_library_book = hod_views.issue_library_book
return_library_book = hod_views.return_library_book

# Fee Management
manage_fee_structure = hod_views.manage_fee_structure
add_fee_structure = hod_views.add_fee_structure
edit_fee_structure = hod_views.edit_fee_structure
view_fee_payments = hod_views.view_fee_payments
record_fee_payment = hod_views.record_fee_payment
fee_defaulters = hod_views.fee_defaulters

# Scholarship Management
manage_scholarships = hod_views.manage_scholarships
add_scholarship = hod_views.add_scholarship
scholarship_applications = hod_views.scholarship_applications
review_scholarship_application = hod_views.review_scholarship_application
disburse_scholarship = hod_views.disburse_scholarship

# Grievance Management  
view_grievances = hod_views.view_grievances
assign_grievance = hod_views.assign_grievance
resolve_grievance = hod_views.resolve_grievance


