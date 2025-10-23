"""
Google Gemini AI Service for College Management System
Provides intelligent AI-powered features using Google's Gemini API
"""

import google.generativeai as genai
from django.conf import settings
import os
import json
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_API_KEY_HERE')
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini Model
model = genai.GenerativeModel('gemini-pro')


class GeminiAIService:
    """
    Main service class for Gemini AI integration
    """
    
    @staticmethod
    def analyze_student_performance(student_data: Dict) -> Dict:
        """
        Analyze student academic performance using AI
        
        Args:
            student_data: Dictionary containing student academic information
            
        Returns:
            Dict with AI analysis and recommendations
        """
        try:
            prompt = f"""
            Analyze this student's academic performance and provide detailed insights:
            
            Student Information:
            - Name: {student_data.get('name', 'Unknown')}
            - Roll Number: {student_data.get('roll_number', 'N/A')}
            - Course: {student_data.get('course', 'N/A')}
            - Current CGPA: {student_data.get('cgpa', 'N/A')}
            - Attendance Percentage: {student_data.get('attendance', 'N/A')}%
            - Subjects: {student_data.get('subjects', [])}
            - Recent Marks: {student_data.get('marks', [])}
            - Assignments Completed: {student_data.get('assignments_completed', 0)}/{student_data.get('total_assignments', 0)}
            
            Please provide:
            1. Overall Performance Analysis (2-3 sentences)
            2. Strengths (bullet points)
            3. Areas for Improvement (bullet points)
            4. Specific Recommendations (bullet points)
            5. Risk Assessment (LOW/MEDIUM/HIGH) with explanation
            6. Predicted Final Grade Range
            
            Format the response as JSON with keys: analysis, strengths, improvements, recommendations, risk_level, risk_explanation, predicted_grade
            """
            
            response = model.generate_content(prompt)
            
            # Parse response
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # If response is not JSON, structure it
                result = {
                    'analysis': response.text,
                    'strengths': [],
                    'improvements': [],
                    'recommendations': [],
                    'risk_level': 'MEDIUM',
                    'risk_explanation': 'Unable to assess automatically',
                    'predicted_grade': 'N/A'
                }
            
            return {
                'success': True,
                'data': result
            }
            
        except Exception as e:
            logger.error(f"Gemini AI performance analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_study_content(subject: str, topic: str, difficulty: str = 'intermediate') -> Dict:
        """
        Generate educational content for a subject/topic using AI
        
        Args:
            subject: Subject name
            topic: Specific topic to generate content for
            difficulty: beginner, intermediate, or advanced
            
        Returns:
            Dict with generated content
        """
        try:
            prompt = f"""
            Create comprehensive study material for:
            Subject: {subject}
            Topic: {topic}
            Difficulty Level: {difficulty}
            
            Please provide:
            1. Brief Introduction (2-3 sentences)
            2. Key Concepts (5-7 bullet points)
            3. Detailed Explanation (3-4 paragraphs)
            4. Real-world Applications (2-3 examples)
            5. Practice Questions (5 questions with difficulty levels)
            6. Important Formulas/Terms (if applicable)
            7. Study Tips (3-4 tips)
            8. Additional Resources (suggested topics to explore next)
            
            Format as structured text suitable for students.
            """
            
            response = model.generate_content(prompt)
            
            return {
                'success': True,
                'content': response.text,
                'subject': subject,
                'topic': topic,
                'difficulty': difficulty
            }
            
        except Exception as e:
            logger.error(f"Gemini AI content generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def chatbot_response(user_message: str, context: Optional[Dict] = None) -> str:
        """
        Generate intelligent chatbot responses for student queries
        
        Args:
            user_message: User's message/question
            context: Optional context (user role, previous messages, etc.)
            
        Returns:
            AI-generated response
        """
        try:
            context_info = ""
            if context:
                context_info = f"\nContext: {json.dumps(context)}"
            
            prompt = f"""
            You are an intelligent educational assistant for a College Management System.
            Your role is to help students, faculty, and staff with queries about:
            - Academic information (courses, schedules, exams)
            - Administrative procedures (applications, certificates)
            - General college guidance
            {context_info}
            
            Student/User Question: {user_message}
            
            Provide a helpful, friendly, and informative response (2-4 sentences).
            If you don't have specific information, guide them to the appropriate department or resource.
            """
            
            response = model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini AI chatbot error: {str(e)}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later or contact the administration for assistance."
    
    @staticmethod
    def compose_email(purpose: str, recipient_type: str, context: Dict) -> Dict:
        """
        Generate professional email content using AI
        
        Args:
            purpose: Email purpose (notification, reminder, announcement, etc.)
            recipient_type: student, faculty, parent, etc.
            context: Context data for the email
            
        Returns:
            Dict with subject and body
        """
        try:
            prompt = f"""
            Compose a professional email for a college management system:
            
            Purpose: {purpose}
            Recipient Type: {recipient_type}
            Context: {json.dumps(context)}
            
            Please provide:
            1. Subject line (concise, professional)
            2. Email body (formal, clear, with proper greeting and closing)
            
            Format as JSON with keys: subject, body
            """
            
            response = model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                # Fallback parsing
                lines = response.text.split('\n')
                result = {
                    'subject': lines[0] if lines else 'Notification from College',
                    'body': '\n'.join(lines[1:]) if len(lines) > 1 else response.text
                }
            
            return {
                'success': True,
                'email': result
            }
            
        except Exception as e:
            logger.error(f"Gemini AI email composition error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def generate_exam_questions(subject: str, topic: str, num_questions: int = 10, difficulty: str = 'mixed') -> Dict:
        """
        Generate exam questions using AI
        
        Args:
            subject: Subject name
            topic: Topic for questions
            num_questions: Number of questions to generate
            difficulty: easy, medium, hard, or mixed
            
        Returns:
            Dict with generated questions
        """
        try:
            prompt = f"""
            Generate {num_questions} exam questions for:
            Subject: {subject}
            Topic: {topic}
            Difficulty: {difficulty}
            
            For each question, provide:
            1. Question text
            2. Question type (MCQ, Short Answer, Long Answer)
            3. If MCQ: 4 options (A, B, C, D) and correct answer
            4. Marks allocation
            5. Difficulty level (Easy/Medium/Hard)
            6. Expected answer/Solution outline
            
            Format as JSON array with objects containing: question, type, options, correct_answer, marks, difficulty, solution
            """
            
            response = model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                result = {
                    'questions': [],
                    'raw_response': response.text
                }
            
            return {
                'success': True,
                'questions': result
            }
            
        except Exception as e:
            logger.error(f"Gemini AI question generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def analyze_feedback(feedback_list: List[str], category: str = 'general') -> Dict:
        """
        Analyze student/faculty feedback using AI
        
        Args:
            feedback_list: List of feedback texts
            category: Category of feedback
            
        Returns:
            Dict with sentiment analysis and insights
        """
        try:
            feedback_text = '\n'.join([f"- {fb}" for fb in feedback_list])
            
            prompt = f"""
            Analyze the following feedback from a college management system:
            Category: {category}
            
            Feedback:
            {feedback_text}
            
            Provide:
            1. Overall Sentiment (Positive/Neutral/Negative with percentage)
            2. Key Themes (3-5 main themes identified)
            3. Common Issues (bullet points)
            4. Positive Highlights (bullet points)
            5. Actionable Recommendations (3-5 specific recommendations)
            6. Priority Level (HIGH/MEDIUM/LOW)
            
            Format as JSON with keys: sentiment, sentiment_score, themes, issues, highlights, recommendations, priority
            """
            
            response = model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                result = {
                    'sentiment': 'Neutral',
                    'sentiment_score': 50,
                    'analysis': response.text
                }
            
            return {
                'success': True,
                'analysis': result
            }
            
        except Exception as e:
            logger.error(f"Gemini AI feedback analysis error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def summarize_document(document_text: str, max_length: int = 200) -> Dict:
        """
        Summarize long documents or content
        
        Args:
            document_text: Full text to summarize
            max_length: Maximum words in summary
            
        Returns:
            Dict with summary
        """
        try:
            prompt = f"""
            Provide a concise summary of the following text in approximately {max_length} words:
            
            {document_text}
            
            Focus on key points and main ideas.
            """
            
            response = model.generate_content(prompt)
            
            return {
                'success': True,
                'summary': response.text,
                'original_length': len(document_text.split()),
                'summary_length': len(response.text.split())
            }
            
        except Exception as e:
            logger.error(f"Gemini AI summarization error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def career_counseling(student_profile: Dict) -> Dict:
        """
        Provide AI-powered career counseling recommendations
        
        Args:
            student_profile: Student's academic and interest data
            
        Returns:
            Dict with career recommendations
        """
        try:
            prompt = f"""
            Provide career counseling based on this student profile:
            
            Academic Performance:
            - Course: {student_profile.get('course', 'N/A')}
            - CGPA: {student_profile.get('cgpa', 'N/A')}
            - Strong Subjects: {student_profile.get('strong_subjects', [])}
            - Weak Subjects: {student_profile.get('weak_subjects', [])}
            - Skills: {student_profile.get('skills', [])}
            - Interests: {student_profile.get('interests', [])}
            - Projects: {student_profile.get('projects', [])}
            
            Provide:
            1. Top 5 Career Paths (with brief descriptions)
            2. Recommended Skills to Develop (5-7 skills)
            3. Industry Certifications to Consider
            4. Higher Education Options
            5. Internship/Job Search Tips
            6. Next Steps (actionable 3-month plan)
            
            Format as structured JSON.
            """
            
            response = model.generate_content(prompt)
            
            try:
                result = json.loads(response.text)
            except json.JSONDecodeError:
                result = {
                    'recommendations': response.text
                }
            
            return {
                'success': True,
                'counseling': result
            }
            
        except Exception as e:
            logger.error(f"Gemini AI career counseling error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }


# Convenience functions for quick access
def analyze_student(student_data: Dict) -> Dict:
    """Quick access to student performance analysis"""
    return GeminiAIService.analyze_student_performance(student_data)


def generate_content(subject: str, topic: str, difficulty: str = 'intermediate') -> Dict:
    """Quick access to content generation"""
    return GeminiAIService.generate_study_content(subject, topic, difficulty)


def chatbot(message: str, context: Optional[Dict] = None) -> str:
    """Quick access to chatbot"""
    return GeminiAIService.chatbot_response(message, context)


def compose_email(purpose: str, recipient: str, context: Dict) -> Dict:
    """Quick access to email composer"""
    return GeminiAIService.compose_email(purpose, recipient, context)









