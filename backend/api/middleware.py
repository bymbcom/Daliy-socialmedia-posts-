"""Middleware and authentication patterns for the Social Media Content Visual Pipeline API.

This module provides comprehensive middleware for:
- Request/response logging and monitoring
- Rate limiting and throttling
- Security headers and CORS handling
- API key validation and management
- Performance monitoring and metrics
- Error handling and response formatting
"""

import time
import json
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.responses import JSONResponse
import httpx

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Comprehensive request and response logging middleware."""
    
    def __init__(self, app, log_level: str = "INFO"):
        super().__init__(app)
        self.log_level = getattr(logging, log_level.upper())
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with comprehensive logging."""
        start_time = time.time()
        request_id = f"req_{int(start_time * 1000)}_{id(request) % 10000}"
        
        # Log request details
        request_details = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path": request.url.path,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "user_agent": request.headers.get("user-agent", ""),
            "client_ip": self._get_client_ip(request),
            "timestamp": datetime.now().isoformat()
        }
        
        # Remove sensitive headers from logging
        sensitive_headers = ["authorization", "x-api-key", "cookie"]
        for header in sensitive_headers:
            if header in request_details["headers"]:
                request_details["headers"][header] = "[REDACTED]"
        
        logger.log(self.log_level, f"Request started: {json.dumps(request_details)}")
        
        # Process request
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Log response details
            response_details = {
                "request_id": request_id,
                "status_code": response.status_code,
                "processing_time_ms": round(processing_time * 1000, 2),
                "response_size_bytes": len(response.body) if hasattr(response, 'body') else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add processing time header
            response.headers["X-Processing-Time"] = str(response_details["processing_time_ms"])
            response.headers["X-Request-ID"] = request_id
            
            logger.log(self.log_level, f"Request completed: {json.dumps(response_details)}")
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_details = {
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "processing_time_ms": round(processing_time * 1000, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            logger.error(f"Request failed: {json.dumps(error_details)}")
            raise
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (load balancer/proxy)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip
        
        # Fallback to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host
        
        return "unknown"


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """Advanced rate limiting middleware with multiple strategies."""
    
    def __init__(
        self,
        app,
        default_rate_limit: int = 100,  # requests per minute
        burst_limit: int = 20,  # burst capacity
        time_window: int = 60,  # seconds
        key_extractor: Callable = None
    ):
        super().__init__(app)
        self.default_rate_limit = default_rate_limit
        self.burst_limit = burst_limit
        self.time_window = time_window
        self.key_extractor = key_extractor or self._default_key_extractor
        self.request_counts: Dict[str, Dict] = {}
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Apply rate limiting logic."""
        # Skip rate limiting for certain paths
        if self._should_skip_rate_limiting(request):
            return await call_next(request)
        
        # Extract rate limiting key (IP, user ID, API key, etc.)
        rate_limit_key = await self.key_extractor(request)
        
        # Check rate limit
        if await self._is_rate_limited(rate_limit_key, request):
            return self._rate_limit_response(rate_limit_key)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        rate_info = self.request_counts.get(rate_limit_key, {})
        remaining = max(0, self.default_rate_limit - rate_info.get("count", 0))
        reset_time = rate_info.get("reset_time", time.time() + self.time_window)
        
        response.headers["X-RateLimit-Limit"] = str(self.default_rate_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(reset_time))
        
        return response
    
    async def _is_rate_limited(self, key: str, request: Request) -> bool:
        """Check if request should be rate limited."""
        current_time = time.time()
        
        if key not in self.request_counts:
            self.request_counts[key] = {
                "count": 0,
                "reset_time": current_time + self.time_window,
                "burst_count": 0,
                "burst_reset": current_time + 60  # 1 minute burst window
            }
        
        rate_data = self.request_counts[key]
        
        # Reset counters if time window expired
        if current_time >= rate_data["reset_time"]:
            rate_data["count"] = 0
            rate_data["reset_time"] = current_time + self.time_window
        
        if current_time >= rate_data["burst_reset"]:
            rate_data["burst_count"] = 0
            rate_data["burst_reset"] = current_time + 60
        
        # Check burst limit
        if rate_data["burst_count"] >= self.burst_limit:
            logger.warning(f"Burst rate limit exceeded for key: {key}")
            return True
        
        # Check standard rate limit
        if rate_data["count"] >= self.default_rate_limit:
            logger.warning(f"Rate limit exceeded for key: {key}")
            return True
        
        # Increment counters
        rate_data["count"] += 1
        rate_data["burst_count"] += 1
        
        return False
    
    def _rate_limit_response(self, key: str) -> JSONResponse:
        """Return rate limit exceeded response."""
        rate_info = self.request_counts.get(key, {})
        reset_time = rate_info.get("reset_time", time.time() + self.time_window)
        
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "message": "Rate limit exceeded. Please try again later.",
                    "details": {
                        "limit": self.default_rate_limit,
                        "window_seconds": self.time_window,
                        "reset_time": int(reset_time),
                        "retry_after": max(1, int(reset_time - time.time()))
                    }
                }
            },
            headers={
                "X-RateLimit-Limit": str(self.default_rate_limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(reset_time)),
                "Retry-After": str(max(1, int(reset_time - time.time())))
            }
        )
    
    def _should_skip_rate_limiting(self, request: Request) -> bool:
        """Determine if rate limiting should be skipped for this request."""
        skip_paths = ["/docs", "/redoc", "/openapi.json", "/healthcheck", "/"]
        return request.url.path in skip_paths
    
    async def _default_key_extractor(self, request: Request) -> str:
        """Extract rate limiting key from request."""
        # Try to get user ID from JWT token
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            # In production, would decode JWT to get user ID
            return f"user_jwt_{hash(auth_header) % 10000}"
        
        # Try to get API key
        api_key = request.headers.get("x-api-key", "")
        if api_key:
            return f"api_key_{hash(api_key) % 10000}"
        
        # Fallback to IP address
        client_ip = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
        if not client_ip:
            client_ip = request.headers.get("x-real-ip", "")
        if not client_ip and hasattr(request, "client") and request.client:
            client_ip = request.client.host
        
        return f"ip_{client_ip or 'unknown'}"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""
    
    def __init__(self, app, security_config: Optional[Dict] = None):
        super().__init__(app)
        self.security_config = security_config or self._default_security_config()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in self.security_config.items():
            response.headers[header] = value
        
        return response
    
    def _default_security_config(self) -> Dict[str, str]:
        """Default security headers configuration."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            ),
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }


class APIKeyValidationMiddleware(BaseHTTPMiddleware):
    """Validate API keys for service-to-service authentication."""
    
    def __init__(self, app, valid_api_keys: Optional[List[str]] = None):
        super().__init__(app)
        self.valid_api_keys = set(valid_api_keys or [])
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Validate API key if present."""
        # Skip validation for public endpoints
        if self._is_public_endpoint(request):
            return await call_next(request)
        
        api_key = request.headers.get("x-api-key", "")
        
        # If API key is provided, validate it
        if api_key:
            if not self._is_valid_api_key(api_key):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={
                        "error": {
                            "code": "INVALID_API_KEY",
                            "message": "Invalid API key provided",
                            "details": {
                                "api_key_format": "Expected format: bymb_xxxxxxxxxxxxxxxx",
                                "authentication_methods": ["Bearer token", "API key"]
                            }
                        }
                    }
                )
            
            # Add API key info to request state
            request.state.api_key = api_key
            request.state.auth_method = "api_key"
        
        return await call_next(request)
    
    def _is_public_endpoint(self, request: Request) -> bool:
        """Check if endpoint is public (doesn't require authentication)."""
        public_paths = [
            "/docs", "/redoc", "/openapi.json", "/healthcheck", "/",
            "/api/v1/auth/login", "/api/brand/profile", "/api/health"
        ]
        return request.url.path in public_paths
    
    def _is_valid_api_key(self, api_key: str) -> bool:
        """Validate API key format and existence."""
        # Check format
        if not api_key.startswith("bymb_") or len(api_key) != 21:
            return False
        
        # In production, would validate against database
        # For now, use mock validation
        return api_key in self.valid_api_keys or api_key.startswith("bymb_")


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Monitor API performance and collect metrics."""
    
    def __init__(self, app, metrics_enabled: bool = True):
        super().__init__(app)
        self.metrics_enabled = metrics_enabled
        self.metrics_data: Dict[str, List] = {
            "request_times": [],
            "endpoint_stats": {},
            "error_rates": {},
            "slow_requests": []
        }
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Monitor request performance."""
        if not self.metrics_enabled:
            return await call_next(request)
        
        start_time = time.time()
        endpoint = f"{request.method} {request.url.path}"
        
        try:
            response = await call_next(request)
            processing_time = time.time() - start_time
            
            # Collect performance metrics
            self._record_metrics(endpoint, processing_time, response.status_code, None)
            
            # Add performance headers
            response.headers["X-Performance-Timing"] = str(round(processing_time * 1000, 2))
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._record_metrics(endpoint, processing_time, 500, str(e))
            raise
    
    def _record_metrics(self, endpoint: str, processing_time: float, status_code: int, error: Optional[str]):
        """Record performance metrics."""
        # Record processing time
        self.metrics_data["request_times"].append({
            "endpoint": endpoint,
            "processing_time": processing_time,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update endpoint statistics
        if endpoint not in self.metrics_data["endpoint_stats"]:
            self.metrics_data["endpoint_stats"][endpoint] = {
                "count": 0,
                "total_time": 0,
                "min_time": float("inf"),
                "max_time": 0,
                "errors": 0
            }
        
        stats = self.metrics_data["endpoint_stats"][endpoint]
        stats["count"] += 1
        stats["total_time"] += processing_time
        stats["min_time"] = min(stats["min_time"], processing_time)
        stats["max_time"] = max(stats["max_time"], processing_time)
        
        if status_code >= 400:
            stats["errors"] += 1
        
        # Record slow requests (> 2 seconds)
        if processing_time > 2.0:
            self.metrics_data["slow_requests"].append({
                "endpoint": endpoint,
                "processing_time": processing_time,
                "status_code": status_code,
                "error": error,
                "timestamp": datetime.now().isoformat()
            })
        
        # Limit memory usage by keeping only recent data
        max_records = 10000
        if len(self.metrics_data["request_times"]) > max_records:
            self.metrics_data["request_times"] = self.metrics_data["request_times"][-max_records//2:]
        if len(self.metrics_data["slow_requests"]) > 1000:
            self.metrics_data["slow_requests"] = self.metrics_data["slow_requests"][-500:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance metrics summary."""
        if not self.metrics_data["request_times"]:
            return {"message": "No performance data available"}
        
        times = [r["processing_time"] for r in self.metrics_data["request_times"]]
        
        return {
            "summary": {
                "total_requests": len(times),
                "average_response_time": sum(times) / len(times),
                "min_response_time": min(times),
                "max_response_time": max(times),
                "slow_requests_count": len(self.metrics_data["slow_requests"]),
                "error_rate": len([t for t in self.metrics_data["request_times"] if t["status_code"] >= 400]) / len(times)
            },
            "endpoint_stats": {
                endpoint: {
                    "count": stats["count"],
                    "average_time": stats["total_time"] / stats["count"],
                    "min_time": stats["min_time"],
                    "max_time": stats["max_time"],
                    "error_rate": stats["errors"] / stats["count"]
                }
                for endpoint, stats in self.metrics_data["endpoint_stats"].items()
            },
            "recent_slow_requests": self.metrics_data["slow_requests"][-10:]
        }


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Standardize error responses and handling."""
    
    def __init__(self, app, debug: bool = False):
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle errors and standardize responses."""
        try:
            return await call_next(request)
        except HTTPException as e:
            return self._format_http_exception(e, request)
        except Exception as e:
            return self._format_generic_exception(e, request)
    
    def _format_http_exception(self, exc: HTTPException, request: Request) -> JSONResponse:
        """Format HTTP exceptions with standardized structure."""
        error_response = {
            "error": {
                "code": self._get_error_code(exc.status_code),
                "message": exc.detail,
                "status_code": exc.status_code,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        if self.debug:
            error_response["error"]["debug_info"] = {
                "headers": dict(exc.headers or {}),
                "request_id": request.headers.get("x-request-id", "unknown")
            }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers=exc.headers
        )
    
    def _format_generic_exception(self, exc: Exception, request: Request) -> JSONResponse:
        """Format generic exceptions with standardized structure."""
        error_response = {
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An internal server error occurred",
                "status_code": 500,
                "timestamp": datetime.now().isoformat(),
                "path": request.url.path,
                "method": request.method
            }
        }
        
        if self.debug:
            error_response["error"]["debug_info"] = {
                "exception_type": type(exc).__name__,
                "exception_message": str(exc),
                "request_id": request.headers.get("x-request-id", "unknown")
            }
        
        logger.error(f"Unhandled exception in {request.method} {request.url.path}: {exc}")
        
        return JSONResponse(
            status_code=500,
            content=error_response
        )
    
    def _get_error_code(self, status_code: int) -> str:
        """Get standardized error code for status code."""
        error_codes = {
            400: "BAD_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN", 
            404: "NOT_FOUND",
            405: "METHOD_NOT_ALLOWED",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            502: "BAD_GATEWAY",
            503: "SERVICE_UNAVAILABLE"
        }
        return error_codes.get(status_code, f"HTTP_{status_code}")


# Middleware configuration function
def setup_middleware(app, config: Optional[Dict] = None):
    """Setup all middleware for the application."""
    config = config or {}
    
    # Error handling (first to catch all exceptions)
    app.add_middleware(
        ErrorHandlingMiddleware,
        debug=config.get("debug", False)
    )
    
    # Performance monitoring
    app.add_middleware(
        PerformanceMonitoringMiddleware,
        metrics_enabled=config.get("metrics_enabled", True)
    )
    
    # Security headers
    app.add_middleware(
        SecurityHeadersMiddleware,
        security_config=config.get("security_headers")
    )
    
    # API key validation
    app.add_middleware(
        APIKeyValidationMiddleware,
        valid_api_keys=config.get("valid_api_keys", [])
    )
    
    # Rate limiting
    app.add_middleware(
        RateLimitingMiddleware,
        default_rate_limit=config.get("rate_limit", 100),
        burst_limit=config.get("burst_limit", 20),
        time_window=config.get("time_window", 60)
    )
    
    # Request logging (last to log final response)
    app.add_middleware(
        RequestLoggingMiddleware,
        log_level=config.get("log_level", "INFO")
    )
    
    # CORS (very first to handle preflight requests)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get("cors_origins", ["*"]),
        allow_credentials=True,
        allow_methods=config.get("cors_methods", ["*"]),
        allow_headers=config.get("cors_headers", ["*"]),
        expose_headers=["X-Processing-Time", "X-Request-ID", "X-RateLimit-Limit", "X-RateLimit-Remaining"]
    )
    
    logger.info("All middleware configured successfully")