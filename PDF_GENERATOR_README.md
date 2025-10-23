# Project Documentation PDF Generator

A Python script that generates professionally formatted project documentation PDFs following academic standards.

## Features

✓ **Consistent Styling** - Follows document_style.txt specifications:
  - Times-Bold 18pt for headings
  - Times-Bold 14pt for subheadings  
  - Times-Roman 12pt for body text with 1.5x line spacing
  - A4 page size with 1-inch margins
  - Justified text alignment

✓ **Complete Structure** - Includes all standard sections:
  - Title Page (centered, uppercase)
  - Certificate
  - Declaration
  - Acknowledgment
  - Abstract
  - Table of Contents
  - Main Chapters (Introduction, Requirements, Design, Implementation, Testing, Coding, Screens, Conclusion)
  - Bibliography

✓ **Automatic Page Numbers** - Bottom-center page numbering on all pages

✓ **Modular & Reusable** - Clean class-based structure for easy customization

## Requirements

```bash
pip install reportlab
```

The script will automatically install Pillow (required by reportlab) if not present.

## Quick Start

1. **Generate PDF with default content:**
```bash
python generate_project_documentation.py
```

This creates `Generated_Project_Report.pdf` with placeholder content.

2. **Customize the content** by editing the `main()` function in `generate_project_documentation.py`

## Customization Guide

### Update Project Details

Edit the title page section:
```python
generator.add_title_page(
    project_title="Your Project Title",
    subtitle="Your Subtitle",
    team_details=[
        "Student Name 1 (Roll No: 123)",
        "Student Name 2 (Roll No: 456)",
    ],
    guide_name="Prof. Guide Name<br/>Department"
)
```

### Add Custom Chapters

Use the `add_chapter()` method:
```python
generator.add_chapter(
    chapter_number=1,
    chapter_title="YOUR CHAPTER",
    sections=[
        {
            "title": "Section Name",
            "content": "Your content here with <b>HTML formatting</b> supported."
        },
        {
            "title": "Another Section",
            "content": "More content..."
        }
    ]
)
```

### Modify Styles

Edit the `_create_styles()` method to change fonts, sizes, spacing:
```python
styles['Body'] = ParagraphStyle(
    'Body',
    fontName='Times-Roman',
    fontSize=12,
    leading=18,  # Line spacing
    alignment=TA_JUSTIFY,
    spaceAfter=12,
)
```

### Add Images

To add images to sections:
```python
from reportlab.platypus import Image

# In your section content:
generator.story.append(Image('path/to/image.png', width=4*inch, height=3*inch))
generator.story.append(Spacer(1, 0.2*inch))
```

### Add Tables

For data tables in sections:
```python
from reportlab.platypus import Table, TableStyle

data = [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Row 1 Col 1', 'Row 1 Col 2', 'Row 1 Col 3'],
    ['Row 2 Col 1', 'Row 2 Col 2', 'Row 2 Col 3'],
]

table = Table(data)
table.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
    ('FONTSIZE', (0, 0), (-1, 0), 12),
    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ('GRID', (0, 0), (-1, -1), 1, colors.black),
]))

generator.story.append(table)
```

## Class Structure

### `ProjectDocumentGenerator`

Main class for PDF generation.

**Key Methods:**
- `add_title_page()` - Title page with project details
- `add_certificate_page()` - Official certificate
- `add_declaration_page()` - Student declaration
- `add_acknowledgment_page()` - Acknowledgments
- `add_abstract_page()` - Project abstract
- `add_table_of_contents()` - TOC with chapters
- `add_chapter()` - Add chapters with sections
- `add_bibliography()` - References section
- `generate()` - Build final PDF

### `NumberedCanvas`

Custom canvas class that adds automatic page numbering.

## Advanced Customization

### Change Page Size

```python
from reportlab.lib.pagesizes import LETTER, A4

self.doc = SimpleDocTemplate(
    output_filename,
    pagesize=LETTER,  # or A4
    # ... margins
)
```

### Custom Headers/Footers

Modify `NumberedCanvas.draw_page_number()` to add headers:
```python
def draw_page_number(self, page_count):
    # Header
    self.setFont("Times-Bold", 10)
    self.drawCentredString(A4[0] / 2, A4[1] - 0.5*inch, "Your Header Text")
    
    # Footer (page number)
    self.setFont("Times-Roman", 10)
    self.drawCentredString(A4[0] / 2, 0.5 * inch, f"Page {self._pageNumber}")
```

### Add Watermark

```python
def draw_page_number(self, page_count):
    # Watermark
    self.saveState()
    self.setFont("Times-Roman", 60)
    self.setFillGray(0.9)
    self.drawCentredString(A4[0]/2, A4[1]/2, "DRAFT")
    self.restoreState()
    
    # Page number
    self.setFont("Times-Roman", 10)
    self.drawCentredString(A4[0] / 2, 0.5 * inch, f"Page {self._pageNumber}")
```

## Output

The script generates `Generated_Project_Report.pdf` in the current directory with:
- Professional academic formatting
- Automatic page numbering
- All standard sections
- Ready-to-fill placeholders

## Tips

1. **Test Incrementally** - Generate PDF after each major change to catch formatting issues early
2. **Use HTML Tags** - Content supports basic HTML: `<b>`, `<i>`, `<br/>`, `<u>`
3. **Paragraph Breaks** - Use `<br/><br/>` for paragraph spacing in content
4. **Keep It Simple** - Don't over-complicate layouts; academic docs favor clarity
5. **Check Margins** - Preview PDF to ensure content fits within margins

## Example Usage for Different Projects

### Quick Template

```python
from generate_project_documentation import ProjectDocumentGenerator

# Initialize
gen = ProjectDocumentGenerator("MyProject_Report.pdf")

# Add pages
gen.add_title_page("My Project", "Subtitle", ["Student 1"], "Prof. Guide")
gen.add_certificate_page("University", "CS Dept", "My Project", ["Student 1"])
gen.add_declaration_page(["Student 1"], "My Project")
gen.add_acknowledgment_page()
gen.add_abstract_page("My project abstract text...")

# TOC
gen.add_table_of_contents([{"title": "INTRODUCTION"}, {"title": "CONCLUSION"}])

# Chapters
gen.add_chapter(1, "INTRODUCTION", [
    {"title": "Overview", "content": "Project overview..."},
])

gen.add_chapter(2, "CONCLUSION", [
    {"title": "Summary", "content": "Summary..."},
])

# Bibliography
gen.add_bibliography(["Reference 1", "Reference 2"])

# Generate
gen.generate()
```

## Troubleshooting

**PDF not generating?**
- Check reportlab is installed: `pip list | grep reportlab`
- Ensure write permissions in current directory
- Check console for error messages

**Formatting issues?**
- Verify HTML tags are properly closed
- Check content doesn't contain special characters that need escaping
- Test with simpler content first

**Missing fonts?**
- Times-Roman and Times-Bold are standard PDF fonts
- For custom fonts, register them with reportlab's `pdfmetrics`

## License

This script is part of the College Management System project.

## Support

For issues or questions, please refer to the project documentation or contact the development team.
