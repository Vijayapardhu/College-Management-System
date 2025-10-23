from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


@login_required(login_url='login')
def payroll_dashboard(request):
    """Payroll dashboard"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Payroll Dashboard'}
    return render(request, 'hod_template/payroll_dashboard.html', context)


@login_required(login_url='login')
def configure_salary_structure(request):
    """Configure salary structure"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Configure Salary Structure'}
    return render(request, 'hod_template/configure_salary_structure.html', context)


@login_required(login_url='login')
def assign_employee_salary(request):
    """Assign employee salary"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Assign Employee Salary'}
    return render(request, 'hod_template/assign_employee_salary.html', context)


@login_required(login_url='login')
def process_payroll(request):
    """Process payroll"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Process Payroll'}
    return render(request, 'hod_template/process_payroll.html', context)


@login_required(login_url='login')
def view_payslips(request):
    """View payslips"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'View Payslips'}
    return render(request, 'hod_template/view_payslips.html', context)


@login_required(login_url='login')
def view_payslip_detail(request, payslip_id):
    """View payslip detail"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Payslip Detail', 'payslip_id': payslip_id}
    return render(request, 'hod_template/view_payslip_detail.html', context)


@login_required(login_url='login')
def tax_declaration_management(request):
    """Tax declaration management"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Tax Declaration Management'}
    return render(request, 'hod_template/tax_declaration_management.html', context)


@login_required(login_url='login')
def verify_tax_document(request, declaration_id):
    """Verify tax document"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Verify Tax Document', 'declaration_id': declaration_id}
    return render(request, 'hod_template/verify_tax_document.html', context)


@login_required(login_url='login')
def leave_balance_management(request):
    """Leave balance management"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Leave Balance Management'}
    return render(request, 'hod_template/leave_balance_management.html', context)


@login_required(login_url='login')
def attendance_register(request):
    """Attendance register"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Attendance Register'}
    return render(request, 'hod_template/attendance_register.html', context)


@login_required(login_url='login')
def bonus_management(request):
    """Bonus management"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Bonus Management'}
    return render(request, 'hod_template/bonus_management.html', context)


@login_required(login_url='login')
def loan_management(request):
    """Loan management"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Loan Management'}
    return render(request, 'hod_template/loan_management.html', context)


@login_required(login_url='login')
def approve_loan(request, loan_id):
    """Approve loan"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Approve Loan', 'loan_id': loan_id}
    return render(request, 'hod_template/approve_loan.html', context)


@login_required(login_url='login')
def payroll_analytics(request):
    """Payroll analytics"""
    if request.user.user_type != '1':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Payroll Analytics'}
    return render(request, 'hod_template/payroll_analytics.html', context)


@login_required(login_url='login')
def employee_self_service(request):
    """Employee self service"""
    if request.user.user_type != '2':
        messages.error(request, 'Access denied')
        return redirect('login')
    
    context = {'page_title': 'Employee Self Service'}
    return render(request, 'staff_template/employee_self_service.html', context)


def get_employee_salary_ajax(request, employee_id):
    """AJAX endpoint to get employee salary"""
    if request.method == 'GET':
        # Add logic to fetch employee salary
        salary_data = {}  # Replace with actual data
        return JsonResponse({'salary': salary_data})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def calculate_salary_ajax(request):
    """AJAX endpoint to calculate salary"""
    if request.method == 'POST':
        # Add logic to calculate salary
        calculated_salary = 0  # Replace with actual calculation
        return JsonResponse({'calculated_salary': calculated_salary})
    return JsonResponse({'error': 'Invalid request'}, status=400)


def payroll_summary_ajax(request):
    """AJAX endpoint for payroll summary"""
    if request.method == 'GET':
        # Add logic to get payroll summary
        summary = {}  # Replace with actual data
        return JsonResponse({'summary': summary})
    return JsonResponse({'error': 'Invalid request'}, status=400)
