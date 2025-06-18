# Search/utils.py

import base64
from django.core.files.uploadedfile import UploadedFile

def image_to_data_uri(image_file: UploadedFile) -> str:
    mime_type = image_file.content_type
    image_bytes = image_file.read()
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_str}"
