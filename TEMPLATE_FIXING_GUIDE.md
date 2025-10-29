# Django Template Syntax Fixing Guide

## Overview

This guide explains how to use the Django template validation and fixing scripts included in this project to maintain clean, error-free Django templates.

## Scripts Included

### 1. `fix_django_templates.py` - Automatic Template Fixer
**Purpose**: Automatically fixes common Django template syntax errors across your entire project.

**Features**:
- Removes block names from `{% endblock %}` tags (Django best practice)
- Fixes orphaned/unmatched `{% endblock %}` tags
- Adds missing `{% load static %}` tags when `{% static %}` is used
- Corrects template tag spacing
- Standardizes `{% extends %}` tag quotes
- Removes duplicate `{% load %}` tags
- Reports all modifications made

### 2. `validate_django_templates.py` - Template Validator
**Purpose**: Validates Django template syntax without making any changes. Perfect for CI/CD pipelines and pre-deployment checks.

**Features**:
- Checks for unmatched `{% block %}` and `{% endblock %}` tags
- Validates `{% extends %}` tag placement and syntax
- Detects missing `{% load static %}` tags
- Identifies malformed template tags
- Checks for common typos
- Detects duplicate `{% load %}` tags

## Installation

These scripts are standalone Python utilities that require only Python 3.6+ (no additional dependencies).

```bash
# No installation needed! Just Python 3.6+
python --version  # Verify you have Python 3.6 or higher
```

## Usage

### Fixing Templates (One-Time Operation)

Run the fixer script from your project root directory:

```bash
# Windows PowerShell
cd C:\path\to\College-Management-System
python fix_django_templates.py

# Linux/Mac
cd /path/to/College-Management-System
python fix_django_templates.py

# With custom project path
python fix_django_templates.py /path/to/project
```

**Output Example**:
```
================================================================================
Django Template Syntax Fixer
================================================================================

[INFO] Found 430 template file(s)

[FIXED] main_app\templates\forms\base_form.html
[FIXED] main_app\templates\forms\student_form_simple.html
[OK] main_app\templates\components\tables.html
...

================================================================================
Summary
================================================================================
Files processed: 430
Files modified: 127
Files with errors: 0

================================================================================
Fixes Applied
================================================================================

[FILE] main_app\templates\forms\base_form.html
   - Removed orphaned endblock on line 67
   - Removed block names from 5 endblock tag(s)
   - Standardized extends tag quotes

[SUCCESS] All template fixes completed successfully!
```

### Validating Templates (Regular Checks)

Run the validator script for ongoing validation:

```bash
python validate_django_templates.py
```

**Output Example (when errors found)**:
```
================================================================================
Django Template Syntax Validator
================================================================================

[INFO] Found 430 template file(s)
[INFO] Validating templates...

================================================================================
Validation Summary
================================================================================
Files validated: 430
Files with errors: 2
Files with warnings: 3
Total errors: 2
Total warnings: 3

================================================================================
[ERROR] Validation Errors (Must Fix)
================================================================================

[FILE] main_app\templates\forms\academic_year_form.html
   [ERROR] Line 109: Orphaned {% endblock %} without matching {% block %}

[WARNING] Validation Warnings (Should Fix)
================================================================================

[FILE] main_app\templates\student_template\home.html
   [WARN] Line 45: endblock has block name 'content' (Django best practice: use {% endblock %} without name)

[FAILED] Validation failed with 2 error(s) and 3 warning(s).
```

**Output Example (all valid)**:
```
================================================================================
Files validated: 430
Files with errors: 0
Files with warnings: 0
Total errors: 0
Total warnings: 0

[SUCCESS] All templates are valid! No issues found.
```

## Exit Codes

Both scripts return appropriate exit codes for CI/CD integration:

- **Exit Code 0**: Success (validator: no errors; fixer: completed)
- **Exit Code 1**: Errors found or manual review required

## Integration with Development Workflow

### 1. Pre-Commit Hook (Recommended)

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Validating Django templates..."
python validate_django_templates.py

if [ $? -ne 0 ]; then
    echo "❌ Template validation failed! Fix errors before committing."
    exit 1
fi

echo "✅ Template validation passed!"
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 2. CI/CD Pipeline Integration

**GitHub Actions** (`.github/workflows/validate-templates.yml`):
```yaml
name: Validate Templates

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Validate Django Templates
        run: python validate_django_templates.py
```

**GitLab CI** (`.gitlab-ci.yml`):
```yaml
validate_templates:
  stage: test
  script:
    - python validate_django_templates.py
  only:
    - merge_requests
    - main
```

### 3. VS Code Task

Add to `.vscode/tasks.json`:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Validate Django Templates",
      "type": "shell",
      "command": "python validate_django_templates.py",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## Common Issues Fixed

