#!/usr/bin/env python3
"""
Django Template Syntax Validator
Validates Django template syntax without making changes.
Perfect for CI/CD pipelines and pre-deployment checks.

Usage:
    python validate_django_templates.py
    
Exit codes:
    0 - All templates valid
    1 - Validation errors found
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict


class DjangoTemplateValidator:
    """
    Validates Django template syntax without modifying files.
    """
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.validation_errors = defaultdict(list)
        self.validation_warnings = defaultdict(list)
        self.files_validated = 0
        
    def find_all_templates(self) -> List[Path]:
        """Find all HTML template files in the project."""
        template_files = []
        templates_dir = self.project_root / 'main_app' / 'templates'
        
        if templates_dir.exists():
            template_files.extend(templates_dir.rglob('*.html'))
        
        # Also check root templates directory
        root_templates = self.project_root / 'templates'
        if root_templates.exists():
            template_files.extend(root_templates.rglob('*.html'))
        
        return sorted(template_files)
    
    def read_template(self, file_path: Path) -> str:
        """Read template file with proper encoding."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def check_block_matching(self, content: str) -> Tuple[List[str], List[str]]:
        """
        Check that all {% block %} tags have matching {% endblock %} tags.
        Returns (errors, warnings).
        """
        errors = []
        warnings = []
        
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        endblock_pattern = r'{%\s*endblock\s*(?:(\w+))?\s*%}'
        
        lines = content.split('\n')
        block_stack = []
        
        for idx, line in enumerate(lines, 1):
            # Track block openings
            for match in re.finditer(block_pattern, line):
                block_name = match.group(1)
                block_stack.append((block_name, idx))
            
            # Track block closings
            for match in re.finditer(endblock_pattern, line):
                block_name = match.group(1)
                
                if block_name:
                    warnings.append(
                        f"Line {idx}: endblock has block name '{block_name}' "
                        f"(Django best practice: use {{% endblock %}} without name)"
                    )
                
                if block_stack:
                    opened_name, opened_line = block_stack.pop()
                    if block_name and block_name != opened_name:
                        errors.append(
                            f"Line {idx}: endblock '{block_name}' doesn't match "
                            f"block '{opened_name}' opened on line {opened_line}"
                        )
                else:
                    errors.append(
                        f"Line {idx}: Orphaned {{% endblock %}} without matching {{% block %}}"
                    )
        
        # Check for unclosed blocks
        for block_name, line_num in block_stack:
            errors.append(
                f"Line {line_num}: Unclosed {{% block {block_name} %}}"
            )
        
        return errors, warnings
    
    def check_load_static(self, content: str) -> List[str]:
        """
        Check if {% static %} is used without {% load static %}.
        """
        warnings = []
        
        uses_static = bool(re.search(r'{%\s*static\s+', content))
        has_load_static = bool(re.search(r'{%\s*load\s+static\s*%}', content))
        
        if uses_static and not has_load_static:
            warnings.append("Template uses {{% static %}} but missing {{% load static %}}")
        
        return warnings
    
    def check_template_tag_syntax(self, content: str) -> List[str]:
        """
        Check for malformed template tag syntax.
        """
        errors = []
        lines = content.split('\n')
        
        for idx, line in enumerate(lines, 1):
            # Check for template tags with excessive spaces
            if re.search(r'{%\s{3,}|\s{3,}%}', line):
                errors.append(f"Line {idx}: Excessive whitespace in template tag")
            
            # Check for unclosed template tags
            open_tags = line.count('{%')
            close_tags = line.count('%}')
            if open_tags != close_tags:
                errors.append(f"Line {idx}: Mismatched template tag delimiters")
            
            # Check for unclosed variables
            open_vars = line.count('{{')
            close_vars = line.count('}}')
            if open_vars != close_vars:
                errors.append(f"Line {idx}: Mismatched variable delimiters")
        
        return errors
    
    def check_extends_syntax(self, content: str) -> List[str]:
        """
        Check {% extends %} tag syntax and placement.
        """
        errors = []
        lines = content.split('\n')
        
        extends_pattern = r'{%\s*extends\s+["\']([^"\']+)["\']\s*%}'
        found_extends = False
        extends_line = -1
        
        for idx, line in enumerate(lines):
            # Check if line has extends
            if re.search(r'{%\s*extends\s+', line):
                if found_extends:
                    errors.append(
                        f"Line {idx + 1}: Multiple {{% extends %}} tags found "
                        f"(first at line {extends_line + 1})"
                    )
                else:
                    found_extends = True
                    extends_line = idx
                    
                    # Check if extends is not at the top (allowing comments/whitespace)
                    non_empty_before = False
                    for prev_line in lines[:idx]:
                        stripped = prev_line.strip()
                        if stripped and not stripped.startswith('{#') and not stripped.startswith('<!--'):
                            non_empty_before = True
                            break
                    
                    if non_empty_before:
                        errors.append(
                            f"Line {idx + 1}: {{% extends %}} should be the first tag in the template"
                        )
                
                # Check proper quote usage
                if not re.search(extends_pattern, line):
                    errors.append(
                        f"Line {idx + 1}: {{% extends %}} tag has improper syntax "
                        f"(should be: {{{{ extends 'template.html' }}}})"
                    )
        
        return errors
    
    def check_common_typos(self, content: str) -> List[str]:
        """
        Check for common typos in template tags.
        """
        warnings = []
        lines = content.split('\n')
        
        common_typos = {
            r'{%\s*end\s+block\s*%}': '{{% endblock %}}',
            r'{%\s*end\s+if\s*%}': '{{% endif %}}',
            r'{%\s*end\s+for\s*%}': '{{% endfor %}}',
            r'{%\s*end\s+with\s*%}': '{{% endwith %}}',
        }
        
        for idx, line in enumerate(lines, 1):
            for typo_pattern, correct in common_typos.items():
                if re.search(typo_pattern, line):
                    warnings.append(
                        f"Line {idx}: Possible typo - use '{correct}' instead"
                    )
        
        return warnings
    
    def check_duplicate_loads(self, content: str) -> List[str]:
        """
        Check for duplicate {% load %} tags.
        """
        warnings = []
        lines = content.split('\n')
        
        load_pattern = r'{%\s*load\s+(.+?)\s*%}'
        seen_loads = {}
        
        for idx, line in enumerate(lines, 1):
            match = re.search(load_pattern, line)
            if match:
                load_content = match.group(1)
                if load_content in seen_loads:
                    warnings.append(
                        f"Line {idx}: Duplicate {{{{ load {load_content} }}}} "
                        f"(already loaded on line {seen_loads[load_content]})"
                    )
                else:
                    seen_loads[load_content] = idx
        
        return warnings
    
    def validate_template(self, file_path: Path):
        """
        Validate a single template file.
        """
        try:
            content = self.read_template(file_path)
            file_key = str(file_path)
            
            # Run all validation checks
            errors, warnings = self.check_block_matching(content)
            self.validation_errors[file_key].extend(errors)
            self.validation_warnings[file_key].extend(warnings)
            
            warnings = self.check_load_static(content)
            self.validation_warnings[file_key].extend(warnings)
            
            errors = self.check_template_tag_syntax(content)
            self.validation_errors[file_key].extend(errors)
            
            errors = self.check_extends_syntax(content)
            self.validation_errors[file_key].extend(errors)
            
            warnings = self.check_common_typos(content)
            self.validation_warnings[file_key].extend(warnings)
            
            warnings = self.check_duplicate_loads(content)
            self.validation_warnings[file_key].extend(warnings)
            
        except Exception as e:
            self.validation_errors[file_key].append(f"Failed to read file: {str(e)}")
    
    def validate_all_templates(self):
        """Validate all templates in the project."""
        print("=" * 80)
        print("Django Template Syntax Validator")
        print("=" * 80)
        print()
        
        templates = self.find_all_templates()
        
        if not templates:
            print("[ERROR] No template files found!")
            return False
        
        print(f"[INFO] Found {len(templates)} template file(s)")
        print("[INFO] Validating templates...\n")
        
        for template in templates:
            self.files_validated += 1
            self.validate_template(template)
        
        # Calculate results
        files_with_errors = sum(1 for errors in self.validation_errors.values() if errors)
        files_with_warnings = sum(1 for warnings in self.validation_warnings.values() if warnings)
        total_errors = sum(len(errors) for errors in self.validation_errors.values())
        total_warnings = sum(len(warnings) for warnings in self.validation_warnings.values())
        
        # Print summary
        print("=" * 80)
        print("Validation Summary")
        print("=" * 80)
        print(f"Files validated: {self.files_validated}")
        print(f"Files with errors: {files_with_errors}")
        print(f"Files with warnings: {files_with_warnings}")
        print(f"Total errors: {total_errors}")
        print(f"Total warnings: {total_warnings}")
        print()
        
        # Print errors
        if self.validation_errors:
            print("=" * 80)
            print("[ERROR] Validation Errors (Must Fix)")
            print("=" * 80)
            for file_path, errors in self.validation_errors.items():
                if errors:
                    rel_path = Path(file_path).relative_to(self.project_root)
                    print(f"\n[FILE] {rel_path}")
                    for error in errors:
                        print(f"   [ERROR] {error}")
        
        # Print warnings
        if self.validation_warnings:
            print("\n" + "=" * 80)
            print("[WARNING] Validation Warnings (Should Fix)")
            print("=" * 80)
            for file_path, warnings in self.validation_warnings.items():
                if warnings:
                    rel_path = Path(file_path).relative_to(self.project_root)
                    print(f"\n[FILE] {rel_path}")
                    for warning in warnings:
                        print(f"   [WARN] {warning}")
        
        # Final result
        if not self.validation_errors and not self.validation_warnings:
            print("\n[SUCCESS] All templates are valid! No issues found.")
            return True
        elif not self.validation_errors:
            print("\n[SUCCESS] No errors found! Only warnings present.")
            return True
        else:
            print(f"\n[FAILED] Validation failed with {total_errors} error(s) and {total_warnings} warning(s).")
            return False


def main():
    """Main entry point."""
    # Determine project root
    if len(sys.argv) > 1:
        project_root = sys.argv[1]
    else:
        project_root = '.'
    
    # Check if we're in the right directory
    project_path = Path(project_root)
    if not (project_path / 'main_app').exists():
        print("[ERROR] main_app directory not found!")
        print("Please run this script from the project root directory.")
        print("Usage: python validate_django_templates.py [project_root]")
        sys.exit(1)
    
    # Create validator and validate templates
    validator = DjangoTemplateValidator(project_root)
    success = validator.validate_all_templates()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()

