from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from main_app.models import Student, StudyMaterial, FeeStructure, FeePayment
from django.db.models import Sum


def public_roll_verify(request):
    """Public page to verify roll number and view materials/fees"""
    if request.method == 'POST':
        roll_number = request.POST.get('roll_number')
        
        try:
            student = Student.objects.select_related('admin', 'course', 'session').get(
                roll_number=roll_number
            )
            # Store student ID in session
            request.session['public_student_id'] = student.id
            request.session['public_roll_number'] = roll_number
            return redirect('public_student_info')
        except Student.DoesNotExist:
            messages.error(request, 'Invalid roll number. Please check and try again.')
    
    return render(request, 'public/roll_verify.html', {
        'page_title': 'Student Access Portal'
    })


def public_student_info(request):
    """Display student materials and fee structure (public access)"""
    student_id = request.session.get('public_student_id')
    
    if not student_id:
        messages.warning(request, 'Please enter your roll number first.')
        return redirect('public_roll_verify')
    
    try:
        student = Student.objects.select_related('admin', 'course', 'session').get(id=student_id)
        
        # Get study materials for student's course
        materials = StudyMaterial.objects.filter(
            subject__course=student.course
        ).select_related('subject', 'uploaded_by').order_by('-created_at')[:20]
        
        # Get fee structure
        fee_structures = FeeStructure.objects.filter(
            course=student.course,
            session=student.session
        ).order_by('-created_at')
        
        # Get fee payments
        payments = FeePayment.objects.filter(
            student=student
        ).order_by('-payment_date')
        
        # Calculate totals
        total_fees = fee_structures.aggregate(total=Sum('amount'))['total'] or 0
        paid_amount = payments.aggregate(total=Sum('amount'))['total'] or 0
        balance = total_fees - paid_amount
        
        context = {
            'page_title': f'Student Portal - {student.roll_number}',
            'student': student,
            'materials': materials,
            'fee_structures': fee_structures,
            'payments': payments,
            'total_fees': total_fees,
            'paid_amount': paid_amount,
            'balance': balance,
        }
        
        return render(request, 'public/student_info.html', context)
        
    except Student.DoesNotExist:
        messages.error(request, 'Student record not found.')
        return redirect('public_roll_verify')


def clear_public_session(request):
    """Clear public student session"""
    if 'public_student_id' in request.session:
        del request.session['public_student_id']
    if 'public_roll_number' in request.session:
        del request.session['public_roll_number']
    messages.success(request, 'Session cleared successfully.')
    return redirect('public_roll_verify')





