import os
from django.core.exceptions import ValidationError

def validate_file_size(value):
    """Limit upload file size to 10 MB."""
    filesize = value.size
    max_mb = 10
    if filesize > max_mb * 1024 * 1024:
        raise ValidationError(f"The maximum file size allowed is {max_mb} MB. Your file size is {round(filesize / (1024*1024), 1)} MB.")

def validate_document_extension(value):
    """Allow safe documents and images."""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx', '.zip', '.rar', '.txt', '.png', '.jpg', '.jpeg', '.webp']
    if ext not in valid_extensions:
        raise ValidationError(f"Unsupported file extension '{ext}'. Allowed types: {', '.join(valid_extensions)}")
