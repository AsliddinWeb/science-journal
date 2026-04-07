from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery("journal_tasks", broker=settings.REDIS_URL, backend=settings.REDIS_URL)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_routes={
        "app.tasks.email_tasks.*": {"queue": "email"},
        "app.tasks.pdf_tasks.*": {"queue": "pdf"},
    },
    beat_schedule={
        "send-review-reminders": {
            "task": "app.tasks.email_tasks.send_due_review_reminders",
            "schedule": crontab(hour=9, minute=0),
        },
        "check-overdue-reviews": {
            "task": "app.tasks.email_tasks.check_overdue_reviews",
            "schedule": crontab(hour=8, minute=0),
        },
    },
)


# ─── Per-event tasks ──────────────────────────────────────────────────────────

@celery_app.task(name="send_verification_email_task", bind=True, max_retries=3)
def send_verification_email_task(self, user_email: str, user_name: str, token: str) -> None:
    import asyncio
    from app.services.email import send_verification_email
    try:
        asyncio.run(send_verification_email(user_email, user_name, token))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_reviewer_invitation_task", bind=True, max_retries=3)
def send_reviewer_invitation_task(
    self, review_id: str, reviewer_email: str, reviewer_name: str, article_title: str
) -> None:
    import asyncio
    from app.services.email import send_review_invitation
    try:
        asyncio.run(send_review_invitation(reviewer_email, reviewer_name, article_title, review_id))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# Legacy alias kept for backward compat
@celery_app.task(name="send_review_invitation_task", bind=True, max_retries=3)
def send_review_invitation_task(
    self, reviewer_email: str, reviewer_name: str, article_title: str
) -> None:
    import asyncio
    from app.services.email import send_review_invitation
    try:
        asyncio.run(send_review_invitation(reviewer_email, reviewer_name, article_title))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_submission_confirmation_task", bind=True, max_retries=3)
def send_submission_confirmation_task(
    self, author_email: str, author_name: str, article_title: str
) -> None:
    import asyncio
    from app.services.email import send_submission_confirmation
    try:
        asyncio.run(send_submission_confirmation(author_email, author_name, article_title))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_status_update_task", bind=True, max_retries=3)
def send_status_update_task(
    self, author_email: str, author_name: str, article_title: str,
    new_status: str, comments: str = "",
) -> None:
    import asyncio
    from app.services.email import send_status_update_email
    try:
        asyncio.run(send_status_update_email(author_email, author_name, article_title, new_status, comments))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_author_decision_task", bind=True, max_retries=3)
def send_author_decision_task(
    self, author_email: str, author_name: str, article_title: str,
    decision: str, comments: str = "",
) -> None:
    import asyncio
    from app.services.email import send_author_decision
    try:
        asyncio.run(send_author_decision(author_email, author_name, article_title, decision, comments))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_review_reminder_task", bind=True, max_retries=3)
def send_review_reminder_task(
    self, reviewer_email: str, reviewer_name: str, article_title: str, days_left: int
) -> None:
    import asyncio
    from app.services.email import send_review_reminder
    try:
        asyncio.run(send_review_reminder(reviewer_email, reviewer_name, article_title, days_left))
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


@celery_app.task(name="send_editor_new_review_task", bind=True, max_retries=3)
def send_editor_new_review_task(self, review_id: str) -> None:
    """Fetch review from DB and notify all editors."""
    import asyncio

    async def _run() -> None:
        from app.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.review import Review
        from app.models.user import User, UserRole
        from app.services.email import send_editor_review_submitted
        import uuid as _uuid

        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Review)
                .options(selectinload(Review.reviewer), selectinload(Review.article))
                .where(Review.id == _uuid.UUID(review_id))
            )
            review = result.scalar_one_or_none()
            if not review:
                return

            editors_result = await db.execute(
                select(User).where(User.role.in_([UserRole.editor, UserRole.superadmin]))
            )
            editors = editors_result.scalars().all()
            article_title = (
                review.article.title.get("en")
                or review.article.title.get("ru")
                or review.article.title.get("uz")
                or "Untitled"
            ) if review.article else "Untitled"
            rec = review.recommendation.value if review.recommendation else "unknown"

            for editor in editors:
                try:
                    await send_editor_review_submitted(
                        editor.email,
                        review.reviewer.full_name if review.reviewer else "Reviewer",
                        article_title,
                        rec,
                    )
                except Exception:
                    pass

    try:
        asyncio.run(_run())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)


