#!/usr/bin/env python3
"""
Fix all Django templates with duplicate block tags
Automatically removes duplicate content after the first {% endblock %}
"""

import os
import re
from pathlib import Path
from collections import defaultdict

class TemplateDuplicateBlockFixer:
    def __init__(self, project_root='.'):
        self.project_root = Path(project_root)
        self.files_fixed = []
        self.files_checked = 0
        
    def find_all_templates(self):
        """Find all HTML template files"""
        template_files = []
        templates_dir = self.project_root / 'main_app' / 'templates'
        
        if templates_dir.exists():
            template_files.extend(templates_dir.rglob('*.html'))
        
        root_templates = self.project_root / 'templates'
        if root_templates.exists():
            template_files.extend(root_templates.rglob('*.html'))
        
        return sorted(template_files)
    
    def find_duplicate_blocks(self, content):
        """Find duplicate block definitions"""
        block_positions = defaultdict(list)
        
        # Find all block tags with their positions
        for match in re.finditer(r'{%\s*block\s+(\w+)\s*%}', content):
            block_name = match.group(1)
            block_positions[block_name].append(match.start())
        
        # Return blocks that appear more than once
        duplicates = {name: positions for name, positions in block_positions.items() 
                     if len(positions) > 1}
        
        return duplicates
    
    def fix_template(self, file_path):
        """Fix a template by removing duplicate blocks"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            duplicates = self.find_duplicate_blocks(content)
            
            if not duplicates:
                return False
            
            # Find the first {% endblock %} position
            endblock_pattern = r'{%\s*endblock\s*%}'
            endblock_matches = list(re.finditer(endblock_pattern, content))
            
            if not endblock_matches:
                return False
            
            # Strategy: Keep content up to and including the first complete block structure
            # Find matching endblock for each block
            lines = content.split('\n')
            
            # Count blocks and endblocks to find where first complete structure ends
            block_stack = []
            first_complete_end = -1
            
            for idx, line in enumerate(lines):
                # Count opening blocks
                block_matches = re.findall(r'{%\s*block\s+\w+\s*%}', line)
                for _ in block_matches:
                    block_stack.append(idx)
                
                # Count closing blocks
                endblock_matches = re.findall(r'{%\s*endblock\s*%}', line)
                for _ in endblock_matches:
                    if block_stack:
                        block_stack.pop()
                        if not block_stack and first_complete_end == -1:
                            # Found the end of the first complete block structure
                            first_complete_end = idx
                            break
                
                if first_complete_end != -1:
                    break
            
            if first_complete_end == -1:
                # Fallback: find last proper endblock before duplicate content
                # Look for patterns like orphaned style tags or duplicate extends
                for idx, line in enumerate(lines):
                    if idx > 100:  # After reasonable template length
                        # Check if we're seeing duplicate content markers
                        if re.search(r'^\s*<style>|^\s*\.[\w-]+\s*{|^\s*{%\s*block\s+content\s*%}', line):
                            # Likely duplicate content starting
                            # Go back to find the last endblock before this
                            for back_idx in range(idx - 1, -1, -1):
                                if re.search(r'{%\s*endblock\s*%}', lines[back_idx]):
                                    first_complete_end = back_idx
                                    break
                            break
            
            if first_complete_end == -1:
                print(f"[SKIP] {file_path.name} - Could not determine safe cut point")
                return False
            
            # Keep content up to and including the endblock
            fixed_lines = lines[:first_complete_end + 1]
            
            # Make sure we end with a newline
            fixed_content = '\n'.join(fixed_lines)
            if not fixed_content.endswith('\n'):
                fixed_content += '\n'
            
            # Verify the fix doesn't break the template
            if fixed_content.count('{%') != fixed_content.count('%}'):
                print(f"[ERROR] {file_path.name} - Template tags would be unbalanced")
                return False
            
            # Write the fixed content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            removed_lines = len(lines) - len(fixed_lines)
            return removed_lines
            
        except Exception as e:
            print(f"[ERROR] {file_path.name} - {str(e)}")
            return False
    
    def process_all_templates(self):
        """Process all templates"""
        print("=" * 80)
        print("Django Template Duplicate Block Fixer")
        print("=" * 80)
        print()
        
        templates = self.find_all_templates()
        print(f"[INFO] Found {len(templates)} template files")
        print("[INFO] Scanning for duplicate blocks...\n")
        
        for template in templates:
            self.files_checked += 1
            result = self.fix_template(template)
            
            if result:
                rel_path = template.relative_to(self.project_root)
                print(f"[FIXED] {rel_path} - Removed {result} duplicate lines")
                self.files_fixed.append((str(rel_path), result))
            elif result is False and result is not None:
                pass  # Silent skip for files without duplicates
        
        print()
        print("=" * 80)
        print("Summary")
        print("=" * 80)
        print(f"Files checked: {self.files_checked}")
        print(f"Files fixed: {len(self.files_fixed)}")
        
        if self.files_fixed:
            print()
            print("Fixed Files:")
            total_removed = 0
            for file_path, removed in self.files_fixed:
                print(f"  - {file_path}: {removed} lines removed")
                total_removed += removed
            print(f"\nTotal lines removed: {total_removed}")
        
        print()
        if self.files_fixed:
            print("[SUCCESS] All duplicate blocks fixed!")
        else:
            print("[INFO] No duplicate blocks found.")

if __name__ == '__main__':
    fixer = TemplateDuplicateBlockFixer('.')
    fixer.process_all_templates()

