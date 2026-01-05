"""
Custom Cloudinary storage for PDF files using image resource type
"""
from cloudinary_storage.storage import MediaCloudinaryStorage


class PdfCloudinaryStorage(MediaCloudinaryStorage):
    """
    Storage backend for PDF files that uses Cloudinary's image resource type
    (PDFs are uploaded as images by default in Cloudinary)
    """
    pass
