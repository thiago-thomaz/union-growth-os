import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_v1_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, check_db_health, engine, run_automatic_schema_migrations
from app.services.automation_scheduler import get_scheduler_status, start_native_scheduler
from app.services.seed_service import ensure_initial_workspace_seeded
from app.services.seo_and_market_engine import generate_dynamic_robots_txt, generate_dynamic_sitemap_xml
from app.services.versioning_engine import sync_release_records_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    run_automatic_schema_migrations(engine)
    db = SessionLocal()
    try:
        ensure_initial_workspace_seeded(db)
        sync_release_records_service(db)
    finally:
        db.close()
    start_native_scheduler()
    yield


app = FastAPI(
    title="UNION GROWTH OS — AI Business & Marketing Director",
    version=settings.APP_VERSION,
    description="Plataforma Autônoma Multiagente de Gestão Empresarial, Marketing, SEO, Social Media, Creative Studio, Copywriting, Growth e CRM.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Tenant-Id"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    response.headers.setdefault("X-XSS-Protection", "1; mode=block")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    return response


@app.get("/robots.txt", include_in_schema=False)
def robots_txt():
    return PlainTextResponse(generate_dynamic_robots_txt())


@app.get("/sitemap.xml", include_in_schema=False)
def sitemap_xml():
    db = SessionLocal()
    try:
        return Response(content=generate_dynamic_sitemap_xml(db), media_type="application/xml")
    finally:
        db.close()


@app.get("/health")
def health_endpoint():
    db_info = check_db_health()
    sched_info = get_scheduler_status()
    return {
        "status": "ok" if db_info["status"] == "healthy" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "release_channel": "STABLE",
        "git_tag": f"v{settings.APP_VERSION}",
        "git_commit": os.getenv("SOURCE_COMMIT", "local"),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": db_info,
        "scheduler": sched_info,
    }


@app.get("/ready")
def readiness_endpoint():
    db_info = check_db_health()
    if db_info["status"] != "healthy":
        return JSONResponse(status_code=503, content={"ready": False, "database": db_info})
    return {
        "ready": True,
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "git_tag": f"v{settings.APP_VERSION}",
        "git_commit": os.getenv("SOURCE_COMMIT", "local"),
        "database": db_info,
        "scheduler": get_scheduler_status(),
    }


app.include_router(api_v1_router)


@app.api_route("/api/{full_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"], include_in_schema=False)
async def api_not_found_catchall(full_path: str):
    return JSONResponse(
        status_code=404,
        content={"detail": f"Endpoint API não encontrado: /api/{full_path}"},
    )


@app.get("/lp/{slug}", include_in_schema=False)
def public_landing_page_view(slug: str):
    from app.models.entities import LandingPage, Tenant
    from app.services.phase17_commercial_engine import (
        ensure_phase17_multibusiness_seeded,
        render_public_landing_page_html,
    )

    db = SessionLocal()
    try:
        primary_tenant = db.query(Tenant).order_by(Tenant.id.asc()).first()
        if primary_tenant:
            ensure_phase17_multibusiness_seeded(db, primary_tenant)
        lp = (
            db.query(LandingPage)
            .filter(LandingPage.slug == slug, LandingPage.is_published == True)
            .order_by(LandingPage.id.asc())
            .first()
        )
        if not lp:
            return JSONResponse(status_code=404, content={"detail": f"Landing Page '/lp/{slug}' não encontrada."})
        lp.views_count = (lp.views_count or 0) + 1
        db.commit()
        db.refresh(lp)
        return HTMLResponse(content=render_public_landing_page_html(lp), status_code=200)
    finally:
        db.close()


# Serve AI generated assets (images & MP4 videos)
ASSETS_STORAGE_DIR = Path(settings.ASSETS_DIR)
ASSETS_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/assets", StaticFiles(directory=str(ASSETS_STORAGE_DIR)), name="generated_assets")

# Static frontend serving (Next.js static export in frontend/out or static/)
FRONTEND_OUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "out"
if FRONTEND_OUT_DIR.exists():
    next_static = FRONTEND_OUT_DIR / "_next"
    if next_static.exists():
        app.mount("/_next", StaticFiles(directory=str(next_static)), name="next_static")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        normalized = full_path.strip("/")
        lower_norm = normalized.lower()
        if normalized == "api" or normalized.startswith("api/"):
            return JSONResponse(
                status_code=404,
                content={"detail": f"Endpoint API não encontrado: /{normalized}"},
            )
        if (
            lower_norm.endswith(".php")
            or lower_norm.startswith(".env")
            or lower_norm.startswith(".git")
            or "wp-admin" in lower_norm
            or "wp-login" in lower_norm
        ):
            return JSONResponse(status_code=404, content={"detail": "Recurso não encontrado."})
        target = FRONTEND_OUT_DIR / full_path
        if full_path and target.exists() and target.is_file():
            return FileResponse(str(target))
        index_html = FRONTEND_OUT_DIR / "index.html"
        if index_html.exists():
            return FileResponse(
                str(index_html),
                headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"},
            )
        return JSONResponse({"service": settings.APP_NAME, "status": "running"})
else:
    @app.get("/", include_in_schema=False)
    async def root_info():
        return {
            "service": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "health": "/health",
            "ready": "/ready",
        }

