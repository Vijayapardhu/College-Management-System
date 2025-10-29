from typing import Optional, Iterable

from django.db.models import Prefetch, QuerySet

from main_app.models import (
    Student,
    Subject,
    Timetable,
    Curriculum,
    ClassGroup,
)


def get_enrolled_subjects_for_student(student_id: int) -> QuerySet[Subject]:
    """
    Return a queryset of Subjects a student is enrolled in, optimized with select_related.
    """
    return (
        Subject.objects.select_related('department', 'staff__admin', 'curriculum')
        .filter(enrolled_students__id=student_id)
        .order_by('semester', 'name')
    )


def get_class_timetable(
    class_group_id: int,
    weekday: Optional[str] = None,
) -> QuerySet[Timetable]:
    """
    Return timetable entries for a class group. Optionally filter by weekday.
    """
    qs = (
        Timetable.objects.select_related(
            'class_group', 'department', 'subject', 'staff__admin', 'session', 'course'
        )
        .filter(class_group_id=class_group_id)
        .order_by('weekday', 'period', 'start_time')
    )
    if weekday:
        qs = qs.filter(weekday=weekday)
    return qs


def get_curriculum_subjects(
    curriculum_id: int,
    department_id: Optional[int] = None,
    semester: Optional[int] = None,
) -> QuerySet[Subject]:
    """
    Return subjects under a curriculum, optionally filtered by department and semester.
    """
    qs = Subject.objects.select_related('department', 'staff__admin', 'curriculum').filter(
        curriculum_id=curriculum_id
    )
    if department_id:
        qs = qs.filter(department_id=department_id)
    if semester:
        qs = qs.filter(semester=semester)
    return qs.order_by('semester', 'name')


