# import logging
import os
from typing import Any, Dict

import emails
from emails.template import JinjaTemplate

from src.config import settings

template_dir = os.path.join(os.path.dirname(__file__), "email_templates")


def send_email(
        email_to: str,
        subject_template: str = "",
        html_template: str = "",
        environment: Dict[str, Any] = dict,
) -> None:
    assert settings.EMAILS_ENABLED, "no provided configuration for email variable"
    message = emails.Message(
        subject=JinjaTemplate(subject_template),
        html=JinjaTemplate(html_template),
        mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL)
    )
    smtp_options = {"host": settings.SMTP_HOST, "port": settings.SMTP_PORT}
    if settings.SMTP_TLS:
        smtp_options["tls"] = True
    if settings.SMTP_USER:
        smtp_options["user"] = settings.SMTP_USER
    if settings.SMTP_PASSWORD:
        smtp_options["password"] = settings.SMTP_PASSWORD
    response = message.send(to=email_to, render=environment, smtp=smtp_options)
    # logging.info(f"send email result: {response}")


def send_new_account_email(email_to: str, username: str, password: str, code) -> None:
    project_name = settings.PROJECT_NAME
    subject = f"{project_name} - New account for user {username}"

    template_path = os.path.join(template_dir, "new_account.html")

    with open(template_path, 'r') as f:
        template_str = f.read()
    link = 'http://127.0.0.1:8000/api/users/activate/' + code
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
