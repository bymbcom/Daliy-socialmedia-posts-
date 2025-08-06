"""Comprehensive Freepik API client with advanced features."""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging

import httpx
from tenacity import (
    retry, 
    stop_after_attempt, 
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log
)

from .rate_limiter import FreepikRateLimiter, RateLimitedRequest, RateLimitConfig
from .cost_tracker import CostTracker, track_cost

logger = logging.getLogger(__name__)


class ContentType(Enum):
    """Freepik content types."""
    PHOTO = "photo"
    VECTOR = "vector"
    PSD = "psd"
    VIDEO = "video"
    AI_GENERATED = "ai"


class Orientation(Enum):
    """Image orientation options."""
    ALL = "all"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    SQUARE = "square"


class LicenseType(Enum):
    """License types."""
    FREE = "free"
    PREMIUM = "premium"
    ALL = "all"


@dataclass
class SearchFilters:
    """Search filters for Freepik API."""
    query: str
    content_type: ContentType = ContentType.PHOTO
    orientation: Orientation = Orientation.ALL
    license_type: LicenseType = LicenseType.ALL
    limit: int = 20
    page: int = 1
    order_by: str = "relevance"  # relevance, popular, latest
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    color: Optional[str] = None
    exclude_words: Optional[str] = None


@dataclass
class FreepikResource:
    """Freepik resource data structure."""
    id: str
    title: str
    description: str
    url: str
    preview_url: str
    download_url: Optional[str]
    thumbnail_url: str
    tags: List[str]
    content_type: str
    orientation: str
    width: int
    height: int
    file_size: Optional[int]
    license: str
    author: Dict[str, Any]
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class DownloadResult:
    """Result of a download operation."""
    success: bool
    file_path: Optional[str]
    file_size: Optional[int]
    download_url: Optional[str]
    error_message: Optional[str]
    metadata: Dict[str, Any]


