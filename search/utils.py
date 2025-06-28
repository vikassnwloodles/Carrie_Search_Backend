# Search/utils.py

import base64
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def get_best_model(model):
    return "sonar-pro" if model == "best" else model


def image_to_data_uri(image_file: UploadedFile) -> str:
    mime_type = image_file.content_type
    image_bytes = image_file.read()
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    return f"data:{mime_type};base64,{base64_str}"


def send_verification_email(user, verification_link):
    subject = "Verify your email"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        "user": user,
        "verification_link": verification_link,
    }

    text_content = f"Hi {user.username}, please verify your email: {verification_link}"
    html_content = render_to_string("email/verification_email.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def send_password_reset_email(user, reset_link):
    subject = "Reset your password"
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = user.email

    context = {
        "user": user,
        "reset_link": reset_link,
    }

    text_content = f"Hi {user.username}, you requested a password reset. Click the link below to reset your password:\n{reset_link}\n\nIf you didn't request this, you can safely ignore this email."
    html_content = render_to_string("email/password_reset_email.html", context)

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")
    msg.send()