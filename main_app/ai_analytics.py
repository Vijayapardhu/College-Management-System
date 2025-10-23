"""
AI-Powered Analytics for Student Performance Prediction
Uses simple machine learning to predict at-risk students
"""

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')


class StudentPerformancePredictor:
    """Predict student performance and identify at-risk students"""
    
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, student_data):
        """
        Prepare feature vector from student data
        Features: attendance %, avg marks, total absences, subjects failed, participation score
        """
        features = []
        for data in student_data:
            feature_vector = [
                data.get('attendance_percentage', 0),
                data.get('average_marks', 0),
                data.get('total_absences', 0),
                data.get('subjects_failed', 0),
                data.get('assignment_completion', 0),
            ]
            features.append(feature_vector)
        
        return np.array(features)
    
    def train_model(self, student_data, labels):
        """
        Train the model on historical student data
        Labels: 0 = At Risk, 1 = Safe
        """
        if len(student_data) < 10:
            # Not enough data to train
            return False
        
        features = self.prepare_features(student_data)
        
        # Scale features
        features_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(features_scaled, labels)
        self.is_trained = True
        
        return True
    
    def predict_risk(self, student_data):
        """
        Predict if student is at risk
        Returns: probability of being at risk (0 to 1)
        """
        if not self.is_trained:
            # Use simple rule-based prediction if model not trained
            return self._rule_based_prediction(student_data)
        
        features = self.prepare_features([student_data])
        features_scaled = self.scaler.transform(features)
        
        # Get probability of class 0 (at risk)
        risk_probability = self.model.predict_proba(features_scaled)[0][0]
        
        return risk_probability
    
    def _rule_based_prediction(self, student_data):
        """
        Simple rule-based prediction when ML model not available
        """
        attendance = student_data.get('attendance_percentage', 100)
        avg_marks = student_data.get('average_marks', 100)
        
        # Calculate risk score
        risk_score = 0
        
        # Attendance factor (weight: 40%)
        if attendance < 50:
            risk_score += 40
        elif attendance < 65:
            risk_score += 30
        elif attendance < 75:
            risk_score += 20
        elif attendance < 85:
            risk_score += 10
        
        # Marks factor (weight: 40%)
        if avg_marks < 35:
            risk_score += 40
        elif avg_marks < 45:
            risk_score += 30
        elif avg_marks < 55:
            risk_score += 20
        elif avg_marks < 65:
            risk_score += 10
        
        # Subjects failed factor (weight: 20%)
        subjects_failed = student_data.get('subjects_failed', 0)
        if subjects_failed >= 3:
            risk_score += 20
        elif subjects_failed >= 2:
            risk_score += 15
        elif subjects_failed >= 1:
            risk_score += 10
        
        return min(risk_score / 100, 1.0)
    
    def get_risk_level(self, risk_probability):
        """
        Convert probability to risk level
        """
        if risk_probability >= 0.7:
            return 'CRITICAL', 'danger'
        elif risk_probability >= 0.5:
            return 'HIGH', 'warning'
        elif risk_probability >= 0.3:
            return 'MODERATE', 'info'
        else:
            return 'LOW', 'success'
    
    def suggest_interventions(self, student_data, risk_probability):
        """
        Suggest remedial actions based on risk factors
        """
        interventions = []
        
        attendance = student_data.get('attendance_percentage', 100)
        avg_marks = student_data.get('average_marks', 100)
        subjects_failed = student_data.get('subjects_failed', 0)
        
        if attendance < 75:
            interventions.append({
                'type': 'Attendance',
                'severity': 'high',
                'action': f'Immediate attention required - Attendance is only {attendance:.1f}%',
                'recommendation': 'Contact parents, schedule counseling session, monitor daily attendance'
            })
        
        if avg_marks < 40:
            interventions.append({
                'type': 'Academic Performance',
                'severity': 'high',
                'action': f'Poor performance - Average marks: {avg_marks:.1f}%',
                'recommendation': 'Arrange extra classes, provide study materials, peer tutoring'
            })
        elif avg_marks < 55:
            interventions.append({
                'type': 'Academic Performance',
                'severity': 'medium',
                'action': f'Below average performance - {avg_marks:.1f}%',
                'recommendation': 'Regular monitoring, doubt-clearing sessions, practice tests'
            })
        
        if subjects_failed > 0:
            interventions.append({
                'type': 'Subject Failures',
                'severity': 'high',
                'action': f'Failed in {subjects_failed} subject(s)',
                'recommendation': 'Subject-specific remedial classes, mentorship program'
            })
        
        assignment_completion = student_data.get('assignment_completion', 100)
        if assignment_completion < 60:
            interventions.append({
                'type': 'Engagement',
                'severity': 'medium',
                'action': f'Low assignment completion - {assignment_completion:.0f}%',
                'recommendation': 'Follow-up on pending assignments, time management counseling'
            })
        
        if not interventions:
            interventions.append({
                'type': 'General',
                'severity': 'low',
                'action': 'Student is performing well',
                'recommendation': 'Continue monitoring and encourage participation'
            })
        
        return interventions


