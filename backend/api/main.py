"""Main module for the Social Media Content Visual Pipeline FastAPI application."""

import logging
from typing import Dict

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.config import Settings
from api.routes import router as api_router
from api.middleware import setup_middleware

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = Settings()

# Create the FastAPI app with comprehensive documentation
app = FastAPI(
    title="Social Media Content Visual Pipeline API",
    description="""
    # Social Media Content Visual Pipeline API
    
    Complete API for BYMB Consultancy's social media content generation system.
    
    ## Features
    
    * **Content Generation**: End-to-end content creation from business insights to branded visuals
    * **Brand Management**: Comprehensive brand compliance validation and enforcement  
    * **Multi-Platform Optimization**: Platform-specific content adaptation and optimization
    * **Analytics & Performance**: Detailed performance tracking and optimization insights
    * **Asset Management**: Brand asset library and template management
    * **Workflow Orchestration**: Complex workflow management with human-in-the-loop capabilities
    * **Authentication & Security**: JWT-based auth with role-based access control
    * **Webhook Integration**: Event-driven notifications and integrations
    
    ## Authentication
    
    The API supports multiple authentication methods:
    - **Bearer Token**: JWT-based authentication for user sessions
    - **API Key**: Service-to-service authentication via X-API-Key header
    
    ## Rate Limiting
    
    - Default: 100 requests/minute per user/IP
    - Burst: 20 requests in quick succession
    - Custom limits available for premium tiers
    
    ## Support
    
    For technical support and API documentation, contact BYMB Consultancy at api-support@bymbconsultancy.com
    """,
    version="1.0.0",
    contact={
        "name": "BYMB Consultancy API Team",
        "email": "api-support@bymbconsultancy.com",
        "url": "https://bymbconsultancy.com"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://bymbconsultancy.com/license"
    },
    terms_of_service="https://bymbconsultancy.com/terms",
    servers=[
        {
            "url": "https://api.bymbconsultancy.com",
            "description": "Production server"
        },
        {
            "url": "https://api-staging.bymbconsultancy.com", 
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
)

# Setup comprehensive middleware
middleware_config = {
    "debug": settings.backend_port == 8000,  # Debug mode for development
    "metrics_enabled": True,
    "rate_limit": 100,
    "burst_limit": 20,
    "time_window": 60,
    "log_level": "INFO",
    "cors_origins": ["http://localhost:3000", "http://127.0.0.1:3000"],  # Development CORS
    "valid_api_keys": []  # API keys now loaded from environment variables
}

setup_middleware(app, middleware_config)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint of the API.

    Returns
    -------
    Dict[str, str]
        A welcome message for the API.
    """
    return {"message": "Welcome to the MVP API"}


@app.get("/healthcheck")
async def healthcheck() -> Dict[str, str]:
    """Health check endpoint.

    This endpoint can be used to verify that the API is running and responsive.

    Returns
    -------
    Dict[str, str]
        A dictionary indicating the health status of the API.
    """
    return {"status": "healthy"}