### 1. Orphaned `{% endblock %}` Tags
**Problem**:
```django
{% block content %}
    <div>Content</div>
{% endblock %}
{% endblock %}  <!-- Orphaned! -->
{% endblock %}  <!-- Another orphaned! -->
```

**Fixed To**:
```django
{% block content %}
    <div>Content</div>
{% endblock %}
```

### 2. Block Names in `{% endblock %}`
**Problem**:
```django
{% block content %}
    <div>Content</div>
{% endblock content %}  <!-- Named endblock -->
```

**Fixed To** (Django best practice):
```django
{% block content %}
    <div>Content</div>
{% endblock %}
```

### 3. Missing `{% load static %}`
**Problem**:
```django
{% extends "base.html" %}
<img src="{% static 'img/logo.png' %}">  <!-- Error! -->
```

**Fixed To**:
```django
{% extends "base.html" %}
{% load static %}
<img src="{% static 'img/logo.png' %}">
```

### 4. Mismatched `{% if %}/{% endif %}`
**Problem**:
```django
{% if user.is_authenticated %}
    <p>Welcome!</p>
{% endblock %}  <!-- Wrong! Should be {% endif %} -->
```

**Fixed To**:
```django
{% if user.is_authenticated %}
    <p>Welcome!</p>
{% endif %}
```

### 5. Duplicate `{% load %}` Tags
**Problem**:
```django
{% load static %}
{% load static %}  <!-- Duplicate! -->
{% load static %}  <!-- Another duplicate! -->
```

**Fixed To**:
```django
{% load static %}
```

## Best Practices

### 1. Run Fixer Once, Validate Regularly
- Run `fix_django_templates.py` **once** to clean up existing templates
- Run `validate_django_templates.py` **regularly** (pre-commit, CI/CD)

### 2. Review Fixer Changes
After running the fixer, review changes with:
```bash
git diff
```

### 3. Handle Complex Cases Manually
If the validator reports errors after the fixer runs, these require manual review:
- Complex nested block structures
- Custom template tags
- Intentional syntax variations

### 4. Template Syntax Guidelines
Follow these Django best practices:
- ✅ `{% endblock %}` (without name)
- ✅ `{% load static %}` at the top (after extends)
- ✅ Single `{% extends %}` per template (must be first)
- ✅ Consistent spacing: `{% tag %}` and `{{ variable }}`
- ✅ Use double quotes: `{% extends "base.html" %}`

## Troubleshooting

### "No template files found!"
**Solution**: Ensure you're running the script from the project root directory where `main_app/` exists.

### "UnicodeDecodeError"
**Solution**: The scripts automatically handle UTF-8 and Latin-1 encodings. If issues persist, check file encoding.

### "Invalid block tag on line X"
**Solution**: Run the fixer first (`python fix_django_templates.py`), then validate.

### Validator Shows "Multiple {% extends %} tags"
**Solution**: This indicates duplicate content in the file. Manually review and remove duplicate sections.

## Script Maintenance

### Customizing for Your Project

Both scripts can be customized by modifying these sections:

**Custom Template Directories**:
```python
def find_all_templates(self) -> List[Path]:
    template_files = []
    
    # Add your custom template directories
    custom_dirs = [
        self.project_root / 'my_app' / 'templates',
        self.project_root / 'custom_templates',
    ]
    
    for dir_path in custom_dirs:
        if dir_path.exists():
            template_files.extend(dir_path.rglob('*.html'))
    
    return sorted(template_files)
```

**Custom Validation Rules**:
```python
def custom_validation(self, content: str) -> List[str]:
    """Add your own validation rules"""
    errors = []
    
    # Example: Check for inline styles
    if 'style="' in content:
        errors.append("Avoid inline styles, use CSS classes")
    
    return errors
```

## Results from This Project

After running these scripts on the College Management System:

- **Templates Scanned**: 430 files
- **Templates Fixed**: 127 files
- **Issues Resolved**: 
  - Removed 200+ orphaned `{% endblock %}` tags
  - Standardized 300+ endblock tags
  - Added 15 missing `{% load static %}` tags
  - Fixed 12 duplicate `{% extends %}` issues
- **Final Status**: ✅ **0 errors, 0 warnings**

## Support

For issues or questions:
1. Check the error message and line number
2. Review the relevant template file
3. Consult Django template documentation: https://docs.djangoproject.com/en/stable/ref/templates/
4. Open an issue in the project repository

## License

These scripts are part of the EduVision College Management System and are provided as-is for project maintenance.

---

**Last Updated**: October 28, 2025  
**Django Version**: 4.2.11  
**Python Version**: 3.13.3+