class FreepikAPIError(Exception):
    """Base exception for Freepik API errors."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data or {}
        super().__init__(self.message)


class RateLimitError(FreepikAPIError):
    """Exception for rate limit exceeded errors."""
    pass


class AuthenticationError(FreepikAPIError):
    """Exception for authentication errors."""
    pass


class QuotaExceededError(FreepikAPIError):
    """Exception for quota exceeded errors."""
    pass


class FreepikClient:
    """Advanced Freepik API client with comprehensive features."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.freepik.com/v1",
        rate_limiter: Optional[FreepikRateLimiter] = None,
        cost_tracker: Optional[CostTracker] = None,
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize Freepik client.
        
        Args:
            api_key: Freepik API key
            base_url: API base URL
            rate_limiter: Optional rate limiter
            cost_tracker: Optional cost tracker
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Rate limiting and cost tracking
        self.rate_limiter = rate_limiter
        self.cost_tracker = cost_tracker
        
        # HTTP client with proper configuration
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "x-freepik-api-key": api_key,
                "Content-Type": "application/json",
                "User-Agent": "BYMB-SocialMedia-Pipeline/1.0"
            },
            follow_redirects=True
        )
        
        logger.info(f"Initialized Freepik client with base URL: {base_url}")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        data: Optional[Dict] = None,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Make HTTP request with retries and error handling.
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            user_id: User making the request
            
        Returns:
            Response data
            
        Raises:
            FreepikAPIError: For API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_id = str(uuid.uuid4())
        
        # Rate limiting
        if self.rate_limiter:
            async with RateLimitedRequest(self.rate_limiter, user_id):
                response = await self._execute_request(method, url, params, data, request_id)
        else:
            response = await self._execute_request(method, url, params, data, request_id)
        
        # Cost tracking
        if self.cost_tracker:
            await self.cost_tracker.record_usage(
                endpoint=endpoint,
                user_id=user_id,
                request_id=request_id,
                success=response.status_code < 400,
                metadata={
                    "method": method,
                    "status_code": response.status_code,
                    "response_size": len(response.content) if response.content else 0
                }
            )
        
        return await self._handle_response(response, endpoint)
    
    async def _execute_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict],
        data: Optional[Dict],
        request_id: str
    ) -> httpx.Response:
        """Execute HTTP request.
        
        Args:
            method: HTTP method
            url: Request URL
            params: Query parameters
            data: Request body
            request_id: Unique request ID
            
        Returns:
            HTTP response
        """
        # Add request ID for debugging
        headers = {"X-Request-ID": request_id}
        
        logger.info(f"Making {method} request to {url} (ID: {request_id})")
        
        try:
            if method.upper() == "GET":
                response = await self.client.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await self.client.post(url, params=params, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await self.client.put(url, params=params, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await self.client.delete(url, params=params, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout for {method} {url}: {e}")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error for {method} {url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error for {method} {url}: {e}")
            raise FreepikAPIError(f"Request failed: {str(e)}")
    
    async def _handle_response(
        self, 
        response: httpx.Response, 
        endpoint: str
    ) -> Dict[str, Any]:
        """Handle API response and errors.
        
        Args:
            response: HTTP response
            endpoint: API endpoint
            
        Returns:
            Parsed response data
            
        Raises:
            FreepikAPIError: For various API errors
        """
        try:
            response_data = response.json() if response.content else {}
        except json.JSONDecodeError:
            response_data = {"raw_content": response.text}
        
        # Handle different status codes
        if response.status_code == 200:
            logger.debug(f"Successful request to {endpoint}")
            return response_data
        
        elif response.status_code == 401:
            logger.error(f"Authentication failed for {endpoint}")
            raise AuthenticationError(
                "Invalid API key or authentication failed",
                response.status_code,
                response_data
            )
        
        elif response.status_code == 403:
            logger.error(f"Permission denied for {endpoint}")
            raise QuotaExceededError(
                "API quota exceeded or insufficient permissions",
                response.status_code,
                response_data
            )
        
        elif response.status_code == 429:
            logger.warning(f"Rate limit exceeded for {endpoint}")
            raise RateLimitError(
                "Rate limit exceeded",
                response.status_code,
                response_data
            )
        
        elif response.status_code >= 500:
            logger.error(f"Server error for {endpoint}: {response.status_code}")
            raise FreepikAPIError(
                f"Server error: {response.status_code}",
                response.status_code,
                response_data
            )
        
        else:
            logger.error(f"API error for {endpoint}: {response.status_code}")
            error_message = response_data.get("message", f"HTTP {response.status_code}")
            raise FreepikAPIError(
                error_message,
                response.status_code,
                response_data
            )
    
    @track_cost(None, "search")  # Will be injected by service
    async def search_resources(
        self,
        filters: SearchFilters,
        user_id: str = "default"
    ) -> Dict[str, Any]:
        """Search for resources using filters.
        
        Args:
            filters: Search filters
            user_id: User making the request
            
        Returns:
            Search results with metadata
        """
        params = {
            "query": filters.query,
            "content_type": filters.content_type.value,
            "orientation": filters.orientation.value,
            "license": filters.license_type.value,
            "limit": min(filters.limit, 200),  # API max limit
            "page": filters.page,
            "order": filters.order_by
        }
        
        # Optional filters
        if filters.min_width:
            params["min_width"] = filters.min_width
        if filters.min_height:
            params["min_height"] = filters.min_height
        if filters.color:
            params["color"] = filters.color
        if filters.exclude_words:
            params["exclude"] = filters.exclude_words
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = await self._make_request("GET", "resources", params=params, user_id=user_id)
        
        # Parse resources
        resources = []
        for item in response.get("data", []):
            try:
                resource = self._parse_resource(item)
                resources.append(resource)
            except Exception as e:
                logger.warning(f"Failed to parse resource: {e}")
                continue
        
        return {
            "resources": resources,
            "pagination": {
                "page": response.get("page", filters.page),
                "total_pages": response.get("total_pages", 1),
                "total_results": response.get("total", len(resources)),
                "per_page": response.get("per_page", filters.limit)
            },
            "query_info": {
                "query": filters.query,
                "filters_applied": params,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _parse_resource(self, item: Dict[str, Any]) -> FreepikResource:
        """Parse API response item into FreepikResource.
        
        Args:
            item: Raw API response item
            
        Returns:
            Parsed FreepikResource
        """
        return FreepikResource(
            id=str(item.get("id", "")),
            title=item.get("title", ""),
            description=item.get("description", ""),
            url=item.get("url", ""),
            preview_url=item.get("preview", {}).get("url", ""),
            download_url=item.get("download", {}).get("url"),
            thumbnail_url=item.get("thumbnail", {}).get("url", ""),
            tags=item.get("tags", []),
            content_type=item.get("content_type", ""),
            orientation=item.get("orientation", ""),
            width=item.get("image", {}).get("width", 0),
            height=item.get("image", {}).get("height", 0),
            file_size=item.get("file_size"),
            license=item.get("license", ""),
            author=item.get("author", {}),
            created_at=datetime.fromisoformat(
                item.get("created_at", datetime.now().isoformat()).replace("Z", "+00:00")
            ),
            metadata=item
        )
    
    @track_cost(None, "download")  # Will be injected by service
    async def download_resource(
        self,
        resource_id: str,
        download_path: str,
        user_id: str = "default"
    ) -> DownloadResult:
        """Download a resource by ID.
        
        Args:
            resource_id: Resource ID to download
            download_path: Local path to save the file
            user_id: User making the request
            
        Returns:
            Download result
        """
        try:
            # Get download URL
            response = await self._make_request(
                "GET", 
                f"resources/{resource_id}/download",
                user_id=user_id
            )
            
            download_url = response.get("url")
            if not download_url:
                return DownloadResult(
                    success=False,
                    file_path=None,
                    file_size=None,
                    download_url=None,
                    error_message="No download URL provided",
                    metadata=response
                )
            
            # Download the actual file
            file_size = await self._download_file(download_url, download_path)
            
            return DownloadResult(
                success=True,
                file_path=download_path,
                file_size=file_size,
                download_url=download_url,
                error_message=None,
                metadata=response
            )
            
        except Exception as e:
            logger.error(f"Download failed for resource {resource_id}: {e}")
            return DownloadResult(
                success=False,
                file_path=None,
                file_size=None,
                download_url=None,
                error_message=str(e),
                metadata={}
            )
    
    async def _download_file(self, url: str, file_path: str) -> int:
        """Download file from URL to local path.
        
        Args:
            url: Download URL
            file_path: Local file path
            
        Returns:
            File size in bytes
        """
        async with self.client.stream("GET", url) as response:
            response.raise_for_status()
            
            total_size = 0
            with open(file_path, "wb") as file:
                async for chunk in response.aiter_bytes():
                    file.write(chunk)
                    total_size += len(chunk)
            
            logger.info(f"Downloaded {total_size} bytes to {file_path}")
            return total_size
    
    async def get_resource_details(
        self,
        resource_id: str,
        user_id: str = "default"
    ) -> Optional[FreepikResource]:
        """Get detailed information about a specific resource.
        
        Args:
            resource_id: Resource ID
            user_id: User making the request
            
        Returns:
            Resource details or None if not found
        """
        try:
            response = await self._make_request(
                "GET",
                f"resources/{resource_id}",
                user_id=user_id
            )
            
            return self._parse_resource(response.get("data", {}))
            
        except FreepikAPIError as e:
            if e.status_code == 404:
                logger.warning(f"Resource {resource_id} not found")
                return None
            raise
    
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Get API usage statistics.
        
        Returns:
            Usage statistics
        """
        stats = {}
        
        if self.rate_limiter:
            stats["rate_limiting"] = await self.rate_limiter.get_usage_stats()
        
        if self.cost_tracker:
            stats["cost_tracking"] = {
                "daily": await self.cost_tracker.get_daily_usage(),
                "monthly": await self.cost_tracker.get_monthly_usage(),
                "projections": await self.cost_tracker.get_cost_projections()
            }
        
        return stats
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on API connection.
        
        Returns:
            Health check results
        """
        try:
            # Simple search to test connectivity
            test_filters = SearchFilters(query="test", limit=1)
            await self.search_resources(test_filters)
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "api_accessible": True
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "timestamp": datetime.now().isoformat(),
                "api_accessible": False,
                "error": str(e)
            }