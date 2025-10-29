#!/usr/bin/env python3
"""
Django Template Syntax Fixer
Automatically fixes common Django template syntax errors across the project.

Usage:
    python fix_django_templates.py

Features:
- Fixes unmatched {% block %} and {% endblock %} tags
- Removes block names from {% endblock %} tags (Django best practice)
- Adds missing {% load static %} tags when {% static %} is used
- Corrects template tag spacing
- Fixes template inheritance issues
- Reports all modifications made
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple, Dict
from collections import defaultdict


class DjangoTemplateFixer:
    """
    Comprehensive Django template syntax fixer and validator.
    """
    
    def __init__(self, project_root: str = '.'):
        self.project_root = Path(project_root)
        self.fixes_applied = defaultdict(list)
        self.errors_found = defaultdict(list)
        self.files_processed = 0
        self.files_modified = 0
        
    def find_all_templates(self) -> List[Path]:
        """Find all HTML template files in the project."""
        template_files = []
        templates_dir = self.project_root / 'main_app' / 'templates'
        
        if templates_dir.exists():
            template_files.extend(templates_dir.rglob('*.html'))
        
        # Also check root templates directory if it exists
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
            # Try with different encoding if utf-8 fails
            with open(file_path, 'r', encoding='latin-1') as f:
                return f.read()
    
    def write_template(self, file_path: Path, content: str):
        """Write template file with UTF-8 encoding."""
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
    
    def fix_endblock_tags(self, content: str) -> Tuple[str, List[str]]:
        """
        Remove block names from {% endblock %} tags.
        Django best practice: {% endblock %} instead of {% endblock blockname %}
        """
        fixes = []
        
        # Pattern to find {% endblock blockname %}
        pattern = r'{%\s*endblock\s+(\w+)\s*%}'
        matches = re.findall(pattern, content)
        
        if matches:
            fixes.append(f"Removed block names from {len(matches)} endblock tag(s)")
            content = re.sub(pattern, '{% endblock %}', content)
        
        return content, fixes
    
    def fix_orphaned_endblocks(self, content: str) -> Tuple[str, List[str]]:
        """
        Remove orphaned {% endblock %} tags that don't have matching {% block %}.
        This is a common cause of TemplateSyntaxError.
        """
        fixes = []
        
        # Find all block and endblock tags
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        endblock_pattern = r'{%\s*endblock\s*(?:\w+)?\s*%}'
        
        blocks = re.findall(block_pattern, content)
        endblocks = re.findall(r'{%\s*endblock\s*(?:(\w+))?\s*%}', content)
        
        # Split content into lines for better processing
        lines = content.split('\n')
        block_stack = []
        lines_to_remove = []
        
        for idx, line in enumerate(lines):
            # Track block openings
            block_match = re.search(block_pattern, line)
            if block_match:
                block_stack.append((block_match.group(1), idx))
            
            # Track block closings
            endblock_match = re.search(endblock_pattern, line)
            if endblock_match:
                if block_stack:
                    block_stack.pop()
                else:
                    # This is an orphaned endblock
                    # Check if this line ONLY contains the endblock tag
                    if line.strip() == endblock_match.group(0).strip():
                        lines_to_remove.append(idx)
                        fixes.append(f"Removed orphaned endblock on line {idx + 1}")
        
        # Remove lines in reverse order to maintain indices
        for idx in reversed(lines_to_remove):
            lines.pop(idx)
        
        content = '\n'.join(lines)
        return content, fixes
    
    def add_missing_load_static(self, content: str) -> Tuple[str, List[str]]:
        """
        Add {% load static %} at the top of templates that use {% static %} but don't load it.
        """
        fixes = []
        
        # Check if template uses {% static %}
        uses_static = bool(re.search(r'{%\s*static\s+', content))
        
        if not uses_static:
            return content, fixes
        
        # Check if {% load static %} is already present
        has_load_static = bool(re.search(r'{%\s*load\s+static\s*%}', content))
        
        if has_load_static:
            return content, fixes
        
        # Find the position to insert {% load static %}
        lines = content.split('\n')
        insert_position = 0
        
        # Skip {% extends %} tag if present (load must come after extends)
        for idx, line in enumerate(lines):
            if re.search(r'{%\s*extends\s+', line):
                insert_position = idx + 1
                break
        
        # Insert {% load static %}
        lines.insert(insert_position, '{% load static %}')
        fixes.append("Added missing {% load static %} tag")
        
        content = '\n'.join(lines)
        return content, fixes
    
    def fix_template_tag_spacing(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix improper spacing in template tags.
        Ensures format: {% tag %} and {{ variable }}
        """
        fixes = []
        original = content
        
        # Fix excessive spaces in template tags: {%  tag  %} -> {% tag %}
        content = re.sub(r'{%\s{2,}', '{% ', content)
        content = re.sub(r'\s{2,}%}', ' %}', content)
        
        # Fix excessive spaces in variables: {{  var  }} -> {{ var }}
        content = re.sub(r'{{\s{2,}', '{{ ', content)
        content = re.sub(r'\s{2,}}}', ' }}', content)
        
        if content != original:
            fixes.append("Fixed template tag spacing")
        
        return content, fixes
    
    def validate_block_matching(self, content: str, file_path: Path) -> List[str]:
        """
        Validate that all {% block %} tags have matching {% endblock %} tags.
        Returns list of errors found.
        """
        errors = []
        
        # Find all block tags
        block_pattern = r'{%\s*block\s+(\w+)\s*%}'
        endblock_pattern = r'{%\s*endblock\s*%}'
        
        lines = content.split('\n')
        block_stack = []
        
        for idx, line in enumerate(lines, 1):
            # Track block openings
            for match in re.finditer(block_pattern, line):
                block_name = match.group(1)
                block_stack.append((block_name, idx))
            
            # Track block closings
            endblock_count = len(re.findall(endblock_pattern, line))
            for _ in range(endblock_count):
                if block_stack:
                    block_stack.pop()
                else:
                    errors.append(f"Line {idx}: Orphaned endblock without matching block")
        
        # Check for unclosed blocks
        for block_name, line_num in block_stack:
            errors.append(f"Line {line_num}: Unclosed block '{block_name}'")
        
        return errors
    
    def fix_extends_syntax(self, content: str) -> Tuple[str, List[str]]:
        """
        Fix common {% extends %} syntax issues.
        """
        fixes = []
        
        # Ensure extends uses quotes properly
        # Fix single quotes to double quotes for consistency
        pattern = r"{%\s*extends\s+'([^']+)'\s*%}"
        if re.search(pattern, content):
            content = re.sub(pattern, r'{% extends "\1" %}', content)
            fixes.append("Standardized extends tag quotes")
        
        return content, fixes
    
    def remove_duplicate_load_tags(self, content: str) -> Tuple[str, List[str]]:
        """
        Remove duplicate {% load %} tags.
        """
        fixes = []
        lines = content.split('\n')
        seen_loads = set()
        new_lines = []
        removed_count = 0
        
        for line in lines:
            load_match = re.match(r'{%\s*load\s+(.+?)\s*%}', line.strip())
            if load_match:
                load_content = load_match.group(1)
                if load_content in seen_loads:
                    removed_count += 1
                    continue
                seen_loads.add(load_content)
            new_lines.append(line)
        
        if removed_count > 0:
            fixes.append(f"Removed {removed_count} duplicate load tag(s)")
            content = '\n'.join(new_lines)
        
        return content, fixes
    
    def fix_template(self, file_path: Path) -> bool:
        """
        Apply all fixes to a single template file.
        Returns True if file was modified.
        """
        try:
            original_content = self.read_template(file_path)
            content = original_content
            all_fixes = []
            
            # Apply all fixes
            content, fixes = self.fix_orphaned_endblocks(content)
            all_fixes.extend(fixes)
            
            content, fixes = self.fix_endblock_tags(content)
            all_fixes.extend(fixes)
            
            content, fixes = self.add_missing_load_static(content)
            all_fixes.extend(fixes)
            
            content, fixes = self.fix_template_tag_spacing(content)
            all_fixes.extend(fixes)
            
            content, fixes = self.fix_extends_syntax(content)
            all_fixes.extend(fixes)
            
            content, fixes = self.remove_duplicate_load_tags(content)
            all_fixes.extend(fixes)
            
            # Validate after fixes
            errors = self.validate_block_matching(content, file_path)
            
            if errors:
                self.errors_found[str(file_path)] = errors
            
            # Write back if modified
            if content != original_content:
                self.write_template(file_path, content)
                self.fixes_applied[str(file_path)] = all_fixes
                return True
            
            return False
            
        except Exception as e:
            self.errors_found[str(file_path)].append(f"Error processing file: {str(e)}")
            return False
    
    def process_all_templates(self):
        """Process all templates in the project."""
        print("=" * 80)
        print("Django Template Syntax Fixer")
        print("=" * 80)
        print()
        
        templates = self.find_all_templates()
        
        if not templates:
            print("[ERROR] No template files found!")
            return
        
        print(f"[INFO] Found {len(templates)} template file(s)")
        print()
        
        for template in templates:
            self.files_processed += 1
            relative_path = template.relative_to(self.project_root)
            
            if self.fix_template(template):
                self.files_modified += 1
                print(f"[FIXED] {relative_path}")
            else:
                print(f"[OK] {relative_path}")
        
        # Print summary
        print()
        print("=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Files processed: {self.files_processed}")
        print(f"Files modified: {self.files_modified}")
        print(f"Files with errors: {len(self.errors_found)}")
        print()
        
        # Print detailed fixes
        if self.fixes_applied:
            print("\n" + "=" * 80)
            print("Fixes Applied")
            print("=" * 80)
            for file_path, fixes in self.fixes_applied.items():
                rel_path = Path(file_path).relative_to(self.project_root)
                print(f"\n[FILE] {rel_path}")
                for fix in fixes:
                    print(f"   - {fix}")
        
        # Print errors
        if self.errors_found:
            print("\n" + "=" * 80)
            print("[WARNING] Errors Found (Manual Review Required)")
            print("=" * 80)
            for file_path, errors in self.errors_found.items():
                rel_path = Path(file_path).relative_to(self.project_root)
                print(f"\n[ERROR] {rel_path}")
                for error in errors:
                    print(f"   - {error}")
        else:
            print("\n[SUCCESS] No errors found! All templates are valid.")


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
        print("Usage: python fix_django_templates.py [project_root]")
        sys.exit(1)
    
    # Create fixer and process templates
    fixer = DjangoTemplateFixer(project_root)
    fixer.process_all_templates()
    
    # Exit with appropriate code
    if fixer.errors_found:
        print("\n[WARNING] Some issues require manual review. Please check the errors above.")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All template fixes completed successfully!")
        sys.exit(0)


if __name__ == '__main__':
    main()

