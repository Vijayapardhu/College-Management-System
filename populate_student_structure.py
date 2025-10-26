"""
Script to populate initial data for the new student structure
Run this after migrations: python populate_student_structure.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'student_management_system.settings')
django.setup()

from main_app.models import AcademicYear, Section, Session

def populate_academic_years():
    """Create Academic Years 1-3 (for 3-year programs)"""
    print("\n📚 Creating Academic Years...")
    years = [
        (1, "First Year"),
        (2, "Second Year"),
        (3, "Third Year"),
    ]
    
    for year_num, year_name in years:
        year, created = AcademicYear.objects.get_or_create(
            year_number=year_num,
            defaults={'year_name': year_name}
        )
        if created:
            print(f"   ✓ Created: {year}")
        else:
            print(f"   ℹ Already exists: {year}")

def populate_sections():
    """Create Sections A-D"""
    print("\n📋 Creating Sections...")
    sections = ['A', 'B', 'C', 'D']
    
    for section_name in sections:
        section, created = Section.objects.get_or_create(
            name=section_name,
            defaults={'capacity': 60}
        )
        if created:
            print(f"   ✓ Created: Section {section_name} (capacity: 60)")
        else:
            print(f"   ℹ Already exists: Section {section_name}")

def update_sessions():
    """Update existing sessions with session names"""
    print("\n📅 Updating Sessions with session names...")
    
    sessions = Session.objects.all()
    
    if not sessions.exists():
        print("   ℹ No sessions found.")
        print("\n   📝 Admin can create sessions from the admin panel:")
        print("   • Go to http://127.0.0.1:8000/session/manage/")
        print("   • Click 'Add New Session'")
        print("   • Example: C23 (2023-2026), C24 (2024-2027)")
        return
    
    for session in sessions:
        print(f"   Session: {session}")
        if not session.session_name and session.session_start_year:
            year = session.session_start_year.year
            session_name = f"C{str(year)[2:]}"
            session.session_name = session_name
            session.start_year = year
            session.end_year = year + 3
            session.save()
            print(f"   ✓ Updated to: {session}")

def main():
    print("═" * 60)
    print("  POPULATING STUDENT STRUCTURE DATA")
    print("═" * 60)
    
    try:
        # Populate Academic Years
        populate_academic_years()
        
        # Populate Sections
        populate_sections()
        
        # Update Sessions
        update_sessions()
        
        print("\n" + "═" * 60)
        print("  ✅ DATA POPULATION COMPLETE!")
        print("═" * 60)
        print("\n📊 Summary:")
        print(f"   • Academic Years: {AcademicYear.objects.count()}")
        print(f"   • Sections: {Section.objects.count()}")
        print(f"   • Sessions: {Session.objects.count()}")
        
        print("\n🔧 Admin can manage these from:")
        print("   • Academic Years: http://127.0.0.1:8000/admin/years/")
        print("   • Sections: http://127.0.0.1:8000/admin/sections/")
        print("   • Sessions: http://127.0.0.1:8000/session/manage/")
        print("\n✨ Your student structure is ready!")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()

