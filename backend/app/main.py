"""
Application entry point.

Why this file exists:
    This is the only file that knows the app exists as a whole. Its job
    is narrow and mechanical:
      1. Create the FastAPI instance
      2. Configure CORS so the React frontend (different origin) can call it
      3. Register each router (auth, employees, attendance, dashboard)
      4. (Phase 5+) register global exception handlers

    No business logic, no database queries, no request handling lives
    here — that keeps this file short and stable even as the rest of
    the app grows.

Run locally with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.exceptions import (
    AppException,
    ConflictException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.routers import auth, employees, attendance, dashboard

app = FastAPI(
    title=settings.APP_NAME,
    description="Mini Attendance Management System — REST API",
    version="1.0.0",
)

# CORS: allows the React dev server (a different origin) to call this API.
# Origins come from an environment variable, not a hardcoded list, so
# this works the same way in every environment without code changes.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # Content-Disposition carries the real filename for file downloads
    # (e.g. attendance_export.csv). Browsers block JS from reading most
    # custom response headers across origins unless the server
    # explicitly allows it — without this, the frontend's export code
    # can't see the filename at all, and falls back to a name with no
    # file extension, which is why the OS shows it as a generic file.
    expose_headers=["Content-Disposition"],
)
# --- Global exception handlers ---
# Services raise plain Python exceptions from app/exceptions.py without
# knowing anything about HTTP. These handlers are the ONE place that
# maps each domain exception to the correct status code and a clean
# JSON body — so no router needs a try/except, and no raw Python
# traceback or SQLAlchemy error ever reaches the client.
_STATUS_MAP = {
    UnauthorizedException: 401,
    ForbiddenException: 403,
    NotFoundException: 404,
    ConflictException: 409,
    ValidationException: 422,
}


@app.exception_handler(AppException)
def handle_app_exception(request: Request, exc: AppException):
    status_code = _STATUS_MAP.get(type(exc), 400)
    return JSONResponse(status_code=status_code, content={"detail": exc.message})


# Each router owns one resource / one URL prefix. Registering them here
# is the only place main.py touches the rest of the app.
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(attendance.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Health"])
def health_check():
    """Basic liveness check — useful to confirm the server is up before debugging further."""
    return {"status": "ok", "app": settings.APP_NAME, "environment": settings.ENVIRONMENT}