# ─── Periodic tasks ───────────────────────────────────────────────────────────

@celery_app.task(name="app.tasks.email_tasks.send_due_review_reminders")
def send_due_review_reminders() -> None:
    """Daily: find reviews due in exactly 3 days and send reminder emails."""
    import asyncio

    async def _run() -> None:
        from datetime import datetime, timezone, timedelta
        from app.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.review import Review, ReviewStatus
        from app.services.email import send_review_reminder

        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            target_start = now + timedelta(days=2, hours=23)
            target_end = now + timedelta(days=3, hours=1)
            result = await db.execute(
                select(Review)
                .options(selectinload(Review.reviewer), selectinload(Review.article))
                .where(Review.status == ReviewStatus.accepted)
                .where(Review.deadline >= target_start)
                .where(Review.deadline <= target_end)
            )
            reviews = result.scalars().all()
            for r in reviews:
                if not r.reviewer or not r.article:
                    continue
                title = (
                    r.article.title.get("en") or r.article.title.get("ru") or r.article.title.get("uz") or "Untitled"
                )
                try:
                    await send_review_reminder(r.reviewer.email, r.reviewer.full_name, title, 3)
                except Exception:
                    pass

    asyncio.run(_run())


@celery_app.task(name="app.tasks.email_tasks.check_overdue_reviews")
def check_overdue_reviews() -> None:
    """Daily: find overdue reviews, notify editors."""
    import asyncio

    async def _run() -> None:
        from datetime import datetime, timezone
        from app.database import AsyncSessionLocal
        from sqlalchemy import select
        from sqlalchemy.orm import selectinload
        from app.models.review import Review, ReviewStatus
        from app.models.user import User, UserRole
        from app.services.email import send_email
        from app.config import settings as cfg

        async with AsyncSessionLocal() as db:
            now = datetime.now(timezone.utc)
            result = await db.execute(
                select(Review)
                .options(selectinload(Review.reviewer), selectinload(Review.article))
                .where(Review.status.in_([ReviewStatus.pending, ReviewStatus.accepted]))
                .where(Review.deadline < now)
            )
            overdue = result.scalars().all()
            if not overdue:
                return

            editors_result = await db.execute(
                select(User).where(User.role.in_([UserRole.editor, UserRole.superadmin]))
            )
            editors = editors_result.scalars().all()

            rows = ""
            for r in overdue:
                title = (
                    r.article.title.get("en") or r.article.title.get("ru") or r.article.title.get("uz") or "Untitled"
                ) if r.article else "?"
                reviewer_name = r.reviewer.full_name if r.reviewer else "?"
                deadline_str = r.deadline.strftime("%Y-%m-%d") if r.deadline else "?"
                rows += f"<tr><td>{title}</td><td>{reviewer_name}</td><td>{deadline_str}</td></tr>"

            body = f"""
            <div style="font-family:sans-serif;max-width:600px;margin:auto;">
              <h2 style="color:#dc2626;">Overdue Reviews Report</h2>
              <p>The following reviews are past their deadline:</p>
              <table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;font-size:13px;">
                <thead style="background:#f8fafc;">
                  <tr><th>Article</th><th>Reviewer</th><th>Deadline</th></tr>
                </thead>
                <tbody>{rows}</tbody>
              </table>
              <p style="margin-top:16px;">
                <a href="{cfg.APP_URL}/admin/articles" style="color:#4f46e5;">Manage Articles →</a>
              </p>
            </div>
            """
            for editor in editors:
                try:
                    await send_email([editor.email], f"Overdue Reviews — {cfg.APP_NAME}", body)
                except Exception:
                    pass

    asyncio.run(_run())
