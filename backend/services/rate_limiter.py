"""Advanced rate limiter implementation with token bucket algorithm."""

import asyncio
import time
from typing import Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting."""
    
    requests_per_second: int
    burst_capacity: int
    daily_quota: int
    window_size_seconds: int = 5


class TokenBucket:
    """Thread-safe token bucket for rate limiting."""
    
    def __init__(self, capacity: int, refill_rate: float):
        """Initialize token bucket.
        
        Args:
            capacity: Maximum number of tokens
            refill_rate: Rate at which tokens are added (per second)
        """
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate
        self.last_refill = time.time()
        self._lock = asyncio.Lock()
    
    async def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens from the bucket.
        
        Args:
            tokens: Number of tokens to consume
            
        Returns:
            True if tokens were available and consumed, False otherwise
        """
        async with self._lock:
            now = time.time()
            
            # Add tokens based on elapsed time
            elapsed = now - self.last_refill
            tokens_to_add = elapsed * self.refill_rate
            self.tokens = min(self.capacity, self.tokens + tokens_to_add)
            self.last_refill = now
            
            # Try to consume tokens
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    async def wait_for_tokens(self, tokens: int = 1) -> None:
        """Wait until enough tokens are available.
        
        Args:
            tokens: Number of tokens needed
        """
        while not await self.consume(tokens):
            # Calculate wait time for next token
            wait_time = tokens / self.refill_rate
            await asyncio.sleep(min(wait_time, 1.0))  # Cap at 1 second


