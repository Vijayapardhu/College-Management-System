"""
Management command to setup academic sessions and initial data.
Usage: python manage.py setup_academic_data
"""
from django.core.management.base import BaseCommand
from main_app.models import Session


class Command(BaseCommand):
    help = 'Creates academic sessions (c23, c20) for the system'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting academic data setup...'))
        
        # Create c23 session
        c23, created = Session.objects.get_or_create(
            session_name='c23',
            defaults={
                'start_year': 2023,
                'end_year': 2024,
                'is_active': True
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created session: c23 (2023-2024)'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Session c23 already exists'))
        
        # Create c20 session
        c20, created = Session.objects.get_or_create(
            session_name='c20',
            defaults={
                'start_year': 2020,
                'end_year': 2021,
                'is_active': False
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('✅ Created session: c20 (2020-2021)'))
        else:
            self.stdout.write(self.style.WARNING('ℹ️  Session c20 already exists'))
        
        # Display all sessions
        self.stdout.write(self.style.SUCCESS('\n📋 All Sessions:'))
        for session in Session.objects.all().order_by('start_year'):
            status = '🟢 Active' if session.is_active else '⚪ Inactive'
            self.stdout.write(f'  - {session.session_name} ({session.start_year}-{session.end_year}) {status}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Setup complete! Total sessions: {Session.objects.count()}'))
        
        # Note about semesters
        self.stdout.write(self.style.WARNING('\n📝 Note: Semesters are handled via Subject.semester field'))
        self.stdout.write(self.style.WARNING('When creating subjects, set semester=1, 3, 4, 5, or 6'))

