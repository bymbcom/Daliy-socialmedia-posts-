"""Cost tracking and budget management for API usage."""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import json
import logging
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class AlertType(Enum):
    """Types of cost alerts."""
    BUDGET_WARNING = "budget_warning"
    BUDGET_EXCEEDED = "budget_exceeded"
    DAILY_LIMIT = "daily_limit"
    HOURLY_SPIKE = "hourly_spike"


@dataclass
class CostAlert:
    """Cost alert configuration."""
    alert_type: AlertType
    threshold: float
    enabled: bool = True
    message: str = ""


@dataclass
class UsageRecord:
    """Record of API usage."""
    timestamp: datetime
    endpoint: str
    cost: float
    user_id: str
    request_id: str
    success: bool
    metadata: Dict = None


@dataclass
class BudgetConfig:
    """Budget configuration."""
    daily_budget: float
    monthly_budget: float
    cost_per_request: float
    warning_threshold: float = 0.8  # 80% of budget
    critical_threshold: float = 0.95  # 95% of budget


class CostTracker:
    """Advanced cost tracking with alerts and budget management."""
    
    def __init__(
        self, 
        budget_config: BudgetConfig,
        redis_client: Optional[redis.Redis] = None
    ):
        """Initialize cost tracker.
        
        Args:
            budget_config: Budget configuration
            redis_client: Optional Redis client for persistence
        """
        self.config = budget_config
        self.redis = redis_client
        
        # In-memory tracking
        self.daily_usage: List[UsageRecord] = []
        self.monthly_usage: List[UsageRecord] = []
        self.usage_lock = asyncio.Lock()
        
        # Alert system
        self.alerts: List[CostAlert] = [
            CostAlert(
                AlertType.BUDGET_WARNING,
                budget_config.daily_budget * budget_config.warning_threshold,
                True,
                f"Daily budget warning: {budget_config.warning_threshold*100}% reached"
            ),
            CostAlert(
                AlertType.BUDGET_EXCEEDED,
                budget_config.daily_budget * budget_config.critical_threshold,
                True,
                f"Daily budget critical: {budget_config.critical_threshold*100}% reached"
            ),
            CostAlert(
                AlertType.DAILY_LIMIT,
                budget_config.daily_budget,
                True,
                "Daily budget limit exceeded"
            )
        ]
        
        # Alert callback
        self.alert_callbacks: List = []
        
        logger.info(f"Initialized cost tracker with daily budget: ${budget_config.daily_budget}")
    
    async def record_usage(
        self,
        endpoint: str,
        user_id: str,
        request_id: str,
        success: bool = True,
        custom_cost: Optional[float] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """Record API usage and cost.
        
        Args:
            endpoint: API endpoint used
            user_id: User making the request
            request_id: Unique request identifier
            success: Whether the request was successful
            custom_cost: Custom cost override
            metadata: Additional metadata
        """
        cost = custom_cost or self.config.cost_per_request
        
        record = UsageRecord(
            timestamp=datetime.now(),
            endpoint=endpoint,
            cost=cost,
            user_id=user_id,
            request_id=request_id,
            success=success,
            metadata=metadata or {}
        )
        
        async with self.usage_lock:
            self.daily_usage.append(record)
            self.monthly_usage.append(record)
            
            # Clean old records
            await self._cleanup_old_records()
        
        # Persist to Redis if available
        if self.redis:
            await self._persist_record(record)
        
        # Check for alerts
        await self._check_alerts()
        
        logger.info(
            f"Recorded usage: {endpoint} for {user_id}, "
            f"cost: ${cost:.4f}, success: {success}"
        )
    
    async def get_daily_usage(self, user_id: Optional[str] = None) -> Dict:
        """Get daily usage statistics.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            Dictionary with usage statistics
        """
        async with self.usage_lock:
            today = datetime.now().date()
            daily_records = [
                r for r in self.daily_usage
                if r.timestamp.date() == today
            ]
            
            if user_id:
                daily_records = [r for r in daily_records if r.user_id == user_id]
            
            total_cost = sum(r.cost for r in daily_records)
            successful_requests = len([r for r in daily_records if r.success])
            failed_requests = len([r for r in daily_records if not r.success])
            
            # Group by endpoint
            endpoint_usage = {}
            for record in daily_records:
                if record.endpoint not in endpoint_usage:
                    endpoint_usage[record.endpoint] = {
                        "requests": 0,
                        "cost": 0.0,
                        "success_rate": 0.0
                    }
                endpoint_usage[record.endpoint]["requests"] += 1
                endpoint_usage[record.endpoint]["cost"] += record.cost
            
            # Calculate success rates
            for endpoint_data in endpoint_usage.values():
                endpoint_records = [r for r in daily_records if r.endpoint == endpoint_data]
                successful = len([r for r in endpoint_records if r.success])
                endpoint_data["success_rate"] = successful / len(endpoint_records) if endpoint_records else 0
            
            return {
                "date": today.isoformat(),
                "total_cost": total_cost,
                "budget_used_percentage": (total_cost / self.config.daily_budget) * 100,
                "remaining_budget": max(0, self.config.daily_budget - total_cost),
                "total_requests": len(daily_records),
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / len(daily_records) if daily_records else 0,
                "endpoint_breakdown": endpoint_usage,
                "average_cost_per_request": total_cost / len(daily_records) if daily_records else 0
            }
    
    async def get_monthly_usage(self, user_id: Optional[str] = None) -> Dict:
        """Get monthly usage statistics.
        
        Args:
            user_id: Optional user filter
            
        Returns:
            Dictionary with monthly statistics
        """
        async with self.usage_lock:
            now = datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            monthly_records = [
                r for r in self.monthly_usage
                if r.timestamp >= month_start
            ]
            
            if user_id:
                monthly_records = [r for r in monthly_records if r.user_id == user_id]
            
            total_cost = sum(r.cost for r in monthly_records)
            
            # Daily breakdown
            daily_breakdown = {}
            for record in monthly_records:
                day = record.timestamp.date().isoformat()
                if day not in daily_breakdown:
                    daily_breakdown[day] = {"cost": 0.0, "requests": 0}
                daily_breakdown[day]["cost"] += record.cost
                daily_breakdown[day]["requests"] += 1
            
            return {
                "month": f"{now.year}-{now.month:02d}",
                "total_cost": total_cost,
                "budget_used_percentage": (total_cost / self.config.monthly_budget) * 100,
                "remaining_budget": max(0, self.config.monthly_budget - total_cost),
                "total_requests": len(monthly_records),
                "average_daily_cost": total_cost / now.day if now.day > 0 else 0,
                "daily_breakdown": daily_breakdown,
                "projected_monthly_cost": (total_cost / now.day) * 30 if now.day > 0 else 0
            }
    
    async def can_make_request(
        self, 
        user_id: str,
        estimated_cost: Optional[float] = None
    ) -> Tuple[bool, str]:
        """Check if a request can be made within budget.
        
        Args:
            user_id: User making the request
            estimated_cost: Estimated cost of the request
            
        Returns:
            Tuple of (can_proceed, reason_if_blocked)
        """
        cost = estimated_cost or self.config.cost_per_request
        
        # Get current usage
        daily_stats = await self.get_daily_usage()
        monthly_stats = await self.get_monthly_usage()
        
        # Check daily budget
        if daily_stats["total_cost"] + cost > self.config.daily_budget:
            return False, "Daily budget would be exceeded"
        
        # Check monthly budget
        if monthly_stats["total_cost"] + cost > self.config.monthly_budget:
            return False, "Monthly budget would be exceeded"
        
        # Check user-specific limits if implemented
        user_daily = await self.get_daily_usage(user_id)
        user_monthly = await self.get_monthly_usage(user_id)
        
        # You can add per-user budget limits here
        # For now, we'll allow the request if global budgets are okay
        
        return True, ""
    
    async def add_alert_callback(self, callback) -> None:
        """Add callback function for alerts.
        
        Args:
            callback: Async function to call when alert is triggered
        """
        self.alert_callbacks.append(callback)
    
    async def _cleanup_old_records(self) -> None:
        """Clean up old usage records."""
        now = datetime.now()
        
        # Keep only last 24 hours for daily usage
        cutoff_daily = now - timedelta(hours=24)
        self.daily_usage = [r for r in self.daily_usage if r.timestamp > cutoff_daily]
        
        # Keep only current month for monthly usage
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        self.monthly_usage = [r for r in self.monthly_usage if r.timestamp > month_start]
    
    async def _persist_record(self, record: UsageRecord) -> None:
        """Persist usage record to Redis.
        
        Args:
            record: Usage record to persist
        """
        try:
            key = f"usage_record:{record.timestamp.strftime('%Y-%m-%d')}"
            value = json.dumps({
                "timestamp": record.timestamp.isoformat(),
                "endpoint": record.endpoint,
                "cost": record.cost,
                "user_id": record.user_id,
                "request_id": record.request_id,
                "success": record.success,
                "metadata": record.metadata
            })
            
            await self.redis.lpush(key, value)
            await self.redis.expire(key, 86400 * 31)  # Keep for 31 days
            
        except Exception as e:
            logger.warning(f"Failed to persist usage record: {e}")
    
    async def _check_alerts(self) -> None:
        """Check if any alerts should be triggered."""
        daily_stats = await self.get_daily_usage()
        current_cost = daily_stats["total_cost"]
        
        for alert in self.alerts:
            if not alert.enabled:
                continue
            
            if current_cost >= alert.threshold:
                await self._trigger_alert(alert, daily_stats)
    
    async def _trigger_alert(self, alert: CostAlert, stats: Dict) -> None:
        """Trigger a cost alert.
        
        Args:
            alert: Alert configuration
            stats: Current usage statistics
        """
        alert_data = {
            "alert_type": alert.alert_type.value,
            "message": alert.message,
            "current_cost": stats["total_cost"],
            "threshold": alert.threshold,
            "budget_percentage": stats["budget_used_percentage"],
            "timestamp": datetime.now().isoformat(),
            "stats": stats
        }
        
        logger.warning(f"Cost alert triggered: {alert.message}")
        
        # Call registered callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert_data)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    async def get_cost_projections(self) -> Dict:
        """Get cost projections based on current usage.
        
        Returns:
            Dictionary with cost projections
        """
        daily_stats = await self.get_daily_usage()
        monthly_stats = await self.get_monthly_usage()
        
        now = datetime.now()
        days_in_month = (now.replace(month=now.month + 1, day=1) - timedelta(days=1)).day
        
        # Simple linear projection
        daily_avg = monthly_stats["total_cost"] / now.day if now.day > 0 else 0
        projected_monthly = daily_avg * days_in_month
        
        # Hourly trend (last 24 hours)
        hourly_records = [
            r for r in self.daily_usage
            if r.timestamp > datetime.now() - timedelta(hours=24)
        ]
        
        hourly_avg = sum(r.cost for r in hourly_records) / 24 if hourly_records else 0
        projected_daily_from_hourly = hourly_avg * 24
        
        return {
            "daily_projection": projected_daily_from_hourly,
            "monthly_projection": projected_monthly,
            "will_exceed_daily_budget": projected_daily_from_hourly > self.config.daily_budget,
            "will_exceed_monthly_budget": projected_monthly > self.config.monthly_budget,
            "days_until_monthly_budget_exceeded": (
                (self.config.monthly_budget - monthly_stats["total_cost"]) / daily_avg
                if daily_avg > 0 else float('inf')
            ),
            "recommended_daily_limit": self.config.monthly_budget / days_in_month
        }


# Decorator for automatic cost tracking
def track_cost(cost_tracker: CostTracker, endpoint: str):
    """Decorator to automatically track API costs.
    
    Args:
        cost_tracker: CostTracker instance
        endpoint: API endpoint name
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            import uuid
            request_id = str(uuid.uuid4())
            user_id = kwargs.get('user_id', 'system')
            
            try:
                result = await func(*args, **kwargs)
                await cost_tracker.record_usage(
                    endpoint=endpoint,
                    user_id=user_id,
                    request_id=request_id,
                    success=True
                )
                return result
            except Exception as e:
                await cost_tracker.record_usage(
                    endpoint=endpoint,
                    user_id=user_id,
                    request_id=request_id,
                    success=False,
                    metadata={"error": str(e)}
                )
                raise
        
        return wrapper
    return decorator