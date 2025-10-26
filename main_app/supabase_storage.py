"""
Supabase Storage Integration for EduVision College Management System
Handles file uploads, deletions, and URL generation for student documents
"""

import os
import uuid
from typing import Optional, Tuple
from datetime import datetime
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: supabase-py not installed. Run: pip install supabase")


class SupabaseStorage:
    """
    Helper class for managing file uploads to Supabase Storage
    """
    
    def __init__(self):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py package is required. Install with: pip install supabase")
        
        self.url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL'))
        self.key = getattr(settings, 'SUPABASE_KEY', os.getenv('SUPABASE_KEY'))
        self.bucket = getattr(settings, 'SUPABASE_BUCKET', os.getenv('SUPABASE_BUCKET', 'student-documents'))
        
        if not self.url or not self.key:
            raise ValueError(
                "Supabase configuration missing. Set SUPABASE_URL and SUPABASE_KEY "
                "in settings.py or environment variables."
            )
        
        self.client: Client = create_client(self.url, self.key)
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the storage bucket exists"""
        try:
            # Try to get bucket info
            buckets = self.client.storage.list_buckets()
            bucket_names = [b['name'] for b in buckets]
            
            if self.bucket not in bucket_names:
                # Create bucket if it doesn't exist
                self.client.storage.create_bucket(
                    self.bucket,
                    options={"public": False}
                )
                print(f"Created Supabase bucket: {self.bucket}")
        except Exception as e:
            print(f"Warning: Could not verify/create bucket: {e}")
    
    def validate_file(
        self, 
        file: UploadedFile, 
        allowed_types: list = None,
        max_size_mb: int = 5
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate uploaded file
        
        Args:
            file: Django UploadedFile object
            allowed_types: List of allowed MIME types
            max_size_mb: Maximum file size in megabytes
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if allowed_types is None:
            allowed_types = [
                'image/jpeg', 'image/jpg', 'image/png', 'image/gif',
                'application/pdf'
            ]
        
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        if file.size > max_size_bytes:
            return False, f"File size exceeds {max_size_mb}MB limit"
        
        # Check file type
        if file.content_type not in allowed_types:
            return False, f"File type {file.content_type} not allowed"
        
        return True, None
    
    def upload_file(
        self,
        file: UploadedFile,
        folder: str = "documents",
        filename: str = None,
        student_id: int = None
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Upload file to Supabase storage
        
        Args:
            file: Django UploadedFile object
            folder: Folder path in bucket (e.g., 'documents', 'photos')
            filename: Custom filename (optional, auto-generated if None)
            student_id: Student ID for organizing files
        
        Returns:
            Tuple of (success, file_path, error_message)
        """
        try:
            # Validate file
            is_valid, error = self.validate_file(file)
            if not is_valid:
                return False, None, error
            
            # Generate unique filename
            if filename is None:
                ext = os.path.splitext(file.name)[1]
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                unique_id = str(uuid.uuid4())[:8]
                filename = f"{timestamp}_{unique_id}{ext}"
            
            # Build file path
            if student_id:
                file_path = f"{folder}/student_{student_id}/{filename}"
            else:
                file_path = f"{folder}/{filename}"
            
            # Read file content
            file.seek(0)  # Reset file pointer
            file_content = file.read()
            
            # Upload to Supabase
            response = self.client.storage.from_(self.bucket).upload(
                path=file_path,
                file=file_content,
                file_options={"content-type": file.content_type}
            )
            
            return True, file_path, None
            
        except Exception as e:
            return False, None, f"Upload failed: {str(e)}"
    
    def get_public_url(self, file_path: str) -> Optional[str]:
        """
        Get public URL for a file
        
        Args:
            file_path: Path to file in bucket
        
        Returns:
            Public URL or None if error
        """
        try:
            response = self.client.storage.from_(self.bucket).get_public_url(file_path)
            return response
        except Exception as e:
            print(f"Error getting public URL: {e}")
            return None
    
    def get_signed_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        Get signed URL for private file access
        
        Args:
            file_path: Path to file in bucket
            expires_in: Expiration time in seconds (default 1 hour)
        
        Returns:
            Signed URL or None if error
        """
        try:
            response = self.client.storage.from_(self.bucket).create_signed_url(
                file_path, 
                expires_in
            )
            return response.get('signedURL')
        except Exception as e:
            print(f"Error creating signed URL: {e}")
            return None
    
    def delete_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Delete file from Supabase storage
        
        Args:
            file_path: Path to file in bucket
        
        Returns:
            Tuple of (success, error_message)
        """
        try:
            self.client.storage.from_(self.bucket).remove([file_path])
            return True, None
        except Exception as e:
            return False, f"Delete failed: {str(e)}"
    
    def list_files(self, folder: str = "") -> list:
        """
        List files in a folder
        
        Args:
            folder: Folder path
        
        Returns:
            List of file objects
        """
        try:
            files = self.client.storage.from_(self.bucket).list(folder)
            return files
        except Exception as e:
            print(f"Error listing files: {e}")
            return []


# Singleton instance
_storage_instance = None


def get_storage() -> SupabaseStorage:
    """Get or create Supabase storage instance"""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = SupabaseStorage()
    return _storage_instance



