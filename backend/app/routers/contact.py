from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, EmailStr, field_validator
from app.config import settings
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

router = APIRouter(prefix="/api", tags=["contact"])
logger = logging.getLogger(__name__)


class ContactForm(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name is required")
        return v.strip()

    @field_validator("subject")
    @classmethod
    def subject_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Subject is required")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_min_length(cls, v: str) -> str:
        if len(v.strip()) < 20:
            raise ValueError("Message must be at least 20 characters")
        return v.strip()


def _send_email(form: ContactForm) -> None:
    """Send contact form email via SMTP. Silently fails if mail not configured."""
    if not settings.MAIL_USERNAME or not settings.MAIL_SERVER:
        logger.info("Mail not configured — skipping contact email send")
        return

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Contact] {form.subject}"
        msg["From"] = f"{settings.MAIL_FROM_NAME} <{settings.MAIL_FROM}>"
        msg["To"] = settings.MAIL_FROM
        msg["Reply-To"] = f"{form.name} <{form.email}>"

        body = (
            f"Name: {form.name}\n"
            f"Email: {form.email}\n"
            f"Subject: {form.subject}\n\n"
            f"Message:\n{form.message}"
        )
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_STARTTLS:
                server.starttls()
            if settings.MAIL_USERNAME:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            server.sendmail(settings.MAIL_FROM, settings.MAIL_FROM, msg.as_string())

        logger.info(f"Contact email sent from {form.email}")
    except Exception as exc:
        logger.error(f"Failed to send contact email: {exc}")


@router.post("/contact", status_code=200)
async def submit_contact(form: ContactForm, background_tasks: BackgroundTasks):
    """Accept a contact form submission and send an email notification."""
    background_tasks.add_task(_send_email, form)
    return {"ok": True}
