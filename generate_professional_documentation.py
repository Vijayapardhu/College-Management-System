"""
Professional Project Documentation Generator
Generates publication-quality PDF documents with sophisticated formatting
matching academic project report standards
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    Image, KeepTogether, Frame, PageTemplate, Indenter
)
from reportlab.pdfgen import canvas
from datetime import datetime
import os


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for page numbering and headers/footers"""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.show_page_numbers = True
        self.header_text = None
        self.footer_text = None

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        """Draw headers, footers and page numbers"""
        page_num = self._pageNumber
        
        # Draw page number at bottom center
        if self.show_page_numbers and page_num > 3:  # Skip first 3 pages (title, certificate, etc.)
            self.saveState()
            self.setFont('Times-Roman', 10)
            self.drawCentredString(A4[0] / 2, 0.5 * inch, f"{page_num - 3}")
            self.restoreState()
        
        # Draw header line on content pages
        if page_num > 3:
            self.saveState()
            self.setStrokeColor(colors.grey)
            self.setLineWidth(0.5)
            self.line(inch, A4[1] - 0.75 * inch, A4[0] - inch, A4[1] - 0.75 * inch)
            self.restoreState()


class ProfessionalDocGenerator:
    """
    Professional Documentation Generator with publication-quality formatting
    """
    
    def __init__(self, filename="Project_Documentation.pdf"):
        """Initialize the document generator"""
        self.filename = filename
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch,
            title="Project Documentation"
        )
        
        self.elements = []
        self.styles = self._create_styles()
        self.width = A4[0] - 2 * inch
        
    def _create_styles(self):
        """Create custom paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Main Title Style
        styles.add(ParagraphStyle(
            name='MainTitle',
            parent=styles['Title'],
            fontName='Times-Bold',
            fontSize=20,
            textColor=colors.HexColor('#1a1a1a'),
            alignment=TA_CENTER,
            spaceAfter=12,
            leading=24
        ))
        
        # Subtitle Style
        styles.add(ParagraphStyle(
            name='SubTitle',
            parent=styles['Normal'],
            fontName='Times-Bold',
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            alignment=TA_CENTER,
            spaceAfter=10,
            spaceBefore=6
        ))
        
        # College Name Style
        styles.add(ParagraphStyle(
            name='CollegeName',
            parent=styles['Normal'],
            fontName='Times-Bold',
            fontSize=13,
            textColor=colors.HexColor('#000080'),
            alignment=TA_CENTER,
            spaceAfter=4,
            spaceBefore=4
        ))
        
        # Header Styles
        styles.add(ParagraphStyle(
            name='ChapterHeading',
            parent=styles['Heading1'],
            fontName='Times-Bold',
            fontSize=16,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            spaceBefore=12,
            alignment=TA_LEFT
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=styles['Heading2'],
            fontName='Times-Bold',
            fontSize=14,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=10,
            spaceBefore=10,
            alignment=TA_LEFT
        ))
        
        styles.add(ParagraphStyle(
            name='SubSectionHeading',
            parent=styles['Heading3'],
            fontName='Times-Bold',
            fontSize=12,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=8,
            spaceBefore=8,
            alignment=TA_LEFT
        ))
        
        # Body Text Style
        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['Normal'],
            fontName='Times-Roman',
            fontSize=12,
            textColor=colors.black,
            alignment=TA_JUSTIFY,
            spaceAfter=10,
            leading=16,
            firstLineIndent=0
        ))
        
        # Centered Body Text
        styles.add(ParagraphStyle(
            name='CustomBodyCenter',
            parent=styles['CustomBody'],
            alignment=TA_CENTER
        ))
        
        # Bold Body Text
        styles.add(ParagraphStyle(
            name='CustomBodyBold',
            parent=styles['CustomBody'],
            fontName='Times-Bold'
        ))
        
        # List Item Style
        styles.add(ParagraphStyle(
            name='CustomListItem',
            parent=styles['CustomBody'],
            leftIndent=20,
            bulletIndent=10,
            spaceAfter=6
        ))
        
        # Code Style
        styles.add(ParagraphStyle(
            name='CustomCode',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=10,
            textColor=colors.HexColor('#2c3e50'),
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=20,
            rightIndent=20,
            spaceAfter=10,
            spaceBefore=10,
            borderPadding=8
        ))
        
        return styles

    def add_title_page(self, project_title, subtitle, team_members, guide_name, 
                       college_name, department, degree, date=None):
        """
        Add a professional title page
        
        Args:
            project_title: Main project title
            subtitle: Project subtitle/tagline
            team_members: List of tuples [(name, roll_number), ...]
            guide_name: Guide/Supervisor name with designation
            college_name: Institution name
            department: Department name
            degree: Degree/Diploma program
            date: Submission date (defaults to current date)
        """
        if date is None:
            date = datetime.now().strftime("%B %Y")
        
        # Add logo space (can be replaced with actual logo)
        self.elements.append(Spacer(1, 0.5 * inch))
        
        # College Name
        self.elements.append(Paragraph(college_name.upper(), self.styles['CollegeName']))
        self.elements.append(Spacer(1, 0.1 * inch))
        
        # Divider line
        line_table = Table([['']], colWidths=[self.width * 0.6])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#1a1a1a'))
        ]))
        self.elements.append(line_table)
        self.elements.append(Spacer(1, 0.3 * inch))
        
        # Main Title
        self.elements.append(Paragraph(project_title.upper(), self.styles['MainTitle']))
        if subtitle:
            self.elements.append(Paragraph(subtitle, self.styles['SubTitle']))
        
        self.elements.append(Spacer(1, 0.4 * inch))
        
        # "A Project Report" section
        self.elements.append(Paragraph("A Project Report", self.styles['CustomBodyCenter']))
        self.elements.append(Paragraph(
            f"Submitted in the partial fulfillment of the Requirements", 
            self.styles['CustomBodyCenter']
        ))
        self.elements.append(Paragraph(f"For the award of the Degree of", self.styles['CustomBodyCenter']))
        self.elements.append(Spacer(1, 0.1 * inch))
        self.elements.append(Paragraph(f"<b>{degree.upper()}</b>", self.styles['CustomBodyCenter']))
        self.elements.append(Paragraph(f"IN", self.styles['CustomBodyCenter']))
        self.elements.append(Paragraph(f"<b>{department.upper()}</b>", self.styles['CustomBodyCenter']))
        
        self.elements.append(Spacer(1, 0.4 * inch))
        
        # Team Members
        self.elements.append(Paragraph("<b>SUBMITTED BY</b>", self.styles['CustomBodyCenter']))
        self.elements.append(Spacer(1, 0.1 * inch))
        
        team_data = [[member[0], member[1]] for member in team_members]
        team_table = Table(team_data, colWidths=[self.width * 0.5, self.width * 0.3])
        team_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        self.elements.append(team_table)
        
        self.elements.append(Spacer(1, 0.3 * inch))
        
        # Guide
        self.elements.append(Paragraph("<b>Under the Esteemed Guidance of</b>", self.styles['CustomBodyCenter']))
        self.elements.append(Spacer(1, 0.05 * inch))
        self.elements.append(Paragraph(f"<b>{guide_name}</b>", self.styles['CustomBodyCenter']))
        
        self.elements.append(Spacer(1, 0.3 * inch))
        
        # Department and Date
        self.elements.append(Paragraph(f"<b>{department.upper()}</b>", self.styles['CustomBodyCenter']))
        self.elements.append(Paragraph(college_name.upper(), self.styles['CustomBodyCenter']))
        self.elements.append(Spacer(1, 0.1 * inch))
        self.elements.append(Paragraph(f"<b>{date}</b>", self.styles['CustomBodyCenter']))
        
        self.elements.append(PageBreak())

    def add_certificate_page(self, project_title, team_members, guide_name, 
                            hod_name, principal_name, college_name, date=None):
        """
        Add certificate page
        """
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
        
        self.elements.append(Spacer(1, 0.3 * inch))
        
        # College Header
        self.elements.append(Paragraph(college_name.upper(), self.styles['CollegeName']))
        self.elements.append(Spacer(1, 0.05 * inch))
        self.elements.append(Paragraph("APPROVED BY A.I.C.T.E, NEW DELHI – AFFILIATED TO SBTET", 
                                      self.styles['CustomBodyCenter']))
        self.elements.append(Spacer(1, 0.3 * inch))
        
        # Certificate Title
        self.elements.append(Paragraph("<b>CERTIFICATE</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        
        # Certificate Text
        team_names = ", ".join([f"{m[0]} ({m[1]})" for m in team_members])
        cert_text = f"""
        This is to certify that the project work entitled <b>"{project_title.upper()}"</b> 
        done by {team_names}, is a bonafide work carried out by them in partial fulfillment 
        for the award of the Diploma in their respective department during the academic year, 
        under my guidance and supervision.
        """
        self.elements.append(Paragraph(cert_text, self.styles['CustomBody']))
        
        self.elements.append(Spacer(1, 0.5 * inch))
        
        # Signatures
        sig_data = [
            [f"<b>{guide_name}</b>", "", f"<b>{hod_name}</b>"],
            ["Project Guide", "", "Head of the Department"],
            ["", "", ""],
            ["", f"<b>{principal_name}</b>", ""],
            ["", "Principal", ""]
        ]
        
        sig_table = Table(sig_data, colWidths=[self.width * 0.33, self.width * 0.34, self.width * 0.33])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.elements.append(sig_table)
        
        self.elements.append(Spacer(1, 0.3 * inch))
        self.elements.append(Paragraph(f"Date: {date}", self.styles['CustomBody']))
        
        self.elements.append(PageBreak())

    def add_declaration_page(self, team_members, project_title, date=None):
        """Add declaration page"""
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
        
        self.elements.append(Spacer(1, 0.5 * inch))
        self.elements.append(Paragraph("<b>DECLARATION</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        
        team_names = ", ".join([m[0] for m in team_members])
        
        declaration_text = f"""
        We, {team_names}, hereby declare that the project work entitled 
        <b>"{project_title}"</b> submitted to the Department, is a record of an original 
        work done by us under the guidance of our project guide, and this project work has 
        not formed the basis for the award of any degree/diploma/fellowship or similar title 
        to any candidate of any university.
        """
        
        self.elements.append(Paragraph(declaration_text, self.styles['CustomBody']))
        self.elements.append(Spacer(1, 0.5 * inch))
        
        # Student signatures
        sig_data = []
        for i, member in enumerate(team_members):
            sig_data.append([f"<b>{member[0]}</b>", member[1]])
        
        sig_table = Table(sig_data, colWidths=[self.width * 0.6, self.width * 0.4])
        sig_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
        ]))
        self.elements.append(sig_table)
        
        self.elements.append(Spacer(1, 0.3 * inch))
        self.elements.append(Paragraph(f"Date: {date}", self.styles['CustomBody']))
        
        self.elements.append(PageBreak())

    def add_acknowledgment(self, acknowledgment_text):
        """Add acknowledgment section"""
        self.elements.append(Spacer(1, 0.3 * inch))
        self.elements.append(Paragraph("<b>ACKNOWLEDGMENT</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        self.elements.append(Paragraph(acknowledgment_text, self.styles['CustomBody']))
        self.elements.append(PageBreak())

    def add_abstract(self, abstract_text, keywords=None):
        """Add abstract section"""
        self.elements.append(Spacer(1, 0.3 * inch))
        self.elements.append(Paragraph("<b>ABSTRACT</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        self.elements.append(Paragraph(abstract_text, self.styles['CustomBody']))
        
        if keywords:
            self.elements.append(Spacer(1, 0.2 * inch))
            keywords_text = f"<b>Keywords:</b> {', '.join(keywords)}"
            self.elements.append(Paragraph(keywords_text, self.styles['CustomBody']))
        
        self.elements.append(PageBreak())

    def add_table_of_contents(self, contents):
        """
        Add table of contents
        
        Args:
            contents: List of tuples [(chapter_num, title, page_num), ...]
        """
        self.elements.append(Spacer(1, 0.3 * inch))
        self.elements.append(Paragraph("<b>TABLE OF CONTENTS</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        
        toc_data = [["Chapter", "Title", "Page"]]
        for item in contents:
            toc_data.append([str(item[0]), item[1], str(item[2])])
        
        toc_table = Table(toc_data, colWidths=[inch * 0.8, inch * 4.5, inch * 0.7])
        toc_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
            ('FONTSIZE', (0, 1), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('LINEBELOW', (0, 0), (-1, 0), 1, colors.black),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        self.elements.append(toc_table)
        self.elements.append(PageBreak())

    def add_chapter(self, chapter_num, chapter_title, sections):
        """
        Add a complete chapter with sections
        
        Args:
            chapter_num: Chapter number
            chapter_title: Chapter title
            sections: List of tuples [(section_title, content), ...]
                     content can be string, list of strings, or dict with 'text', 'image', 'table'
        """
        # Chapter Header
        self.elements.append(Spacer(1, 0.2 * inch))
        chapter_header = f"CHAPTER {chapter_num}"
        self.elements.append(Paragraph(chapter_header, self.styles['ChapterHeading']))
        self.elements.append(Paragraph(chapter_title.upper(), self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.2 * inch))
        
        # Add sections
        for section in sections:
            if len(section) >= 2:
                section_title, content = section[0], section[1]
                
                # Section header
                if section_title:
                    self.elements.append(Paragraph(f"<b>{section_title}</b>", self.styles['SectionHeading']))
                    self.elements.append(Spacer(1, 0.1 * inch))
                
                # Handle different content types
                if isinstance(content, str):
                    # Simple text paragraph
                    self.elements.append(Paragraph(content, self.styles['CustomBody']))
                
                elif isinstance(content, list):
                    # List of paragraphs or bullet points
                    for item in content:
                        if isinstance(item, str):
                            self.elements.append(Paragraph(item, self.styles['CustomBody']))
                        self.elements.append(Spacer(1, 0.05 * inch))
                
                elif isinstance(content, dict):
                    # Complex content with text, tables, images
                    if 'text' in content:
                        self.elements.append(Paragraph(content['text'], self.styles['CustomBody']))
                    
                    if 'table' in content:
                        self.add_table(content['table']['data'], 
                                      content['table'].get('colWidths'),
                                      content['table'].get('style'))
                    
                    if 'image' in content:
                        self.add_image(content['image'], 
                                      content.get('image_width', self.width * 0.6))
                    
                    if 'code' in content:
                        self.elements.append(Paragraph(content['code'], self.styles['CustomCode']))
                
                self.elements.append(Spacer(1, 0.15 * inch))
        
        self.elements.append(PageBreak())

    def add_table(self, data, col_widths=None, custom_style=None):
        """Add a formatted table"""
        if col_widths is None:
            col_widths = [self.width / len(data[0])] * len(data[0])
        
        table = Table(data, colWidths=col_widths)
        
        if custom_style is None:
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 11),
                ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
            ]))
        else:
            table.setStyle(custom_style)
        
        self.elements.append(table)
        self.elements.append(Spacer(1, 0.2 * inch))

    def add_image(self, image_path, width=None, caption=None):
        """Add an image with optional caption"""
        if width is None:
            width = self.width * 0.6
        
        try:
            img = Image(image_path, width=width, height=width * 0.75, kind='proportional')
            self.elements.append(img)
            
            if caption:
                self.elements.append(Spacer(1, 0.05 * inch))
                self.elements.append(Paragraph(f"<i>{caption}</i>", self.styles['CustomBodyCenter']))
            
            self.elements.append(Spacer(1, 0.15 * inch))
        except Exception as e:
            print(f"Warning: Could not load image {image_path}: {e}")

    def add_list(self, items, ordered=False):
        """Add bulleted or numbered list"""
        for i, item in enumerate(items):
            if ordered:
                text = f"{i+1}. {item}"
            else:
                text = f"• {item}"
            self.elements.append(Paragraph(text, self.styles['CustomListItem']))
        self.elements.append(Spacer(1, 0.1 * inch))

    def add_code_block(self, code, language="python"):
        """Add formatted code block"""
        self.elements.append(Paragraph(f"<font face='courier' size=10>{code}</font>", 
                                      self.styles['CustomCode']))
        self.elements.append(Spacer(1, 0.15 * inch))

    def add_references(self, references):
        """
        Add references/bibliography section
        
        Args:
            references: List of reference strings
        """
        self.elements.append(Spacer(1, 0.2 * inch))
        self.elements.append(Paragraph("<b>REFERENCES</b>", self.styles['ChapterHeading']))
        self.elements.append(Spacer(1, 0.15 * inch))
        
        for i, ref in enumerate(references, 1):
            ref_text = f"[{i}] {ref}"
            self.elements.append(Paragraph(ref_text, self.styles['CustomBody']))
            self.elements.append(Spacer(1, 0.05 * inch))

    def generate(self):
        """Build and save the PDF document"""
        print(f"Generating PDF: {self.filename}")
        self.doc.build(
            self.elements,
            canvasmaker=NumberedCanvas
        )
        print(f"✓ PDF generated successfully: {self.filename}")
        return self.filename


# Example usage demonstrating all features
def main():
    """Example: Generate a complete project documentation"""
    
    # Initialize generator
    doc = ProfessionalDocGenerator("College_Management_System_Documentation.pdf")
    
    # Add Title Page
    doc.add_title_page(
        project_title="College Management System",
        subtitle="An Integrated ERP Solution for Educational Institutions",
        team_members=[
            ("Vijayapardhu", "22249-CSE-001"),
            ("Student Name 2", "22249-CSE-002"),
            ("Student Name 3", "22249-CSE-003"),
            ("Student Name 4", "22249-CSE-004"),
        ],
        guide_name="Ms. Guide Name, M.Tech, Assistant Professor",
        college_name="Your College Name",
        department="Computer Science and Engineering",
        degree="Bachelor of Technology"
    )
    
    # Add Certificate Page
    doc.add_certificate_page(
        project_title="College Management System",
        team_members=[
            ("Vijayapardhu", "22249-CSE-001"),
            ("Student Name 2", "22249-CSE-002"),
        ],
        guide_name="Ms. Guide Name",
        hod_name="Dr. HOD Name",
        principal_name="Dr. Principal Name",
        college_name="Your College Name"
    )
    
    # Add Declaration
    doc.add_declaration_page(
        team_members=[
            ("Vijayapardhu", "22249-CSE-001"),
            ("Student Name 2", "22249-CSE-002"),
        ],
        project_title="College Management System"
    )
    
    # Add Acknowledgment
    acknowledgment = """
    We would like to express our sincere gratitude to all those who have contributed to the 
    successful completion of this project. We are deeply grateful to our project guide, 
    Ms. Guide Name, for her invaluable guidance, constant encouragement, and expert advice 
    throughout the development of this project. We extend our heartfelt thanks to the Head 
    of the Department, Dr. HOD Name, and the Principal, Dr. Principal Name, for providing 
    us with the necessary facilities and support. We are also thankful to all the faculty 
    members and our fellow students for their cooperation and suggestions. Finally, we 
    express our gratitude to our parents and friends for their moral support and encouragement.
    """
    doc.add_acknowledgment(acknowledgment)
    
    # Add Abstract
    abstract = """
    This project presents a comprehensive College Management System designed to streamline 
    and automate various administrative and academic processes within educational institutions. 
    The system provides an integrated platform for managing student records, faculty information, 
    course management, attendance tracking, examination management, and communication between 
    stakeholders. Built using Django framework with PostgreSQL database, the system ensures 
    data integrity, security, and scalability. The web-based interface offers role-based access 
    control for administrators, faculty, and students. Key features include real-time attendance 
    tracking, automated grade calculation, timetable management, and comprehensive reporting 
    capabilities. The system significantly reduces manual effort, minimizes errors, and enhances 
    the overall efficiency of college administration.
    """
    doc.add_abstract(
        abstract,
        keywords=["College Management", "ERP", "Django", "Education Technology", "Automation"]
    )
    
    # Add Table of Contents
    doc.add_table_of_contents([
        (1, "Introduction", 1),
        (2, "Literature Survey", 8),
        (3, "System Analysis", 15),
        (4, "System Design", 22),
        (5, "Implementation", 35),
        (6, "Testing", 48),
        (7, "Conclusion and Future Work", 55),
        ("", "References", 60),
    ])
    
    # Chapter 1: Introduction
    doc.add_chapter(
        1,
        "Introduction",
        [
            ("1.1 Overview", """
            The College Management System is a comprehensive software solution designed to address 
            the complex administrative and academic needs of modern educational institutions. 
            In today's digital age, educational institutions face increasing challenges in managing 
            large volumes of data, coordinating between various departments, and providing efficient 
            services to students and faculty. Traditional manual systems are time-consuming, 
            error-prone, and unable to meet the demands of growing student populations and evolving 
            educational requirements.
            """),
            
            ("1.2 Problem Statement", """
            Educational institutions currently face several challenges: inefficient manual record-keeping, 
            lack of real-time information access, poor communication between stakeholders, difficulty 
            in tracking student performance, time-consuming attendance management, complex examination 
            and grading processes, and limited reporting capabilities. These issues lead to increased 
            administrative overhead, delayed decision-making, and reduced overall efficiency.
            """),
            
            ("1.3 Objectives", [
                "To develop a centralized system for managing all college operations",
                "To automate attendance tracking and examination management processes",
                "To provide real-time access to information for all stakeholders",
                "To implement role-based access control for enhanced security",
                "To generate comprehensive reports for administrative decision-making",
                "To improve communication between students, faculty, and administration"
            ]),
            
            ("1.4 Scope", """
            The system encompasses student management, faculty management, course and curriculum 
            management, attendance tracking, examination and grading, timetable management, 
            fee management, library management, hostel management, and comprehensive reporting 
            and analytics modules. The web-based architecture ensures accessibility from any 
            device with internet connectivity.
            """),
        ]
    )
    
    # Chapter 2: Literature Survey
    doc.add_chapter(
        2,
        "Literature Survey",
        [
            ("2.1 Existing Systems", """
            Several college management systems exist in the market, each with varying capabilities. 
            Commercial solutions like Campus Management, Ellucian, and Fedena offer comprehensive 
            features but often come with high costs and complex implementation requirements. 
            Open-source alternatives like OpenSIS and RosarioSIS provide basic functionality 
            but may lack advanced features and customization options.
            """),
            
            ("2.2 Technology Stack Analysis", {
                'text': """
                Modern college management systems utilize various technology stacks. The most 
                popular combinations include:
                """,
                'table': {
                    'data': [
                        ["Technology", "Purpose", "Advantages"],
                        ["Django", "Backend Framework", "Rapid development, Security"],
                        ["PostgreSQL", "Database", "Reliability, ACID compliance"],
                        ["React/Vue", "Frontend", "Interactive UI, Performance"],
                        ["Redis", "Caching", "Speed, Scalability"],
                        ["Docker", "Deployment", "Portability, Consistency"],
                    ],
                    'colWidths': [inch * 1.5, inch * 2, inch * 2.5]
                }
            }),
            
            ("2.3 Comparative Analysis", """
            Our analysis of existing systems reveals that while commercial solutions offer 
            extensive features, they often lack flexibility and come with significant costs. 
            Open-source solutions provide cost benefits but may require extensive customization. 
            Our proposed system aims to bridge this gap by providing a customizable, scalable, 
            and cost-effective solution tailored to the specific needs of educational institutions.
            """),
        ]
    )
    
    # Chapter 3: System Analysis
    doc.add_chapter(
        3,
        "System Analysis",
        [
            ("3.1 Feasibility Study", """
            The feasibility study examines technical, operational, and economic aspects. 
            Technically, the system utilizes well-established technologies with strong community 
            support. Operationally, the system aligns with existing institutional workflows 
            while introducing automation. Economically, the open-source technology stack 
            significantly reduces licensing costs while providing enterprise-grade capabilities.
            """),
            
            ("3.2 Functional Requirements", [
                "User authentication and authorization with role-based access",
                "Student profile management with academic history",
                "Faculty management with workload tracking",
                "Course and curriculum management",
                "Automated attendance tracking and reporting",
                "Examination scheduling and grade management",
                "Dynamic timetable generation",
                "Fee management and payment tracking",
                "Communication tools (notifications, messaging)",
                "Comprehensive reporting and analytics"
            ]),
            
            ("3.3 Non-Functional Requirements", [
                "Security: Data encryption, secure authentication, SQL injection prevention",
                "Performance: Response time < 2 seconds, support for 1000+ concurrent users",
                "Scalability: Horizontal and vertical scaling capabilities",
                "Usability: Intuitive interface, mobile-responsive design",
                "Reliability: 99.9% uptime, automated backups",
                "Maintainability: Modular architecture, comprehensive documentation"
            ]),
        ]
    )
    
    # Chapter 4: System Design
    doc.add_chapter(
        4,
        "System Design",
        [
            ("4.1 System Architecture", """
            The system follows a three-tier architecture: Presentation Layer (web browser, 
            mobile app), Application Layer (Django backend, business logic), and Data Layer 
            (PostgreSQL database, Redis cache). This architecture ensures separation of concerns, 
            scalability, and maintainability. The system utilizes RESTful API design for 
            communication between frontend and backend components.
            """),
            
            ("4.2 Database Design", """
            The database schema comprises normalized tables for users, students, faculty, 
            courses, attendance, examinations, grades, and administrative data. Relationships 
            between entities are established using foreign keys with appropriate constraints. 
            Indexes are implemented on frequently queried columns to optimize performance.
            """),
            
            ("4.3 Module Design", """
            The system is organized into modular components: Authentication Module, Student 
            Management Module, Faculty Management Module, Academic Module, Attendance Module, 
            Examination Module, Timetable Module, Fee Management Module, and Reporting Module. 
            Each module is designed with loose coupling and high cohesion principles.
            """),
        ]
    )
    
    # Add more chapters as needed...
    
    # Add References
    doc.add_references([
        "Django Documentation, https://docs.djangoproject.com/",
        "PostgreSQL Official Documentation, https://www.postgresql.org/docs/",
        "Smith, J. (2022). Modern Web Application Development. Tech Publishers.",
        "Johnson, A., & Williams, B. (2021). Database Design Principles. Academic Press.",
        "Brown, C. (2023). Educational Technology Systems. Education Tech Journal, 15(3), 45-67.",
    ])
    
    # Generate PDF
    doc.generate()


if __name__ == "__main__":
    main()

