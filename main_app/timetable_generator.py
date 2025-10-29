"""
Smart Timetable Auto-Generator with Conflict Detection
Simple constraint-based solver for timetable generation
"""

from datetime import time
from collections import defaultdict


class TimetableGenerator:
    """Automatic timetable generation with conflict detection"""
    
    WEEKDAYS = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
    PERIODS = list(range(1, 9))  # 8 periods per day
    
    # Standard time slots
    PERIOD_TIMES = {
        1: {'start': time(9, 0), 'end': time(9, 50)},
        2: {'start': time(10, 0), 'end': time(10, 50)},
        3: {'start': time(11, 0), 'end': time(11, 50)},
        4: {'start': time(12, 0), 'end': time(12, 50)},
        5: {'start': time(14, 0), 'end': time(14, 50)},   # After lunch
        6: {'start': time(15, 0), 'end': time(15, 50)},
        7: {'start': time(16, 0), 'end': time(16, 50)},
        8: {'start': time(17, 0), 'end': time(17, 50)},
    }
    
    def __init__(self, session, course, semester):
        self.session = session
        self.course = course
        self.semester = semester
        self.schedule = defaultdict(dict)  # {weekday: {period: slot}}
        self.conflicts = []
    
    def generate(self, subjects_config):
        """
        Generate timetable for given subjects
        
        subjects_config = [
            {'subject': subject_obj, 'staff': staff_obj, 'lectures_per_week': 4, 'is_lab': False},
            ...
        ]
        """
        # Clear existing schedule
        self.schedule = defaultdict(dict)
        self.conflicts = []
        
        # Sort by lectures per week (descending) - assign high-frequency subjects first
        subjects_config.sort(key=lambda x: x['lectures_per_week'], reverse=True)
        
        for config in subjects_config:
            subject = config['subject']
            staff = config['staff']
            lectures_needed = config['lectures_per_week']
            is_lab = config.get('is_lab', False)
            
            lectures_assigned = 0
            
            for weekday in self.WEEKDAYS:
                if lectures_assigned >= lectures_needed:
                    break
                
                for period in self.PERIODS:
                    if lectures_assigned >= lectures_needed:
                        break
                    
                    # For labs, need consecutive periods
                    if is_lab:
                        if self._can_assign_lab(weekday, period):
                            # Assign 2 consecutive periods
                            self._assign_slot(weekday, period, subject, staff, 'lab')
                            self._assign_slot(weekday, period + 1, subject, staff, 'lab')
                            lectures_assigned += 2
                    else:
                        if self._can_assign_lecture(weekday, period, subject, staff):
                            self._assign_slot(weekday, period, subject, staff, 'lecture')
                            lectures_assigned += 1
            
            # Check if all lectures assigned
            if lectures_assigned < lectures_needed:
                self.conflicts.append({
                    'type': 'insufficient_slots',
                    'subject': subject.name,
                    'required': lectures_needed,
                    'assigned': lectures_assigned,
                    'message': f"Could not assign all {lectures_needed} lectures for {subject.name}, only {lectures_assigned} slots available"
                })
        
        return self.schedule, self.conflicts
    
    def _can_assign_lecture(self, weekday, period, subject, staff):
        """Check if slot can be assigned"""
        # Check if slot is empty
        if weekday in self.schedule and period in self.schedule[weekday]:
            return False
        
        # Check faculty conflict (same faculty teaching different class)
        for day, periods in self.schedule.items():
            for p, slot in periods.items():
                if day == weekday and p == period and slot['staff'].id == staff.id:
                    return False
        
        # Avoid consecutive periods of same subject on same day
        if weekday in self.schedule:
            if (period - 1) in self.schedule[weekday]:
                if self.schedule[weekday][period - 1]['subject'].id == subject.id:
                    return False
            if (period + 1) in self.schedule[weekday]:
                if self.schedule[weekday][period + 1]['subject'].id == subject.id:
                    return False
        
        return True
    
    def _can_assign_lab(self, weekday, period):
        """Check if 2 consecutive periods are available for lab"""
        if period >= 8:  # Not enough periods left
            return False
        
        # Check both periods are empty
        if weekday in self.schedule:
            if period in self.schedule[weekday] or (period + 1) in self.schedule[weekday]:
                return False
        
        return True
    
    def _assign_slot(self, weekday, period, subject, staff, slot_type):
        """Assign a slot in timetable"""
        self.schedule[weekday][period] = {
            'subject': subject,
            'staff': staff,
            'type': slot_type,
            'room': self._suggest_room(subject, slot_type),
            'start_time': self.PERIOD_TIMES[period]['start'],
            'end_time': self.PERIOD_TIMES[period]['end']
        }
    
    def _suggest_room(self, subject, slot_type):
        """Suggest appropriate room for subject"""
        if slot_type == 'lab':
            return f"Lab-{subject.id % 10 + 1}"  # Simple room allocation
        else:
            return f"Room-{subject.id % 20 + 1}"
    
    def detect_conflicts(self):
        """Detect all conflicts in current timetable"""
        conflicts = []
        
        # Faculty conflict check
        for weekday, periods in self.schedule.items():
            for period, slot in periods.items():
                # Check if same faculty is teaching in multiple places at same time
                count = sum(
                    1 for day, periods_dict in self.schedule.items()
                    if day == weekday
                    for p, s in periods_dict.items()
                    if p == period and s['staff'].id == slot['staff'].id
                )
                
                if count > 1:
                    conflicts.append({
                        'type': 'faculty_conflict',
                        'weekday': weekday,
                        'period': period,
                        'staff': slot['staff'].admin.first_name + ' ' + slot['staff'].admin.last_name,
                        'message': f"Faculty {slot['staff'].admin.first_name} has multiple classes on {weekday.title()} period {period}"
                    })
        
        self.conflicts.extend(conflicts)
        return conflicts
    
    def get_faculty_load(self, staff):
        """Calculate teaching load for a faculty"""
        hours = 0
        for weekday, periods in self.schedule.items():
            for period, slot in periods.items():
                if slot['staff'].id == staff.id:
                    hours += 1
        return hours
    
    def optimize_schedule(self):
        """
        Optimize timetable:
        - Distribute lectures evenly across week
        - Avoid consecutive same subjects
        - Balance faculty workload
        """
        # Simple optimization: try to spread subjects across days
        # This is a placeholder for more complex optimization
        pass
    
    def save_to_database(self):
        """Save generated timetable to database"""
        from main_app.models import Timetable
        
        created_count = 0
        
        for weekday, periods in self.schedule.items():
            for period, slot in periods.items():
                try:
                    Timetable.objects.create(
                        session=self.session,
                        course=self.course,
                        semester=self.semester,
                        weekday=weekday,
                        period=period,
                        subject=slot['subject'],
                        staff=slot['staff'],
                        room_number=slot['room'],
                        start_time=slot['start_time'],
                        end_time=slot['end_time'],
                        class_type=slot['type']
                    )
                    created_count += 1
                except Exception as e:
                    self.conflicts.append({
                        'type': 'database_error',
                        'message': f"Failed to save {slot['subject'].name} on {weekday} period {period}: {str(e)}"
                    })
        
        return created_count
    
    def export_to_dict(self):
        """Export schedule as dictionary for display"""
        export_data = {}
        
        for weekday in self.WEEKDAYS:
            export_data[weekday] = {}
            for period in self.PERIODS:
                if weekday in self.schedule and period in self.schedule[weekday]:
                    slot = self.schedule[weekday][period]
                    export_data[weekday][period] = {
                        'subject_name': slot['subject'].name,
                        'subject_code': slot['subject'].code if hasattr(slot['subject'], 'code') else '',
                        'faculty_name': f"{slot['staff'].admin.first_name} {slot['staff'].admin.last_name}",
                        'room': slot['room'],
                        'type': slot['type'],
                        'start_time': slot['start_time'].strftime('%H:%M'),
                        'end_time': slot['end_time'].strftime('%H:%M')
                    }
                else:
                    export_data[weekday][period] = None
        
        return export_data


def validate_timetable_slot(session, course, semester, weekday, period, staff, exclude_id=None):
    """
    Validate if a timetable slot can be assigned
    Returns: (is_valid, conflicts_list)
    """
    from main_app.models import Timetable
    
    conflicts = []
    
    # Check for existing slot
    query = Timetable.objects.filter(
        session=session,
        course=course,
        semester=semester,
        weekday=weekday,
        period=period
    )
    
    if exclude_id:
        query = query.exclude(id=exclude_id)
    
    if query.exists():
        conflicts.append({
            'type': 'slot_occupied',
            'message': f"Slot already occupied on {weekday} period {period}"
        })
    
    # Check faculty conflict
    faculty_conflicts = Timetable.objects.filter(
        session=session,
        weekday=weekday,
        period=period,
        staff=staff
    )
    
    if exclude_id:
        faculty_conflicts = faculty_conflicts.exclude(id=exclude_id)
    
    if faculty_conflicts.exists():
        conflict_slot = faculty_conflicts.first()
        conflicts.append({
            'type': 'faculty_conflict',
            'message': f"Faculty already teaching {conflict_slot.subject.name} to {conflict_slot.course.name} at this time"
        })
    
    is_valid = len(conflicts) == 0
    return is_valid, conflicts


















