"""Content scheduling service for optimized social media posting.

This service provides intelligent scheduling recommendations, content calendar
management, and automated posting optimization for BYMB Consultancy.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import calendar
import pytz

from .social_media_optimizer import SocialPlatform, ContentType, ToneOfVoice, ContentOptimization

logger = logging.getLogger(__name__)


class SchedulingStrategy(Enum):
    """Content scheduling strategies."""
    OPTIMAL_TIMES = "optimal_times"
    CONSISTENT_SPACING = "consistent_spacing"
    AUDIENCE_ACTIVITY = "audience_activity"
    COMPETITOR_GAPS = "competitor_gaps"
    TRENDING_OPPORTUNITIES = "trending_opportunities"


class PostingFrequency(Enum):
    """Posting frequency options."""
    DAILY = "daily"
    EVERY_OTHER_DAY = "every_other_day"
    THREE_TIMES_WEEK = "three_times_week"
    WEEKLY = "weekly"
    BI_WEEKLY = "bi_weekly"


class ContentPriority(Enum):
    """Content priority levels."""
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    EVERGREEN = "evergreen"


@dataclass
class ScheduledContent:
    """Scheduled content item."""
    content_id: str
    optimization: ContentOptimization
    scheduled_time: datetime
    priority: ContentPriority
    strategy_used: SchedulingStrategy
    platform: SocialPlatform
    content_type: ContentType
    tags: List[str]
    performance_prediction: Dict[str, float]
    auto_publish: bool
    status: str  # scheduled, published, failed, cancelled


@dataclass
class ContentCalendar:
    """Content calendar for a specific period."""
    start_date: datetime
    end_date: datetime
    platform: SocialPlatform
    scheduled_content: List[ScheduledContent]
    frequency_target: PostingFrequency
    strategy: SchedulingStrategy
    timezone: str
    calendar_metadata: Dict[str, Any]


@dataclass
class SchedulingRecommendation:
    """Scheduling recommendation with rationale."""
    recommended_time: datetime
    confidence_score: float
    expected_engagement: float
    reasoning: List[str]
    alternative_times: List[Tuple[datetime, float]]
    considerations: List[str]


class ContentScheduler:
    """Intelligent content scheduling service."""
    
    def __init__(self, default_timezone: str = "Asia/Bahrain"):
        """Initialize content scheduler.
        
        Args:
            default_timezone: Default timezone for scheduling
        """
        self.default_timezone = pytz.timezone(default_timezone)
        self.optimal_times = self._initialize_optimal_times()
        self.audience_activity = self._initialize_audience_patterns()
        self.business_calendar = self._initialize_business_calendar()
        self.content_sequences = self._initialize_content_sequences()
        
        logger.info(f"Content scheduler initialized for timezone: {default_timezone}")
    
    def _initialize_optimal_times(self) -> Dict[SocialPlatform, Dict[str, Any]]:
        """Initialize optimal posting times by platform."""
        return {
            SocialPlatform.LINKEDIN: {
                "weekdays": {
                    0: ["07:30", "08:45", "11:00", "12:30", "16:30"],  # Monday
                    1: ["08:00", "10:30", "12:00", "15:30", "17:00"],  # Tuesday
                    2: ["07:45", "09:30", "11:30", "13:00", "16:00"],  # Wednesday
                    3: ["08:15", "10:00", "12:30", "14:30", "17:30"],  # Thursday
                    4: ["07:30", "09:00", "11:00", "13:30", "16:00"],  # Friday
                    5: ["09:00", "11:00"],  # Saturday - limited
                    6: ["10:00", "14:00"]   # Sunday - limited
                },
                "peak_days": [1, 2, 3],  # Tuesday, Wednesday, Thursday
                "avoid_times": ["18:00-06:00"],  # Outside business hours
                "seasonal_adjustments": {
                    "ramadan": {"shift_hours": -2, "reduced_frequency": True},
                    "summer": {"shift_hours": -1},
                    "winter": {"shift_hours": 1}
                }
            },
            
            SocialPlatform.INSTAGRAM: {
                "weekdays": {
                    0: ["06:00", "08:00", "11:00", "14:00", "17:00", "19:00"],
                    1: ["07:00", "09:00", "12:00", "15:00", "18:00", "20:00"],
                    2: ["06:30", "08:30", "11:30", "14:30", "17:30", "19:30"],
                    3: ["07:30", "09:30", "12:30", "15:30", "18:30", "20:30"],
                    4: ["06:00", "08:00", "11:00", "14:00", "17:00", "21:00"],
                    5: ["09:00", "12:00", "15:00", "18:00", "21:00"],
                    6: ["10:00", "13:00", "16:00", "19:00", "21:30"]
                },
                "peak_days": [4, 5, 6],  # Friday, Saturday, Sunday
                "story_times": ["08:00", "12:00", "17:00", "20:00"],
                "reel_times": ["17:00", "19:00", "21:00"]
            },
            
            SocialPlatform.TWITTER: {
                "weekdays": {
                    0: ["08:00", "09:00", "12:00", "15:00", "17:00", "20:00"],
                    1: ["08:30", "09:30", "12:30", "15:30", "17:30", "20:30"],
                    2: ["08:00", "09:00", "12:00", "15:00", "17:00", "20:00"],
                    3: ["08:30", "09:30", "12:30", "15:30", "17:30", "20:30"],
                    4: ["08:00", "09:00", "12:00", "15:00", "17:00", "21:00"],
                    5: ["09:00", "12:00", "15:00", "18:00", "21:00"],
                    6: ["10:00", "13:00", "16:00", "19:00", "21:30"]
                },
                "peak_days": [1, 2, 3],  # High engagement mid-week
                "real_time_opportunities": True,
                "trending_boost_times": ["09:00-10:00", "15:00-16:00", "20:00-21:00"]
            },
            
            SocialPlatform.FACEBOOK: {
                "weekdays": {
                    0: ["09:00", "13:00", "15:00"],
                    1: ["09:00", "13:00", "15:00"],
                    2: ["09:00", "13:00", "15:00"],
                    3: ["09:00", "13:00", "15:00"],
                    4: ["09:00", "13:00", "15:00"],
                    5: ["12:00", "15:00", "18:00"],
                    6: ["12:00", "14:00", "18:00"]
                },
                "peak_days": [2, 3, 4],
                "video_optimal_times": ["15:00", "18:00", "20:00"]
            }
        }
    
    def _initialize_audience_patterns(self) -> Dict[str, Any]:
        """Initialize BYMB audience activity patterns."""
        return {
            "business_leaders": {
                "active_hours": ["07:00-09:00", "11:00-13:00", "16:00-18:00"],
                "time_zones": ["Asia/Bahrain", "Asia/Dubai", "Asia/Riyadh"],
                "peak_engagement_days": [1, 2, 3],  # Tue, Wed, Thu
                "seasonal_behavior": {
                    "q1": {"increased_planning_content": True},
                    "q2": {"execution_focus": True},
                    "q3": {"strategy_review": True},
                    "q4": {"year_end_planning": True}
                }
            },
            "entrepreneurs": {
                "active_hours": ["06:00-08:00", "12:00-14:00", "19:00-21:00"],
                "weekend_activity": True,
                "evening_engagement": True
            },
            "corporate_executives": {
                "active_hours": ["08:00-10:00", "13:00-15:00", "17:00-18:00"],
                "weekday_focus": True,
                "professional_hours_only": True
            }
        }
    
    def _initialize_business_calendar(self) -> Dict[str, Any]:
        """Initialize business calendar considerations."""
        return {
            "bahrain_holidays": [
                "new_year", "prophet_birthday", "labour_day", "eid_al_fitr",
                "arafat_day", "eid_al_adha", "islamic_new_year", "national_day"
            ],
            "industry_events": {
                "q1": ["business_planning_season", "new_year_resolutions"],
                "q2": ["mid_year_reviews", "strategy_updates"],
                "q3": ["performance_assessments", "goal_adjustments"],
                "q4": ["year_end_planning", "next_year_strategy"]
            },
            "avoid_periods": {
                "ramadan": {"reduced_posting": True, "timing_shift": "-2 hours"},
                "summer_vacation": {"july_august": "reduced_activity"},
                "year_end": {"december_last_week": "minimal_posting"}
            },
            "opportunity_periods": {
                "new_year": {"planning_content": True},
                "mid_year": {"review_content": True},
                "quarter_end": {"performance_content": True}
            }
        }
    
    def _initialize_content_sequences(self) -> Dict[str, List[str]]:
        """Initialize content sequence patterns."""
        return {
            "thought_leadership_series": [
                "insight_introduction",
                "detailed_analysis", 
                "practical_application",
                "results_showcase",
                "call_to_action"
            ],
            "case_study_series": [
                "challenge_presentation",
                "solution_approach",
                "implementation_process",
                "results_achieved",
                "lessons_learned"
            ],
            "educational_series": [
                "concept_introduction",
                "step_by_step_guide",
                "common_mistakes",
                "best_practices",
                "next_steps"
            ]
        }
    
    async def generate_optimal_schedule(
        self,
        content_list: List[ContentOptimization],
        start_date: datetime,
        end_date: datetime,
        platform: SocialPlatform,
        frequency: PostingFrequency = PostingFrequency.DAILY,
        strategy: SchedulingStrategy = SchedulingStrategy.OPTIMAL_TIMES
    ) -> ContentCalendar:
        """Generate optimal content schedule."""
        
        # Calculate posting frequency
        total_days = (end_date - start_date).days
        posts_needed = self._calculate_posts_needed(frequency, total_days, platform)
        
        # Prioritize content
        prioritized_content = await self._prioritize_content(content_list, platform)
        
        # Select content for schedule
        selected_content = prioritized_content[:posts_needed]
        
        # Generate time slots
        time_slots = await self._generate_time_slots(
            start_date, end_date, platform, frequency, strategy
        )
        
        # Assign content to time slots
        scheduled_content = await self._assign_content_to_slots(
            selected_content, time_slots, platform, strategy
        )
        
        return ContentCalendar(
            start_date=start_date,
            end_date=end_date,
            platform=platform,
            scheduled_content=scheduled_content,
            frequency_target=frequency,
            strategy=strategy,
            timezone=str(self.default_timezone),
            calendar_metadata={
                "total_posts": len(scheduled_content),
                "content_types_distribution": self._analyze_content_distribution(scheduled_content),
                "engagement_predictions": await self._calculate_calendar_predictions(scheduled_content),
                "generated_at": datetime.now().isoformat()
            }
        )
    
    async def recommend_posting_time(
        self,
        content: ContentOptimization,
        target_date: Optional[datetime] = None,
        avoid_conflicts: Optional[List[datetime]] = None
    ) -> SchedulingRecommendation:
        """Recommend optimal posting time for content."""
        
        if target_date is None:
            target_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        platform = content.platform
        content_type = content.content_type
        
        # Get optimal times for the platform and day
        weekday = target_date.weekday()
        optimal_times = self.optimal_times[platform]["weekdays"].get(weekday, [])
        
        # Apply content-type specific adjustments
        if platform == SocialPlatform.INSTAGRAM:
            if content_type == ContentType.STORY:
                optimal_times = self.optimal_times[platform]["story_times"]
            elif content_type == ContentType.VIDEO:
                optimal_times = self.optimal_times[platform]["reel_times"]
        
        # Calculate best time with scoring
        time_scores = []
        for time_str in optimal_times:
            time_obj = datetime.strptime(time_str, "%H:%M").time()
            posting_datetime = datetime.combine(target_date.date(), time_obj)
            posting_datetime = self.default_timezone.localize(posting_datetime)
            
            # Skip if conflicts with existing schedule
            if avoid_conflicts and any(
                abs((posting_datetime - conflict).total_seconds()) < 3600  # 1 hour buffer
                for conflict in avoid_conflicts
            ):
                continue
            
            # Calculate engagement score
            score = await self._calculate_time_score(
                posting_datetime, platform, content_type, content
            )
            
            time_scores.append((posting_datetime, score))
        
        # Sort by score
        time_scores.sort(key=lambda x: x[1], reverse=True)
        
        if not time_scores:
            # Fallback to default time
            default_time = datetime.combine(
                target_date.date(),
                datetime.strptime("09:00", "%H:%M").time()
            )
            time_scores = [(self.default_timezone.localize(default_time), 0.5)]
        
        best_time, best_score = time_scores[0]
        
        # Generate reasoning
        reasoning = await self._generate_scheduling_reasoning(
            best_time, platform, content_type, content
        )
        
        # Get alternative times
        alternatives = [(time, score) for time, score in time_scores[1:6]]
        
        # Generate considerations
        considerations = await self._generate_scheduling_considerations(
            best_time, platform, content
        )
        
        return SchedulingRecommendation(
            recommended_time=best_time,
            confidence_score=best_score,
            expected_engagement=best_score * content.performance_predictions.get("engagement_rate", 0.03),
            reasoning=reasoning,
            alternative_times=alternatives,
            considerations=considerations
        )
    
    async def _calculate_posts_needed(
        self,
        frequency: PostingFrequency,
        total_days: int,
        platform: SocialPlatform
    ) -> int:
        """Calculate number of posts needed for the period."""
        
        frequency_map = {
            PostingFrequency.DAILY: 1.0,
            PostingFrequency.EVERY_OTHER_DAY: 0.5,
            PostingFrequency.THREE_TIMES_WEEK: 3/7,
            PostingFrequency.WEEKLY: 1/7,
            PostingFrequency.BI_WEEKLY: 1/14
        }
        
        base_posts = int(total_days * frequency_map[frequency])
        
        # Platform-specific adjustments
        if platform == SocialPlatform.INSTAGRAM:
            # Instagram allows for more frequent posting
            base_posts = int(base_posts * 1.2)
        elif platform == SocialPlatform.LINKEDIN:
            # LinkedIn prefers quality over quantity
            base_posts = int(base_posts * 0.8)
        
        return max(1, base_posts)
    
    async def _prioritize_content(
        self,
        content_list: List[ContentOptimization],
        platform: SocialPlatform
    ) -> List[ContentOptimization]:
        """Prioritize content based on various factors."""
        
        scored_content = []
        
        for content in content_list:
            score = 0
            
            # Performance prediction score
            score += content.performance_predictions.get("engagement_rate", 0) * 10
            
            # Brand compliance score
            if content.brand_compliance.get("overall_compliant", False):
                score += 5
            
            # Platform-specific scoring
            if platform == SocialPlatform.LINKEDIN:
                # Favor professional, educational content
                if "professional" in content.tone.value:
                    score += 3
                if "education" in content.engagement_elements:
                    score += 2
            
            elif platform == SocialPlatform.INSTAGRAM:
                # Favor visual, engaging content
                if content.content_type == ContentType.CAROUSEL:
                    score += 3
                if "visual" in content.engagement_elements:
                    score += 2
            
            # Content freshness (newer content gets slight boost)
            score += 1  # Assuming all content is recent
            
            scored_content.append((content, score))
        
        # Sort by score (highest first)
        scored_content.sort(key=lambda x: x[1], reverse=True)
        
        return [content for content, score in scored_content]
    
    async def _generate_time_slots(
        self,
        start_date: datetime,
        end_date: datetime,
        platform: SocialPlatform,
        frequency: PostingFrequency,
        strategy: SchedulingStrategy
    ) -> List[datetime]:
        """Generate optimal time slots for posting."""
        
        time_slots = []
        current_date = start_date
        
        # Get optimal times for platform
        platform_times = self.optimal_times[platform]
        
        while current_date <= end_date:
            weekday = current_date.weekday()
            
            # Skip weekends for LinkedIn if not weekend posting day
            if platform == SocialPlatform.LINKEDIN and weekday in [5, 6]:
                if frequency not in [PostingFrequency.DAILY]:
                    current_date += timedelta(days=1)
                    continue
            
            # Get optimal times for this day
            day_times = platform_times["weekdays"].get(weekday, [])
            
            # Apply frequency logic
            if frequency == PostingFrequency.DAILY:
                # One post per day
                if day_times:
                    best_time = day_times[0]  # First optimal time
                    time_obj = datetime.strptime(best_time, "%H:%M").time()
                    posting_datetime = datetime.combine(current_date.date(), time_obj)
                    time_slots.append(self.default_timezone.localize(posting_datetime))
            
            elif frequency == PostingFrequency.EVERY_OTHER_DAY:
                # Every other day
                if len(time_slots) == 0 or (current_date - time_slots[-1].date()).days >= 2:
                    if day_times:
                        best_time = day_times[0]
                        time_obj = datetime.strptime(best_time, "%H:%M").time()
                        posting_datetime = datetime.combine(current_date.date(), time_obj)
                        time_slots.append(self.default_timezone.localize(posting_datetime))
            
            elif frequency == PostingFrequency.THREE_TIMES_WEEK:
                # Monday, Wednesday, Friday
                if weekday in [0, 2, 4] and day_times:
                    best_time = day_times[0]
                    time_obj = datetime.strptime(best_time, "%H:%M").time()
                    posting_datetime = datetime.combine(current_date.date(), time_obj)
                    time_slots.append(self.default_timezone.localize(posting_datetime))
            
            elif frequency == PostingFrequency.WEEKLY:
                # Once per week on best day
                best_days = platform_times.get("peak_days", [1])  # Default to Tuesday
                if weekday == best_days[0] and day_times:
                    best_time = day_times[0]
                    time_obj = datetime.strptime(best_time, "%H:%M").time()
                    posting_datetime = datetime.combine(current_date.date(), time_obj)
                    time_slots.append(self.default_timezone.localize(posting_datetime))
            
            current_date += timedelta(days=1)
        
        return time_slots
    
    async def _assign_content_to_slots(
        self,
        content_list: List[ContentOptimization],
        time_slots: List[datetime],
        platform: SocialPlatform,
        strategy: SchedulingStrategy
    ) -> List[ScheduledContent]:
        """Assign content to time slots optimally."""
        
        scheduled_content = []
        
        for i, content in enumerate(content_list):
            if i >= len(time_slots):
                break
            
            # Assign content to time slot
            slot_time = time_slots[i]
            
            # Determine priority
            priority = await self._determine_content_priority(content, platform)
            
            # Create scheduled content item
            scheduled_item = ScheduledContent(
                content_id=str(uuid.uuid4()),
                optimization=content,
                scheduled_time=slot_time,
                priority=priority,
                strategy_used=strategy,
                platform=platform,
                content_type=content.content_type,
                tags=content.hashtags,
                performance_prediction=content.performance_predictions,
                auto_publish=False,  # Manual approval required
                status="scheduled"
            )
            
            scheduled_content.append(scheduled_item)
        
        return scheduled_content
    
    async def _calculate_time_score(
        self,
        posting_time: datetime,
        platform: SocialPlatform,
        content_type: ContentType,
        content: ContentOptimization
    ) -> float:
        """Calculate engagement score for posting time."""
        
        base_score = 0.5
        
        # Platform optimal times bonus
        weekday = posting_time.weekday()
        time_str = posting_time.strftime("%H:%M")
        
        platform_times = self.optimal_times[platform]["weekdays"].get(weekday, [])
        if time_str in platform_times:
            position = platform_times.index(time_str)
            # First time gets highest bonus
            base_score += 0.3 * (1 - position * 0.1)
        
        # Peak day bonus
        peak_days = self.optimal_times[platform].get("peak_days", [])
        if weekday in peak_days:
            base_score += 0.2
        
        # Content type specific timing
        if platform == SocialPlatform.INSTAGRAM and content_type == ContentType.STORY:
            story_times = self.optimal_times[platform].get("story_times", [])
            if time_str in story_times:
                base_score += 0.15
        
        # Audience activity alignment
        hour = posting_time.hour
        if 8 <= hour <= 18:  # Business hours
            base_score += 0.1
        
        # Avoid early morning and late night
        if hour < 6 or hour > 22:
            base_score -= 0.2
        
        return min(1.0, max(0.1, base_score))
    
    async def _generate_scheduling_reasoning(
        self,
        posting_time: datetime,
        platform: SocialPlatform,
        content_type: ContentType,
        content: ContentOptimization
    ) -> List[str]:
        """Generate reasoning for scheduling recommendation."""
        
        reasoning = []
        
        # Time-based reasoning
        hour = posting_time.hour
        weekday_name = posting_time.strftime("%A")
        
        reasoning.append(f"Scheduled for {weekday_name} at {posting_time.strftime('%H:%M')} based on historical engagement data")
        
        # Platform-specific reasoning
        if platform == SocialPlatform.LINKEDIN:
            if 8 <= hour <= 18:
                reasoning.append("Optimal for LinkedIn's professional audience during business hours")
            if posting_time.weekday() in [1, 2, 3]:
                reasoning.append("Mid-week posting for maximum professional engagement")
        
        elif platform == SocialPlatform.INSTAGRAM:
            if content_type == ContentType.STORY:
                reasoning.append("Story content optimized for high-engagement times")
            if hour >= 17:
                reasoning.append("Evening timing for increased Instagram activity")
        
        # Content-specific reasoning
        if "education" in content.engagement_elements:
            reasoning.append("Educational content scheduled when audience is most receptive")
        
        if content.tone == ToneOfVoice.THOUGHT_LEADER:
            reasoning.append("Thought leadership content timed for professional audience availability")
        
        return reasoning
    
    async def _generate_scheduling_considerations(
        self,
        posting_time: datetime,
        platform: SocialPlatform,
        content: ContentOptimization
    ) -> List[str]:
        """Generate scheduling considerations and warnings."""
        
        considerations = []
        
        # Weekend considerations
        if posting_time.weekday() in [5, 6]:
            if platform == SocialPlatform.LINKEDIN:
                considerations.append("Weekend posting may have lower engagement on LinkedIn")
            else:
                considerations.append("Weekend posting may reach different audience segments")
        
        # Holiday considerations
        # This would be enhanced with actual holiday checking
        considerations.append("Check for local holidays or industry events that might affect engagement")
        
        # Content freshness
        considerations.append("Monitor performance and adjust timing based on actual engagement data")
        
        # Platform algorithm considerations
        if platform == SocialPlatform.INSTAGRAM:
            considerations.append("Instagram algorithm favors content with immediate engagement - consider boosting initially")
        elif platform == SocialPlatform.LINKEDIN:
            considerations.append("LinkedIn values meaningful professional interactions - encourage thoughtful comments")
        
        return considerations
    
    async def _determine_content_priority(
        self,
        content: ContentOptimization,
        platform: SocialPlatform
    ) -> ContentPriority:
        """Determine content priority level."""
        
        # High performance prediction = high priority
        engagement_rate = content.performance_predictions.get("engagement_rate", 0)
        
        if engagement_rate > 0.08:
            return ContentPriority.HIGH
        elif engagement_rate > 0.05:
            return ContentPriority.MEDIUM
        elif engagement_rate > 0.02:
            return ContentPriority.LOW
        else:
            return ContentPriority.EVERGREEN
    
    def _analyze_content_distribution(self, scheduled_content: List[ScheduledContent]) -> Dict[str, int]:
        """Analyze distribution of content types in schedule."""
        distribution = {}
        
        for item in scheduled_content:
            content_type = item.content_type.value
            distribution[content_type] = distribution.get(content_type, 0) + 1
        
        return distribution
    
    async def _calculate_calendar_predictions(self, scheduled_content: List[ScheduledContent]) -> Dict[str, float]:
        """Calculate overall calendar performance predictions."""
        if not scheduled_content:
            return {}
        
        total_engagement = sum(
            item.performance_prediction.get("engagement_rate", 0)
            for item in scheduled_content
        )
        
        return {
            "average_engagement_rate": total_engagement / len(scheduled_content),
            "total_predicted_engagement": total_engagement,
            "high_priority_posts": len([
                item for item in scheduled_content 
                if item.priority == ContentPriority.HIGH
            ])
        }
    
    async def optimize_existing_schedule(
        self,
        calendar: ContentCalendar,
        performance_data: Optional[Dict[str, float]] = None
    ) -> ContentCalendar:
        """Optimize existing schedule based on performance data."""
        
        optimized_content = []
        
        for item in calendar.scheduled_content:
            # Skip already published content
            if item.status == "published":
                optimized_content.append(item)
                continue
            
            # Get new recommendation for unpublished content
            recommendation = await self.recommend_posting_time(
                item.optimization,
                item.scheduled_time,
                [other.scheduled_time for other in optimized_content]
            )
            
            # Update scheduling if significantly better
            if recommendation.confidence_score > 0.8:
                item.scheduled_time = recommendation.recommended_time
                item.performance_prediction.update({
                    "engagement_rate": recommendation.expected_engagement
                })
            
            optimized_content.append(item)
        
        # Update calendar
        calendar.scheduled_content = optimized_content
        calendar.calendar_metadata["optimized_at"] = datetime.now().isoformat()
        calendar.calendar_metadata["optimization_improvements"] = len([
            item for item in optimized_content if item.status == "scheduled"
        ])
        
        return calendar
    
    async def get_scheduling_analytics(
        self,
        calendar: ContentCalendar,
        actual_performance: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Generate scheduling performance analytics."""
        
        analytics = {
            "calendar_overview": {
                "total_posts": len(calendar.scheduled_content),
                "date_range": f"{calendar.start_date.date()} to {calendar.end_date.date()}",
                "platform": calendar.platform.value,
                "strategy": calendar.strategy.value
            },
            "performance_predictions": calendar.calendar_metadata.get("engagement_predictions", {}),
            "content_distribution": calendar.calendar_metadata.get("content_types_distribution", {}),
            "timing_analysis": {},
            "optimization_opportunities": []
        }
        
        # Timing analysis
        posting_hours = [item.scheduled_time.hour for item in calendar.scheduled_content]
        posting_days = [item.scheduled_time.weekday() for item in calendar.scheduled_content]
        
        analytics["timing_analysis"] = {
            "most_common_hour": max(set(posting_hours), key=posting_hours.count),
            "most_common_day": max(set(posting_days), key=posting_days.count),
            "time_distribution": {hour: posting_hours.count(hour) for hour in set(posting_hours)},
            "day_distribution": {day: posting_days.count(day) for day in set(posting_days)}
        }
        
        # Compare with actual performance if provided
        if actual_performance:
            predicted_vs_actual = []
            for i, item in enumerate(calendar.scheduled_content):
                if i < len(actual_performance):
                    actual = actual_performance[i]
                    predicted = item.performance_prediction.get("engagement_rate", 0)
                    actual_rate = actual.get("engagement_rate", 0)
                    
                    predicted_vs_actual.append({
                        "predicted": predicted,
                        "actual": actual_rate,
                        "accuracy": 1 - abs(predicted - actual_rate) / max(predicted, actual_rate, 0.01)
                    })
            
            if predicted_vs_actual:
                analytics["prediction_accuracy"] = {
                    "average_accuracy": sum(item["accuracy"] for item in predicted_vs_actual) / len(predicted_vs_actual),
                    "prediction_details": predicted_vs_actual
                }
        
        return analytics