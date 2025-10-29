"""
Django Storage Backend for Supabase
Implements Django's file storage interface for Supabase integration
"""

from django.core.files.storage import Storage
from django.core.files.base import ContentFile
from django.conf import settings
import os
from datetime import datetime
import uuid

try:
    from .supabase_storage import get_storage
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


class SupabaseStorage(Storage):
    """
    Django Storage backend for Supabase
    Provides Django-compatible file storage interface for Supabase Storage
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if SUPABASE_AVAILABLE:
            try:
                self.supabase_client = get_storage()
            except Exception as e:
                print(f"Warning: Could not initialize Supabase storage: {e}")
                self.supabase_client = None
        else:
            self.supabase_client = None
    
    def _save(self, name, content):
        """
        Save file to Supabase storage
        
        Args:
            name: The filename
            content: File content (Django File object)
        
        Returns:
            The name of the saved file
        """
        if not self.supabase_client:
            raise Exception("Supabase storage not available. Check SUPABASE_URL and SUPABASE_KEY in settings.")
        
        try:
            # Read file content
            content.seek(0)
            file_content = content.read()
            
            # Determine folder based on content type or use default
            folder = 'uploads'
            
            # Generate unique filename to avoid conflicts
            ext = os.path.splitext(name)[1]
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_id = str(uuid.uuid4())[:8]
            unique_name = f"{timestamp}_{unique_id}{ext}"
            
            # Build file path
            file_path = f"{folder}/{unique_name}"
            
            # Upload directly to Supabase
            response = self.supabase_client.client.storage.from_(
                self.supabase_client.bucket
            ).upload(
                path=file_path,
                file=file_content,
                file_options={
                    "content-type": getattr(content, 'content_type', 'application/octet-stream')
                }
            )
            
            return file_path
            
        except Exception as e:
            # Fallback to local storage if Supabase fails
            print(f"Supabase upload failed: {str(e)}")
            raise Exception(f"Failed to save file to Supabase: {str(e)}")
    
    def _open(self, name, mode='rb'):
        """
        Open file from Supabase storage
        Note: This is a simplified implementation
        """
        # For now, return signed URL instead of file content
        # Full implementation would download the file
        if not self.supabase_client:
            raise Exception("Supabase storage not available")
        
        url = self.supabase_client.get_signed_url(name)
        if not url:
            raise FileNotFoundError(f"File not found: {name}")
        
        # Return a ContentFile with the URL as metadata
        # In production, you might want to download the actual content
        return ContentFile(b'', name=name)
    
    def exists(self, name):
        """
        Check if file exists in Supabase storage
        """
        if not self.supabase_client:
            return False
        
        try:
            url = self.supabase_client.get_signed_url(name)
            return url is not None
        except:
            return False
    
    def url(self, name):
        """
        Get URL for accessing the file
        Returns public or signed URL depending on bucket settings
        Fallback to local /media/ URL if Supabase is unavailable
        """
        if not self.supabase_client:
            # Fallback to local media URL
            from django.conf import settings
            return f"{settings.MEDIA_URL}{name}"
        
        try:
            # Try to get public URL first (works for public buckets)
            public_url = self.supabase_client.client.storage.from_(
                self.supabase_client.bucket
            ).get_public_url(name)
            
            if public_url:
                return public_url
                
            # If public URL doesn't work, return signed URL for private buckets
            signed_response = self.supabase_client.client.storage.from_(
                self.supabase_client.bucket
            ).create_signed_url(name, 3600)  # 1 hour expiry
            
            if signed_response and 'signedURL' in signed_response:
                return signed_response['signedURL']
            
            # Fallback to local media URL
            from django.conf import settings
            return f"{settings.MEDIA_URL}{name}"
        except Exception as e:
            print(f"Error getting file URL: {e}")
            # Fallback to local media URL
            from django.conf import settings
            return f"{settings.MEDIA_URL}{name}"
    
    def delete(self, name):
        """
        Delete file from Supabase storage
        """
        if not self.supabase_client:
            return
        
        try:
            self.supabase_client.client.storage.from_(
                self.supabase_client.bucket
            ).remove([name])
            print(f"Successfully deleted {name} from Supabase")
        except Exception as e:
            print(f"Error deleting file {name}: {e}")
    
    def size(self, name):
        """
        Get file size
        Note: Supabase doesn't provide direct file size API
        """
        return 0  # Would need to implement file metadata retrieval
    
    def get_available_name(self, name, max_length=None):
        """
        Get available name for file
        """
        if max_length is None:
            max_length = 255
        
        if len(name) > max_length:
            ext = os.path.splitext(name)[1]
            name = name[:max_length - len(ext)] + ext
        
        return name

