from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router as api_v1_router
from app.core.config import settings
from app.core.database import Base, SessionLocal, check_db_health, engine
from app.services.automation_scheduler import get_scheduler_status, start_native_scheduler
from app.services.seed_service import ensure_initial_workspace_seeded
from app.services.seo_and_market_engine import generate_dynamic_robots_txt, generate_dynamic_sitemap_xml


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        ensure_initial_workspace_seeded(db)
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
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
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
        "database": db_info,
        "scheduler": get_scheduler_status(),
    }


app.include_router(api_v1_router)

# Static frontend serving (Next.js static export in frontend/out or static/)
FRONTEND_OUT_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "out"
if FRONTEND_OUT_DIR.exists():
    next_static = FRONTEND_OUT_DIR / "_next"
    if next_static.exists():
        app.mount("/_next", StaticFiles(directory=str(next_static)), name="next_static")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa(full_path: str):
        target = FRONTEND_OUT_DIR / full_path
        if full_path and target.exists() and target.is_file():
            return FileResponse(str(target))
        index_html = FRONTEND_OUT_DIR / "index.html"
        if index_html.exists():
            return FileResponse(str(index_html))
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

