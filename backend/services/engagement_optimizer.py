"""Engagement optimization service for social media content.

This service provides advanced engagement strategies, performance prediction,
and automated optimization recommendations for BYMB Consultancy's social media content.
"""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import statistics
import math

from .social_media_optimizer import SocialPlatform, ContentType, ToneOfVoice

logger = logging.getLogger(__name__)


class EngagementMetric(Enum):
    """Types of engagement metrics."""
    LIKES = "likes"
    COMMENTS = "comments" 
    SHARES = "shares"
    SAVES = "saves"
    CLICKS = "clicks"
    REACH = "reach"
    IMPRESSIONS = "impressions"
    ENGAGEMENT_RATE = "engagement_rate"
    CONVERSION_RATE = "conversion_rate"


class ContentTrigger(Enum):
    """Psychological triggers for engagement."""
    CURIOSITY = "curiosity"
    URGENCY = "urgency"
    SOCIAL_PROOF = "social_proof"
    AUTHORITY = "authority"
    SCARCITY = "scarcity"
    RECIPROCITY = "reciprocity"
    CONTROVERSY = "controversy"
    EMOTION = "emotion"
    EDUCATION = "education"
    INSPIRATION = "inspiration"


@dataclass
class EngagementPattern:
    """Pattern analysis for content engagement."""
    content_type: ContentType
    platform: SocialPlatform
    triggers_used: List[ContentTrigger]
    engagement_score: float
    audience_response: Dict[str, float]
    optimal_posting_time: str
    hashtag_performance: Dict[str, float]
    content_elements: List[str]


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    platform: SocialPlatform
    content_id: str
    metrics: Dict[EngagementMetric, float]
    timestamp: datetime
    audience_demographics: Dict[str, Any]
    content_characteristics: Dict[str, Any]
    comparative_performance: Dict[str, float]


@dataclass
class EngagementPrediction:
    """Predicted engagement performance."""
    predicted_metrics: Dict[EngagementMetric, float]
    confidence_score: float
    key_factors: List[str]
    optimization_suggestions: List[str]
    risk_factors: List[str]
    expected_timeline: Dict[str, float]


@dataclass
class OptimizationRecommendation:
    """Content optimization recommendation."""
    category: str
    priority: int  # 1-5, 5 being highest
    recommendation: str
    expected_impact: float
    implementation_effort: str
    platform_specific: bool
    reasoning: str


