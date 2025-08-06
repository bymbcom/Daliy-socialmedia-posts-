"""Advanced caching service for API responses and processed images."""

import asyncio
import json
import hashlib
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import os
from pathlib import Path

import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheType(Enum):
    """Types of cache entries."""
    SEARCH_RESULTS = "search"
    RESOURCE_DETAILS = "resource"
    DOWNLOAD_METADATA = "download"
    PROCESSED_IMAGE = "processed"
    USER_PREFERENCES = "preferences"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    key: str
    data: Any
    cache_type: CacheType
    created_at: datetime
    expires_at: datetime
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    metadata: Dict[str, Any] = None


class CacheService:
    """Advanced caching service with Redis and local fallback."""
    
    def __init__(
        self,
        redis_client: Optional[redis.Redis] = None,
        local_cache_size: int = 1000,
        default_ttl: int = 3600,
        file_cache_dir: Optional[str] = None
    ):
        """Initialize cache service.
        
        Args:
            redis_client: Optional Redis client
            local_cache_size: Maximum entries in local cache
            default_ttl: Default TTL in seconds
            file_cache_dir: Directory for file caching
        """
        self.redis = redis_client
        self.default_ttl = default_ttl
        
        # Local in-memory cache as fallback
        self.local_cache: Dict[str, CacheEntry] = {}
        self.local_cache_size = local_cache_size
        self.local_lock = asyncio.Lock()
        
        # File-based cache for large objects
        self.file_cache_dir = Path(file_cache_dir) if file_cache_dir else None
        if self.file_cache_dir:
            self.file_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "redis_hits": 0,
            "local_hits": 0,
            "file_hits": 0,
            "evictions": 0
        }
        
        logger.info(f"Initialized cache service with Redis: {redis_client is not None}")
    
    def _generate_key(
        self, 
        base_key: str, 
        cache_type: CacheType,
        **kwargs
    ) -> str:
        """Generate cache key with type prefix and optional parameters.
        
        Args:
            base_key: Base cache key
            cache_type: Type of cache entry
            **kwargs: Additional parameters for key generation
            
        Returns:
            Generated cache key
        """
        # Create a deterministic key from parameters
        if kwargs:
            param_str = json.dumps(kwargs, sort_keys=True)
            param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
            return f"{cache_type.value}:{base_key}:{param_hash}"
        else:
            return f"{cache_type.value}:{base_key}"
    
    async def get(
        self,
        key: str,
        cache_type: CacheType,
        default: Any = None,
        **key_params
    ) -> Any:
        """Get value from cache.
        
        Args:
            key: Cache key
            cache_type: Type of cache entry
            default: Default value if not found
            **key_params: Additional parameters for key generation
            
        Returns:
            Cached value or default
        """
        full_key = self._generate_key(key, cache_type, **key_params)
        
        # Try Redis first
        if self.redis:
            try:
                value = await self._get_from_redis(full_key)
                if value is not None:
                    self.stats["hits"] += 1
                    self.stats["redis_hits"] += 1
                    await self._update_access_stats(full_key)
                    return value
            except Exception as e:
                logger.warning(f"Redis get failed for {full_key}: {e}")
        
        # Try local cache
        async with self.local_lock:
            if full_key in self.local_cache:
                entry = self.local_cache[full_key]
                if entry.expires_at > datetime.now():
                    entry.access_count += 1
                    entry.last_accessed = datetime.now()
                    self.stats["hits"] += 1
                    self.stats["local_hits"] += 1
                    return entry.data
                else:
                    # Expired entry
                    del self.local_cache[full_key]
        
        # Try file cache for large objects
        if self.file_cache_dir:
            file_value = await self._get_from_file(full_key)
            if file_value is not None:
                self.stats["hits"] += 1
                self.stats["file_hits"] += 1
                return file_value
        
        self.stats["misses"] += 1
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        cache_type: CacheType,
        ttl: Optional[int] = None,
        store_in_file: bool = False,
        **key_params
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache entry
            ttl: Time to live in seconds
            store_in_file: Whether to store in file cache
            **key_params: Additional parameters for key generation
            
        Returns:
            True if successfully cached
        """
        full_key = self._generate_key(key, cache_type, **key_params)
        ttl = ttl or self.default_ttl
        
        success = False
        
        # Store in Redis
        if self.redis:
            try:
                await self._set_in_redis(full_key, value, ttl)
                success = True
            except Exception as e:
                logger.warning(f"Redis set failed for {full_key}: {e}")
        
        # Store in local cache
        try:
            await self._set_in_local(full_key, value, cache_type, ttl)
            success = True
        except Exception as e:
            logger.warning(f"Local cache set failed for {full_key}: {e}")
        
        # Store in file cache if requested
        if store_in_file and self.file_cache_dir:
            try:
                await self._set_in_file(full_key, value, ttl)
                success = True
            except Exception as e:
                logger.warning(f"File cache set failed for {full_key}: {e}")
        
        return success
    
    async def delete(
        self,
        key: str,
        cache_type: CacheType,
        **key_params
    ) -> bool:
        """Delete value from all cache layers.
        
        Args:
            key: Cache key
            cache_type: Type of cache entry
            **key_params: Additional parameters for key generation
            
        Returns:
            True if deleted from at least one layer
        """
        full_key = self._generate_key(key, cache_type, **key_params)
        success = False
        
        # Delete from Redis
        if self.redis:
            try:
                deleted = await self.redis.delete(full_key)
                success = success or bool(deleted)
            except Exception as e:
                logger.warning(f"Redis delete failed for {full_key}: {e}")
        
        # Delete from local cache
        async with self.local_lock:
            if full_key in self.local_cache:
                del self.local_cache[full_key]
                success = True
        
        # Delete from file cache
        if self.file_cache_dir:
            file_path = self.file_cache_dir / f"{full_key}.json"
            if file_path.exists():
                file_path.unlink()
                success = True
        
        return success
    
    async def clear_type(self, cache_type: CacheType) -> int:
        """Clear all entries of a specific type.
        
        Args:
            cache_type: Type of cache entries to clear
            
        Returns:
            Number of entries cleared
        """
        pattern = f"{cache_type.value}:*"
        cleared = 0
        
        # Clear from Redis
        if self.redis:
            try:
                keys = await self.redis.keys(pattern)
                if keys:
                    cleared += await self.redis.delete(*keys)
            except Exception as e:
                logger.warning(f"Redis clear failed for pattern {pattern}: {e}")
        
        # Clear from local cache
        async with self.local_lock:
            to_remove = [k for k in self.local_cache.keys() if k.startswith(f"{cache_type.value}:")]
            for key in to_remove:
                del self.local_cache[key]
                cleared += 1
        
        # Clear from file cache
        if self.file_cache_dir:
            for file_path in self.file_cache_dir.glob(f"{cache_type.value}_*.json"):
                file_path.unlink()
                cleared += 1
        
        logger.info(f"Cleared {cleared} entries of type {cache_type.value}")
        return cleared
    
    async def _get_from_redis(self, key: str) -> Any:
        """Get value from Redis.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None
    
    async def _set_in_redis(self, key: str, value: Any, ttl: int) -> None:
        """Set value in Redis.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        data = json.dumps(value, default=str)
        await self.redis.setex(key, ttl, data)
    
    async def _set_in_local(
        self, 
        key: str, 
        value: Any, 
        cache_type: CacheType,
        ttl: int
    ) -> None:
        """Set value in local cache.
        
        Args:
            key: Cache key
            value: Value to cache
            cache_type: Type of cache entry
            ttl: Time to live in seconds
        """
        async with self.local_lock:
            # Evict oldest entries if cache is full
            if len(self.local_cache) >= self.local_cache_size:
                await self._evict_lru()
            
            now = datetime.now()
            entry = CacheEntry(
                key=key,
                data=value,
                cache_type=cache_type,
                created_at=now,
                expires_at=now + timedelta(seconds=ttl),
                metadata={}
            )
            
            self.local_cache[key] = entry
    
    async def _evict_lru(self) -> None:
        """Evict least recently used entries from local cache."""
        if not self.local_cache:
            return
        
        # Sort by last access time (oldest first)
        sorted_entries = sorted(
            self.local_cache.items(),
            key=lambda x: x[1].last_accessed or x[1].created_at
        )
        
        # Remove oldest 10% or at least 1 entry
        to_remove = max(1, len(sorted_entries) // 10)
        for i in range(to_remove):
            key, _ = sorted_entries[i]
            del self.local_cache[key]
            self.stats["evictions"] += 1
    
    async def _get_from_file(self, key: str) -> Any:
        """Get value from file cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        file_path = self.file_cache_dir / f"{key}.json"
        
        if not file_path.exists():
            return None
        
        try:
            # Check if file has expired
            stat = file_path.stat()
            modified_time = datetime.fromtimestamp(stat.st_mtime)
            if datetime.now() - modified_time > timedelta(seconds=self.default_ttl):
                file_path.unlink()
                return None
            
            with open(file_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.warning(f"File cache read failed for {key}: {e}")
            return None
    
    async def _set_in_file(self, key: str, value: Any, ttl: int) -> None:
        """Set value in file cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
        """
        file_path = self.file_cache_dir / f"{key}.json"
        
        with open(file_path, 'w') as f:
            json.dump(value, f, default=str)
    
    async def _update_access_stats(self, key: str) -> None:
        """Update access statistics for a key.
        
        Args:
            key: Cache key
        """
        # This could be extended to track detailed access patterns
        pass
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.
        
        Returns:
            Cache statistics
        """
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        local_cache_size = len(self.local_cache)
        
        redis_info = {}
        if self.redis:
            try:
                redis_info = await self.redis.info("memory")
            except Exception:
                redis_info = {"status": "unavailable"}
        
        return {
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests,
            "hits": self.stats["hits"],
            "misses": self.stats["misses"],
            "redis_hits": self.stats["redis_hits"],
            "local_hits": self.stats["local_hits"],
            "file_hits": self.stats["file_hits"],
            "evictions": self.stats["evictions"],
            "local_cache_size": local_cache_size,
            "local_cache_limit": self.local_cache_size,
            "redis_info": redis_info,
            "file_cache_enabled": self.file_cache_dir is not None
        }
    
    async def warm_cache(self, warm_data: List[Dict[str, Any]]) -> int:
        """Warm the cache with precomputed data.
        
        Args:
            warm_data: List of cache entries to preload
            
        Returns:
            Number of entries loaded
        """
        loaded = 0
        
        for entry in warm_data:
            try:
                await self.set(
                    key=entry["key"],
                    value=entry["value"],
                    cache_type=CacheType(entry["cache_type"]),
                    ttl=entry.get("ttl", self.default_ttl)
                )
                loaded += 1
            except Exception as e:
                logger.warning(f"Failed to warm cache entry {entry.get('key')}: {e}")
        
        logger.info(f"Warmed cache with {loaded} entries")
        return loaded
    
    async def cleanup_expired(self) -> int:
        """Clean up expired entries from local cache.
        
        Returns:
            Number of entries cleaned up
        """
        now = datetime.now()
        cleaned = 0
        
        async with self.local_lock:
            expired_keys = [
                key for key, entry in self.local_cache.items()
                if entry.expires_at <= now
            ]
            
            for key in expired_keys:
                del self.local_cache[key]
                cleaned += 1
        
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired cache entries")
        
        return cleaned


# Decorators for automatic caching
def cached(
    cache_service: CacheService,
    cache_type: CacheType,
    ttl: Optional[int] = None,
    key_func: Optional[callable] = None
):
    """Decorator for automatic function result caching.
    
    Args:
        cache_service: Cache service instance
        cache_type: Type of cache entry
        ttl: Time to live in seconds
        key_func: Function to generate cache key from arguments
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Simple key generation from function name and arguments
                import hashlib
                key_data = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"
                cache_key = hashlib.md5(key_data.encode()).hexdigest()
            
            # Try to get from cache
            cached_result = await cache_service.get(cache_key, cache_type)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_service.set(cache_key, result, cache_type, ttl)
            
            return result
        
        return wrapper
    return decorator