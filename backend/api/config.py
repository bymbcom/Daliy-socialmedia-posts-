"""Configuration settings for the FastAPI application."""

from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the API.

    This class uses Pydantic's BaseSettings to load configuration from environment
    variables. The class attributes will be populated from environment variables
    with the same name (case-insensitive).
    """

    # API settings
    backend_port: int = Field(default=8000, description="Port for the backend service")
    frontend_port: int = Field(
        default=3000, description="Port for the frontend service"
    )

    # Freepik API settings
    freepik_api_key: str = Field(
        default="", description="API key for Freepik service"
    )
    freepik_base_url: str = Field(
        default="https://api.freepik.com/v1", description="Freepik API base URL"
    )
    
    # Rate limiting settings
    freepik_rate_limit_per_second: int = Field(
        default=45, description="Freepik requests per second (buffer below 50 limit)"
    )
    freepik_rate_limit_burst: int = Field(
        default=10, description="Freepik burst capacity"
    )
    freepik_daily_quota: int = Field(
        default=10000, description="Daily API request quota"
    )
    
    # Cost tracking settings  
    freepik_cost_per_request: float = Field(
        default=0.01, description="Cost per API request in USD"
    )
    freepik_daily_budget: float = Field(
        default=100.0, description="Daily budget limit in USD"
    )
    
    # Cache settings
    redis_url: str = Field(
        default="redis://localhost:6379", description="Redis connection URL"
    )
    cache_ttl_search: int = Field(
        default=3600, description="Search results cache TTL in seconds"
    )
    cache_ttl_images: int = Field(
        default=86400, description="Downloaded images cache TTL in seconds"
    )
    
    # Image processing settings
    brand_logo_path: str = Field(
        default="assets/brand/logo.png", description="Path to brand logo"
    )
    output_formats: list[str] = Field(
        default=["instagram_post", "instagram_story", "linkedin_post"], 
        description="Supported output formats"
    )
    
    # Brand system settings
    brand_assets_directory: str = Field(
        default="assets/brand", description="Directory for brand assets"
    )
    brand_templates_directory: str = Field(
        default="assets/templates", description="Directory for brand templates"
    )
    generated_content_directory: str = Field(
        default="generated_content", description="Directory for generated content"
    )
    
    # Brand validation settings
    brand_validation_enabled: bool = Field(
        default=True, description="Enable brand validation"
    )
    brand_enforcement_level: str = Field(
        default="moderate", description="Brand enforcement level (strict, moderate, flexible, advisory)"
    )
    minimum_brand_score: float = Field(
        default=0.8, description="Minimum acceptable brand compliance score"
    )
    
    # Brand template settings
    template_cache_ttl: int = Field(
        default=3600, description="Template cache TTL in seconds"
    )
    max_template_variations: int = Field(
        default=5, description="Maximum template variations to generate"
    )
    
    # Brand analytics settings
    analytics_retention_days: int = Field(
        default=90, description="Days to retain brand analytics data"
    )
    compliance_monitoring_enabled: bool = Field(
        default=True, description="Enable real-time compliance monitoring"
    )
    
    # Webhook settings
    webhook_secret_key: str = Field(
        default="", description="Secret key for webhook signature verification"
    )
    webhook_enabled: bool = Field(
        default=False, description="Enable webhook functionality"
    )

    model_config = SettingsConfigDict(
        env_file=".env.development", env_file_encoding="utf-8", case_sensitive=False
    )


def get_fastapi_settings() -> Dict[str, Any]:
    """Get FastAPI application settings.

    Returns
    -------
    Dict[str, Any]
        Dictionary with FastAPI settings.
    """
    return {
        "title": "MVP API",
        "description": "API for MVP application",
        "version": "0.1.0",
        "docs_url": "/docs",
        "redoc_url": "/redoc",
    }
