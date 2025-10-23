"""
Custom validators for the College Management System
"""

import os
import re
try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import mimetypes


class PasswordComplexityValidator:
    """
    Validate password complexity for production security
    """
    
    def __init__(self, min_length=8, require_uppercase=True, require_lowercase=True, 
                 require_numbers=True, require_special_chars=True):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special_chars = require_special_chars
    
    def validate(self, password, user=None):
        """
        Validate password complexity
        """
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(
                ValidationError(
                    f'Password must be at least {self.min_length} characters long.',
                    code='password_too_short',
                )
            )
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one uppercase letter.',
                    code='password_no_upper',
                )
            )
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one lowercase letter.',
                    code='password_no_lower',
                )
            )
        
        # Check for numbers
        if self.require_numbers and not re.search(r'\d', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one number.',
                    code='password_no_number',
                )
            )
        
        # Check for special characters
        if self.require_special_chars and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append(
                ValidationError(
                    'Password must contain at least one special character (!@#$%^&*(),.?":{}|<>)',
                    code='password_no_special',
                )
            )
        
        # Check for common weak patterns
        weak_patterns = [
            r'(.)\1{2,}',  # Repeated characters (aaa, 111, etc.)
            r'(012|123|234|345|456|567|678|789|890)',  # Sequential numbers
            r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
            r'(qwerty|asdfgh|zxcvbn)',  # Keyboard patterns
        ]
        
        for pattern in weak_patterns:
            if re.search(pattern, password.lower()):
                errors.append(
                    ValidationError(
                        'Password contains weak patterns. Avoid repeated characters, sequential numbers/letters, or keyboard patterns.',
                        code='password_weak_pattern',
                    )
                )
                break
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """
        Return help text for password requirements
        """
        requirements = [f'At least {self.min_length} characters']
        
        if self.require_uppercase:
            requirements.append('One uppercase letter')
        if self.require_lowercase:
            requirements.append('One lowercase letter')
        if self.require_numbers:
            requirements.append('One number')
        if self.require_special_chars:
            requirements.append('One special character')
        
        return 'Password must contain: ' + ', '.join(requirements)


class FileUploadValidator:
    """
    Validate uploaded files for security and type
    """
    
    # Allowed file types by category
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'spreadsheet': ['.xls', '.xlsx', '.csv'],
        'presentation': ['.ppt', '.pptx'],
        'archive': ['.zip', '.rar', '.7z'],
        'video': ['.mp4', '.avi', '.mov', '.wmv', '.flv'],
        'audio': ['.mp3', '.wav', '.ogg', '.m4a'],
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 5 * 1024 * 1024,  # 5MB
        'document': 10 * 1024 * 1024,  # 10MB
        'spreadsheet': 5 * 1024 * 1024,  # 5MB
        'presentation': 20 * 1024 * 1024,  # 20MB
        'archive': 50 * 1024 * 1024,  # 50MB
        'video': 100 * 1024 * 1024,  # 100MB
        'audio': 20 * 1024 * 1024,  # 20MB
    }
    
    # Dangerous file extensions
    DANGEROUS_EXTENSIONS = [
        '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js',
        '.jar', '.app', '.deb', '.pkg', '.dmg', '.iso', '.bin'
    ]
    
    def __init__(self, allowed_types=None, max_size=None):
        self.allowed_types = allowed_types or list(self.ALLOWED_EXTENSIONS.keys())
        self.max_size = max_size
    
    def validate(self, uploaded_file):
        """
        Validate uploaded file
        """
        if not uploaded_file:
            raise ValidationError('No file provided.')
        
        # Check file name
        if not uploaded_file.name:
            raise ValidationError('Invalid file name.')
        
        # Get file extension
        file_name = uploaded_file.name.lower()
        file_extension = os.path.splitext(file_name)[1]
        
        # Check for dangerous extensions
        if file_extension in self.DANGEROUS_EXTENSIONS:
            raise ValidationError(f'File type {file_extension} is not allowed for security reasons.')
        
        # Check file size
        file_size = uploaded_file.size
        if self.max_size and file_size > self.max_size:
            raise ValidationError(f'File size ({file_size} bytes) exceeds maximum allowed size ({self.max_size} bytes).')
        
        # Determine file type
        file_type = self._get_file_type(file_extension)
        if not file_type:
            raise ValidationError(f'File type {file_extension} is not supported.')
        
        # Check if file type is allowed
        if file_type not in self.allowed_types:
            raise ValidationError(f'File type {file_type} is not allowed.')
        
        # Check file size for specific type
        type_max_size = self.MAX_FILE_SIZES.get(file_type)
        if type_max_size and file_size > type_max_size:
            raise ValidationError(f'File size exceeds maximum allowed size for {file_type} files ({type_max_size} bytes).')
        
        # Validate file content using python-magic (if available)
        if HAS_MAGIC:
            try:
                uploaded_file.seek(0)
                file_content = uploaded_file.read(1024)  # Read first 1KB
                uploaded_file.seek(0)  # Reset file pointer
                
                if hasattr(magic, 'from_buffer'):
                    mime_type = magic.from_buffer(file_content, mime=True)
                    expected_mime = mimetypes.guess_type(file_name)[0]
                    
                    if expected_mime and mime_type != expected_mime:
                        # Allow some flexibility for similar MIME types
                        if not self._is_similar_mime_type(mime_type, expected_mime):
                            raise ValidationError(f'File content does not match expected type. Expected: {expected_mime}, Detected: {mime_type}')
            except Exception as e:
                raise ValidationError(f'Error validating file content: {str(e)}')
        
        return True
    
    def _get_file_type(self, extension):
        """
        Determine file type from extension
        """
        for file_type, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return file_type
        return None
    
    def _is_similar_mime_type(self, mime1, mime2):
        """
        Check if two MIME types are similar enough to allow
        """
        # Common similar MIME types
        similar_types = {
            'image/jpeg': ['image/jpg'],
            'image/jpg': ['image/jpeg'],
            'text/plain': ['text/csv'],
            'application/vnd.ms-excel': ['application/csv'],
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['application/vnd.ms-excel'],
        }
        
        if mime1 == mime2:
            return True
        
        if mime1 in similar_types and mime2 in similar_types[mime1]:
            return True
        
        return False


