from app.tasks.email_tasks import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(name="extract_pdf_metadata_task", bind=True, max_retries=2)
def extract_pdf_metadata_task(self, s3_key: str, article_id: str) -> dict:
    """
    Extract metadata (page count, title, author) from uploaded PDF.
    Updates article record in database.
    """
    try:
        # Placeholder: in production, download from S3 and use PyPDF2/pdfplumber
        logger.info(f"Processing PDF metadata for article {article_id}, key: {s3_key}")
        return {"status": "processed", "article_id": article_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30)