class EngagementOptimizer:
    """Advanced engagement optimization service."""
    
    def __init__(self):
        """Initialize engagement optimizer."""
        self.engagement_patterns = self._initialize_engagement_patterns()
        self.trigger_effectiveness = self._initialize_trigger_effectiveness()
        self.platform_algorithms = self._initialize_platform_algorithms()
        self.bymb_performance_data = self._initialize_performance_baselines()
        
        logger.info("Engagement optimizer initialized")
    
    def _initialize_engagement_patterns(self) -> Dict[str, Any]:
        """Initialize historical engagement patterns."""
        return {
            "time_patterns": {
                SocialPlatform.LINKEDIN: {
                    "weekdays": [0.8, 0.9, 1.0, 0.7, 0.6],  # Mon-Fri multipliers
                    "hours": {
                        "07:00": 0.7, "08:00": 0.9, "09:00": 1.0,
                        "10:00": 0.8, "11:00": 0.9, "12:00": 1.0,
                        "13:00": 0.8, "14:00": 0.7, "15:00": 0.6,
                        "16:00": 0.8, "17:00": 0.9, "18:00": 0.6
                    }
                },
                SocialPlatform.INSTAGRAM: {
                    "weekdays": [0.8, 0.9, 0.9, 0.9, 1.0],
                    "hours": {
                        "06:00": 0.6, "07:00": 0.7, "08:00": 0.8,
                        "09:00": 0.9, "11:00": 1.0, "12:00": 0.9,
                        "14:00": 0.8, "17:00": 1.0, "19:00": 1.0,
                        "20:00": 0.9, "21:00": 0.8
                    }
                },
                SocialPlatform.TWITTER: {
                    "weekdays": [0.9, 1.0, 1.0, 0.9, 0.8],
                    "hours": {
                        "08:00": 0.8, "09:00": 1.0, "12:00": 1.0,
                        "15:00": 0.9, "17:00": 0.8, "18:00": 1.0,
                        "20:00": 0.9, "21:00": 0.7
                    }
                },
                SocialPlatform.FACEBOOK: {
                    "weekdays": [0.8, 0.9, 0.9, 0.8, 0.7],
                    "hours": {
                        "09:00": 1.0, "13:00": 1.0, "15:00": 0.9,
                        "19:00": 0.8, "20:00": 0.9
                    }
                }
            },
            "content_type_performance": {
                ContentType.POST: {"base_engagement": 0.03, "virality_factor": 1.0},
                ContentType.CAROUSEL: {"base_engagement": 0.05, "virality_factor": 1.2},
                ContentType.INFOGRAPHIC: {"base_engagement": 0.04, "virality_factor": 0.8},
                ContentType.STORY: {"base_engagement": 0.08, "virality_factor": 0.5},
                ContentType.VIDEO: {"base_engagement": 0.06, "virality_factor": 1.5}
            },
            "industry_benchmarks": {
                "business_consulting": {
                    "average_engagement_rate": 0.025,
                    "top_quartile_engagement": 0.08,
                    "conversion_rate": 0.02
                }
            }
        }
    
    def _initialize_trigger_effectiveness(self) -> Dict[ContentTrigger, Dict[str, float]]:
        """Initialize psychological trigger effectiveness by platform."""
        return {
            ContentTrigger.CURIOSITY: {
                SocialPlatform.INSTAGRAM: 0.8,
                SocialPlatform.LINKEDIN: 0.7,
                SocialPlatform.TWITTER: 0.9,
                SocialPlatform.FACEBOOK: 0.6
            },
            ContentTrigger.AUTHORITY: {
                SocialPlatform.INSTAGRAM: 0.6,
                SocialPlatform.LINKEDIN: 0.9,
                SocialPlatform.TWITTER: 0.7,
                SocialPlatform.FACEBOOK: 0.7
            },
            ContentTrigger.SOCIAL_PROOF: {
                SocialPlatform.INSTAGRAM: 0.9,
                SocialPlatform.LINKEDIN: 0.8,
                SocialPlatform.TWITTER: 0.6,
                SocialPlatform.FACEBOOK: 0.8
            },
            ContentTrigger.EDUCATION: {
                SocialPlatform.INSTAGRAM: 0.7,
                SocialPlatform.LINKEDIN: 0.9,
                SocialPlatform.TWITTER: 0.8,
                SocialPlatform.FACEBOOK: 0.7
            },
            ContentTrigger.INSPIRATION: {
                SocialPlatform.INSTAGRAM: 0.8,
                SocialPlatform.LINKEDIN: 0.7,
                SocialPlatform.TWITTER: 0.6,
                SocialPlatform.FACEBOOK: 0.8
            },
            ContentTrigger.URGENCY: {
                SocialPlatform.INSTAGRAM: 0.5,
                SocialPlatform.LINKEDIN: 0.4,
                SocialPlatform.TWITTER: 0.7,
                SocialPlatform.FACEBOOK: 0.5
            }
        }
    
    def _initialize_platform_algorithms(self) -> Dict[SocialPlatform, Dict[str, Any]]:
        """Initialize platform algorithm preferences."""
        return {
            SocialPlatform.INSTAGRAM: {
                "engagement_weight": 0.4,
                "recency_weight": 0.3,
                "relationship_weight": 0.2,
                "interest_weight": 0.1,
                "preferred_content": ["carousel", "reels", "stories"],
                "engagement_velocity_importance": 0.8,
                "hashtag_optimization": True
            },
            SocialPlatform.LINKEDIN: {
                "engagement_weight": 0.3,
                "recency_weight": 0.2,
                "relationship_weight": 0.3,
                "interest_weight": 0.2,
                "preferred_content": ["articles", "professional_posts"],
                "engagement_velocity_importance": 0.6,
                "professional_relevance": 0.9
            },
            SocialPlatform.TWITTER: {
                "engagement_weight": 0.5,
                "recency_weight": 0.4,
                "relationship_weight": 0.1,
                "interest_weight": 0.0,
                "preferred_content": ["threads", "real_time_updates"],
                "engagement_velocity_importance": 0.9,
                "trending_boost": 0.3
            },
            SocialPlatform.FACEBOOK: {
                "engagement_weight": 0.4,
                "recency_weight": 0.2,
                "relationship_weight": 0.3,
                "interest_weight": 0.1,
                "preferred_content": ["videos", "community_posts"],
                "engagement_velocity_importance": 0.7,
                "meaningful_social_interactions": 0.8
            }
        }
    
    def _initialize_performance_baselines(self) -> Dict[str, Any]:
        """Initialize BYMB Consultancy performance baselines."""
        return {
            "historical_averages": {
                SocialPlatform.LINKEDIN: {
                    EngagementMetric.ENGAGEMENT_RATE: 0.045,
                    EngagementMetric.CLICKS: 0.015,
                    EngagementMetric.COMMENTS: 0.008,
                    EngagementMetric.SHARES: 0.003
                },
                SocialPlatform.INSTAGRAM: {
                    EngagementMetric.ENGAGEMENT_RATE: 0.038,
                    EngagementMetric.SAVES: 0.012,
                    EngagementMetric.COMMENTS: 0.006,
                    EngagementMetric.SHARES: 0.004
                },
                SocialPlatform.TWITTER: {
                    EngagementMetric.ENGAGEMENT_RATE: 0.025,
                    EngagementMetric.CLICKS: 0.018,
                    EngagementMetric.SHARES: 0.008,
                    EngagementMetric.COMMENTS: 0.003
                },
                SocialPlatform.FACEBOOK: {
                    EngagementMetric.ENGAGEMENT_RATE: 0.032,
                    EngagementMetric.CLICKS: 0.012,
                    EngagementMetric.COMMENTS: 0.007,
                    EngagementMetric.SHARES: 0.005
                }
            },
            "top_performing_content": {
                "content_types": [ContentType.CAROUSEL, ContentType.INFOGRAPHIC],
                "triggers": [ContentTrigger.AUTHORITY, ContentTrigger.EDUCATION],
                "topics": ["business_strategy", "growth_insights", "leadership"]
            },
            "audience_insights": {
                "primary_demographics": {
                    "age_range": "35-54",
                    "job_roles": ["CEO", "Director", "Manager"],
                    "industries": ["Consulting", "Finance", "Technology"]
                },
                "engagement_preferences": {
                    "content_length": "medium",
                    "visual_style": "professional",
                    "interaction_type": "educational_discussion"
                }
            }
        }
    
    async def predict_engagement(
        self,
        content: str,
        platform: SocialPlatform,
        content_type: ContentType,
        hashtags: List[str],
        posting_time: str,
        tone: ToneOfVoice
    ) -> EngagementPrediction:
        """Predict engagement performance for content."""
        
        # Analyze content characteristics
        content_features = await self._analyze_content_features(content, tone)
        
        # Calculate base prediction
        base_metrics = await self._calculate_base_metrics(
            platform, content_type, content_features
        )
        
        # Apply platform-specific adjustments
        adjusted_metrics = await self._apply_platform_adjustments(
            base_metrics, platform, content_features, hashtags, posting_time
        )
        
        # Calculate confidence score
        confidence = await self._calculate_prediction_confidence(
            content_features, platform, content_type
        )
        
        # Generate optimization suggestions
        suggestions = await self._generate_optimization_suggestions(
            content_features, platform, adjusted_metrics
        )
        
        # Identify risk factors
        risks = await self._identify_risk_factors(
            content_features, platform, adjusted_metrics
        )
        
        # Create timeline projection
        timeline = await self._create_engagement_timeline(
            adjusted_metrics, platform, content_type
        )
        
        return EngagementPrediction(
            predicted_metrics=adjusted_metrics,
            confidence_score=confidence,
            key_factors=content_features["key_factors"],
            optimization_suggestions=suggestions,
            risk_factors=risks,
            expected_timeline=timeline
        )
    
    async def _analyze_content_features(
        self,
        content: str,
        tone: ToneOfVoice
    ) -> Dict[str, Any]:
        """Analyze content features that impact engagement."""
        
        features = {
            "length": len(content),
            "word_count": len(content.split()),
            "sentence_count": len([s for s in content.split('.') if s.strip()]),
            "has_question": '?' in content,
            "has_call_to_action": any(cta in content.lower() for cta in [
                'comment', 'share', 'like', 'follow', 'click', 'learn more', 'contact'
            ]),
            "emotional_indicators": [],
            "triggers_detected": [],
            "key_factors": []
        }
        
        # Detect psychological triggers
        content_lower = content.lower()
        
        # Curiosity triggers
        curiosity_words = ['secret', 'surprising', 'hidden', 'unknown', 'revealed']
        if any(word in content_lower for word in curiosity_words):
            features["triggers_detected"].append(ContentTrigger.CURIOSITY)
        
        # Authority triggers  
        authority_words = ['expert', 'experience', 'proven', 'results', 'years']
        if any(word in content_lower for word in authority_words):
            features["triggers_detected"].append(ContentTrigger.AUTHORITY)
        
        # Social proof triggers
        social_proof_words = ['clients', 'customers', 'success', 'testimonial']
        if any(word in content_lower for word in social_proof_words):
            features["triggers_detected"].append(ContentTrigger.SOCIAL_PROOF)
        
        # Education triggers
        education_words = ['learn', 'discover', 'understand', 'insight', 'tip']
        if any(word in content_lower for word in education_words):
            features["triggers_detected"].append(ContentTrigger.EDUCATION)
        
        # Emotional indicators
        emotion_words = {
            'positive': ['success', 'growth', 'achievement', 'excellent', 'amazing'],
            'urgency': ['now', 'today', 'immediately', 'urgent', 'deadline'],
            'curiosity': ['why', 'how', 'what', 'secret', 'discover']
        }
        
        for emotion_type, words in emotion_words.items():
            if any(word in content_lower for word in words):
                features["emotional_indicators"].append(emotion_type)
        
        # Key engagement factors
        if features["has_question"]:
            features["key_factors"].append("interactive_question")
        
        if features["has_call_to_action"]:
            features["key_factors"].append("clear_cta")
        
        if features["triggers_detected"]:
            features["key_factors"].append("psychological_triggers")
        
        if tone == ToneOfVoice.THOUGHT_LEADER:
            features["key_factors"].append("thought_leadership_tone")
        
        return features
    
    async def _calculate_base_metrics(
        self,
        platform: SocialPlatform,
        content_type: ContentType,
        content_features: Dict[str, Any]
    ) -> Dict[EngagementMetric, float]:
        """Calculate base engagement metrics."""
        
        # Get historical baselines
        baselines = self.bymb_performance_data["historical_averages"][platform]
        content_performance = self.engagement_patterns["content_type_performance"][content_type]
        
        # Base engagement rate
        base_engagement = baselines.get(EngagementMetric.ENGAGEMENT_RATE, 0.03)
        
        # Content type multiplier
        type_multiplier = content_performance["base_engagement"] / 0.03  # Normalize to 3% base
        
        # Apply content feature adjustments
        feature_multiplier = 1.0
        
        if content_features["has_question"]:
            feature_multiplier *= 1.25  # Questions increase engagement
        
        if content_features["has_call_to_action"]:
            feature_multiplier *= 1.15  # CTAs help
        
        if len(content_features["triggers_detected"]) > 0:
            trigger_boost = sum(
                self.trigger_effectiveness[trigger].get(platform, 0.5)
                for trigger in content_features["triggers_detected"]
            ) / len(content_features["triggers_detected"])
            feature_multiplier *= (1 + trigger_boost * 0.3)
        
        # Calculate individual metrics
        final_engagement = base_engagement * type_multiplier * feature_multiplier
        
        metrics = {
            EngagementMetric.ENGAGEMENT_RATE: final_engagement,
            EngagementMetric.LIKES: final_engagement * 0.7,
            EngagementMetric.COMMENTS: final_engagement * 0.15,
            EngagementMetric.SHARES: final_engagement * 0.12,
            EngagementMetric.SAVES: final_engagement * 0.08,
            EngagementMetric.CLICKS: final_engagement * 0.25,
            EngagementMetric.REACH: final_engagement * 15,  # Reach as multiple of engagement
            EngagementMetric.IMPRESSIONS: final_engagement * 25,
            EngagementMetric.CONVERSION_RATE: final_engagement * 0.1
        }
        
        return metrics
    
    async def _apply_platform_adjustments(
        self,
        base_metrics: Dict[EngagementMetric, float],
        platform: SocialPlatform,
        content_features: Dict[str, Any],
        hashtags: List[str],
        posting_time: str
    ) -> Dict[EngagementMetric, float]:
        """Apply platform-specific adjustments to metrics."""
        
        adjusted = base_metrics.copy()
        algorithm_data = self.platform_algorithms[platform]
        
        # Time-based adjustment
        time_patterns = self.engagement_patterns["time_patterns"][platform]
        time_multiplier = time_patterns["hours"].get(posting_time, 0.8)
        
        # Hashtag optimization (mainly for Instagram and Twitter)
        hashtag_multiplier = 1.0
        if platform in [SocialPlatform.INSTAGRAM, SocialPlatform.TWITTER] and hashtags:
            # Optimize hashtag count
            optimal_count = 11 if platform == SocialPlatform.INSTAGRAM else 2
            hashtag_count = len(hashtags)
            
            if hashtag_count == optimal_count:
                hashtag_multiplier = 1.2
            elif abs(hashtag_count - optimal_count) <= 2:
                hashtag_multiplier = 1.1
            elif hashtag_count > optimal_count * 1.5:
                hashtag_multiplier = 0.9  # Too many hashtags
        
        # Apply platform-specific boosts
        if platform == SocialPlatform.LINKEDIN:
            if ContentTrigger.AUTHORITY in content_features["triggers_detected"]:
                adjusted[EngagementMetric.ENGAGEMENT_RATE] *= 1.3
            if ContentTrigger.EDUCATION in content_features["triggers_detected"]:
                adjusted[EngagementMetric.COMMENTS] *= 1.5
        
        elif platform == SocialPlatform.INSTAGRAM:
            if ContentTrigger.INSPIRATION in content_features["triggers_detected"]:
                adjusted[EngagementMetric.SAVES] *= 1.4
            if ContentTrigger.SOCIAL_PROOF in content_features["triggers_detected"]:
                adjusted[EngagementMetric.SHARES] *= 1.3
        
        elif platform == SocialPlatform.TWITTER:
            if ContentTrigger.CURIOSITY in content_features["triggers_detected"]:
                adjusted[EngagementMetric.CLICKS] *= 1.4
            # Twitter's real-time nature boosts immediate engagement
            adjusted[EngagementMetric.ENGAGEMENT_RATE] *= 1.1
        
        # Apply multipliers
        for metric in adjusted:
            adjusted[metric] *= time_multiplier * hashtag_multiplier
        
        return adjusted
    
    async def _calculate_prediction_confidence(
        self,
        content_features: Dict[str, Any],
        platform: SocialPlatform,
        content_type: ContentType
    ) -> float:
        """Calculate confidence score for predictions."""
        
        confidence_factors = []
        
        # Historical data availability
        confidence_factors.append(0.8)  # We have good baseline data
        
        # Content feature completeness
        feature_score = len(content_features["key_factors"]) / 4.0  # Max 4 key factors
        confidence_factors.append(min(feature_score, 1.0))
        
        # Platform-specific confidence
        platform_confidence = {
            SocialPlatform.LINKEDIN: 0.85,  # Business content performs predictably
            SocialPlatform.INSTAGRAM: 0.75,  # More variable
            SocialPlatform.TWITTER: 0.70,    # Highly variable
            SocialPlatform.FACEBOOK: 0.80    # Moderate variability
        }
        confidence_factors.append(platform_confidence[platform])
        
        # Content type confidence
        type_confidence = {
            ContentType.POST: 0.85,
            ContentType.CAROUSEL: 0.80,
            ContentType.INFOGRAPHIC: 0.75,
            ContentType.STORY: 0.70,
            ContentType.VIDEO: 0.65
        }
        confidence_factors.append(type_confidence.get(content_type, 0.7))
        
        # Calculate weighted average
        return statistics.mean(confidence_factors)
    
    async def _generate_optimization_suggestions(
        self,
        content_features: Dict[str, Any],
        platform: SocialPlatform,
        predicted_metrics: Dict[EngagementMetric, float]
    ) -> List[str]:
        """Generate actionable optimization suggestions."""
        
        suggestions = []
        
        # Content-based suggestions
        if not content_features["has_question"]:
            suggestions.append("Add an engaging question to encourage comments")
        
        if not content_features["has_call_to_action"]:
            suggestions.append("Include a clear call-to-action to drive specific engagement")
        
        if len(content_features["triggers_detected"]) < 2:
            suggestions.append("Incorporate more psychological triggers (authority, social proof, curiosity)")
        
        # Platform-specific suggestions
        if platform == SocialPlatform.LINKEDIN:
            if ContentTrigger.AUTHORITY not in content_features["triggers_detected"]:
                suggestions.append("Emphasize your expertise and 23+ years of experience")
            if predicted_metrics[EngagementMetric.COMMENTS] < 0.01:
                suggestions.append("Ask for professional opinions to increase discussion")
        
        elif platform == SocialPlatform.INSTAGRAM:
            if predicted_metrics[EngagementMetric.SAVES] < 0.015:
                suggestions.append("Create more save-worthy content with actionable tips")
            suggestions.append("Consider using carousel format for better engagement")
        
        elif platform == SocialPlatform.TWITTER:
            if content_features["word_count"] > 30:
                suggestions.append("Consider creating a thread for longer content")
            if predicted_metrics[EngagementMetric.SHARES] < 0.01:
                suggestions.append("Add more shareable insights or statistics")
        
        # Performance-based suggestions
        if predicted_metrics[EngagementMetric.ENGAGEMENT_RATE] < 0.03:
            suggestions.append("Content may need stronger hook or more compelling value proposition")
        
        return suggestions
    
    async def _identify_risk_factors(
        self,
        content_features: Dict[str, Any],
        platform: SocialPlatform,
        predicted_metrics: Dict[EngagementMetric, float]
    ) -> List[str]:
        """Identify potential risk factors for low performance."""
        
        risks = []
        
        # Content risks
        if content_features["word_count"] > 100 and platform == SocialPlatform.TWITTER:
            risks.append("Content may be too long for Twitter's fast-paced environment")
        
        if not content_features["emotional_indicators"]:
            risks.append("Content lacks emotional engagement elements")
        
        if not content_features["triggers_detected"]:
            risks.append("No psychological triggers detected - may not capture attention")
        
        # Platform-specific risks
        if platform == SocialPlatform.LINKEDIN and "professional" not in str(content_features["emotional_indicators"]):
            risks.append("Content may not align with LinkedIn's professional context")
        
        # Performance risks
        if predicted_metrics[EngagementMetric.ENGAGEMENT_RATE] < 0.02:
            risks.append("Predicted engagement rate below industry average")
        
        if predicted_metrics[EngagementMetric.REACH] < 5:
            risks.append("Limited organic reach predicted")
        
        return risks
    
    async def _create_engagement_timeline(
        self,
        predicted_metrics: Dict[EngagementMetric, float],
        platform: SocialPlatform,
        content_type: ContentType
    ) -> Dict[str, float]:
        """Create timeline of expected engagement."""
        
        # Platform-specific engagement curves
        platform_curves = {
            SocialPlatform.TWITTER: {
                "1_hour": 0.6, "6_hours": 0.8, "24_hours": 0.95, "7_days": 1.0
            },
            SocialPlatform.INSTAGRAM: {
                "1_hour": 0.3, "6_hours": 0.6, "24_hours": 0.85, "7_days": 1.0
            },
            SocialPlatform.LINKEDIN: {
                "1_hour": 0.2, "6_hours": 0.5, "24_hours": 0.75, "7_days": 1.0
            },
            SocialPlatform.FACEBOOK: {
                "1_hour": 0.25, "6_hours": 0.5, "24_hours": 0.8, "7_days": 1.0
            }
        }
        
        curve = platform_curves[platform]
        base_engagement = predicted_metrics[EngagementMetric.ENGAGEMENT_RATE]
        
        timeline = {}
        for timepoint, multiplier in curve.items():
            timeline[timepoint] = base_engagement * multiplier
        
        return timeline
    
    async def generate_optimization_recommendations(
        self,
        content: str,
        platform: SocialPlatform,
        current_performance: Optional[Dict[EngagementMetric, float]] = None
    ) -> List[OptimizationRecommendation]:
        """Generate comprehensive optimization recommendations."""
        
        recommendations = []
        
        # Analyze current content
        content_features = await self._analyze_content_features(content, ToneOfVoice.PROFESSIONAL)
        
        # Content structure recommendations
        if not content_features["has_question"]:
            recommendations.append(OptimizationRecommendation(
                category="engagement",
                priority=4,
                recommendation="Add an engaging question at the end to encourage comments",
                expected_impact=0.25,
                implementation_effort="low",
                platform_specific=False,
                reasoning="Questions increase comment engagement by 25% on average"
            ))
        
        if not content_features["has_call_to_action"]:
            recommendations.append(OptimizationRecommendation(
                category="conversion",
                priority=5,
                recommendation="Include a clear call-to-action aligned with business goals",
                expected_impact=0.35,
                implementation_effort="low",
                platform_specific=False,
                reasoning="CTAs improve conversion rates and direct user behavior"
            ))
        
        # Platform-specific recommendations
        if platform == SocialPlatform.LINKEDIN:
            if ContentTrigger.AUTHORITY not in content_features["triggers_detected"]:
                recommendations.append(OptimizationRecommendation(
                    category="credibility",
                    priority=5,
                    recommendation="Highlight BYMB's 23+ years experience and $35M+ client results",
                    expected_impact=0.30,
                    implementation_effort="low",
                    platform_specific=True,
                    reasoning="Authority signals perform exceptionally well on LinkedIn"
                ))
        
        elif platform == SocialPlatform.INSTAGRAM:
            recommendations.append(OptimizationRecommendation(
                category="format",
                priority=3,
                recommendation="Consider carousel format with visual breakdown of key points",
                expected_impact=0.40,
                implementation_effort="medium",
                platform_specific=True,
                reasoning="Carousel posts get 1.4x more engagement than single images on Instagram"
            ))
        
        # Performance-based recommendations
        if current_performance:
            current_engagement = current_performance.get(EngagementMetric.ENGAGEMENT_RATE, 0)
            if current_engagement < 0.03:
                recommendations.append(OptimizationRecommendation(
                    category="performance",
                    priority=5,
                    recommendation="Revise content hook and value proposition for stronger initial impact",
                    expected_impact=0.50,
                    implementation_effort="medium",
                    platform_specific=False,
                    reasoning="Current engagement below industry benchmark requires content refresh"
                ))
        
        # Sort by priority
        recommendations.sort(key=lambda x: x.priority, reverse=True)
        
        return recommendations
    
    async def analyze_competitor_engagement(
        self,
        competitor_content: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze competitor engagement patterns for insights."""
        
        analysis = {
            "top_performing_content": [],
            "common_triggers": [],
            "engagement_patterns": {},
            "content_gaps": [],
            "opportunities": []
        }
        
        # Analyze each competitor content piece
        for content_data in competitor_content:
            content = content_data.get("content", "")
            engagement_rate = content_data.get("engagement_rate", 0)
            platform = content_data.get("platform", SocialPlatform.LINKEDIN)
            
            if engagement_rate > 0.05:  # High performing content
                features = await self._analyze_content_features(content, ToneOfVoice.PROFESSIONAL)
                analysis["top_performing_content"].append({
                    "content": content,
                    "engagement_rate": engagement_rate,
                    "triggers": features["triggers_detected"],
                    "features": features["key_factors"]
                })
        
        # Find common success patterns
        if analysis["top_performing_content"]:
            all_triggers = []
            for item in analysis["top_performing_content"]:
                all_triggers.extend(item["triggers"])
            
            # Count trigger frequency
            trigger_counts = {}
            for trigger in all_triggers:
                trigger_counts[trigger] = trigger_counts.get(trigger, 0) + 1
            
            # Identify most common triggers
            analysis["common_triggers"] = sorted(
                trigger_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        
        # Identify opportunities for BYMB
        bymb_strengths = [
            ContentTrigger.AUTHORITY,
            ContentTrigger.EDUCATION,
            ContentTrigger.SOCIAL_PROOF
        ]
        
        for strength in bymb_strengths:
            if not any(strength in item["triggers"] for item in analysis["top_performing_content"]):
                analysis["opportunities"].append(f"Leverage {strength.value} - underutilized by competitors")
        
        return analysis
    
    async def track_performance_metrics(
        self,
        content_id: str,
        platform: SocialPlatform,
        metrics_data: Dict[str, float],
        timestamp: Optional[datetime] = None
    ) -> PerformanceMetrics:
        """Track and store performance metrics."""
        
        if timestamp is None:
            timestamp = datetime.now()
        
        # Convert raw metrics to EngagementMetric enum
        engagement_metrics = {}
        for key, value in metrics_data.items():
            try:
                metric = EngagementMetric(key)
                engagement_metrics[metric] = value
            except ValueError:
                logger.warning(f"Unknown metric: {key}")
                continue
        
        # Get comparative performance
        baselines = self.bymb_performance_data["historical_averages"][platform]
        comparative = {}
        for metric, value in engagement_metrics.items():
            baseline = baselines.get(metric, 0)
            if baseline > 0:
                comparative[metric.value] = value / baseline
        
        return PerformanceMetrics(
            platform=platform,
            content_id=content_id,
            metrics=engagement_metrics,
            timestamp=timestamp,
            audience_demographics={},  # Would be populated from platform APIs
            content_characteristics={},
            comparative_performance=comparative
        )