class PhoneNumberValidator(RegexValidator):
    """
    Validate Indian phone numbers
    """
    regex = r'^(\+91|91)?[6-9]\d{9}$'
    message = _('Enter a valid Indian phone number.')
    code = 'invalid_phone'


class AadhaarNumberValidator(RegexValidator):
    """
    Validate Aadhaar numbers (12 digits)
    """
    regex = r'^\d{12}$'
    message = _('Enter a valid 12-digit Aadhaar number.')
    code = 'invalid_aadhaar'


class PANNumberValidator(RegexValidator):
    """
    Validate PAN numbers
    """
    regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
    message = _('Enter a valid PAN number (e.g., ABCDE1234F).')
    code = 'invalid_pan'


class IFSCValidator(RegexValidator):
    """
    Validate IFSC codes
    """
    regex = r'^[A-Z]{4}0[A-Z0-9]{6}$'
    message = _('Enter a valid IFSC code (e.g., SBIN0001234).')
    code = 'invalid_ifsc'


class RollNumberValidator(RegexValidator):
    """
    Validate roll numbers (alphanumeric, 6-20 characters)
    """
    regex = r'^[A-Z0-9]{6,20}$'
    message = _('Enter a valid roll number (6-20 alphanumeric characters, uppercase only).')
    code = 'invalid_roll_number'


class EmployeeIDValidator(RegexValidator):
    """
    Validate employee IDs
    """
    regex = r'^[A-Z]{2,4}\d{3,6}$'
    message = _('Enter a valid employee ID (e.g., CS001, MECH1234).')
    code = 'invalid_employee_id'


def validate_file_size(file, max_size_mb=10):
    """
    Validate file size in MB
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB.')


def validate_image_dimensions(image, max_width=2048, max_height=2048):
    """
    Validate image dimensions
    """
    try:
        from PIL import Image
        
        img = Image.open(image)
        width, height = img.size
        
        if width > max_width or height > max_height:
            raise ValidationError(f'Image dimensions cannot exceed {max_width}x{max_height} pixels.')
    except ImportError:
        # PIL not available, skip dimension validation
        pass
    except Exception as e:
        raise ValidationError(f'Error validating image: {str(e)}')


def validate_secure_filename(filename):
    """
    Validate filename for security
    """
    # Check for path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        raise ValidationError('Invalid filename: path traversal not allowed.')
    
    # Check for dangerous characters
    dangerous_chars = ['<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        if char in filename:
            raise ValidationError(f'Invalid filename: character "{char}" not allowed.')
    
    # Check filename length
    if len(filename) > 255:
        raise ValidationError('Filename too long (maximum 255 characters).')
    
    return True


