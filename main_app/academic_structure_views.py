"""
Views for managing Academic Structure (Years, Sections, Class Groups)
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .models import AcademicYear, Section, ClassGroup, Course, Session, Department
from django import forms


# ============================================================================
# FORMS
# ============================================================================

class AcademicYearForm(forms.ModelForm):
    class Meta:
        model = AcademicYear
        fields = ['year_number', 'year_name']
        widgets = {
            'year_number': forms.Select(choices=[
                (1, '1st Year'),
                (2, '2nd Year'),
                (3, '3rd Year'),
                (4, '4th Year'),
                (5, '5th Year'),
            ], attrs={'class': 'form-control'}),
            'year_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., First Year'})
        }


class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'capacity']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A, B, C'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'value': 60, 'min': 1})
        }


class ClassGroupForm(forms.ModelForm):
    class Meta:
        model = ClassGroup
        fields = ['department', 'course', 'academic_year', 'section', 'session', 'class_teacher', 'is_active']
        widgets = {
            'department': forms.Select(attrs={'class': 'form-control'}),
            'course': forms.Select(attrs={'class': 'form-control'}),
            'academic_year': forms.Select(attrs={'class': 'form-control'}),
            'section': forms.Select(attrs={'class': 'form-control'}),
            'session': forms.Select(attrs={'class': 'form-control'}),
            'class_teacher': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


# ============================================================================
# ACADEMIC YEAR VIEWS
# ============================================================================

@login_required
def manage_academic_years(request):
    """List all academic years"""
    years = AcademicYear.objects.all()
    context = {
        'years': years,
        'page_title': 'Manage Academic Years'
    }
    return render(request, 'hod_template/manage_academic_years.html', context)


@login_required
def add_academic_year(request):
    """Add new academic year"""
    form = AcademicYearForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Academic Year Added Successfully")
                return redirect('manage_academic_years')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please fill the form correctly")
    
    context = {'form': form, 'page_title': 'Add Academic Year'}
    return render(request, 'forms/academic_year_form.html', context)


@login_required
def edit_academic_year(request, year_id):
    """Edit academic year"""
    year = get_object_or_404(AcademicYear, id=year_id)
    form = AcademicYearForm(request.POST or None, instance=year)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Academic Year Updated Successfully")
                return redirect('manage_academic_years')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    
    context = {'form': form, 'page_title': 'Edit Academic Year', 'year_id': year_id}
    return render(request, 'forms/academic_year_form.html', context)


@login_required
def delete_academic_year(request, year_id):
    """Delete academic year"""
    year = get_object_or_404(AcademicYear, id=year_id)
    try:
        year.delete()
        messages.success(request, "Academic Year Deleted Successfully")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('manage_academic_years')


# ============================================================================
# SECTION VIEWS
# ============================================================================

@login_required
def manage_sections(request):
    """List all sections"""
    sections = Section.objects.all()
    context = {
        'sections': sections,
        'page_title': 'Manage Sections'
    }
    return render(request, 'hod_template/manage_sections.html', context)


@login_required
def add_section(request):
    """Add new section"""
    form = SectionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Section Added Successfully")
                return redirect('manage_sections')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please fill the form correctly")
    
    context = {'form': form, 'page_title': 'Add Section'}
    return render(request, 'forms/section_form.html', context)


@login_required
def edit_section(request, section_id):
    """Edit section"""
    section = get_object_or_404(Section, id=section_id)
    form = SectionForm(request.POST or None, instance=section)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Section Updated Successfully")
                return redirect('manage_sections')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    
    context = {'form': form, 'page_title': 'Edit Section', 'section_id': section_id}
    return render(request, 'forms/section_form.html', context)


@login_required
def delete_section(request, section_id):
    """Delete section"""
    section = get_object_or_404(Section, id=section_id)
    try:
        section.delete()
        messages.success(request, "Section Deleted Successfully")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('manage_sections')


# ============================================================================
# CLASS GROUP VIEWS
# ============================================================================

@login_required
def manage_class_groups(request):
    """List all class groups"""
    class_groups = ClassGroup.objects.select_related(
        'department', 'course', 'academic_year', 'section', 'session', 'class_teacher'
    ).all()
    context = {
        'class_groups': class_groups,
        'page_title': 'Manage Class Groups'
    }
    return render(request, 'hod_template/manage_class_groups.html', context)


@login_required
def add_class_group(request):
    """Add new class group"""
    form = ClassGroupForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Class Group Created Successfully")
                return redirect('manage_class_groups')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
        else:
            messages.error(request, "Please fill the form correctly")
    
    context = {'form': form, 'page_title': 'Add Class Group'}
    return render(request, 'forms/class_group_form.html', context)


@login_required
def edit_class_group(request, group_id):
    """Edit class group"""
    group = get_object_or_404(ClassGroup, id=group_id)
    form = ClassGroupForm(request.POST or None, instance=group)
    
    if request.method == 'POST':
        if form.is_valid():
            try:
                form.save()
                messages.success(request, "Class Group Updated Successfully")
                return redirect('manage_class_groups')
            except Exception as e:
                messages.error(request, f"Error: {str(e)}")
    
    context = {'form': form, 'page_title': 'Edit Class Group', 'group_id': group_id}
    return render(request, 'forms/class_group_form.html', context)


@login_required
def delete_class_group(request, group_id):
    """Delete class group"""
    group = get_object_or_404(ClassGroup, id=group_id)
    try:
        group.delete()
        messages.success(request, "Class Group Deleted Successfully")
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
    return redirect('manage_class_groups')

