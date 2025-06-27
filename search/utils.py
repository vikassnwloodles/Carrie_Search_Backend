# Search/utils.py

import base64
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def image_to_data_uri(image_file: UploadedFile) -> str:
    mime_type = image_file.content_type
    image_bytes = image_file.read()
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_str}"


def send_verification_email(request, user, verification_link):
    banner_url = request.build_absolute_uri('/static/email/carrie.png')
    subject = "Verify your email"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        "user": user,
        "verification_link": verification_link,
        "banner_url": banner_url
    }

    text_content = f"Hi {user.username}, please verify your email: {verification_link}"
    html_content = render_to_string("email/verification_email.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
