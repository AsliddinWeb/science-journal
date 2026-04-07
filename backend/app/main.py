from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.config import settings
from app.middleware.cors import setup_cors
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers import (
    auth, articles, volumes, stats, editorial, pages,
    upload, reviews, admin, contact, users, categories,
    conferences, admin_conferences, home_settings, indexing,
)
from app.routers import sitemap as sitemap_router
from app.routers import og_image as og_image_router
import logging

logging.basicConfig(level=logging.INFO if not settings.DEBUG else logging.DEBUG)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME}")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="Scientific Journal Platform API",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware
setup_cors(app)
app.add_middleware(RateLimitMiddleware, calls=200, period=60)


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=422, content={"detail": str(exc)})


# Routers
app.include_router(auth.router)
app.include_router(articles.router)
app.include_router(volumes.router)
app.include_router(stats.router)
app.include_router(editorial.router)
app.include_router(pages.router)
app.include_router(upload.router)
app.include_router(reviews.router)
app.include_router(admin.router)
app.include_router(contact.router)
app.include_router(users.router)
app.include_router(categories.router)
app.include_router(conferences.router)
app.include_router(admin_conferences.router)
app.include_router(home_settings.router)
app.include_router(indexing.router)
app.include_router(sitemap_router.router)
app.include_router(og_image_router.router)

# Serve uploaded files
_uploads_dir = Path(__file__).resolve().parents[1] / "uploads"
_uploads_dir.mkdir(parents=True, exist_ok=True)
app.mount("/api/uploads", StaticFiles(directory=str(_uploads_dir)), name="uploads")


@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "ok", "app": settings.APP_NAME}
