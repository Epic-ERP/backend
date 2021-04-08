import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from shutil import copyfileobj
from typing import Any, Dict, Optional
from uuid import uuid4

import emails
from boto3 import session
from decouple import config
from emails.template import JinjaTemplate
from fastapi import UploadFile
from jose import jwt

from app.core.config import settings


def send_email(
    email_to: str,
    subject_template: str = "",
    html_template: str = "",
    environment: Dict[str, Any] = {},
) -> None:
    if settings.EMAILS_ENABLED:
        message = emails.Message(
            subject=JinjaTemplate(subject_template),
            html=JinjaTemplate(html_template),
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )
        smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
        if settings.SMTP_TLS:
            smtp_options["tls"] = True
        if settings.SMTP_USER:
            smtp_options["user"] = settings.SMTP_USER
        if settings.SMTP_PASSWORD:
            smtp_options["password"] = settings.SMTP_PASSWORD
        response = message.send(to=email_to, render=environment, smtp=smtp_options)
        logging.info(f"send email result: {response}")


def send_test_email(email_to: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Test email"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "test_email.html") as f:
        template_str = f.read()
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={"project_name": settings.PROJECT_NAME, "email": email_to},
    )


def send_reset_password_email(email_to: str, email: str, token: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - Password recovery for user {email}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "reset_password.html") as f:
        template_str = f.read()
    server_host = settings.SERVER_HOST
    link = f"{server_host}/reset-password?token={token}"
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": email,
            "email": email_to,
            "valid_hours": settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS,
            "link": link,
        },
    )


def send_new_account_email(email_to: str, username: str, password: str) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_account.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "username": username,
            "password": password,
            "email": email_to,
            "link": link,
        },
    )


def send_new_admin_email(email_to: str, permissions: int) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New admin permissions"
    with open(Path(settings.EMAIL_TEMPLATES_DIR) / "new_admin.html") as f:
        template_str = f.read()
    link = settings.SERVER_HOST
    send_email(
        email_to=email_to,
        subject_template=subject,
        html_template=template_str,
        environment={
            "project_name": settings.PROJECT_NAME,
            "permissions": permissions,
            "email": email_to,
            "link": link,
        },
    )


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.utcnow()
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    return encoded_jwt


def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return decoded_token["email"]
    except jwt.JWTError:
        return None


def save_image(image: UploadFile, directory: str = "profile_pictures") -> str:
    if access_key := config("S3_ACCESS_KEY", default=None):
        if secret_key := config("S3_SECRET_ACCESS_KEY", default=None):
            if endpoint := config("S3_ENDPOINT", default=None):
                if bucket := config("S3_BUCKET_NAME", default=None):
                    return save_image_s3_bucket(image, directory, access_key, secret_key, endpoint, bucket)
    return save_image_local(image, directory)


def save_image_local(image: UploadFile, directory: str) -> str:
    filename = f"{uuid4()}.{image.content_type.replace('image/', '')}"
    with open(f"./{directory}/{filename}", "wb") as buffer:
        copyfileobj(image.file, buffer)
    return filename


def save_image_s3_bucket(
    image: UploadFile, directory: str, access_key: str, secret_key: str, endpoint: str, bucket: str
) -> str:
    client = session.Session().client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
    )
    filename = f"{uuid4()}.{image.content_type.replace('image/', '')}"
    client.upload_fileobj(
        Fileobj=image, Bucket=bucket, Key=os.path.join(directory, filename), ExtraArgs={"ACL": "public-read"}
    )
    return filename