def get_student_performance_data(student):
    """
    Extract performance data for a student from database
    """
    from main_app.models import AttendanceReport, StudentResult, Assignment, AssignmentSubmission
    from django.db.models import Avg, Count, Q
    
    # Calculate attendance percentage
    total_attendance = AttendanceReport.objects.filter(student=student).count()
    present_count = AttendanceReport.objects.filter(student=student, status=True).count()
    attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 100
    
    # Calculate average marks
    results = StudentResult.objects.filter(student=student)
    total_marks = 0
    count = 0
    subjects_failed = 0
    
    for result in results:
        marks = result.test + result.exam
        total_marks += marks
        count += 1
        if marks < 40:
            subjects_failed += 1
    
    average_marks = (total_marks / count) if count > 0 else 0
    
    # Calculate assignment completion
    total_assignments = Assignment.objects.filter(
        subject__course=student.course
    ).count()
    
    completed_assignments = AssignmentSubmission.objects.filter(
        student=student,
        status='graded'
    ).count()
    
    assignment_completion = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 100
    
    return {
        'attendance_percentage': attendance_percentage,
        'average_marks': average_marks,
        'total_absences': total_attendance - present_count,
        'subjects_failed': subjects_failed,
        'assignment_completion': assignment_completion
    }


def analyze_all_students(course=None, session=None):
    """
    Analyze all students and identify at-risk ones
    """
    from main_app.models import Student
    
    predictor = StudentPerformancePredictor()
    
    # Get students
    students = Student.objects.all()
    if course:
        students = students.filter(course=course)
    if session:
        students = students.filter(session=session)
    
    at_risk_students = []
    
    for student in students:
        try:
            student_data = get_student_performance_data(student)
            risk_probability = predictor.predict_risk(student_data)
            risk_level, risk_color = predictor.get_risk_level(risk_probability)
            
            if risk_probability >= 0.3:  # Only include moderate or higher risk
                interventions = predictor.suggest_interventions(student_data, risk_probability)
                
                at_risk_students.append({
                    'student': student,
                    'risk_probability': risk_probability * 100,
                    'risk_level': risk_level,
                    'risk_color': risk_color,
                    'attendance_percentage': student_data['attendance_percentage'],
                    'average_marks': student_data['average_marks'],
                    'subjects_failed': student_data['subjects_failed'],
                    'interventions': interventions
                })
        except Exception as e:
            # Skip students with incomplete data
            continue
    
    # Sort by risk probability (highest first)
    at_risk_students.sort(key=lambda x: x['risk_probability'], reverse=True)
    
    return at_risk_students


def generate_weekly_report():
    """
    Generate weekly at-risk student report for email digest
    """
    from main_app.models import Course
    
    report = {
        'total_at_risk': 0,
        'critical_count': 0,
        'high_count': 0,
        'moderate_count': 0,
        'course_wise': {}
    }
    
    courses = Course.objects.all()
    
    for course in courses:
        at_risk = analyze_all_students(course=course)
        
        if at_risk:
            critical = len([s for s in at_risk if s['risk_level'] == 'CRITICAL'])
            high = len([s for s in at_risk if s['risk_level'] == 'HIGH'])
            moderate = len([s for s in at_risk if s['risk_level'] == 'MODERATE'])
            
            report['course_wise'][course.name] = {
                'total': len(at_risk),
                'critical': critical,
                'high': high,
                'moderate': moderate,
                'students': at_risk[:5]  # Top 5 at-risk students
            }
            
            report['total_at_risk'] += len(at_risk)
            report['critical_count'] += critical
            report['high_count'] += high
            report['moderate_count'] += moderate
    
    return report