class FreepikRateLimiter:
    """Advanced rate limiter for Freepik API with multiple strategies."""
    
    def __init__(
        self, 
        config: RateLimitConfig,
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize rate limiter.
        
        Args:
            config: Rate limiting configuration
            redis_client: Optional Redis client for distributed rate limiting
        """
        self.config = config
        self.redis = redis_client
        
        # Local token bucket for immediate rate limiting
        self.token_bucket = TokenBucket(
            capacity=config.burst_capacity,
            refill_rate=config.requests_per_second / 60  # Convert to per-second rate
        )
        
        # Request history for sliding window
        self.request_history: Dict[str, list] = {}
        self._history_lock = asyncio.Lock()
        
        # Daily quota tracking
        self.daily_requests = 0
        self.quota_reset_time = self._get_next_midnight()
        
        logger.info(
            f"Initialized rate limiter: {config.requests_per_second}/sec, "
            f"burst: {config.burst_capacity}, daily: {config.daily_quota}"
        )
    
    def _get_next_midnight(self) -> datetime:
        """Get next midnight for quota reset."""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
    
    async def can_make_request(self, user_id: str = "default") -> tuple[bool, str]:
        """Check if a request can be made.
        
        Args:
            user_id: User identifier for per-user limits
            
        Returns:
            Tuple of (can_proceed, reason_if_blocked)
        """
        # Check daily quota
        if self.daily_requests >= self.config.daily_quota:
            return False, "Daily quota exceeded"
        
        # Check if quota needs reset
        if datetime.now() >= self.quota_reset_time:
            self.daily_requests = 0
            self.quota_reset_time = self._get_next_midnight()
        
        # Check distributed rate limits via Redis
        if self.redis:
            can_proceed, reason = await self._check_redis_limits(user_id)
            if not can_proceed:
                return False, reason
        
        # Check local token bucket
        if not await self.token_bucket.consume():
            return False, "Rate limit exceeded - too many requests per second"
        
        # Check sliding window
        if not await self._check_sliding_window(user_id):
            return False, "Rate limit exceeded - too many requests in time window"
        
        return True, ""
    
    async def wait_for_availability(self, user_id: str = "default") -> None:
        """Wait until a request can be made."""
        while True:
            can_proceed, reason = await self.can_make_request(user_id)
            if can_proceed:
                break
            
            logger.info(f"Rate limited: {reason}. Waiting...")
            
            if "daily quota" in reason.lower():
                # Wait until quota resets
                wait_time = (self.quota_reset_time - datetime.now()).total_seconds()
                await asyncio.sleep(min(wait_time, 3600))  # Cap at 1 hour
            else:
                # Wait for token bucket to refill
                await asyncio.sleep(1.0)
    
    async def record_request(self, user_id: str = "default") -> None:
        """Record a successful request.
        
        Args:
            user_id: User identifier
        """
        self.daily_requests += 1
        
        # Record in sliding window
        async with self._history_lock:
            now = time.time()
            if user_id not in self.request_history:
                self.request_history[user_id] = []
            
            self.request_history[user_id].append(now)
            
            # Clean old entries
            cutoff = now - self.config.window_size_seconds
            self.request_history[user_id] = [
                timestamp for timestamp in self.request_history[user_id]
                if timestamp > cutoff
            ]
        
        # Record in Redis if available
        if self.redis:
            await self._record_redis_request(user_id)
    
    async def _check_sliding_window(self, user_id: str) -> bool:
        """Check sliding window rate limit.
        
        Args:
            user_id: User identifier
            
        Returns:
            True if within limits
        """
        async with self._history_lock:
            if user_id not in self.request_history:
                return True
            
            now = time.time()
            cutoff = now - self.config.window_size_seconds
            
            # Count requests in current window
            recent_requests = [
                timestamp for timestamp in self.request_history[user_id]
                if timestamp > cutoff
            ]
            
            max_requests = self.config.requests_per_second * self.config.window_size_seconds
            return len(recent_requests) < max_requests
    
    async def _check_redis_limits(self, user_id: str) -> tuple[bool, str]:
        """Check distributed rate limits via Redis.
        
        Args:
            user_id: User identifier
            
        Returns:
            Tuple of (can_proceed, reason_if_blocked)
        """
        try:
            now = int(time.time())
            window_start = now - self.config.window_size_seconds
            
            # Use Redis sorted set to track requests in sliding window
            key = f"rate_limit:{user_id}"
            
            # Remove old entries
            await self.redis.zremrangebyscore(key, 0, window_start)
            
            # Count current requests
            current_count = await self.redis.zcard(key)
            max_requests = self.config.requests_per_second * self.config.window_size_seconds
            
            if current_count >= max_requests:
                return False, "Distributed rate limit exceeded"
            
            return True, ""
            
        except Exception as e:
            logger.warning(f"Redis rate limit check failed: {e}")
            return True, ""  # Allow request if Redis is unavailable
    
    async def _record_redis_request(self, user_id: str) -> None:
        """Record request in Redis for distributed rate limiting.
        
        Args:
            user_id: User identifier
        """
        try:
            now = time.time()
            key = f"rate_limit:{user_id}"
            
            # Add current request to sorted set
            await self.redis.zadd(key, {str(now): now})
            
            # Set expiry for cleanup
            await self.redis.expire(key, self.config.window_size_seconds * 2)
            
        except Exception as e:
            logger.warning(f"Redis request recording failed: {e}")
    
    async def get_usage_stats(self, user_id: str = "default") -> Dict:
        """Get current usage statistics.
        
        Args:
            user_id: User identifier
            
        Returns:
            Dictionary with usage statistics
        """
        # Calculate requests in current window
        async with self._history_lock:
            if user_id in self.request_history:
                now = time.time()
                cutoff = now - self.config.window_size_seconds
                recent_count = len([
                    t for t in self.request_history[user_id] if t > cutoff
                ])
            else:
                recent_count = 0
        
        return {
            "daily_requests": self.daily_requests,
            "daily_quota": self.config.daily_quota,
            "quota_remaining": self.config.daily_quota - self.daily_requests,
            "quota_reset_at": self.quota_reset_time.isoformat(),
            "recent_requests": recent_count,
            "window_limit": self.config.requests_per_second * self.config.window_size_seconds,
            "tokens_available": int(self.token_bucket.tokens),
            "token_capacity": self.token_bucket.capacity
        }


# Context manager for automatic rate limiting
class RateLimitedRequest:
    """Context manager for rate-limited API requests."""
    
    def __init__(self, rate_limiter: FreepikRateLimiter, user_id: str = "default"):
        """Initialize context manager.
        
        Args:
            rate_limiter: Rate limiter instance
            user_id: User identifier
        """
        self.rate_limiter = rate_limiter
        self.user_id = user_id
    
    async def __aenter__(self):
        """Enter context - wait for availability."""
        await self.rate_limiter.wait_for_availability(self.user_id)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit context - record request."""
        if exc_type is None:  # Only record successful requests
            await self.rate_limiter.record_request(self.user_id)