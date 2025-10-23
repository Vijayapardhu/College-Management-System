"""
generate_project_documentation.py

Generates a professionally formatted project documentation PDF following the document_style.txt specifications.
Uses reportlab for structured PDF generation with consistent fonts, spacing, and layout.

Usage:
    python generate_project_documentation.py

Output:
    Generated_Project_Report.pdf (in current directory)

Requirements:
    - reportlab (install via: pip install reportlab)
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from datetime import datetime
import os


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for adding page numbers at bottom center"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Add page numbers to all pages"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        """Draw page number at bottom center"""
        self.setFont("Times-Roman", 10)
        page_num = f"Page {self._pageNumber} of {page_count}"
        self.drawCentredString(A4[0] / 2, 0.5 * inch, page_num)


class ProjectDocumentGenerator:
    """Generate project documentation PDF with consistent styling"""
    
    def __init__(self, output_filename="Generated_Project_Report.pdf"):
        self.output_filename = output_filename
        self.styles = self._create_styles()
        self.story = []
        
        # A4 with 1-inch margins
        self.doc = SimpleDocTemplate(
            output_filename,
            pagesize=A4,
            leftMargin=1*inch,
            rightMargin=1*inch,
            topMargin=1*inch,
            bottomMargin=1*inch,
        )
    
    def _create_styles(self):
        """Create custom paragraph styles based on document_style.txt"""
        styles = {}
        
        # Title style (for cover page)
        styles['Title'] = ParagraphStyle(
            'Title',
            fontName='Times-Bold',
            fontSize=18,
            leading=22,
            alignment=TA_CENTER,
            spaceAfter=12,
            textTransform='uppercase'
        )
        
        # Subtitle style
        styles['Subtitle'] = ParagraphStyle(
            'Subtitle',
            fontName='Times-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=10,
        )
        
        # Heading style (Chapter headings - uppercase, bold)
        styles['Heading1'] = ParagraphStyle(
            'Heading1',
            fontName='Times-Bold',
            fontSize=18,
            leading=22,
            alignment=TA_LEFT,
            spaceAfter=12,
            spaceBefore=12,
            textTransform='uppercase'
        )
        
        # Subheading style (Section numbers + bold)
        styles['Heading2'] = ParagraphStyle(
            'Heading2',
            fontName='Times-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=10,
            spaceBefore=10,
        )
        
        # Body text style (justified, 1.5x line spacing)
        styles['Body'] = ParagraphStyle(
            'Body',
            fontName='Times-Roman',
            fontSize=12,
            leading=18,  # 1.5x line spacing (12 * 1.5)
            alignment=TA_JUSTIFY,
            spaceAfter=12,
        )
        
        # Centered body text
        styles['BodyCenter'] = ParagraphStyle(
            'BodyCenter',
            fontName='Times-Roman',
            fontSize=12,
            leading=18,
            alignment=TA_CENTER,
            spaceAfter=12,
        )
        
        # TOC entry style
        styles['TOC'] = ParagraphStyle(
            'TOC',
            fontName='Times-Roman',
            fontSize=12,
            leading=18,
            alignment=TA_LEFT,
            spaceAfter=6,
        )
        
        return styles
    
    def add_title_page(self, project_title, subtitle, team_details, guide_name):
        """Generate title page with centered content"""
        self.story.append(Spacer(1, 2*inch))
        
        # Project title (uppercase)
        self.story.append(Paragraph(project_title.upper(), self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        if subtitle:
            self.story.append(Paragraph(subtitle, self.styles['Subtitle']))
            self.story.append(Spacer(1, 0.5*inch))
        
        # Team details
        self.story.append(Paragraph("<b>Project Team:</b>", self.styles['BodyCenter']))
        self.story.append(Spacer(1, 0.2*inch))
        for member in team_details:
            self.story.append(Paragraph(member, self.styles['BodyCenter']))
        
        self.story.append(Spacer(1, 0.5*inch))
        
        # Guide
        self.story.append(Paragraph(f"<b>Under the guidance of:</b>", self.styles['BodyCenter']))
        self.story.append(Paragraph(guide_name, self.styles['BodyCenter']))
        
        self.story.append(Spacer(1, 0.5*inch))
        
        # Institution/Year
        current_year = datetime.now().year
        self.story.append(Paragraph(f"<b>{current_year}</b>", self.styles['BodyCenter']))
        
        self.story.append(PageBreak())
    
    def add_certificate_page(self, institution_name, department, project_title, team_members):
        """Generate certificate page"""
        self.story.append(Spacer(1, 1*inch))
        
        self.story.append(Paragraph("CERTIFICATE", self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        cert_text = f"""
        This is to certify that the project titled <b>"{project_title}"</b> is a bonafide 
        work carried out by <b>{', '.join(team_members)}</b> in partial fulfillment of the 
        requirements for the award of the degree in {department}, {institution_name}.
        """
        
        self.story.append(Paragraph(cert_text, self.styles['Body']))
        self.story.append(Spacer(1, 1*inch))
        
        # Signature placeholders
        signature_data = [
            ["Project Guide", "", "Head of Department"],
            ["", "", ""],
            ["_________________", "", "_________________"],
        ]
        
        sig_table = Table(signature_data, colWidths=[2.5*inch, 1*inch, 2.5*inch])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
        ]))
        
        self.story.append(sig_table)
        self.story.append(PageBreak())
    
    def add_declaration_page(self, team_members, project_title):
        """Generate declaration page"""
        self.story.append(Spacer(1, 1*inch))
        
        self.story.append(Paragraph("DECLARATION", self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        declaration_text = f"""
        We, <b>{', '.join(team_members)}</b>, hereby declare that the project work entitled 
        <b>"{project_title}"</b> submitted by us is original and has not been submitted to any 
        other university or institution for the award of any degree or diploma.
        """
        
        self.story.append(Paragraph(declaration_text, self.styles['Body']))
        self.story.append(Spacer(1, 1.5*inch))
        
        # Student signatures
        self.story.append(Paragraph("<b>Date:</b> _________________", self.styles['Body']))
        self.story.append(Spacer(1, 0.3*inch))
        
        for member in team_members:
            self.story.append(Paragraph(f"<b>{member}</b>", self.styles['Body']))
            self.story.append(Paragraph("Signature: _________________", self.styles['Body']))
            self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(PageBreak())
    
    def add_acknowledgment_page(self, acknowledgment_text=None):
        """Generate acknowledgment page"""
        self.story.append(Spacer(1, 1*inch))
        
        self.story.append(Paragraph("ACKNOWLEDGMENT", self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        if acknowledgment_text is None:
            acknowledgment_text = """
            We would like to express our sincere gratitude to all those who have contributed 
            to the successful completion of this project. We are deeply grateful to our project 
            guide for their invaluable guidance, constant encouragement, and support throughout 
            the project work.
            <br/><br/>
            We would like to thank the Head of Department and the faculty members for providing 
            us with the necessary facilities and resources. We also extend our thanks to our 
            family and friends for their continuous support and encouragement.
            """
        
        self.story.append(Paragraph(acknowledgment_text, self.styles['Body']))
        self.story.append(PageBreak())
    
    def add_abstract_page(self, abstract_text=None):
        """Generate abstract page"""
        self.story.append(Spacer(1, 1*inch))
        
        self.story.append(Paragraph("ABSTRACT", self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        if abstract_text is None:
            abstract_text = """
            [Insert your project abstract here. The abstract should provide a brief summary of 
            the project, including the problem statement, objectives, methodology, key features, 
            and expected outcomes. Keep it concise, typically 150-300 words.]
            """
        
        self.story.append(Paragraph(abstract_text, self.styles['Body']))
        self.story.append(PageBreak())
    
    def add_table_of_contents(self, chapters):
        """Generate table of contents"""
        self.story.append(Spacer(1, 0.5*inch))
        
        self.story.append(Paragraph("TABLE OF CONTENTS", self.styles['Title']))
        self.story.append(Spacer(1, 0.5*inch))
        
        # Build TOC entries
        toc_data = []
        for idx, chapter in enumerate(chapters, 1):
            entry = f"{idx}. {chapter['title']}"
            page_placeholder = "..."  # In a full implementation, use TOC with actual page numbers
            toc_data.append([entry, page_placeholder])
        
        # Create TOC table
        toc_table = Table(toc_data, colWidths=[5*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('LEADING', (0, 0), (-1, -1), 18),
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())
    
    def add_chapter(self, chapter_number, chapter_title, sections):
        """
        Add a chapter with sections and subsections
        
        Args:
            chapter_number: int, chapter number
            chapter_title: str, chapter title (will be uppercase)
            sections: list of dicts with 'title' and 'content' keys
        """
        # Chapter heading
        heading = f"{chapter_number}. {chapter_title.upper()}"
        self.story.append(Paragraph(heading, self.styles['Heading1']))
        self.story.append(Spacer(1, 0.3*inch))
        
        # Add sections
        for idx, section in enumerate(sections, 1):
            # Section heading (e.g., 1.1 Introduction)
            section_heading = f"{chapter_number}.{idx} {section['title']}"
            self.story.append(Paragraph(section_heading, self.styles['Heading2']))
            self.story.append(Spacer(1, 0.1*inch))
            
            # Section content
            content = section.get('content', '[Section content placeholder]')
            self.story.append(Paragraph(content, self.styles['Body']))
            self.story.append(Spacer(1, 0.2*inch))
        
        self.story.append(PageBreak())
    
    def add_bibliography(self, references):
        """Add bibliography section"""
        self.story.append(Paragraph("BIBLIOGRAPHY", self.styles['Heading1']))
        self.story.append(Spacer(1, 0.3*inch))
        
        for ref in references:
            self.story.append(Paragraph(f"• {ref}", self.styles['Body']))
            self.story.append(Spacer(1, 0.1*inch))
        
        self.story.append(PageBreak())
    
    def generate(self):
        """Build the PDF document"""
        print(f"Generating PDF: {self.output_filename}")
        self.doc.build(self.story, canvasmaker=NumberedCanvas)
        print(f"✓ PDF generated successfully: {self.output_filename}")


def main():
    """Main function to generate the project documentation"""
    
    # Initialize generator
    generator = ProjectDocumentGenerator("Generated_Project_Report.pdf")
    
    # 1. Title Page
    generator.add_title_page(
        project_title="College Management System",
        subtitle="A Comprehensive Educational ERP Solution",
        team_details=[
            "Student Name 1 (Roll No: XXX)",
            "Student Name 2 (Roll No: XXX)",
            "Student Name 3 (Roll No: XXX)",
        ],
        guide_name="Prof. [Guide Name]<br/>Department of Computer Science"
    )
    
    # 2. Certificate
    generator.add_certificate_page(
        institution_name="[Your Institution Name]",
        department="Computer Science and Engineering",
        project_title="College Management System",
        team_members=["Student 1", "Student 2", "Student 3"]
    )
    
    # 3. Declaration
    generator.add_declaration_page(
        team_members=["Student Name 1", "Student Name 2", "Student Name 3"],
        project_title="College Management System"
    )
    
    # 4. Acknowledgment
    generator.add_acknowledgment_page()
    
    # 5. Abstract
    abstract_text = """
    The College Management System is a comprehensive educational ERP solution designed to 
    streamline administrative and academic operations in educational institutions. This 
    web-based application provides integrated modules for student management, faculty 
    administration, attendance tracking, examination management, and fee processing.
    <br/><br/>
    Built using Django framework with PostgreSQL database, the system offers role-based 
    access control for administrators, faculty, and students. Key features include real-time 
    notifications, automated report generation, and a responsive user interface that works 
    seamlessly across devices.
    <br/><br/>
    This project demonstrates the application of modern web technologies and software 
    engineering principles to solve real-world challenges in educational administration.
    """
    generator.add_abstract_page(abstract_text)
    
    # 6. Table of Contents
    chapters = [
        {"title": "INTRODUCTION"},
        {"title": "REQUIREMENTS & ANALYSIS"},
        {"title": "SYSTEM DESIGN"},
        {"title": "IMPLEMENTATION ISSUES"},
        {"title": "TESTING"},
        {"title": "CODING"},
        {"title": "OUTPUT SCREENS"},
        {"title": "CONCLUSION"},
        {"title": "BIBLIOGRAPHY"},
    ]
    generator.add_table_of_contents(chapters)
    
    # 7. Main Chapters
    
    # Chapter 1: Introduction
    generator.add_chapter(
        chapter_number=1,
        chapter_title="INTRODUCTION",
        sections=[
            {
                "title": "Overview",
                "content": """
                Educational institutions face numerous challenges in managing day-to-day 
                operations, including student records, faculty coordination, attendance 
                tracking, and examination management. Traditional manual systems are 
                time-consuming, error-prone, and difficult to scale.
                <br/><br/>
                The College Management System addresses these challenges by providing a 
                centralized, automated platform that streamlines administrative processes 
                and improves communication between stakeholders.
                """
            },
            {
                "title": "Problem Statement",
                "content": """
                [Describe the specific problems and challenges that motivated this project. 
                Include current limitations of existing systems and the need for automation.]
                """
            },
            {
                "title": "Objectives",
                "content": """
                The primary objectives of this project are:
                <br/>• Develop a user-friendly web-based management system
                <br/>• Automate routine administrative tasks
                <br/>• Provide role-based access control for different user types
                <br/>• Enable real-time data access and reporting
                <br/>• Ensure data security and privacy
                """
            },
            {
                "title": "Scope",
                "content": """
                [Define the scope of the project - what features are included and what 
                limitations exist. Mention future enhancements if applicable.]
                """
            },
        ]
    )
    
    # Chapter 2: Requirements & Analysis
    generator.add_chapter(
        chapter_number=2,
        chapter_title="REQUIREMENTS & ANALYSIS",
        sections=[
            {
                "title": "Functional Requirements",
                "content": """
                [List all functional requirements - what the system should do. Include 
                features for different user roles: Admin, Faculty, Students.]
                """
            },
            {
                "title": "Non-Functional Requirements",
                "content": """
                [Describe non-functional requirements like performance, security, usability, 
                scalability, reliability, and maintainability.]
                """
            },
            {
                "title": "Hardware Requirements",
                "content": """
                • Processor: Intel Core i3 or higher
                <br/>• RAM: 4GB minimum (8GB recommended)
                <br/>• Storage: 20GB available space
                <br/>• Network: Broadband internet connection
                """
            },
            {
                "title": "Software Requirements",
                "content": """
                • Operating System: Windows 10/11, Linux, or macOS
                <br/>• Programming Language: Python 3.11+
                <br/>• Framework: Django 4.2
                <br/>• Database: PostgreSQL 15
                <br/>• Web Server: Gunicorn/Nginx
                <br/>• Browser: Chrome, Firefox, Safari (latest versions)
                """
            },
        ]
    )
    
    # Chapter 3: System Design
    generator.add_chapter(
        chapter_number=3,
        chapter_title="SYSTEM DESIGN",
        sections=[
            {
                "title": "System Architecture",
                "content": """
                [Describe the overall system architecture. Include information about the 
                three-tier architecture: presentation layer, application layer, and data layer.]
                """
            },
            {
                "title": "Database Design",
                "content": """
                [Describe the database schema, entity-relationship diagrams, and key tables. 
                Include relationships between entities.]
                """
            },
            {
                "title": "Module Design",
                "content": """
                The system is divided into several key modules:
                <br/>• User Authentication & Authorization
                <br/>• Student Management
                <br/>• Faculty Management
                <br/>• Attendance Tracking
                <br/>• Examination Management
                <br/>• Fee Management
                <br/>• Report Generation
                """
            },
            {
                "title": "User Interface Design",
                "content": """
                [Describe the UI/UX design principles, wireframes, and mockups. Include 
                information about responsive design for mobile devices.]
                """
            },
        ]
    )
    
    # Chapter 4: Implementation Issues
    generator.add_chapter(
        chapter_number=4,
        chapter_title="IMPLEMENTATION ISSUES",
        sections=[
            {
                "title": "Challenges Faced",
                "content": """
                [Describe technical challenges encountered during development, such as 
                integration issues, performance bottlenecks, or compatibility problems.]
                """
            },
            {
                "title": "Solutions Adopted",
                "content": """
                [Explain how each challenge was addressed, including alternative approaches 
                considered and the rationale for the chosen solution.]
                """
            },
        ]
    )
    
    # Chapter 5: Testing
    generator.add_chapter(
        chapter_number=5,
        chapter_title="TESTING",
        sections=[
            {
                "title": "Testing Strategy",
                "content": """
                [Describe the overall testing approach: unit testing, integration testing, 
                system testing, and user acceptance testing.]
                """
            },
            {
                "title": "Test Cases",
                "content": """
                [Provide sample test cases with inputs, expected outputs, and actual results. 
                Include both positive and negative test scenarios.]
                """
            },
            {
                "title": "Test Results",
                "content": """
                [Summarize test results, including any bugs found and resolved. Include 
                metrics like test coverage and pass/fail rates.]
                """
            },
        ]
    )
    
    # Chapter 6: Coding
    generator.add_chapter(
        chapter_number=6,
        chapter_title="CODING",
        sections=[
            {
                "title": "Development Environment",
                "content": """
                [Describe the development tools and environment used: IDE, version control, 
                package management, etc.]
                """
            },
            {
                "title": "Code Structure",
                "content": """
                [Explain the project structure, folder organization, and naming conventions. 
                Include key files and their purposes.]
                """
            },
            {
                "title": "Key Code Snippets",
                "content": """
                [Include important code snippets with explanations. Show examples of key 
                functions, algorithms, or design patterns used.]
                """
            },
        ]
    )
    
    # Chapter 7: Output Screens
    generator.add_chapter(
        chapter_number=7,
        chapter_title="OUTPUT SCREENS",
        sections=[
            {
                "title": "User Interfaces",
                "content": """
                [Insert screenshots of key user interfaces with descriptions:
                <br/>• Login page
                <br/>• Dashboard (Admin/Faculty/Student)
                <br/>• Student registration form
                <br/>• Attendance management
                <br/>• Report generation
                <br/>• And other key screens]
                """
            },
        ]
    )
    
    # Chapter 8: Conclusion
    generator.add_chapter(
        chapter_number=8,
        chapter_title="CONCLUSION",
        sections=[
            {
                "title": "Summary",
                "content": """
                [Summarize the project achievements, how objectives were met, and the 
                overall success of the implementation.]
                """
            },
            {
                "title": "Future Enhancements",
                "content": """
                [Discuss potential improvements and features that could be added in future 
                versions:
                <br/>• Mobile application development
                <br/>• AI-powered analytics
                <br/>• Integration with external systems
                <br/>• Advanced reporting features]
                """
            },
        ]
    )
    
    # 9. Bibliography
    generator.add_bibliography([
        "Django Documentation. (2023). Django 4.2 Documentation. https://docs.djangoproject.com/",
        "PostgreSQL Global Development Group. (2023). PostgreSQL 15 Documentation.",
        "Python Software Foundation. (2023). Python 3.11 Documentation. https://docs.python.org/",
        "[Add your specific references here - books, research papers, online resources]",
    ])
    
    # Generate the PDF
    generator.generate()


if __name__ == "__main__":
    main()
