import logging

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.api.error_handlers import register_exception_handlers
from app.core.config import settings
from app.core.config_validator import ConfigValidator
from app.core.logger import setup_logging
from app.utils.exceptions import ConfigurationError

# Setup logging first
setup_logging()

# Validate configuration
try:
    ConfigValidator.validate_settings(settings)
    warnings = ConfigValidator.get_warnings(settings)
    for warning in warnings:
        logging.warning(warning)
except ConfigurationError as e:
    logging.error(f"Configuration error: {e.message}")
    raise


def create_app() -> FastAPI:
    app = FastAPI(title="GitLab Repository Sculptor")
    app.include_router(router)
    _add_cors_middleware(app)
    register_exception_handlers(app)
    return app

def _add_cors_middleware(app: FastAPI) -> None:
    """Add CORS middleware to the FastAPI app with secure configuration."""
    cors_origins = settings.get_cors_origins()
    
    # Log the CORS origins being used (without sensitive data)
    logging.info(f"Configuring CORS for {len(cors_origins)} origins")
    
    # In production, we should be restrictive about CORS
    allowed_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    allowed_headers = [
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=allowed_methods,
        allow_headers=allowed_headers,
        max_age=86400,  # 24 hours cache for preflight requests
        expose_headers=["Content-Range", "X-Content-Range"]  # Only expose necessary headers
    )


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
