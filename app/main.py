from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.database import engine, Base
from app.routers import auth, users, records, dashboard

# ── Create all tables on startup ─────────────────────────────────────────────
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Finance Dashboard Backend API.\n\n"
        "**Roles:**\n"
        "- `viewer` — read-only access to records\n"
        "- `analyst` — read + create/update records + dashboard access\n"
        "- `admin` — full access including user management and delete\n\n"
        "**Seed credentials (after running `python -m app.seed`):**\n"
        "- admin@finance.dev / admin123\n"
        "- analyst@finance.dev / analyst123\n"
        "- viewer@finance.dev / viewer123"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Global exception handler for unhandled errors ────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected internal error occurred."},
    )

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(records.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"], summary="Health check")
def root():
    return {"status": "ok", "app": settings.APP_NAME, "version": "1.0.0"}
