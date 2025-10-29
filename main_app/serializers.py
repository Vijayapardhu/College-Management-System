from rest_framework import serializers

from .models import Subject, Timetable, Curriculum, Student


class SubjectSerializer(serializers.ModelSerializer):
    faculty_name = serializers.SerializerMethodField()
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Subject
        fields = (
            'id', 'name', 'semester', 'department', 'department_name',
            'staff', 'faculty_name', 'curriculum', 'created_at', 'updated_at'
        )

    def get_faculty_name(self, obj):
        if obj.staff and obj.staff.admin:
            return f"{obj.staff.admin.first_name} {obj.staff.admin.last_name}".strip()
        return None


class TimetableSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    staff_name = serializers.SerializerMethodField()
    class_group_id = serializers.IntegerField(source='class_group.id', read_only=True)

    class Meta:
        model = Timetable
        fields = (
            'id', 'session', 'course', 'semester', 'department', 'class_group', 'class_group_id',
            'weekday', 'period', 'start_time', 'end_time', 'room_number',
            'subject', 'subject_name', 'staff', 'staff_name', 'is_lab'
        )

    def get_staff_name(self, obj):
        if obj.staff and obj.staff.admin:
            return f"{obj.staff.admin.first_name} {obj.staff.admin.last_name}".strip()
        return None


class StudentEnrolledSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(source='subject', read_only=True)

    class Meta:
        model = Student.subjects.through  # Enrollment model
        fields = ('id', 'subject', 'enrolled_at')


class CurriculumSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ('id', 'name', 'semester', 'department', 'staff')


