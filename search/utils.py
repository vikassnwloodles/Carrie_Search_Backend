# Search/utils.py

import base64
from django.core.files.uploadedfile import UploadedFile
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import cloudscraper
import tldextract
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


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


def scrape_metadata(search_result):
    data = {}
    url = search_result["url"]
    try:
        scraper = cloudscraper.create_scraper()
        res = scraper.get(url, timeout=(3, 5))
        soup = BeautifulSoup(res.text, "html.parser")

        # --- site_name ---
        site_name = soup.find("meta", property="og:site_name")
        if site_name:
            data["site_name"] = site_name.get("content", "").strip()

        # --- icon ---
        icon_link = soup.find("link", rel=lambda x: x and "icon" in x.lower())
        if icon_link and icon_link.get("href"):
            data["icon"] = urljoin(url, icon_link["href"])

        # --- description ---
        desc = soup.find("meta", attrs={"name": "description"})
        if desc and desc.get("content"):
            data["description"] = desc["content"].strip()
        else:
            og_desc = soup.find("meta", property="og:description")
            data["description"] = og_desc.get("content", "").strip() if og_desc else ""

    except Exception as e:
        pass

    if "site_name" not in data: data["site_name"] = urlparse(url).netloc
    if "icon" not in data: data["icon"] = ""

    # --- short domain ---
    ext = tldextract.extract(url)
    short_name = ext.domain
    data["domain_short"] = short_name

    data["site_url"] = url
    data["title"] = search_result["title"]

    return data
