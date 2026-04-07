from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

mail_config = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME),
    VALIDATE_CERTS=True,
)

fast_mail = FastMail(mail_config)


async def send_email(
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html,
) -> None:
    """Send an email via configured SMTP."""
    if not settings.MAIL_USERNAME:
        logger.info(f"Mail not configured — skipping email to {recipients}: {subject}")
        return
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=subtype,
    )
    try:
        await fast_mail.send_message(message)
    except Exception as e:
        logger.error(f"Failed to send email to {recipients}: {e}")
        raise


async def send_verification_email(user_email: str, user_name: str, token: str) -> None:
    """Send email verification link to new user."""
    verify_url = f"{settings.APP_URL}/verify-email?token={token}"
    subject = f"Verify your email — {settings.APP_NAME}"
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">Welcome to {settings.APP_NAME}</h2>
      <p>Dear {user_name},</p>
      <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
      <p style="text-align:center;margin:32px 0;">
        <a href="{verify_url}" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          Verify Email Address
        </a>
      </p>
      <p style="color:#64748b;font-size:13px;">This link expires in 24 hours. If you did not create an account, you can ignore this email.</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([user_email], subject, body)


async def send_submission_confirmation(author_email: str, author_name: str, article_title: str) -> None:
    """Send submission confirmation to the author."""
    subject = f"Article Submission Received — {settings.APP_NAME}"
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">Submission Confirmed</h2>
      <p>Dear {author_name},</p>
      <p>We have received your manuscript submission:</p>
      <p style="background:#f8fafc;padding:12px 16px;border-left:4px solid #4f46e5;margin:16px 0;">
        <strong>{article_title}</strong>
      </p>
      <p>Your submission will be reviewed by our editorial team. You can track its status in your author dashboard.</p>
      <p style="text-align:center;margin:32px 0;">
        <a href="{settings.APP_URL}/author/dashboard" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          Go to Author Dashboard
        </a>
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([author_email], subject, body)


async def send_status_update_email(
    author_email: str,
    author_name: str,
    article_title: str,
    new_status: str,
    comments: str = "",
) -> None:
    """Notify author when article status changes."""
    status_labels = {
        "under_review": "Under Review",
        "revision_required": "Revision Required",
        "accepted": "Accepted",
        "rejected": "Rejected",
        "published": "Published",
    }
    label = status_labels.get(new_status, new_status.replace("_", " ").title())
    subject = f"Article Status Update: {label} — {settings.APP_NAME}"
    comments_block = ""
    if comments:
        comments_block = f"""
        <div style="background:#f8fafc;padding:12px 16px;border-left:4px solid #f59e0b;margin:16px 0;">
          <strong>Reviewer Comments:</strong><br/>
          <p style="white-space:pre-line;margin:8px 0 0;">{comments}</p>
        </div>
        """
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">Article Status Update</h2>
      <p>Dear {author_name},</p>
      <p>The status of your manuscript has been updated:</p>
      <p style="background:#f8fafc;padding:12px 16px;border-left:4px solid #4f46e5;margin:16px 0;">
        <strong>{article_title}</strong><br/>
        <span style="color:#4f46e5;font-weight:600;">New Status: {label}</span>
      </p>
      {comments_block}
      <p style="text-align:center;margin:32px 0;">
        <a href="{settings.APP_URL}/author/articles" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          View Article Status
        </a>
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([author_email], subject, body)


async def send_review_invitation(
    reviewer_email: str, reviewer_name: str, article_title: str, review_id: str = ""
) -> None:
    """Send review invitation email with accept/decline links."""
    dashboard_url = f"{settings.APP_URL}/reviewer/dashboard"
    subject = f"Review Invitation — {settings.APP_NAME}"
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">Review Invitation</h2>
      <p>Dear {reviewer_name},</p>
      <p>You have been invited to review the following manuscript:</p>
      <p style="background:#f8fafc;padding:12px 16px;border-left:4px solid #4f46e5;margin:16px 0;">
        <strong>{article_title}</strong>
      </p>
      <p>Please log in to your reviewer dashboard to accept or decline this invitation.</p>
      <p style="text-align:center;margin:32px 0;">
        <a href="{dashboard_url}" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          Go to Reviewer Dashboard
        </a>
      </p>
      <p style="color:#64748b;font-size:13px;">If you have a conflict of interest or cannot complete this review, please decline from your dashboard.</p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([reviewer_email], subject, body)


async def send_review_reminder(
    reviewer_email: str, reviewer_name: str, article_title: str, days_left: int
) -> None:
    """Send deadline reminder to reviewer."""
    subject = f"Review Reminder: {days_left} days remaining — {settings.APP_NAME}"
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#f59e0b;">Review Deadline Reminder</h2>
      <p>Dear {reviewer_name},</p>
      <p>This is a friendly reminder that your review for the following manuscript is due in <strong>{days_left} day(s)</strong>:</p>
      <p style="background:#fefce8;padding:12px 16px;border-left:4px solid #f59e0b;margin:16px 0;">
        <strong>{article_title}</strong>
      </p>
      <p style="text-align:center;margin:32px 0;">
        <a href="{settings.APP_URL}/reviewer/dashboard" style="background:#f59e0b;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          Submit Review Now
        </a>
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([reviewer_email], subject, body)


async def send_author_decision(
    author_email: str, author_name: str, article_title: str, decision: str, comments: str = ""
) -> None:
    """Notify author of editor's final decision."""
    decision_labels = {
        "accept": ("Accepted", "#16a34a"),
        "reject": ("Rejected", "#dc2626"),
        "minor_revision": ("Minor Revision Required", "#2563eb"),
        "major_revision": ("Major Revision Required", "#d97706"),
    }
    label, color = decision_labels.get(decision, (decision.replace("_", " ").title(), "#4f46e5"))
    subject = f"Editorial Decision: {label} — {settings.APP_NAME}"
    comments_block = ""
    if comments:
        comments_block = f"""
        <div style="background:#f8fafc;padding:12px 16px;border-left:4px solid {color};margin:16px 0;">
          <strong>Editor's Comments:</strong><br/>
          <p style="white-space:pre-line;margin:8px 0 0;">{comments}</p>
        </div>
        """
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">Editorial Decision</h2>
      <p>Dear {author_name},</p>
      <p>The editorial board has made a decision on your manuscript:</p>
      <p style="background:#f8fafc;padding:12px 16px;border-left:4px solid #4f46e5;margin:16px 0;">
        <strong>{article_title}</strong><br/>
        <span style="color:{color};font-weight:600;font-size:15px;">Decision: {label}</span>
      </p>
      {comments_block}
      <p style="text-align:center;margin:32px 0;">
        <a href="{settings.APP_URL}/author/articles" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          View Article Status
        </a>
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([author_email], subject, body)


async def send_editor_review_submitted(
    editor_email: str, reviewer_name: str, article_title: str, recommendation: str
) -> None:
    """Notify editor when a reviewer submits their review."""
    rec_labels = {
        "accept": "Accept",
        "minor_revision": "Minor Revision",
        "major_revision": "Major Revision",
        "reject": "Reject",
    }
    rec_label = rec_labels.get(recommendation, recommendation)
    subject = f"New Review Submitted — {settings.APP_NAME}"
    body = f"""
    <div style="font-family:sans-serif;max-width:560px;margin:auto;">
      <h2 style="color:#4f46e5;">New Review Submitted</h2>
      <p>A reviewer has submitted their review:</p>
      <p style="background:#f8fafc;padding:12px 16px;border-left:4px solid #4f46e5;margin:16px 0;">
        <strong>Article:</strong> {article_title}<br/>
        <strong>Reviewer:</strong> {reviewer_name}<br/>
        <strong>Recommendation:</strong> {rec_label}
      </p>
      <p style="text-align:center;margin:32px 0;">
        <a href="{settings.APP_URL}/admin/articles" style="background:#4f46e5;color:white;padding:12px 28px;
           border-radius:8px;text-decoration:none;font-weight:600;">
          View in Admin
        </a>
      </p>
      <hr style="border:none;border-top:1px solid #e2e8f0;margin:24px 0;"/>
      <p style="color:#94a3b8;font-size:12px;">{settings.APP_NAME} · {settings.APP_URL}</p>
    </div>
    """
    await send_email([editor_email], subject, body)
