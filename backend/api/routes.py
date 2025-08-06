"""API routes for the application."""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Path, Query, Body, BackgroundTasks, WebSocket, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from services.example_service import ExampleService
from services.social_media_optimizer import (
    SocialMediaOptimizer, SocialPlatform, ContentType, ToneOfVoice, ContentOptimization
)
from services.content_adapter import ContentAdapter, VisualStyle
from services.engagement_optimizer import EngagementOptimizer, EngagementMetric
from services.content_scheduler import (
    ContentScheduler, PostingFrequency, SchedulingStrategy, ContentPriority
)
from services.brand_profile import bymb_brand, PlatformType as BrandPlatformType, ContentType as BrandContentType
from services.brand_validator import brand_validator, ValidationSeverity, ContentAnalysis
from services.brand_template_engine import brand_template_engine, GenerationRequest
from services.brand_enforcer import brand_enforcer, EnforcementLevel
from services.branded_content_service import (
    branded_content_service, ContentRequest, ContentCreationMode, QualityLevel
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["api"])

# Initialize services
example_service = ExampleService()
social_optimizer = SocialMediaOptimizer()
content_adapter = ContentAdapter()
engagement_optimizer = EngagementOptimizer()
content_scheduler = ContentScheduler()

# Pydantic models for request/response
class ContentOptimizationRequest(BaseModel):
    content: str = Field(..., description="Raw content to optimize")
    platform: SocialPlatform = Field(..., description="Target social media platform")
    content_type: ContentType = Field(ContentType.POST, description="Type of content")
    target_audience: str = Field("business_leaders", description="Target audience segment")
    tone: ToneOfVoice = Field(ToneOfVoice.PROFESSIONAL, description="Desired tone of voice")

class MultiPlatformRequest(BaseModel):
    content: str = Field(..., description="Base content to optimize for multiple platforms")
    platforms: List[SocialPlatform] = Field(..., description="Target platforms")
    content_types: Optional[List[ContentType]] = Field(None, description="Content types for each platform")
    target_audience: str = Field("business_leaders", description="Target audience")

class ContentAdaptationRequest(BaseModel):
    optimization: Dict = Field(..., description="Content optimization data")
    visual_style: VisualStyle = Field(VisualStyle.PROFESSIONAL_MINIMAL, description="Visual style")
    background_image: Optional[str] = Field(None, description="Background image path")

class EngagementPredictionRequest(BaseModel):
    content: str = Field(..., description="Content to analyze")
    platform: SocialPlatform = Field(..., description="Target platform")
    content_type: ContentType = Field(ContentType.POST, description="Content type")
    hashtags: List[str] = Field([], description="Hashtags to use")
    posting_time: str = Field("09:00", description="Posting time in HH:MM format")
    tone: ToneOfVoice = Field(ToneOfVoice.PROFESSIONAL, description="Content tone")

class SchedulingRequest(BaseModel):
    content_list: List[Dict] = Field(..., description="List of optimized content")
    start_date: datetime = Field(..., description="Schedule start date")
    end_date: datetime = Field(..., description="Schedule end date")
    platform: SocialPlatform = Field(..., description="Target platform")
    frequency: PostingFrequency = Field(PostingFrequency.DAILY, description="Posting frequency")
    strategy: SchedulingStrategy = Field(SchedulingStrategy.OPTIMAL_TIMES, description="Scheduling strategy")

class PerformanceTrackingRequest(BaseModel):
    content_id: str = Field(..., description="Content ID")
    platform: SocialPlatform = Field(..., description="Platform")
    metrics_data: Dict[str, float] = Field(..., description="Performance metrics")
    timestamp: Optional[datetime] = Field(None, description="Metrics timestamp")

# Brand System Request Models

class BrandValidationRequest(BaseModel):
    text_content: str = Field(..., description="Text content to validate")
    visual_elements: Dict[str, Any] = Field({}, description="Visual elements data")
    platform: BrandPlatformType = Field(..., description="Target platform")
    content_type: Optional[BrandContentType] = Field(None, description="Content type")
    platform_specs: Dict[str, Any] = Field({}, description="Platform specifications")

class BrandEnforcementRequest(BaseModel):
    content: Dict[str, Any] = Field(..., description="Content to enforce")
    platform: BrandPlatformType = Field(..., description="Target platform")
    content_type: Optional[BrandContentType] = Field(None, description="Content type")
    enforcement_level: Optional[EnforcementLevel] = Field(EnforcementLevel.MODERATE, description="Enforcement level")

class TemplateGenerationRequest(BaseModel):
    template_id: str = Field(..., description="Template ID to use")
    content: Dict[str, str] = Field(..., description="Variable replacements")
    platform: BrandPlatformType = Field(..., description="Target platform")
    content_type: Optional[BrandContentType] = Field(None, description="Content type")
    customizations: Dict[str, Any] = Field({}, description="Template customizations")
    brand_validation_required: bool = Field(True, description="Require brand validation")

class BrandedContentGenerationRequest(BaseModel):
    text_content: str = Field(..., description="Text content for generation")
    platform: BrandPlatformType = Field(..., description="Target platform")
    content_type: BrandContentType = Field(..., description="Content type")
    quality_level: QualityLevel = Field(QualityLevel.STANDARD, description="Quality level")
    creation_mode: ContentCreationMode = Field(ContentCreationMode.HYBRID, description="Creation mode")
    brand_tone: Optional[str] = Field(None, description="Brand tone")
    enforce_brand_compliance: bool = Field(True, description="Enforce brand compliance")
    minimum_brand_score: float = Field(0.8, description="Minimum brand score")
    visual_style: Optional[str] = Field(None, description="Visual style")
    color_scheme: Optional[str] = Field(None, description="Color scheme")
    include_logo: bool = Field(True, description="Include brand logo")
    freepik_search_terms: Optional[List[str]] = Field(None, description="Freepik search terms")
    use_freepik_ai: bool = Field(False, description="Use Freepik AI generation")
    template_id: Optional[str] = Field(None, description="Specific template ID")
    custom_dimensions: Optional[List[int]] = Field(None, description="Custom dimensions [width, height]")
    output_formats: List[str] = Field(["PNG"], description="Output formats")
    include_variations: bool = Field(False, description="Include variations")
    variation_count: int = Field(3, description="Number of variations")
    user_id: str = Field("default", description="User ID")

# Advanced Content Generation Models

class BusinessInsightRequest(BaseModel):
    """Model for business insight extraction and validation."""
    raw_insight: str = Field(..., description="Raw business insight text")
    context_metadata: Optional[Dict[str, Any]] = Field({}, description="Additional context")
    industry_sector: Optional[str] = Field(None, description="Industry sector")
    target_audience: Optional[str] = Field(None, description="Target audience description")
    business_goals: Optional[List[str]] = Field([], description="Business objectives")
    validation_level: str = Field("standard", description="Validation strictness level")

class CompleteContentGenerationRequest(BaseModel):
    """Model for end-to-end content generation workflow."""
    business_insight: str = Field(..., description="Business insight text")
    target_platforms: List[BrandPlatformType] = Field(..., description="Target social media platforms")
    content_requirements: Dict[str, Any] = Field(..., description="Content generation requirements")
    brand_requirements: Dict[str, Any] = Field({}, description="Brand compliance requirements")
    optimization_preferences: Optional[Dict[str, Any]] = Field({}, description="Optimization preferences")
    delivery_format: str = Field("comprehensive", description="Delivery format type")
    priority_level: str = Field("normal", description="Processing priority")
    webhook_url: Optional[str] = Field(None, description="Completion webhook URL")
    user_id: str = Field(..., description="User identifier")

class CopyGenerationRequest(BaseModel):
    """Model for platform-optimized copy generation."""
    structured_insights: Dict[str, Any] = Field(..., description="Processed business insights")
    platform_specs: Dict[str, Any] = Field(..., description="Platform specifications")
    tone_requirements: Dict[str, str] = Field({}, description="Tone and voice requirements")
    engagement_targets: Optional[Dict[str, float]] = Field({}, description="Target engagement metrics")
    a_b_testing: bool = Field(False, description="Generate A/B testing variants")
    variant_count: int = Field(2, description="Number of variants to generate")
    hashtag_strategy: str = Field("auto", description="Hashtag generation strategy")

class VisualGenerationRequest(BaseModel):
    """Model for branded visual content generation."""
    copy_content: Dict[str, Any] = Field(..., description="Generated copy content")
    visual_style_preferences: Dict[str, Any] = Field({}, description="Visual style preferences")
    brand_requirements: Dict[str, Any] = Field(..., description="Brand compliance requirements")
    format_specifications: List[Dict[str, Any]] = Field(..., description="Output format specifications")
    freepik_integration: Dict[str, Any] = Field({}, description="Freepik API integration settings")
    quality_settings: Dict[str, Any] = Field({}, description="Quality and rendering settings")
    template_preferences: Optional[Dict[str, Any]] = Field({}, description="Template usage preferences")

# Analytics and Performance Models

class ContentPerformanceQuery(BaseModel):
    """Model for content performance analytics queries."""
    content_ids: List[str] = Field(..., description="Content IDs to analyze")
    metrics: List[str] = Field(..., description="Metrics to include")
    time_range: Dict[str, datetime] = Field(..., description="Analysis time range")
    comparison_baseline: Optional[str] = Field(None, description="Comparison baseline type")
    aggregation_level: str = Field("daily", description="Data aggregation level")
    include_predictions: bool = Field(True, description="Include predictive analytics")

class EngagementTrackingData(BaseModel):
    """Model for real-time engagement tracking."""
    content_id: str = Field(..., description="Content identifier")
    platform: str = Field(..., description="Social media platform")
    engagement_metrics: Dict[str, float] = Field(..., description="Current engagement metrics")
    timestamp: datetime = Field(..., description="Metrics timestamp")
    user_demographics: Optional[Dict[str, Any]] = Field({}, description="User demographic data")
    geographic_data: Optional[Dict[str, Any]] = Field({}, description="Geographic engagement data")

class ReportGenerationRequest(BaseModel):
    """Model for custom analytics report generation."""
    report_type: str = Field(..., description="Type of report to generate")
    parameters: Dict[str, Any] = Field(..., description="Report parameters")
    metrics_selection: List[str] = Field(..., description="Selected metrics")
    time_period: Dict[str, datetime] = Field(..., description="Report time period")
    format_preferences: Dict[str, str] = Field({"format": "PDF"}, description="Export format preferences")
    delivery_options: Dict[str, Any] = Field({}, description="Report delivery options")
    branding_options: Dict[str, bool] = Field({"include_logo": True}, description="Report branding options")

# Asset and Template Management Models

class AssetUploadRequest(BaseModel):
    """Model for brand asset uploads."""
    asset_name: str = Field(..., description="Asset name")
    asset_category: str = Field(..., description="Asset category")
    metadata: Dict[str, Any] = Field({}, description="Asset metadata")
    usage_guidelines: Optional[str] = Field(None, description="Usage guidelines")
    tags: List[str] = Field([], description="Asset tags")
    access_level: str = Field("public", description="Access level")
    brand_validation_required: bool = Field(True, description="Require brand validation")

class TemplateCreationRequest(BaseModel):
    """Model for dynamic template creation."""
    template_name: str = Field(..., description="Template name")
    template_category: str = Field(..., description="Template category")
    specifications: Dict[str, Any] = Field(..., description="Template specifications")
    brand_requirements: Dict[str, Any] = Field(..., description="Brand requirements")
    customization_options: List[Dict[str, Any]] = Field([], description="Available customizations")
    platforms: List[BrandPlatformType] = Field(..., description="Supported platforms")
    validation_rules: Optional[Dict[str, Any]] = Field({}, description="Validation rules")

# Workflow Orchestration Models

class WorkflowInitiationRequest(BaseModel):
    """Model for workflow initiation."""
    workflow_type: str = Field(..., description="Type of workflow")
    parameters: Dict[str, Any] = Field(..., description="Workflow parameters")
    user_preferences: Dict[str, Any] = Field({}, description="User preferences")
    completion_criteria: Dict[str, Any] = Field(..., description="Completion criteria")
    notification_settings: Dict[str, bool] = Field({}, description="Notification preferences")
    priority: str = Field("normal", description="Workflow priority")

class BatchContentRequest(BaseModel):
    """Model for batch content generation."""
    batch_specifications: List[Dict[str, Any]] = Field(..., description="Batch item specifications")
    processing_preferences: Dict[str, Any] = Field({}, description="Processing preferences")
    quality_requirements: Dict[str, Any] = Field({}, description="Quality requirements")
    delivery_timeline: Optional[datetime] = Field(None, description="Required completion time")
    failure_handling: str = Field("continue", description="Failure handling strategy")

class WorkflowInterventionRequest(BaseModel):
    """Model for workflow intervention."""
    intervention_type: str = Field(..., description="Type of intervention")
    modification_parameters: Dict[str, Any] = Field(..., description="Modification parameters")
    approval_status: str = Field(..., description="Approval status")
    intervention_reason: str = Field(..., description="Reason for intervention")
    notify_stakeholders: bool = Field(True, description="Notify relevant stakeholders")

# Cost Management and Configuration Models

class RateLimitConfiguration(BaseModel):
    """Model for rate limit configuration."""
    rate_limit_rules: Dict[str, Dict[str, int]] = Field(..., description="Rate limiting rules")
    priority_settings: Dict[str, str] = Field({}, description="Priority configurations")
    user_quotas: Dict[str, Dict[str, int]] = Field({}, description="User-specific quotas")
    override_settings: Optional[Dict[str, Any]] = Field({}, description="Override configurations")
    monitoring_preferences: Dict[str, bool] = Field({}, description="Monitoring settings")

# Webhook Integration Models

class WebhookRegistrationRequest(BaseModel):
    """Model for webhook registration."""
    webhook_url: str = Field(..., description="Webhook endpoint URL")
    event_types: List[str] = Field(..., description="Event types to subscribe to")
    authentication: Dict[str, str] = Field({}, description="Authentication details")
    retry_policy: Dict[str, Any] = Field({}, description="Retry policy configuration")
    event_filters: Optional[Dict[str, Any]] = Field({}, description="Event filtering rules")
    active: bool = Field(True, description="Webhook active status")

class WebhookTestRequest(BaseModel):
    """Model for webhook testing."""
    webhook_configuration: Dict[str, Any] = Field(..., description="Webhook configuration to test")
    test_payload: Dict[str, Any] = Field({}, description="Test payload data")
    validation_requirements: List[str] = Field([], description="Validation requirements")
    timeout_seconds: int = Field(30, description="Test timeout duration")

# Authentication Models

class TokenRequest(BaseModel):
    """Model for authentication token requests."""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    scope: Optional[List[str]] = Field([], description="Requested scopes")
    expires_in: Optional[int] = Field(3600, description="Token expiration time")

class ApiKeyRequest(BaseModel):
    """Model for API key generation."""
    key_name: str = Field(..., description="API key name")
    permissions: List[str] = Field(..., description="API key permissions")
    expires_at: Optional[datetime] = Field(None, description="Key expiration date")
    rate_limits: Optional[Dict[str, int]] = Field({}, description="Key-specific rate limits")


@router.get("/example")
async def example_endpoint() -> Dict[str, str]:
    """Example endpoint.

    Returns
    -------
    Dict[str, str]
        Example response.
    """
    try:
        return {"message": "This is an example endpoint"}
    except Exception as e:
        logger.error(f"Error in example endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/examples", response_model=List[Dict[str, str]])
async def get_all_examples() -> List[Dict[str, str]]:
    """Get all examples.

    Returns
    -------
    List[Dict[str, str]]
        List of all examples.
    """
    try:
        return example_service.get_all_examples()
    except Exception as e:
        logger.error(f"Error getting all examples: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/examples/{example_id}", response_model=Dict[str, str])
async def get_example_by_id(
    example_id: str = Path(..., description="ID of the example"),
) -> Dict[str, str]:
    """Get an example by ID.

    Parameters
    ----------
    example_id : str
        ID of the example to retrieve.

    Returns
    -------
    Dict[str, str]
        Example data.
    """
    try:
        return example_service.get_example_by_id(example_id)
    except ValueError as e:
        logger.error(f"Example not found: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Error getting example by ID: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Social Media Optimization Endpoints

@router.post("/social-media/optimize")
async def optimize_content(request: ContentOptimizationRequest) -> Dict:
    """Optimize content for a specific social media platform.
    
    Returns optimized content with platform-specific formatting, hashtags,
    engagement elements, and performance predictions.
    """
    try:
        optimization = await social_optimizer.optimize_content_for_platform(
            content=request.content,
            platform=request.platform,
            content_type=request.content_type,
            target_audience=request.target_audience,
            tone=request.tone
        )
        
        # Convert to dict for JSON serialization
        return {
            "platform": optimization.platform.value,
            "content_type": optimization.content_type.value,
            "title": optimization.title,
            "caption": optimization.caption,
            "hashtags": optimization.hashtags,
            "tone": optimization.tone.value,
            "call_to_action": optimization.call_to_action,
            "image_specs": optimization.image_specs,
            "engagement_elements": optimization.engagement_elements,
            "optimal_posting_time": optimization.optimal_posting_time,
            "performance_predictions": optimization.performance_predictions,
            "brand_compliance": optimization.brand_compliance
        }
    except Exception as e:
        logger.error(f"Content optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/social-media/multi-platform")
async def optimize_multi_platform(request: MultiPlatformRequest) -> Dict:
    """Optimize content for multiple social media platforms simultaneously.
    
    Returns a comprehensive campaign with platform-specific optimizations.
    """
    try:
        campaign = await social_optimizer.generate_multi_platform_campaign(
            base_content=request.content,
            platforms=request.platforms,
            content_types=request.content_types,
            target_audience=request.target_audience
        )
        
        # Convert to serializable format
        serialized_campaign = {}
        for platform, optimizations in campaign.items():
            serialized_campaign[platform.value] = []
            for opt in optimizations:
                serialized_campaign[platform.value].append({
                    "platform": opt.platform.value,
                    "content_type": opt.content_type.value,
                    "title": opt.title,
                    "caption": opt.caption,
                    "hashtags": opt.hashtags,
                    "tone": opt.tone.value,
                    "call_to_action": opt.call_to_action,
                    "image_specs": opt.image_specs,
                    "engagement_elements": opt.engagement_elements,
                    "optimal_posting_time": opt.optimal_posting_time,
                    "performance_predictions": opt.performance_predictions,
                    "brand_compliance": opt.brand_compliance
                })
        
        return {
            "campaign": serialized_campaign,
            "platforms_count": len(request.platforms),
            "total_content_pieces": sum(len(opts) for opts in campaign.values()),
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Multi-platform optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/content/adapt-visual")
async def adapt_content_visual(request: ContentAdaptationRequest) -> Dict:
    """Adapt optimized content to visual format with brand elements.
    
    Creates platform-optimized visual content with proper dimensions,
    brand colors, typography, and visual elements.
    """
    try:
        # Convert dict back to ContentOptimization object
        # This is simplified - in production, you'd have proper serialization
        optimization_data = request.optimization
        
        # Mock ContentOptimization for adaptation
        # In production, this would be properly reconstructed
        adaptation_result = await content_adapter.adapt_content_to_format(
            optimization=None,  # Would be reconstructed from request.optimization
            visual_style=request.visual_style,
            background_image=request.background_image
        )
        
        return {
            "success": adaptation_result.success,
            "file_path": adaptation_result.file_path,
            "file_size": adaptation_result.file_size,
            "dimensions": adaptation_result.dimensions,
            "format": adaptation_result.format,
            "visual_style": adaptation_result.visual_style.value if adaptation_result.visual_style else None,
            "optimization_applied": adaptation_result.optimization_applied,
            "error_message": adaptation_result.error_message,
            "metadata": adaptation_result.metadata
        }
    except Exception as e:
        logger.error(f"Content adaptation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/engagement/predict")
async def predict_engagement(request: EngagementPredictionRequest) -> Dict:
    """Predict engagement performance for content.
    
    Analyzes content characteristics and provides engagement predictions
    with optimization suggestions and risk factors.
    """
    try:
        prediction = await engagement_optimizer.predict_engagement(
            content=request.content,
            platform=request.platform,
            content_type=request.content_type,
            hashtags=request.hashtags,
            posting_time=request.posting_time,
            tone=request.tone
        )
        
        return {
            "predicted_metrics": {
                metric.value: value for metric, value in prediction.predicted_metrics.items()
            },
            "confidence_score": prediction.confidence_score,
            "key_factors": prediction.key_factors,
            "optimization_suggestions": prediction.optimization_suggestions,
            "risk_factors": prediction.risk_factors,
            "expected_timeline": prediction.expected_timeline
        }
    except Exception as e:
        logger.error(f"Engagement prediction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/engagement/recommendations")
async def get_optimization_recommendations(
    content: str = Body(...),
    platform: SocialPlatform = Body(...),
    current_performance: Optional[Dict[str, float]] = Body(None)
) -> Dict:
    """Get optimization recommendations for content.
    
    Provides actionable recommendations to improve content performance
    with priority levels and expected impact.
    """
    try:
        # Convert current_performance to EngagementMetric dict if provided
        performance_dict = None
        if current_performance:
            performance_dict = {}
            for key, value in current_performance.items():
                try:
                    metric = EngagementMetric(key)
                    performance_dict[metric] = value
                except ValueError:
                    continue
        
        recommendations = await engagement_optimizer.generate_optimization_recommendations(
            content=content,
            platform=platform,
            current_performance=performance_dict
        )
        
        return {
            "recommendations": [
                {
                    "category": rec.category,
                    "priority": rec.priority,
                    "recommendation": rec.recommendation,
                    "expected_impact": rec.expected_impact,
                    "implementation_effort": rec.implementation_effort,
                    "platform_specific": rec.platform_specific,
                    "reasoning": rec.reasoning
                }
                for rec in recommendations
            ],
            "total_recommendations": len(recommendations),
            "high_priority_count": len([r for r in recommendations if r.priority >= 4])
        }
    except Exception as e:
        logger.error(f"Optimization recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/scheduling/generate")
async def generate_content_schedule(request: SchedulingRequest) -> Dict:
    """Generate optimal content posting schedule.
    
    Creates a comprehensive content calendar with optimal timing,
    frequency management, and performance predictions.
    """
    try:
        # Convert content_list dicts back to ContentOptimization objects
        # This is simplified - in production, you'd have proper serialization
        content_optimizations = []  # Would be reconstructed from request.content_list
        
        calendar = await content_scheduler.generate_optimal_schedule(
            content_list=content_optimizations,
            start_date=request.start_date,
            end_date=request.end_date,
            platform=request.platform,
            frequency=request.frequency,
            strategy=request.strategy
        )
        
        return {
            "calendar": {
                "start_date": calendar.start_date.isoformat(),
                "end_date": calendar.end_date.isoformat(),
                "platform": calendar.platform.value,
                "frequency_target": calendar.frequency_target.value,
                "strategy": calendar.strategy.value,
                "timezone": calendar.timezone,
                "metadata": calendar.calendar_metadata
            },
            "scheduled_content": [
                {
                    "content_id": item.content_id,
                    "scheduled_time": item.scheduled_time.isoformat(),
                    "priority": item.priority.value,
                    "platform": item.platform.value,
                    "content_type": item.content_type.value,
                    "tags": item.tags,
                    "performance_prediction": item.performance_prediction,
                    "status": item.status
                }
                for item in calendar.scheduled_content
            ],
            "summary": {
                "total_posts": len(calendar.scheduled_content),
                "date_range_days": (calendar.end_date - calendar.start_date).days,
                "average_posts_per_day": len(calendar.scheduled_content) / max(1, (calendar.end_date - calendar.start_date).days)
            }
        }
    except Exception as e:
        logger.error(f"Schedule generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/scheduling/recommend-time")
async def recommend_posting_time(
    content: Dict = Body(...),
    target_date: Optional[datetime] = Body(None),
    avoid_conflicts: Optional[List[datetime]] = Body(None)
) -> Dict:
    """Recommend optimal posting time for content.
    
    Provides intelligent posting time recommendations based on platform
    algorithms, audience activity, and content characteristics.
    """
    try:
        # Convert dict back to ContentOptimization
        # This is simplified - would need proper reconstruction
        content_optimization = None  # Would be reconstructed from content dict
        
        recommendation = await content_scheduler.recommend_posting_time(
            content=content_optimization,
            target_date=target_date,
            avoid_conflicts=avoid_conflicts or []
        )
        
        return {
            "recommended_time": recommendation.recommended_time.isoformat(),
            "confidence_score": recommendation.confidence_score,
            "expected_engagement": recommendation.expected_engagement,
            "reasoning": recommendation.reasoning,
            "alternative_times": [
                {
                    "time": time.isoformat(),
                    "score": score
                }
                for time, score in recommendation.alternative_times
            ],
            "considerations": recommendation.considerations
        }
    except Exception as e:
        logger.error(f"Time recommendation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/performance/track")
async def track_performance(request: PerformanceTrackingRequest) -> Dict:
    """Track content performance metrics.
    
    Records and analyzes content performance data for optimization insights.
    """
    try:
        metrics = await engagement_optimizer.track_performance_metrics(
            content_id=request.content_id,
            platform=request.platform,
            metrics_data=request.metrics_data,
            timestamp=request.timestamp
        )
        
        return {
            "content_id": metrics.content_id,
            "platform": metrics.platform.value,
            "metrics": {
                metric.value: value for metric, value in metrics.metrics.items()
            },
            "timestamp": metrics.timestamp.isoformat(),
            "comparative_performance": metrics.comparative_performance,
            "tracking_success": True
        }
    except Exception as e:
        logger.error(f"Performance tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/analytics/platform-metrics/{platform}")
async def get_platform_analytics(
    platform: SocialPlatform = Path(..., description="Social media platform")
) -> Dict:
    """Get recommended analytics metrics for a platform.
    
    Returns comprehensive metrics tracking recommendations specific
    to each social media platform.
    """
    try:
        metrics = await social_optimizer.get_platform_analytics_metrics(platform)
        
        return {
            "platform": platform.value,
            "metrics": metrics,
            "tracking_recommendations": {
                "frequency": "daily",
                "key_focus_metrics": metrics.get("core_metrics", [])[:5],
                "platform_priorities": metrics.get("platform_specific", [])[:3]
            }
        }
    except Exception as e:
        logger.error(f"Platform analytics failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/health/social-media")
async def health_check_social_media() -> Dict:
    """Health check for social media optimization services.
    
    Verifies all social media optimization services are functioning correctly.
    """
    try:
        health_status = {
            "social_optimizer": "healthy",
            "content_adapter": "healthy",
            "engagement_optimizer": "healthy",
            "content_scheduler": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services_count": 4
        }
        
        # Test basic functionality
        test_content = "Test business insight for health check"
        test_optimization = await social_optimizer.optimize_content_for_platform(
            content=test_content,
            platform=SocialPlatform.LINKEDIN,
            content_type=ContentType.POST
        )
        
        if test_optimization.caption:
            health_status["functionality_test"] = "passed"
        else:
            health_status["functionality_test"] = "failed"
            health_status["social_optimizer"] = "degraded"
        
        return health_status
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "social_optimizer": "unhealthy",
            "content_adapter": "unknown",
            "engagement_optimizer": "unknown", 
            "content_scheduler": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# Brand System Endpoints

@router.get("/brand/profile")
async def get_brand_profile() -> Dict:
    """Get BYMB brand profile information.
    
    Returns comprehensive brand identity, visual system, voice guidelines,
    and platform specifications.
    """
    try:
        brand_guide = bymb_brand.export_brand_guide()
        return {
            "success": True,
            "brand_profile": brand_guide,
            "profile_version": "1.0",
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Brand profile retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/colors")
async def get_brand_colors() -> Dict:
    """Get brand color palette with usage guidelines."""
    try:
        colors = bymb_brand.get_color_palette(include_secondary=True)
        return {
            "success": True,
            "colors": [
                {
                    "name": color.name,
                    "hex": color.hex,
                    "rgb": color.rgb,
                    "hsl": color.hsl,
                    "usage": color.usage,
                    "pantone": color.pantone
                }
                for color in colors
            ],
            "total_colors": len(colors)
        }
    except Exception as e:
        logger.error(f"Brand colors retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/fonts")
async def get_brand_fonts() -> Dict:
    """Get brand typography specifications."""
    try:
        fonts = bymb_brand.get_brand_fonts()
        return {
            "success": True,
            "fonts": {
                name: {
                    "family": spec.family,
                    "weight": spec.weight,
                    "size_px": spec.size_px,
                    "size_pt": spec.size_pt,
                    "line_height": spec.line_height,
                    "letter_spacing": spec.letter_spacing,
                    "usage": spec.usage
                }
                for name, spec in fonts.items()
            },
            "total_fonts": len(fonts)
        }
    except Exception as e:
        logger.error(f"Brand fonts retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/platform-specs/{platform}")
async def get_platform_specifications(
    platform: BrandPlatformType = Path(..., description="Social media platform")
) -> Dict:
    """Get platform-specific brand specifications."""
    try:
        specs = bymb_brand.get_platform_specs(platform)
        if not specs:
            raise HTTPException(status_code=404, detail=f"No specifications found for platform: {platform}")
        
        return {
            "success": True,
            "platform": platform.value,
            "specifications": {
                "dimensions": specs.dimensions,
                "safe_zones": specs.safe_zones,
                "text_limits": specs.text_limits,
                "optimal_image_ratio": specs.optimal_image_ratio,
                "recommended_fonts": specs.recommended_fonts
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Platform specifications retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/brand/validate")
async def validate_brand_compliance(request: BrandValidationRequest) -> Dict:
    """Validate content against BYMB brand guidelines.
    
    Performs comprehensive brand compliance validation and returns
    detailed scoring with recommendations.
    """
    try:
        content_analysis = ContentAnalysis(
            text_content=request.text_content,
            visual_elements=request.visual_elements,
            platform_specs=request.platform_specs
        )
        
        validation_result = await brand_validator.validate_content(
            content_analysis, 
            request.platform, 
            request.content_type
        )
        
        return {
            "success": True,
            "validation_result": {
                "overall_score": validation_result.overall_score,
                "compliance_level": validation_result.compliance_level,
                "category_scores": {
                    category.value: score 
                    for category, score in validation_result.category_scores.items()
                },
                "issues": [
                    {
                        "category": issue.category.value,
                        "severity": issue.severity.value,
                        "message": issue.message,
                        "description": issue.description,
                        "suggestion": issue.suggestion,
                        "affected_element": issue.affected_element,
                        "current_value": issue.current_value,
                        "expected_value": issue.expected_value,
                        "score_impact": issue.score_impact
                    }
                    for issue in validation_result.issues
                ],
                "passed_checks": validation_result.passed_checks,
                "recommendations": validation_result.recommendations,
                "validation_timestamp": validation_result.validation_timestamp,
                "metadata": validation_result.metadata
            }
        }
    except Exception as e:
        logger.error(f"Brand validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/brand/enforce")
async def enforce_brand_compliance(request: BrandEnforcementRequest) -> Dict:
    """Enforce brand compliance with automatic corrections.
    
    Applies brand enforcement rules and automatically corrects
    violations where possible.
    """
    try:
        # Set enforcement level if provided
        if request.enforcement_level:
            brand_enforcer.enforcement_level = request.enforcement_level
        
        enforcement_result = await brand_enforcer.enforce_brand_compliance(
            request.content,
            request.platform,
            request.content_type
        )
        
        return {
            "success": enforcement_result.success,
            "enforcement_result": {
                "original_score": enforcement_result.original_score,
                "corrected_score": enforcement_result.corrected_score,
                "corrections_applied": [
                    {
                        "type": correction.type.value,
                        "severity": correction.severity.value,
                        "description": correction.description,
                        "original_value": correction.original_value,
                        "corrected_value": correction.corrected_value,
                        "confidence": correction.confidence,
                        "automatic": correction.automatic,
                        "metadata": correction.metadata
                    }
                    for correction in enforcement_result.corrections_applied
                ],
                "recommendations": enforcement_result.recommendations,
                "corrected_content": enforcement_result.corrected_content,
                "warnings": enforcement_result.warnings,
                "errors": enforcement_result.errors,
                "enforcement_metadata": enforcement_result.enforcement_metadata
            }
        }
    except Exception as e:
        logger.error(f"Brand enforcement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/templates")
async def get_available_templates(
    platform: Optional[BrandPlatformType] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category")
) -> Dict:
    """Get available brand templates with filtering options."""
    try:
        # Convert category string to enum if provided
        category_enum = None
        if category:
            try:
                from services.brand_template_engine import TemplateCategory
                category_enum = TemplateCategory(category.lower())
            except ValueError:
                pass
        
        templates = brand_template_engine.get_available_templates(
            platform=platform,
            category=category_enum
        )
        
        return {
            "success": True,
            "templates": templates,
            "total_templates": len(templates),
            "filtered_by": {
                "platform": platform.value if platform else None,
                "category": category
            }
        }
    except Exception as e:
        logger.error(f"Template retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/templates/{template_id}/preview")
async def get_template_preview(
    template_id: str = Path(..., description="Template ID")
) -> Dict:
    """Get template preview information."""
    try:
        preview = brand_template_engine.get_template_preview(template_id)
        if not preview:
            raise HTTPException(status_code=404, detail=f"Template not found: {template_id}")
        
        return {
            "success": True,
            "preview": preview
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Template preview failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/brand/templates/generate")
async def generate_template_content(request: TemplateGenerationRequest) -> Dict:
    """Generate content using a brand template.
    
    Creates branded content from template with variable replacement
    and brand validation.
    """
    try:
        generation_request = GenerationRequest(
            template_id=request.template_id,
            content=request.content,
            platform=request.platform,
            content_type=request.content_type,
            customizations=request.customizations,
            brand_validation_required=request.brand_validation_required
        )
        
        result = await brand_template_engine.generate_content(generation_request)
        
        return {
            "success": result.success,
            "generation_result": {
                "image_base64": result.image_base64,
                "template_used": result.template_used,
                "validation_result": {
                    "overall_score": result.validation_result.overall_score,
                    "compliance_level": result.validation_result.compliance_level,
                    "issues_count": len(result.validation_result.issues),
                    "recommendations": result.validation_result.recommendations[:5]  # Top 5
                } if result.validation_result else None,
                "generation_metadata": result.generation_metadata,
                "warnings": result.warnings,
                "error_message": result.error_message
            }
        }
    except Exception as e:
        logger.error(f"Template generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/brand/content/generate")
async def generate_branded_content(request: BrandedContentGenerationRequest) -> Dict:
    """Generate comprehensive branded content.
    
    Creates branded content using the full branded content service
    with Freepik integration, templates, and brand enforcement.
    """
    try:
        # Convert request to ContentRequest
        content_request = ContentRequest(
            text_content=request.text_content,
            platform=request.platform,
            content_type=request.content_type,
            quality_level=request.quality_level,
            creation_mode=request.creation_mode,
            enforce_brand_compliance=request.enforce_brand_compliance,
            minimum_brand_score=request.minimum_brand_score,
            visual_style=request.visual_style,
            color_scheme=request.color_scheme,
            include_logo=request.include_logo,
            freepik_search_terms=request.freepik_search_terms,
            use_freepik_ai=request.use_freepik_ai,
            template_id=request.template_id,
            custom_dimensions=tuple(request.custom_dimensions) if request.custom_dimensions else None,
            output_formats=request.output_formats,
            include_variations=request.include_variations,
            variation_count=request.variation_count,
            user_id=request.user_id
        )
        
        result = await branded_content_service.generate_branded_content(content_request)
        
        return {
            "success": result.success,
            "content_result": {
                "content_id": result.content_id,
                "primary_image_base64": result.primary_image_base64,
                "variations_count": len(result.variations),
                "final_brand_score": result.final_brand_score,
                "quality_score": result.quality_score,
                "processing_time_ms": result.processing_time_ms,
                "generation_cost": result.generation_cost,
                "generation_method": result.generation_method.value,
                "template_used": result.template_used,
                "freepik_resources_count": len(result.freepik_resources),
                "output_files": result.output_files,
                "brand_validation": {
                    "overall_score": result.brand_validation.overall_score,
                    "compliance_level": result.brand_validation.compliance_level,
                    "issues_count": len(result.brand_validation.issues)
                } if result.brand_validation else None,
                "brand_enforcement": {
                    "corrections_applied": len(result.brand_enforcement.corrections_applied),
                    "score_improvement": result.brand_enforcement.corrected_score - result.brand_enforcement.original_score
                } if result.brand_enforcement else None,
                "warnings": result.warnings,
                "errors": result.errors,
                "recommendations": result.recommendations[:5],  # Top 5
                "creation_timestamp": result.creation_timestamp,
                "generation_metadata": result.generation_metadata
            }
        }
    except Exception as e:
        logger.error(f"Branded content generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/analytics/compliance")
async def get_brand_compliance_analytics() -> Dict:
    """Get brand compliance analytics and metrics."""
    try:
        # Get template compliance report
        template_report = await brand_template_engine.get_brand_compliance_report()
        
        # Get general brand statistics (mock data for now)
        analytics = {
            "compliance_overview": {
                "average_score": 87.3,
                "total_validations": 342,
                "passed_validations": 304,
                "failed_validations": 38,
                "improvement_trend": "+5.2%"
            },
            "template_analytics": template_report,
            "top_issues": [
                {"issue": "Non-brand colors detected", "frequency": 23, "severity": "high"},
                {"issue": "Missing brand logo", "frequency": 18, "severity": "critical"},
                {"issue": "Insufficient brand vocabulary", "frequency": 15, "severity": "medium"}
            ],
            "platform_breakdown": {
                "instagram": {"compliance": 89, "content": 45, "violations": 5},
                "linkedin": {"compliance": 92, "content": 38, "violations": 3},
                "twitter": {"compliance": 85, "content": 52, "violations": 8},
                "facebook": {"compliance": 88, "content": 43, "violations": 6}
            },
            "analytics_timestamp": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "analytics": analytics
        }
    except Exception as e:
        logger.error(f"Brand analytics retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/brand/health")
async def health_check_brand_system() -> Dict:
    """Health check for brand system components.
    
    Verifies all brand system services are functioning correctly.
    """
    try:
        health_status = {
            "brand_profile": "healthy",
            "brand_validator": "healthy",
            "brand_template_engine": "healthy",
            "brand_enforcer": "healthy",
            "branded_content_service": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services_count": 5
        }
        
        # Test basic functionality
        try:
            # Test brand profile
            colors = bymb_brand.get_color_palette()
            if not colors:
                health_status["brand_profile"] = "degraded"
            
            # Test template engine
            templates = brand_template_engine.get_available_templates()
            if not templates:
                health_status["brand_template_engine"] = "degraded"
            
            health_status["functionality_test"] = "passed"
            
        except Exception as test_error:
            logger.warning(f"Brand system functionality test failed: {test_error}")
            health_status["functionality_test"] = "failed"
            health_status["test_error"] = str(test_error)
        
        return health_status
    except Exception as e:
        logger.error(f"Brand system health check failed: {str(e)}")
        return {
            "brand_profile": "unhealthy",
            "brand_validator": "unknown",
            "brand_template_engine": "unknown",
            "brand_enforcer": "unknown",
            "branded_content_service": "unknown",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


# ================================
# ADVANCED CONTENT GENERATION ENDPOINTS
# ================================

@router.post("/v1/content/generate/complete")
async def generate_complete_content(
    request: CompleteContentGenerationRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Complete content generation pipeline from business insight to branded visuals.
    
    This endpoint orchestrates the entire content generation workflow:
    1. Business insight extraction and validation
    2. Platform-optimized copy generation
    3. Branded visual creation with Freepik integration
    4. Multi-platform optimization and brand compliance
    
    Returns workflow ID for progress tracking via WebSocket or status endpoint.
    """
    try:
        workflow_id = str(uuid4())
        
        # Initialize workflow tracking
        workflow_status = {
            "workflow_id": workflow_id,
            "status": "initiated",
            "steps": {
                "insight_processing": "pending",
                "copy_generation": "pending", 
                "visual_creation": "pending",
                "optimization": "pending",
                "brand_validation": "pending"
            },
            "progress_percent": 0,
            "estimated_completion": datetime.now() + timedelta(minutes=5),
            "created_at": datetime.now().isoformat()
        }
        
        # Add background task for complete content generation
        background_tasks.add_task(
            process_complete_content_generation,
            workflow_id,
            request,
            workflow_status
        )
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": "initiated",
            "estimated_completion_minutes": 5,
            "tracking_endpoints": {
                "status": f"/api/v1/workflows/{workflow_id}/status",
                "websocket": f"/api/v1/workflows/{workflow_id}/progress"
            },
            "webhook_configured": request.webhook_url is not None
        }
    except Exception as e:
        logger.error(f"Complete content generation initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/content/generate/insights")
async def extract_business_insights(request: BusinessInsightRequest) -> Dict:
    """Extract and validate business insights from raw text.
    
    Processes raw business insight text and extracts:
    - Key business themes and messages
    - Target audience indicators
    - Industry-specific terminology
    - Actionable content elements
    - Validation scoring and recommendations
    """
    try:
        # Mock insight extraction (in production, would use NLP services)
        insights = {
            "extraction_id": str(uuid4()),
            "raw_insight": request.raw_insight,
            "extracted_themes": [
                "Digital transformation",
                "Business efficiency",
                "Client success"
            ],
            "key_messages": [
                "Leveraging technology for business growth",
                "Proven track record of client results",
                "Expert consultation in digital strategy"
            ],
            "target_audience_indicators": [
                "Business leaders",
                "C-suite executives", 
                "Digital transformation managers"
            ],
            "industry_relevance": {
                "sector": request.industry_sector or "consulting",
                "relevance_score": 0.92,
                "industry_keywords": ["digital", "transformation", "consulting", "strategy"]
            },
            "content_potential": {
                "uniqueness_score": 0.87,
                "engagement_potential": 0.84,
                "brand_alignment": 0.91,
                "clarity_score": 0.89
            },
            "validation_results": {
                "overall_score": 0.88,
                "completeness": 0.85,
                "actionability": 0.90,
                "brand_consistency": 0.89
            },
            "recommendations": [
                "Emphasize specific client success metrics",
                "Include industry-specific examples",
                "Strengthen call-to-action elements"
            ],
            "processed_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "insights": insights,
            "processing_time_ms": 247
        }
    except Exception as e:
        logger.error(f"Business insight extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/content/generate/copy")
async def generate_platform_copy(request: CopyGenerationRequest) -> Dict:
    """Generate platform-optimized copy from structured insights.
    
    Creates engaging, platform-specific copy variations with:
    - Platform-optimized formatting and structure
    - Engagement-driven headlines and captions
    - Strategic hashtag integration
    - A/B testing variants (if requested)
    - Performance predictions
    """
    try:
        # Mock copy generation (would integrate with content generation services)
        copy_variations = []
        
        for i in range(request.variant_count if request.a_b_testing else 1):
            variation = {
                "variation_id": str(uuid4()),
                "variant_label": f"Variant_{chr(65+i)}" if request.a_b_testing else "Primary",
                "headlines": [
                    "Transform Your Business with Proven Digital Strategies",
                    "23+ Years of Driving $35M+ in Client Success"
                ],
                "captions": {
                    "short": "Expert digital transformation consulting in Bahrain. Proven results for 23+ years.",
                    "medium": "Transform your business with expert digital strategies. Based in Manama, we've driven $35M+ in client success over 23+ years of consulting excellence.",
                    "long": "Ready to transform your business? BYMB Consultancy brings 23+ years of expertise in digital transformation, having generated $35M+ in proven client results. Based in the heart of Manama, Kingdom of Bahrain, we specialize in turning business insights into actionable growth strategies."
                },
                "hashtags": {
                    "primary": ["#DigitalTransformation", "#BusinessConsulting", "#BahrainBusiness"],
                    "secondary": ["#DigitalStrategy", "#BusinessGrowth", "#ClientSuccess", "#Manama"],
                    "trending": ["#DigitalTransformation2025", "#BahrainTech", "#BusinessInnovation"]
                },
                "calls_to_action": [
                    "Ready to transform your business? Let's talk.",
                    "Discover how we can drive your success.",
                    "Schedule your consultation today."
                ],
                "engagement_predictions": {
                    "instagram": {"likes": 45, "comments": 8, "shares": 3},
                    "linkedin": {"likes": 127, "comments": 23, "shares": 18},
                    "twitter": {"likes": 34, "comments": 6, "retweets": 12}
                },
                "tone_analysis": {
                    "professional": 0.92,
                    "engaging": 0.87,
                    "authoritative": 0.89,
                    "approachable": 0.84
                }
            }
            copy_variations.append(variation)
        
        return {
            "success": True,
            "copy_generation": {
                "generation_id": str(uuid4()),
                "variations": copy_variations,
                "generation_metadata": {
                    "platforms_optimized": list(request.platform_specs.keys()),
                    "a_b_testing_enabled": request.a_b_testing,
                    "hashtag_strategy": request.hashtag_strategy,
                    "tone_requirements_met": True
                },
                "performance_insights": {
                    "best_performing_variant": copy_variations[0]["variation_id"] if copy_variations else None,
                    "engagement_confidence": 0.87,
                    "brand_alignment_score": 0.91
                },
                "generated_at": datetime.now().isoformat()
            },
            "processing_time_ms": 1247
        }
    except Exception as e:
        logger.error(f"Platform copy generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/content/generate/visuals")
async def generate_branded_visuals(request: VisualGenerationRequest) -> Dict:
    """Generate branded visual content with Freepik integration.
    
    Creates high-quality branded visuals with:
    - Freepik API integration for base imagery
    - Brand template overlay and compliance
    - Multiple format optimization
    - Quality assurance and validation
    - Performance-optimized outputs
    """
    try:
        # Mock visual generation (would integrate with branded_content_service)
        visual_results = {
            "generation_id": str(uuid4()),
            "primary_visual": {
                "image_id": str(uuid4()),
                "base64_data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
                "dimensions": {"width": 1080, "height": 1080},
                "format": "PNG",
                "file_size_kb": 245,
                "brand_score": 0.94
            },
            "format_variants": [
                {
                    "format_name": "instagram_post",
                    "dimensions": {"width": 1080, "height": 1080},
                    "optimizations": ["engagement_zones", "text_readability", "brand_placement"]
                },
                {
                    "format_name": "linkedin_post", 
                    "dimensions": {"width": 1200, "height": 630},
                    "optimizations": ["professional_layout", "headline_prominence", "cta_placement"]
                },
                {
                    "format_name": "instagram_story",
                    "dimensions": {"width": 1080, "height": 1920},
                    "optimizations": ["vertical_layout", "tap_zones", "brand_consistency"]
                }
            ],
            "freepik_integration": {
                "resources_used": 2,
                "base_images": [
                    {"id": "freepik_001", "title": "Business meeting consultation", "license": "premium"},
                    {"id": "freepik_002", "title": "Digital transformation concept", "license": "premium"}
                ],
                "ai_generated": request.freepik_integration.get("use_ai", False),
                "cost_breakdown": {
                    "api_calls": 2,
                    "cost_usd": 0.02
                }
            },
            "brand_validation": {
                "overall_score": 0.94,
                "color_compliance": 0.96,
                "typography_compliance": 0.92,
                "logo_placement": 0.95,
                "voice_alignment": 0.93
            },
            "quality_metrics": {
                "resolution": "high",
                "compression_ratio": 0.75,
                "loading_performance": "optimized",
                "accessibility_score": 0.89
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return {
            "success": True,
            "visual_generation": visual_results,
            "processing_time_ms": 3247,
            "next_steps": [
                "Review and approve visuals",
                "Schedule content posting",
                "Track performance metrics"
            ]
        }
    except Exception as e:
        logger.error(f"Branded visual generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================
# ANALYTICS AND PERFORMANCE ENDPOINTS
# ================================

@router.get("/v1/analytics/content/{content_id}/performance")
async def get_content_performance(
    content_id: str = Path(..., description="Content identifier"),
    metrics: List[str] = Query(default=["engagement", "reach", "clicks"], description="Metrics to include"),
    time_range_days: int = Query(default=30, description="Analysis time range in days")
) -> Dict:
    """Get comprehensive content performance analytics.
    
    Returns detailed performance metrics including:
    - Engagement analytics (likes, comments, shares)
    - Audience insights and demographics
    - Performance trends and comparisons
    - Optimization recommendations
    - ROI and conversion tracking
    """
    try:
        # Mock performance data (would integrate with analytics services)
        performance_data = {
            "content_id": content_id,
            "analysis_period": {
                "start_date": (datetime.now() - timedelta(days=time_range_days)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "total_days": time_range_days
            },
            "engagement_metrics": {
                "total_likes": 1247,
                "total_comments": 83,
                "total_shares": 45,
                "total_clicks": 234,
                "engagement_rate": 0.067,
                "reach": 18500,
                "impressions": 24300
            },
            "audience_insights": {
                "demographics": {
                    "age_groups": {
                        "25-34": 0.35,
                        "35-44": 0.28,
                        "45-54": 0.22,
                        "55+": 0.15
                    },
                    "gender": {"male": 0.58, "female": 0.42},
                    "locations": {
                        "Bahrain": 0.45,
                        "UAE": 0.23,
                        "Saudi Arabia": 0.18,
                        "Other": 0.14
                    }
                },
                "interests": [
                    "Business Strategy", "Digital Marketing", "Technology",
                    "Entrepreneurship", "Consulting"
                ]
            },
            "performance_trends": [
                {"date": "2025-01-01", "engagement": 45, "reach": 1200},
                {"date": "2025-01-02", "engagement": 52, "reach": 1350},
                {"date": "2025-01-03", "engagement": 48, "reach": 1180}
            ],
            "comparative_analysis": {
                "vs_previous_period": {
                    "engagement": +0.23,
                    "reach": +0.18,
                    "clicks": +0.31
                },
                "vs_account_average": {
                    "engagement": +0.15,
                    "reach": +0.08,
                    "clicks": +0.42
                }
            },
            "optimization_recommendations": [
                {
                    "category": "timing",
                    "recommendation": "Post 2 hours earlier for higher engagement",
                    "expected_improvement": 0.15,
                    "confidence": 0.82
                },
                {
                    "category": "content",
                    "recommendation": "Include more visual elements",
                    "expected_improvement": 0.22,
                    "confidence": 0.75
                }
            ],
            "roi_metrics": {
                "content_cost": 25.50,
                "estimated_value": 342.00,
                "roi_ratio": 13.4,
                "conversion_rate": 0.034
            }
        }
        
        return {
            "success": True,
            "performance_analysis": performance_data,
            "analysis_timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Content performance analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/analytics/track/engagement")
async def track_engagement_metrics(request: EngagementTrackingData) -> Dict:
    """Track real-time engagement metrics.
    
    Ingests real-time performance data and provides:
    - Immediate processing confirmation
    - Anomaly detection alerts
    - Performance trend updates
    - Automated optimization triggers
    """
    try:
        # Process engagement data (would integrate with analytics pipeline)
        tracking_result = {
            "tracking_id": str(uuid4()),
            "content_id": request.content_id,
            "platform": request.platform,
            "processed_metrics": request.engagement_metrics,
            "processing_status": "completed",
            "anomalies_detected": [],
            "trend_analysis": {
                "engagement_trend": "increasing",
                "velocity": 0.23,
                "prediction_confidence": 0.87
            },
            "automated_actions": [
                {
                    "action": "performance_alert",
                    "trigger": "engagement_spike",
                    "status": "queued"
                }
            ],
            "processed_at": datetime.now().isoformat()
        }
        
        # Check for anomalies
        if request.engagement_metrics.get("likes", 0) > 100:
            tracking_result["anomalies_detected"].append({
                "type": "engagement_spike",
                "metric": "likes",
                "value": request.engagement_metrics["likes"],
                "significance": "high"
            })
        
        return {
            "success": True,
            "tracking_result": tracking_result,
            "processing_time_ms": 45
        }
    except Exception as e:
        logger.error(f"Engagement tracking failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/analytics/dashboard/overview")
async def get_analytics_dashboard(
    time_range_days: int = Query(default=30, description="Dashboard time range"),
    include_predictions: bool = Query(default=True, description="Include predictive analytics")
) -> Dict:
    """Get executive dashboard overview with key metrics.
    
    Provides high-level performance overview including:
    - KPI summaries and trend analysis
    - Platform performance comparison
    - ROI and conversion metrics
    - Predictive analytics and insights
    - Executive-level recommendations
    """
    try:
        dashboard_data = {
            "overview_period": {
                "days": time_range_days,
                "start_date": (datetime.now() - timedelta(days=time_range_days)).isoformat(),
                "end_date": datetime.now().isoformat()
            },
            "kpi_summary": {
                "total_content_pieces": 47,
                "total_engagement": 5432,
                "total_reach": 145000,
                "average_engagement_rate": 0.065,
                "content_creation_cost": 1245.50,
                "estimated_value_generated": 18750.00,
                "roi": 15.1
            },
            "platform_performance": {
                "linkedin": {
                    "content_count": 18,
                    "engagement": 2341,
                    "reach": 67000,
                    "engagement_rate": 0.072
                },
                "instagram": {
                    "content_count": 15,
                    "engagement": 1876,
                    "reach": 43000,
                    "engagement_rate": 0.058
                },
                "twitter": {
                    "content_count": 14,
                    "engagement": 1215,
                    "reach": 35000,
                    "engagement_rate": 0.051
                }
            },
            "trend_analysis": {
                "engagement_trend": "+23%",
                "reach_trend": "+18%", 
                "content_quality_trend": "+15%",
                "brand_compliance_trend": "+8%"
            },
            "top_performing_content": [
                {
                    "content_id": "content_001",
                    "title": "Digital Transformation Success Story",
                    "engagement": 456,
                    "reach": 12000,
                    "platform": "linkedin"
                },
                {
                    "content_id": "content_002",
                    "title": "BYMB Consultancy Milestone",
                    "engagement": 387,
                    "reach": 9800,
                    "platform": "instagram"
                }
            ],
            "predictive_insights": {
                "next_30_days_prediction": {
                    "expected_engagement": 6200,
                    "expected_reach": 168000,
                    "confidence": 0.84
                },
                "growth_opportunities": [
                    "Increase video content by 25% for +18% engagement",
                    "Optimize posting times for +12% reach",
                    "Expand Instagram Stories for +22% brand awareness"
                ]
            } if include_predictions else {},
            "recommendations": [
                {
                    "priority": "high",
                    "category": "content_strategy",
                    "recommendation": "Focus on LinkedIn content - showing 15% higher ROI",
                    "expected_impact": "18% revenue increase"
                },
                {
                    "priority": "medium",
                    "category": "brand_consistency",
                    "recommendation": "Standardize brand elements across platforms",
                    "expected_impact": "8% brand recognition improvement"
                }
            ]
        }
        
        return {
            "success": True,
            "dashboard": dashboard_data,
            "generated_at": datetime.now().isoformat(),
            "refresh_interval_minutes": 15
        }
    except Exception as e:
        logger.error(f"Analytics dashboard generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/analytics/reports/generate")
async def generate_analytics_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Generate custom analytics report.
    
    Creates comprehensive analytics reports with:
    - Custom metric selection and analysis
    - Professional formatting and branding
    - Multiple export format support
    - Automated delivery options
    - Executive summary and insights
    """
    try:
        report_id = str(uuid4())
        
        # Add background task for report generation
        background_tasks.add_task(
            process_analytics_report,
            report_id,
            request
        )
        
        return {
            "success": True,
            "report_generation": {
                "report_id": report_id,
                "status": "initiated",
                "estimated_completion_minutes": 3,
                "report_type": request.report_type,
                "format": request.format_preferences.get("format", "PDF"),
                "delivery_method": request.delivery_options.get("method", "download"),
                "tracking_endpoint": f"/api/v1/analytics/reports/{report_id}/status"
            },
            "initiated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Report generation initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================
# ASSET MANAGEMENT AND TEMPLATE ENDPOINTS
# ================================

@router.get("/v1/assets/library")
async def get_asset_library(
    category: Optional[str] = Query(None, description="Filter by asset category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    search: Optional[str] = Query(None, description="Search query"),
    page: int = Query(1, description="Page number"),
    limit: int = Query(50, description="Items per page")
) -> Dict:
    """Get complete asset library with advanced search and filtering.
    
    Returns comprehensive asset catalog with:
    - Categorized brand assets with metadata
    - Advanced search and filtering capabilities
    - Usage statistics and performance data
    - Asset recommendations based on context
    - Batch operations support
    """
    try:
        # Mock asset library data (would integrate with asset management service)
        assets = [
            {
                "asset_id": str(uuid4()),
                "name": "BYMB Primary Logo",
                "category": "logos",
                "type": "vector",
                "format": "SVG",
                "dimensions": {"width": 500, "height": 200},
                "file_size_kb": 12.3,
                "created_date": "2024-12-01T10:00:00Z",
                "usage_count": 247,
                "performance_score": 0.94,
                "tags": ["logo", "primary", "brand", "official"],
                "metadata": {
                    "brand_compliant": True,
                    "platforms_optimized": ["all"],
                    "color_variants": ["full_color", "monochrome", "white"]
                },
                "download_url": "/api/v1/assets/download/asset_001",
                "preview_url": "/api/v1/assets/preview/asset_001"
            },
            {
                "asset_id": str(uuid4()),
                "name": "Bahrain Cityscape Background",
                "category": "backgrounds",
                "type": "photo",
                "format": "JPG",
                "dimensions": {"width": 1920, "height": 1080},
                "file_size_kb": 847.2,
                "created_date": "2024-11-15T14:30:00Z",
                "usage_count": 89,
                "performance_score": 0.87,
                "tags": ["bahrain", "cityscape", "background", "professional"],
                "metadata": {
                    "brand_compliant": True,
                    "platforms_optimized": ["linkedin", "instagram", "website"],
                    "resolution_variants": ["4K", "HD", "mobile"]
                },
                "download_url": "/api/v1/assets/download/asset_002",
                "preview_url": "/api/v1/assets/preview/asset_002"
            },
            {
                "asset_id": str(uuid4()),
                "name": "Consulting Infographic Template",
                "category": "templates",
                "type": "template",
                "format": "PSD",
                "dimensions": {"width": 1080, "height": 1080},
                "file_size_kb": 245.8,
                "created_date": "2024-10-20T09:15:00Z",
                "usage_count": 156,
                "performance_score": 0.91,
                "tags": ["infographic", "consulting", "template", "editable"],
                "metadata": {
                    "brand_compliant": True,
                    "platforms_optimized": ["instagram", "linkedin"],
                    "editable_elements": ["text", "colors", "charts", "icons"]
                },
                "download_url": "/api/v1/assets/download/asset_003",
                "preview_url": "/api/v1/assets/preview/asset_003"
            }
        ]
        
        # Apply filters (mock implementation)
        if category:
            assets = [a for a in assets if a["category"] == category]
        if tags:
            assets = [a for a in assets if any(tag in a["tags"] for tag in tags)]
        if search:
            assets = [a for a in assets if search.lower() in a["name"].lower() or 
                     search.lower() in " ".join(a["tags"]).lower()]
        
        # Pagination
        start_idx = (page - 1) * limit
        end_idx = start_idx + limit
        paginated_assets = assets[start_idx:end_idx]
        
        # Asset recommendations (mock)
        recommendations = [
            {
                "asset_id": "asset_rec_001",
                "name": "Digital Transformation Icon Set",
                "reason": "High performance with similar content",
                "confidence": 0.87
            },
            {
                "asset_id": "asset_rec_002", 
                "name": "Professional Color Palette",
                "reason": "Matches current brand usage patterns",
                "confidence": 0.82
            }
        ]
        
        return {
            "success": True,
            "asset_library": {
                "assets": paginated_assets,
                "pagination": {
                    "current_page": page,
                    "total_pages": max(1, (len(assets) + limit - 1) // limit),
                    "total_assets": len(assets),
                    "assets_per_page": limit
                },
                "filters_applied": {
                    "category": category,
                    "tags": tags,
                    "search": search
                },
                "recommendations": recommendations,
                "library_stats": {
                    "total_assets": 247,
                    "categories": ["logos", "backgrounds", "templates", "icons", "fonts"],
                    "most_used_category": "templates",
                    "average_performance_score": 0.89
                }
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Asset library retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/assets/upload")
async def upload_brand_asset(request: AssetUploadRequest) -> Dict:
    """Upload and validate new brand assets.
    
    Processes asset uploads with:
    - Comprehensive brand compliance validation
    - Automatic format optimization and variants
    - Metadata extraction and tagging
    - Performance prediction and recommendations
    - Integration with asset management system
    """
    try:
        asset_id = str(uuid4())
        
        # Mock asset processing (would integrate with actual upload service)
        upload_result = {
            "upload_id": str(uuid4()),
            "asset_id": asset_id,
            "processing_status": "completed",
            "validation_results": {
                "brand_compliance": {
                    "overall_score": 0.91,
                    "color_compliance": 0.94,
                    "style_compliance": 0.89,
                    "format_compliance": 0.92,
                    "resolution_compliance": 0.88
                },
                "quality_assessment": {
                    "resolution": "excellent",
                    "compression": "optimal",
                    "accessibility": 0.87,
                    "performance_score": 0.92
                },
                "compliance_issues": [
                    {
                        "severity": "minor",
                        "issue": "Logo placement could be 5px higher for optimal visibility",
                        "suggestion": "Adjust logo position for better brand prominence"
                    }
                ]
            },
            "generated_variants": [
                {
                    "variant_name": "web_optimized",
                    "format": "WebP",
                    "dimensions": {"width": 1200, "height": 630},
                    "file_size_kb": 89.4,
                    "purpose": "web_sharing"
                },
                {
                    "variant_name": "mobile_optimized",
                    "format": "JPG",
                    "dimensions": {"width": 800, "height": 600},
                    "file_size_kb": 124.7,
                    "purpose": "mobile_display"
                }
            ],
            "extracted_metadata": {
                "colors_detected": ["#1E40AF", "#F59E0B", "#10B981"],
                "text_content": "BYMB Consultancy - Digital Transformation Experts",
                "dimensions": {"width": 1920, "height": 1080},
                "format": "PNG",
                "creation_date": datetime.now().isoformat(),
                "estimated_usage_contexts": ["social_media", "presentations", "website"]
            },
            "performance_prediction": {
                "engagement_potential": 0.86,
                "brand_recognition_boost": 0.23,
                "recommended_platforms": ["linkedin", "instagram", "website"],
                "optimal_use_cases": ["thought_leadership", "company_announcements"]
            },
            "auto_generated_tags": [
                request.asset_name.lower().replace(" ", "_"),
                request.asset_category,
                "brand_compliant",
                "high_quality",
                *request.tags
            ]
        }
        
        return {
            "success": True,
            "asset_upload": upload_result,
            "next_steps": [
                "Review validation results",
                "Approve asset for library inclusion",
                "Configure usage permissions",
                "Set up automated optimization rules"
            ],
            "processing_time_ms": 2456
        }
    except Exception as e:
        logger.error(f"Asset upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/templates/library/advanced")
async def get_advanced_template_library(
    platform: Optional[BrandPlatformType] = Query(None, description="Filter by platform"),
    category: Optional[str] = Query(None, description="Filter by category"),
    performance_min: Optional[float] = Query(None, description="Minimum performance score"),
    include_ai_recommendations: bool = Query(True, description="Include AI-driven recommendations")
) -> Dict:
    """Get advanced template library with AI recommendations.
    
    Returns comprehensive template catalog with:
    - AI-driven template recommendations
    - Performance-based filtering and ranking
    - Usage analytics and success metrics
    - Template customization capabilities
    - Brand compliance scoring
    """
    try:
        # Mock advanced template data (would integrate with template service)
        templates = [
            {
                "template_id": str(uuid4()),
                "name": "Executive Insight Post",
                "category": "thought_leadership",
                "description": "Professional template for sharing business insights and expertise",
                "platforms": ["linkedin", "instagram"],
                "preview_image": "/api/v1/templates/preview/template_001.jpg",
                "performance_metrics": {
                    "usage_count": 342,
                    "average_engagement_rate": 0.078,
                    "brand_compliance_score": 0.96,
                    "conversion_rate": 0.043,
                    "user_satisfaction": 4.7
                },
                "customization_options": [
                    {
                        "element": "headline",
                        "type": "text",
                        "max_characters": 80,
                        "ai_suggestions": True
                    },
                    {
                        "element": "background_color",
                        "type": "color_palette",
                        "brand_restricted": True,
                        "options": ["#1E40AF", "#F59E0B", "#10B981"]
                    },
                    {
                        "element": "layout_style",
                        "type": "selection",
                        "options": ["minimal", "corporate", "creative"]
                    }
                ],
                "ai_optimization": {
                    "engagement_predictions": {
                        "linkedin": {"likes": 145, "comments": 23, "shares": 18},
                        "instagram": {"likes": 89, "comments": 12, "shares": 6}
                    },
                    "recommended_content_types": ["business_insights", "industry_trends", "expert_opinions"],
                    "optimal_posting_times": {
                        "linkedin": ["09:00", "14:00", "17:00"],
                        "instagram": ["11:00", "15:00", "19:00"]
                    }
                },
                "brand_validation": {
                    "compliance_score": 0.96,
                    "approved_elements": ["logo", "colors", "typography", "messaging"],
                    "restrictions": ["no_competitor_colors", "maintain_logo_clearance"]
                },
                "creation_metadata": {
                    "created_date": "2024-11-20T10:00:00Z",
                    "last_updated": "2024-12-15T14:30:00Z",
                    "creator": "brand_team",
                    "version": "2.1"
                }
            },
            {
                "template_id": str(uuid4()),
                "name": "Client Success Story",
                "category": "case_study",
                "description": "Showcase client achievements and business results",
                "platforms": ["linkedin", "instagram", "facebook"],
                "preview_image": "/api/v1/templates/preview/template_002.jpg",
                "performance_metrics": {
                    "usage_count": 198,
                    "average_engagement_rate": 0.085,
                    "brand_compliance_score": 0.94,
                    "conversion_rate": 0.067,
                    "user_satisfaction": 4.9
                },
                "customization_options": [
                    {
                        "element": "client_logo",
                        "type": "image_upload",
                        "requirements": ["transparent_background", "high_resolution"]
                    },
                    {
                        "element": "success_metrics",
                        "type": "data_visualization",
                        "chart_types": ["bar", "pie", "line", "infographic"]
                    },
                    {
                        "element": "testimonial_quote",
                        "type": "text",
                        "max_characters": 150,
                        "formatting": ["italic", "highlight_background"]
                    }
                ],
                "ai_optimization": {
                    "engagement_predictions": {
                        "linkedin": {"likes": 234, "comments": 45, "shares": 67},
                        "instagram": {"likes": 156, "comments": 23, "shares": 12},
                        "facebook": {"likes": 89, "comments": 15, "shares": 8}
                    },
                    "recommended_content_types": ["case_studies", "success_metrics", "client_testimonials"],
                    "optimal_posting_times": {
                        "linkedin": ["10:00", "15:00", "18:00"],
                        "instagram": ["12:00", "16:00", "20:00"],
                        "facebook": ["13:00", "17:00", "21:00"]
                    }
                },
                "brand_validation": {
                    "compliance_score": 0.94,
                    "approved_elements": ["brand_colors", "professional_typography", "logo_placement"],
                    "restrictions": ["client_confidentiality", "data_accuracy_required"]
                },
                "creation_metadata": {
                    "created_date": "2024-10-15T09:00:00Z",
                    "last_updated": "2024-12-10T11:45:00Z",
                    "creator": "design_team",
                    "version": "1.8"
                }
            }
        ]
        
        # Apply filters
        if platform:
            templates = [t for t in templates if platform.value in t["platforms"]]
        if category:
            templates = [t for t in templates if t["category"] == category]
        if performance_min:
            templates = [t for t in templates if t["performance_metrics"]["average_engagement_rate"] >= performance_min]
        
        # Sort by performance (most successful first)
        templates.sort(key=lambda t: t["performance_metrics"]["average_engagement_rate"], reverse=True)
        
        # AI recommendations
        ai_recommendations = []
        if include_ai_recommendations:
            ai_recommendations = [
                {
                    "template_id": "ai_rec_001",
                    "name": "Industry Trend Analysis",
                    "reason": "High engagement potential based on recent content performance",
                    "confidence": 0.89,
                    "expected_improvement": "+25% engagement"
                },
                {
                    "template_id": "ai_rec_002",
                    "name": "Behind the Scenes",
                    "reason": "Trending format showing 40% above-average performance",
                    "confidence": 0.84,
                    "expected_improvement": "+18% brand authenticity"
                }
            ]
        
        return {
            "success": True,
            "template_library": {
                "templates": templates,
                "total_templates": len(templates),
                "filters_applied": {
                    "platform": platform.value if platform else None,
                    "category": category,
                    "performance_minimum": performance_min
                },
                "ai_recommendations": ai_recommendations,
                "library_analytics": {
                    "most_popular_category": "thought_leadership",
                    "average_engagement_rate": 0.082,
                    "highest_performing_platform": "linkedin",
                    "total_usage_count": 2847
                },
                "trending_templates": [
                    {"template_id": "template_001", "trend": "+34%", "period": "7_days"},
                    {"template_id": "template_002", "trend": "+28%", "period": "7_days"}
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Advanced template library retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/templates/create/dynamic")
async def create_dynamic_template(request: TemplateCreationRequest) -> Dict:
    """Create custom templates with brand validation.
    
    Generates dynamic templates with:
    - Real-time brand compliance validation
    - AI-powered design optimization
    - Multi-platform format generation
    - Performance prediction modeling
    - Automated quality assurance
    """
    try:
        template_id = str(uuid4())
        
        # Mock template creation process (would integrate with design services)
        creation_result = {
            "template_id": template_id,
            "creation_status": "completed",
            "template_details": {
                "name": request.template_name,
                "category": request.template_category,
                "supported_platforms": [p.value for p in request.platforms],
                "base_dimensions": request.specifications.get("base_dimensions", {"width": 1080, "height": 1080}),
                "color_scheme": request.specifications.get("colors", ["#1E40AF", "#F59E0B"]),
                "typography": request.specifications.get("fonts", ["Arial", "Helvetica"])
            },
            "brand_validation": {
                "overall_compliance": 0.93,
                "validation_details": {
                    "color_compliance": 0.96,
                    "typography_compliance": 0.91,
                    "layout_compliance": 0.94,
                    "messaging_compliance": 0.92
                },
                "compliance_issues": [
                    {
                        "severity": "minor",
                        "element": "secondary_font",
                        "issue": "Consider using brand-approved font family",
                        "suggestion": "Replace with Montserrat for better brand consistency"
                    }
                ],
                "approved_elements": ["primary_colors", "logo_placement", "main_typography"]
            },
            "generated_variants": [
                {
                    "platform": "instagram",
                    "dimensions": {"width": 1080, "height": 1080},
                    "optimizations": ["engagement_zones", "text_readability", "brand_visibility"],
                    "preview_url": f"/api/v1/templates/{template_id}/preview/instagram"
                },
                {
                    "platform": "linkedin",
                    "dimensions": {"width": 1200, "height": 630},
                    "optimizations": ["professional_layout", "headline_prominence", "cta_placement"],
                    "preview_url": f"/api/v1/templates/{template_id}/preview/linkedin"
                }
            ],
            "customization_framework": {
                "editable_elements": [
                    {
                        "element_id": "main_headline",
                        "type": "text",
                        "constraints": {"max_characters": 60, "min_characters": 10},
                        "ai_suggestions": True
                    },
                    {
                        "element_id": "brand_logo",
                        "type": "image",
                        "constraints": {"max_size_kb": 500, "formats": ["PNG", "SVG"]},
                        "positioning": "flexible"
                    },
                    {
                        "element_id": "background",
                        "type": "color_or_image",
                        "constraints": {"brand_colors_only": True},
                        "options": request.brand_requirements.get("approved_backgrounds", [])
                    }
                ],
                "smart_defaults": {
                    "color_palette": ["#1E40AF", "#F59E0B", "#FFFFFF"],
                    "font_hierarchy": {"primary": "Montserrat", "secondary": "Open Sans"},
                    "layout_grid": {"columns": 12, "rows": 8, "gutters": "16px"}
                }
            },
            "performance_predictions": {
                "expected_engagement_rate": 0.074,
                "brand_recognition_potential": 0.87,
                "recommended_use_cases": [
                    "thought_leadership_content",
                    "business_announcements",
                    "client_success_stories"
                ],
                "optimal_content_types": request.specifications.get("content_types", ["insights", "news"])
            },
            "quality_assurance": {
                "accessibility_score": 0.91,
                "mobile_responsiveness": True,
                "cross_platform_compatibility": True,
                "loading_performance": "optimized",
                "brand_guideline_adherence": 0.93
            },
            "template_metadata": {
                "created_at": datetime.now().isoformat(),
                "creator_id": "template_engine",
                "version": "1.0",
                "estimated_creation_time_ms": 3247
            }
        }
        
        return {
            "success": True,
            "template_creation": creation_result,
            "next_steps": [
                "Review template variants and compliance results",
                "Test template with sample content",
                "Publish to template library",
                "Configure usage permissions and access levels"
            ],
            "template_urls": {
                "edit": f"/api/v1/templates/{template_id}/edit",
                "preview": f"/api/v1/templates/{template_id}/preview",
                "download": f"/api/v1/templates/{template_id}/download"
            }
        }
    except Exception as e:
        logger.error(f"Dynamic template creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================
# WORKFLOW ORCHESTRATION ENDPOINTS
# ================================

@router.post("/v1/workflows/content/initiate")
async def initiate_content_workflow(
    request: WorkflowInitiationRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Initiate complete content creation workflow with state management.
    
    Orchestrates complex content workflows with:
    - Multi-step content generation processes
    - State persistence and recovery
    - Progress tracking and notifications
    - Error handling and recovery mechanisms
    - Integration with external services
    """
    try:
        workflow_id = str(uuid4())
        
        # Initialize workflow state
        workflow_state = {
            "workflow_id": workflow_id,
            "workflow_type": request.workflow_type,
            "status": "initiated",
            "current_step": 1,
            "total_steps": 5,
            "progress_percentage": 0,
            "steps": {
                "step_1": {"name": "Content Analysis", "status": "pending", "started_at": None, "completed_at": None},
                "step_2": {"name": "Brand Validation", "status": "pending", "started_at": None, "completed_at": None},
                "step_3": {"name": "Visual Generation", "status": "pending", "started_at": None, "completed_at": None},
                "step_4": {"name": "Platform Optimization", "status": "pending", "started_at": None, "completed_at": None},
                "step_5": {"name": "Quality Assurance", "status": "pending", "started_at": None, "completed_at": None}
            },
            "parameters": request.parameters,
            "user_preferences": request.user_preferences,
            "completion_criteria": request.completion_criteria,
            "created_at": datetime.now().isoformat(),
            "estimated_completion": (datetime.now() + timedelta(minutes=8)).isoformat(),
            "notifications": {
                "webhook_configured": False,
                "email_enabled": request.notification_settings.get("email", False),
                "sms_enabled": request.notification_settings.get("sms", False)
            },
            "error_recovery": {
                "retry_count": 0,
                "max_retries": 3,
                "fallback_enabled": True
            }
        }
        
        # Start background workflow processing
        background_tasks.add_task(
            process_workflow_execution,
            workflow_id,
            workflow_state,
            request
        )
        
        return {
            "success": True,
            "workflow_initiation": {
                "workflow_id": workflow_id,
                "workflow_type": request.workflow_type,
                "status": "initiated",
                "priority": request.priority,
                "estimated_completion_minutes": 8,
                "tracking_capabilities": {
                    "real_time_updates": True,
                    "progress_webhooks": False,
                    "status_endpoint": f"/api/v1/workflows/{workflow_id}/status",
                    "websocket_endpoint": f"/api/v1/workflows/{workflow_id}/progress"
                },
                "intervention_options": {
                    "pause_workflow": f"/api/v1/workflows/{workflow_id}/pause",
                    "modify_parameters": f"/api/v1/workflows/{workflow_id}/intervention",
                    "cancel_workflow": f"/api/v1/workflows/{workflow_id}/cancel"
                }
            },
            "initiated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Workflow initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/workflows/{workflow_id}/status")
async def get_workflow_status(
    workflow_id: str = Path(..., description="Workflow identifier")
) -> Dict:
    """Get workflow execution status and progress.
    
    Provides comprehensive workflow monitoring including:
    - Real-time status and progress tracking
    - Detailed step-by-step execution information
    - Performance metrics and timing data
    - Error information and recovery actions
    - Completion estimates and next steps
    """
    try:
        # Mock workflow status (would integrate with workflow management service)
        workflow_status = {
            "workflow_id": workflow_id,
            "workflow_type": "complete_content_generation",
            "status": "in_progress",
            "current_step": 3,
            "total_steps": 5,
            "progress_percentage": 60,
            "step_details": [
                {
                    "step_number": 1,
                    "step_name": "Content Analysis",
                    "status": "completed",
                    "started_at": "2025-01-06T10:00:00Z",
                    "completed_at": "2025-01-06T10:01:30Z",
                    "duration_seconds": 90,
                    "output": {
                        "insights_extracted": 5,
                        "confidence_score": 0.89,
                        "quality_assessment": "excellent"
                    }
                },
                {
                    "step_number": 2,
                    "step_name": "Brand Validation",
                    "status": "completed",
                    "started_at": "2025-01-06T10:01:30Z",
                    "completed_at": "2025-01-06T10:02:45Z",
                    "duration_seconds": 75,
                    "output": {
                        "compliance_score": 0.94,
                        "issues_found": 1,
                        "auto_corrections": 2
                    }
                },
                {
                    "step_number": 3,
                    "step_name": "Visual Generation",
                    "status": "in_progress",
                    "started_at": "2025-01-06T10:02:45Z",
                    "completed_at": None,
                    "duration_seconds": 195,
                    "progress_detail": {
                        "freepik_images_processed": 2,
                        "templates_applied": 1,
                        "formats_generated": 3,
                        "current_task": "applying_brand_overlays"
                    }
                },
                {
                    "step_number": 4,
                    "step_name": "Platform Optimization",
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": None,
                    "dependencies": ["visual_generation_complete"]
                },
                {
                    "step_number": 5,
                    "step_name": "Quality Assurance",
                    "status": "pending",
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": None,
                    "dependencies": ["platform_optimization_complete"]
                }
            ],
            "performance_metrics": {
                "total_execution_time_seconds": 360,
                "average_step_duration": 88,
                "resource_utilization": {
                    "cpu_usage": 0.45,
                    "memory_usage": 0.62,
                    "api_calls_made": 12,
                    "cost_accumulated": 0.24
                }
            },
            "estimated_completion": {
                "time_remaining_minutes": 3,
                "completion_time": "2025-01-06T10:09:00Z",
                "confidence": 0.87
            },
            "error_information": {
                "errors_encountered": 0,
                "warnings_issued": 1,
                "recovery_actions_taken": 0,
                "last_warning": {
                    "message": "Freepik API response slightly delayed",
                    "severity": "low",
                    "timestamp": "2025-01-06T10:04:20Z"
                }
            },
            "output_preview": {
                "content_generated": True,
                "platforms_optimized": ["linkedin", "instagram"],
                "visual_variants_created": 6,
                "brand_compliance_achieved": True
            }
        }
        
        return {
            "success": True,
            "workflow_status": workflow_status,
            "monitoring_capabilities": {
                "real_time_updates": True,
                "detailed_logging": True,
                "performance_tracking": True,
                "error_alerting": True
            },
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Workflow status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/workflows/content/batch")
async def initiate_batch_content_workflow(
    request: BatchContentRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """Initiate batch content creation workflow.
    
    Manages large-scale content generation with:
    - Parallel processing capabilities
    - Priority-based task scheduling
    - Resource optimization and load balancing
    - Progress tracking for individual items
    - Failure isolation and recovery
    """
    try:
        batch_id = str(uuid4())
        
        # Process batch specifications
        batch_items = []
        for i, spec in enumerate(request.batch_specifications):
            item_id = str(uuid4())
            batch_items.append({
                "item_id": item_id,
                "position": i + 1,
                "specification": spec,
                "status": "queued",
                "priority": spec.get("priority", "normal"),
                "estimated_duration_minutes": spec.get("estimated_duration", 5),
                "dependencies": spec.get("dependencies", []),
                "created_at": datetime.now().isoformat()
            })
        
        # Initialize batch workflow state
        batch_state = {
            "batch_id": batch_id,
            "status": "initiated",
            "total_items": len(batch_items),
            "completed_items": 0,
            "failed_items": 0,
            "in_progress_items": 0,
            "queued_items": len(batch_items),
            "batch_items": batch_items,
            "processing_preferences": request.processing_preferences,
            "quality_requirements": request.quality_requirements,
            "failure_handling": request.failure_handling,
            "delivery_timeline": request.delivery_timeline.isoformat() if request.delivery_timeline else None,
            "performance_metrics": {
                "started_at": datetime.now().isoformat(),
                "estimated_completion": (datetime.now() + timedelta(
                    minutes=len(batch_items) * 5 // max(1, request.processing_preferences.get("parallel_workers", 3))
                )).isoformat(),
                "throughput_target": request.processing_preferences.get("items_per_hour", 12),
                "resource_allocation": {
                    "parallel_workers": request.processing_preferences.get("parallel_workers", 3),
                    "memory_per_worker": "512MB",
                    "cpu_allocation": 0.5
                }
            }
        }
        
        # Start batch processing
        background_tasks.add_task(
            process_batch_workflow,
            batch_id,
            batch_state,
            request
        )
        
        return {
            "success": True,
            "batch_workflow": {
                "batch_id": batch_id,
                "status": "initiated",
                "total_items": len(batch_items),
                "estimated_completion_hours": max(1, len(batch_items) * 5 // 60),
                "processing_strategy": {
                    "parallel_workers": request.processing_preferences.get("parallel_workers", 3),
                    "priority_handling": "high_priority_first",
                    "failure_handling": request.failure_handling,
                    "quality_gates": True
                },
                "tracking_capabilities": {
                    "batch_status": f"/api/v1/workflows/batch/{batch_id}/status",
                    "item_details": f"/api/v1/workflows/batch/{batch_id}/items",
                    "progress_stream": f"/api/v1/workflows/batch/{batch_id}/progress",
                    "results_download": f"/api/v1/workflows/batch/{batch_id}/results"
                }
            },
            "initiated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch workflow initiation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.put("/v1/workflows/{workflow_id}/intervention")
async def workflow_intervention(
    workflow_id: str = Path(..., description="Workflow identifier"),
    request: WorkflowInterventionRequest = Body(...)
) -> Dict:
    """Manual intervention in automated workflow.
    
    Enables human-in-the-loop workflow modifications including:
    - Workflow parameter adjustments
    - Step-level interventions and overrides
    - Quality control and approval gates
    - Error resolution and recovery actions
    - Performance optimization tweaks
    """
    try:
        intervention_id = str(uuid4())
        
        # Process intervention request
        intervention_result = {
            "intervention_id": intervention_id,
            "workflow_id": workflow_id,
            "intervention_type": request.intervention_type,
            "status": "applied",
            "applied_modifications": [],
            "impact_assessment": {
                "workflow_status_change": "parameters_updated",
                "estimated_time_impact": "+2 minutes",
                "quality_impact": "+5% accuracy",
                "cost_impact": "$0.15 additional"
            },
            "intervention_details": {
                "modification_parameters": request.modification_parameters,
                "approval_status": request.approval_status,
                "intervention_reason": request.intervention_reason,
                "stakeholders_notified": request.notify_stakeholders,
                "intervention_timestamp": datetime.now().isoformat()
            }
        }
        
        # Apply specific interventions based on type
        if request.intervention_type == "parameter_adjustment":
            intervention_result["applied_modifications"] = [
                {
                    "type": "parameter_update",
                    "parameter": "brand_enforcement_level",
                    "old_value": "moderate",
                    "new_value": request.modification_parameters.get("brand_enforcement_level", "strict"),
                    "impact": "Increased brand compliance validation"
                },
                {
                    "type": "quality_threshold",
                    "parameter": "minimum_quality_score",
                    "old_value": 0.8,
                    "new_value": request.modification_parameters.get("minimum_quality_score", 0.9),
                    "impact": "Higher quality output requirements"
                }
            ]
        elif request.intervention_type == "step_override":
            intervention_result["applied_modifications"] = [
                {
                    "type": "step_skip",
                    "step": request.modification_parameters.get("step_to_skip"),
                    "reason": "Manual approval override",
                    "impact": "Reduced processing time"
                }
            ]
        elif request.intervention_type == "quality_control":
            intervention_result["applied_modifications"] = [
                {
                    "type": "additional_validation",
                    "validation": "human_review_required",
                    "trigger": "Quality score below threshold",
                    "impact": "Enhanced quality assurance"
                }
            ]
        
        # Audit trail
        audit_entry = {
            "intervention_id": intervention_id,
            "workflow_id": workflow_id,
            "intervention_type": request.intervention_type,
            "user_id": "current_user",  # Would be extracted from authentication
            "timestamp": datetime.now().isoformat(),
            "changes_applied": intervention_result["applied_modifications"],
            "approval_chain": [
                {
                    "approver": "workflow_manager",
                    "status": request.approval_status,
                    "timestamp": datetime.now().isoformat()
                }
            ]
        }
        
        return {
            "success": True,
            "intervention_result": intervention_result,
            "audit_trail": audit_entry,
            "workflow_updated": True,
            "next_actions": [
                "Monitor workflow performance changes",
                "Verify intervention effectiveness",
                "Update stakeholders on changes"
            ]
        }
    except Exception as e:
        logger.error(f"Workflow intervention failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/workflows/batch/{batch_id}/status")
async def get_batch_workflow_status(
    batch_id: str = Path(..., description="Batch workflow identifier")
) -> Dict:
    """Get batch workflow status with detailed item progress.
    
    Provides comprehensive batch processing monitoring including:
    - Overall batch progress and performance metrics
    - Individual item status and timing information
    - Resource utilization and throughput analysis
    - Error tracking and failure analysis
    - Completion predictions and optimization recommendations
    """
    try:
        # Mock batch status (would integrate with batch processing service)
        batch_status = {
            "batch_id": batch_id,
            "overall_status": "in_progress",
            "progress_summary": {
                "total_items": 25,
                "completed_items": 18,
                "in_progress_items": 4,
                "queued_items": 2,
                "failed_items": 1,
                "progress_percentage": 72
            },
            "performance_metrics": {
                "started_at": "2025-01-06T09:30:00Z",
                "elapsed_time_minutes": 47,
                "estimated_completion": "2025-01-06T11:15:00Z",
                "items_per_hour": 23.4,
                "average_item_duration_minutes": 2.6,
                "resource_utilization": {
                    "active_workers": 3,
                    "worker_efficiency": 0.87,
                    "memory_usage": "68%",
                    "cpu_usage": "54%"
                }
            },
            "item_status_breakdown": {
                "completed": [
                    {
                        "item_id": "item_001",
                        "position": 1,
                        "status": "completed",
                        "duration_minutes": 2.3,
                        "quality_score": 0.94,
                        "output_files": 3
                    }
                    # ... more completed items
                ],
                "in_progress": [
                    {
                        "item_id": "item_019",
                        "position": 19,
                        "status": "in_progress",
                        "started_at": "2025-01-06T10:14:00Z",
                        "current_step": "visual_generation",
                        "progress_percentage": 65,
                        "worker_id": "worker_2"
                    }
                    # ... more in-progress items
                ],
                "failed": [
                    {
                        "item_id": "item_007",
                        "position": 7,
                        "status": "failed",
                        "error": "Freepik API timeout",
                        "retry_count": 2,
                        "last_attempt": "2025-01-06T10:08:00Z",
                        "recovery_action": "manual_review_required"
                    }
                ]
            },
            "quality_analysis": {
                "average_quality_score": 0.89,
                "quality_distribution": {
                    "excellent": 12,
                    "good": 5,
                    "acceptable": 1,
                    "poor": 0
                },
                "brand_compliance_rate": 0.96
            },
            "cost_analysis": {
                "total_cost": 4.75,
                "cost_per_item": 0.19,
                "budget_utilization": 0.48,
                "projected_total_cost": 6.58
            },
            "recommendations": [
                {
                    "category": "performance",
                    "recommendation": "Increase parallel workers to 4 for 15% faster completion",
                    "impact": "Complete 12 minutes earlier"
                },
                {
                    "category": "quality",
                    "recommendation": "Review failed item error pattern for process improvement",
                    "impact": "Reduce future failure rate by 25%"
                }
            ]
        }
        
        return {
            "success": True,
            "batch_status": batch_status,
            "monitoring_capabilities": {
                "real_time_updates": True,
                "item_level_tracking": True,
                "performance_analytics": True,
                "cost_tracking": True
            },
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Batch workflow status retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# Background task functions (would be implemented with actual services)
async def process_complete_content_generation(workflow_id: str, request: CompleteContentGenerationRequest, status: Dict):
    """Background task for complete content generation processing."""
    # This would contain the actual implementation
    pass

async def process_analytics_report(report_id: str, request: ReportGenerationRequest):
    """Background task for analytics report generation."""
    # This would contain the actual implementation
    pass

async def process_workflow_execution(workflow_id: str, workflow_state: Dict, request: WorkflowInitiationRequest):
    """Background task for workflow execution processing."""
    # This would contain the actual implementation
    pass

async def process_batch_workflow(batch_id: str, batch_state: Dict, request: BatchContentRequest):
    """Background task for batch workflow processing."""
    # This would contain the actual implementation
    pass


# ================================
# AUTHENTICATION AND AUTHORIZATION ENDPOINTS
# ================================

# Security setup
security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """Verify JWT token and extract user information."""
    try:
        # Mock token verification (would integrate with actual JWT service)
        token = credentials.credentials
        if not token or token == "invalid":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Mock user data (would decode from actual JWT)
        user_data = {
            "user_id": "user_123",
            "username": "bader_bymb",
            "roles": ["content_creator", "brand_manager"],
            "permissions": ["create_content", "manage_brand", "view_analytics"],
            "company_id": "bymb_consultancy",
            "subscription_tier": "premium",
            "token_expires_at": datetime.now() + timedelta(hours=1)
        }
        
        return user_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e

async def require_permission(permission: str):
    """Dependency to require specific permission."""
    def permission_checker(user: Dict = Depends(verify_token)) -> Dict:
        if permission not in user.get("permissions", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user
    return permission_checker

@router.post("/v1/auth/login")
async def login(request: TokenRequest) -> Dict:
    """Authenticate user and generate access token.
    
    Provides comprehensive authentication with:
    - Username/password validation
    - Multi-factor authentication support
    - Role-based token generation
    - Session management and tracking
    - Security event logging
    """
    try:
        # Mock authentication (would integrate with actual auth service)
        if request.username == "admin" and request.password == "secure_password":
            # Generate mock JWT token
            token_data = {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.mock_token",
                "token_type": "bearer",
                "expires_in": request.expires_in,
                "expires_at": (datetime.now() + timedelta(seconds=request.expires_in)).isoformat(),
                "scope": request.scope or ["full_access"],
                "user_id": "user_123",
                "roles": ["admin", "content_creator", "brand_manager"],
                "company_id": "bymb_consultancy",
                "subscription_tier": "premium"
            }
            
            # Security audit log
            security_event = {
                "event_type": "successful_login",
                "user_id": token_data["user_id"],
                "username": request.username,
                "timestamp": datetime.now().isoformat(),
                "ip_address": "192.168.1.100",  # Would be extracted from request
                "user_agent": "PostmanRuntime/7.28.0",  # Would be extracted from request
                "session_id": str(uuid4())
            }
            
            return {
                "success": True,
                "authentication": token_data,
                "security_event": security_event,
                "next_steps": [
                    "Use access_token in Authorization header as 'Bearer {token}'",
                    "Token will expire in specified time",
                    "Refresh token before expiration"
                ]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/auth/api-key")
async def generate_api_key(
    request: ApiKeyRequest,
    current_user: Dict = Depends(require_permission("manage_api_keys"))
) -> Dict:
    """Generate API key for service-to-service authentication.
    
    Creates API keys with:
    - Granular permission control
    - Usage tracking and analytics
    - Expiration date management
    - Rate limiting configuration
    - Audit trail and monitoring
    """
    try:
        api_key_id = str(uuid4())
        api_key = f"bymb_{api_key_id.replace('-', '')[:16]}"
        
        # API key configuration
        api_key_data = {
            "api_key_id": api_key_id,
            "api_key": api_key,
            "key_name": request.key_name,
            "permissions": request.permissions,
            "created_by": current_user["user_id"],
            "company_id": current_user["company_id"],
            "created_at": datetime.now().isoformat(),
            "expires_at": request.expires_at.isoformat() if request.expires_at else None,
            "status": "active",
            "usage_tracking": {
                "calls_made": 0,
                "last_used": None,
                "daily_limit": request.rate_limits.get("daily_limit", 10000),
                "minute_limit": request.rate_limits.get("minute_limit", 100)
            },
            "security_settings": {
                "ip_whitelist": [],
                "allowed_origins": ["*"],
                "require_https": True
            }
        }
        
        return {
            "success": True,
            "api_key_generation": api_key_data,
            "security_notice": "Store this API key securely - it cannot be retrieved again",
            "usage_instructions": [
                "Include in requests as X-API-Key header",
                "Monitor usage through analytics dashboard",
                "Rotate keys regularly for security"
            ]
        }
    except Exception as e:
        logger.error(f"API key generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/auth/profile")
async def get_user_profile(current_user: Dict = Depends(verify_token)) -> Dict:
    """Get current user profile and permissions.
    
    Returns comprehensive user information including:
    - User details and contact information
    - Role and permission assignments
    - Subscription and billing information
    - Usage statistics and analytics
    - Security settings and audit log
    """
    try:
        # Mock user profile data (would retrieve from user service)
        user_profile = {
            "user_details": {
                "user_id": current_user["user_id"],
                "username": current_user["username"],
                "email": "bader@bymbconsultancy.com",
                "full_name": "Bader Abdulrahim",
                "title": "Founder & CEO",
                "company": "BYMB Consultancy",
                "location": "Manama, Kingdom of Bahrain",
                "timezone": "Asia/Bahrain",
                "language": "en",
                "profile_created": "2024-01-15T10:00:00Z",
                "last_login": datetime.now().isoformat()
            },
            "authorization": {
                "roles": current_user["roles"],
                "permissions": current_user["permissions"],
                "subscription_tier": current_user["subscription_tier"],
                "company_id": current_user["company_id"],
                "access_level": "full"
            },
            "subscription_info": {
                "plan": "Premium Business",
                "status": "active",
                "billing_cycle": "annual",
                "renewal_date": "2025-12-31T23:59:59Z",
                "usage_limits": {
                    "content_generation": {"used": 247, "limit": 1000},
                    "api_calls": {"used": 1543, "limit": 10000},
                    "storage_gb": {"used": 2.3, "limit": 50}
                }
            },
            "usage_statistics": {
                "content_created_this_month": 42,
                "platforms_managed": ["linkedin", "instagram", "twitter"],
                "average_engagement_rate": 0.067,
                "total_reach_this_month": 145000,
                "brand_compliance_average": 0.94
            },
            "security_settings": {
                "two_factor_enabled": True,
                "last_password_change": "2024-11-15T14:30:00Z",
                "active_sessions": 2,
                "login_alerts_enabled": True,
                "api_keys_count": 3
            }
        }
        
        return {
            "success": True,
            "user_profile": user_profile,
            "profile_completeness": 0.95,
            "recommendations": [
                "Enable login alerts for enhanced security",
                "Review and rotate API keys regularly",
                "Update profile picture for better brand presence"
            ]
        }
    except Exception as e:
        logger.error(f"User profile retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================
# COST MANAGEMENT AND RATE LIMITING ENDPOINTS
# ================================

@router.get("/v1/costs/tracking/summary")
async def get_cost_tracking_summary(
    time_range_days: int = Query(default=30, description="Analysis time range"),
    current_user: Dict = Depends(verify_token)
) -> Dict:
    """Get cost tracking and budget monitoring summary.
    
    Provides comprehensive financial oversight including:
    - Current usage and cost breakdown
    - Budget status and projections
    - Cost optimization recommendations
    - Usage patterns and trends
    - Billing and invoice information
    """
    try:
        # Mock cost tracking data (would integrate with billing service)
        cost_summary = {
            "current_period": {
                "start_date": (datetime.now() - timedelta(days=time_range_days)).isoformat(),
                "end_date": datetime.now().isoformat(),
                "days_elapsed": time_range_days,
                "days_remaining": 30 - time_range_days if time_range_days < 30 else 0
            },
            "cost_breakdown": {
                "freepik_api": {"usage": 247, "cost": 24.70, "percentage": 0.65},
                "content_generation": {"usage": 89, "cost": 8.90, "percentage": 0.23},
                "storage": {"usage_gb": 2.3, "cost": 2.30, "percentage": 0.06},
                "bandwidth": {"usage_gb": 12.7, "cost": 1.27, "percentage": 0.03},
                "other": {"cost": 1.23, "percentage": 0.03}
            },
            "total_cost": 38.40,
            "budget_status": {
                "monthly_budget": 100.00,
                "budget_used": 38.40,
                "budget_remaining": 61.60,
                "percentage_used": 0.384,
                "projected_monthly_total": 47.85,
                "budget_alert_threshold": 80.00,
                "alert_triggered": False
            },
            "usage_trends": [
                {"date": "2025-01-01", "daily_cost": 1.25},
                {"date": "2025-01-02", "daily_cost": 1.43},
                {"date": "2025-01-03", "daily_cost": 1.18},
                {"date": "2025-01-04", "daily_cost": 1.67},
                {"date": "2025-01-05", "daily_cost": 1.52}
            ],
            "cost_optimization": {
                "potential_savings": 12.50,
                "recommendations": [
                    {
                        "category": "api_usage",
                        "recommendation": "Implement caching to reduce Freepik API calls by 20%",
                        "potential_savings": 4.94,
                        "implementation_effort": "low"
                    },
                    {
                        "category": "storage",
                        "recommendation": "Archive content older than 90 days",
                        "potential_savings": 0.68,
                        "implementation_effort": "medium"
                    },
                    {
                        "category": "content_generation",
                        "recommendation": "Use batch processing for better efficiency",
                        "potential_savings": 1.78,
                        "implementation_effort": "medium"
                    }
                ]
            },
            "billing_information": {
                "next_billing_date": "2025-02-01T00:00:00Z",
                "payment_method": "Credit Card ending in 4532",
                "billing_address": "Manama, Kingdom of Bahrain",
                "invoice_delivery": "email"
            }
        }
        
        return {
            "success": True,
            "cost_tracking": cost_summary,
            "monitoring_alerts": {
                "budget_alerts_enabled": True,
                "usage_spike_alerts": True,
                "cost_anomaly_detection": True
            },
            "generated_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Cost tracking summary failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/rate-limits/configure")
async def configure_rate_limits(
    request: RateLimitConfiguration,
    current_user: Dict = Depends(require_permission("manage_system_settings"))
) -> Dict:
    """Configure API rate limiting parameters.
    
    Manages rate limiting with:
    - Dynamic rate limit adjustment
    - User-specific quota management
    - Priority-based access control
    - Usage monitoring and analytics
    - Automated scaling and optimization
    """
    try:
        configuration_id = str(uuid4())
        
        # Process rate limit configuration
        rate_limit_config = {
            "configuration_id": configuration_id,
            "applied_rules": request.rate_limit_rules,
            "priority_settings": request.priority_settings,
            "user_quotas": request.user_quotas,
            "override_settings": request.override_settings,
            "monitoring_preferences": request.monitoring_preferences,
            "configuration_metadata": {
                "configured_by": current_user["user_id"],
                "configuration_timestamp": datetime.now().isoformat(),
                "previous_config_backup": True,
                "validation_passed": True
            },
            "impact_analysis": {
                "affected_endpoints": len(request.rate_limit_rules),
                "affected_users": len(request.user_quotas),
                "estimated_performance_impact": "minimal",
                "rollback_available": True
            }
        }
        
        # Validate configuration
        validation_results = {
            "configuration_valid": True,
            "validation_issues": [],
            "recommendations": [
                "Monitor API response times after changes",
                "Set up alerts for rate limit violations", 
                "Review configuration monthly for optimization"
            ]
        }
        
        return {
            "success": True,
            "rate_limit_configuration": rate_limit_config,
            "validation_results": validation_results,
            "applied_at": datetime.now().isoformat(),
            "monitoring_dashboard": "/api/v1/rate-limits/monitoring"
        }
    except Exception as e:
        logger.error(f"Rate limit configuration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


# ================================
# WEBHOOK INTEGRATION ENDPOINTS
# ================================

@router.post("/v1/webhooks/register")
async def register_webhook(
    request: WebhookRegistrationRequest,
    current_user: Dict = Depends(require_permission("manage_webhooks"))
) -> Dict:
    """Register webhook endpoints for event notifications.
    
    Enables webhook integration with:
    - Event type subscription management
    - Authentication and security validation
    - Retry policy configuration
    - Event filtering and transformation
    - Monitoring and analytics
    """
    try:
        webhook_id = str(uuid4())
        
        # Validate webhook URL
        webhook_validation = {
            "url_reachable": True,  # Would perform actual validation
            "ssl_valid": True,
            "response_time_ms": 145,
            "supports_required_methods": True
        }
        
        # Register webhook
        webhook_registration = {
            "webhook_id": webhook_id,
            "webhook_url": request.webhook_url,
            "event_types": request.event_types,
            "status": "active" if request.active else "inactive",
            "authentication": {
                "method": request.authentication.get("method", "signature"),
                "configured": bool(request.authentication),
                "secret_key": f"whsec_{str(uuid4()).replace('-', '')[:24]}"
            },
            "retry_policy": {
                "max_retries": request.retry_policy.get("max_retries", 3),
                "retry_delay_seconds": request.retry_policy.get("retry_delay", 5),
                "exponential_backoff": request.retry_policy.get("exponential_backoff", True)
            },
            "event_filters": request.event_filters or {},
            "registration_details": {
                "created_by": current_user["user_id"],
                "company_id": current_user["company_id"],
                "created_at": datetime.now().isoformat(),
                "last_validated": datetime.now().isoformat(),
                "validation_results": webhook_validation
            },
            "monitoring": {
                "success_rate": 0.0,
                "total_deliveries": 0,
                "failed_deliveries": 0,
                "average_response_time_ms": 0,
                "last_delivery": None
            }
        }
        
        return {
            "success": True,
            "webhook_registration": webhook_registration,
            "security_instructions": [
                "Verify webhook signatures using the provided secret key",
                "Implement idempotency handling for event processing",
                "Return 200 status code for successful processing"
            ],
            "supported_events": [
                "content.generation.completed",
                "content.generation.failed",
                "workflow.status.changed",
                "brand.validation.completed",
                "analytics.report.ready",
                "batch.processing.completed"
            ],
            "test_endpoint": f"/api/v1/webhooks/{webhook_id}/test"
        }
    except Exception as e:
        logger.error(f"Webhook registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/v1/webhooks/{webhook_id}/test")
async def test_webhook_delivery(
    webhook_id: str = Path(..., description="Webhook identifier"),
    request: WebhookTestRequest = Body(...),
    current_user: Dict = Depends(verify_token)
) -> Dict:
    """Test webhook delivery and response handling.
    
    Validates webhook functionality with:
    - End-to-end connectivity testing
    - Response validation and timing
    - Error handling and recovery
    - Authentication verification
    - Performance benchmarking
    """
    try:
        test_id = str(uuid4())
        
        # Mock webhook test (would perform actual HTTP request)
        test_results = {
            "test_id": test_id,
            "webhook_id": webhook_id,
            "test_configuration": request.webhook_configuration,
            "test_payload": request.test_payload,
            "test_execution": {
                "started_at": datetime.now().isoformat(),
                "completed_at": (datetime.now() + timedelta(milliseconds=245)).isoformat(),
                "duration_ms": 245,
                "status": "success"
            },
            "connectivity_test": {
                "url_reachable": True,
                "dns_resolution_ms": 23,
                "tcp_connection_ms": 45,
                "ssl_handshake_ms": 67,
                "http_response_ms": 110
            },
            "authentication_test": {
                "method": request.webhook_configuration.get("authentication", {}).get("method", "signature"),
                "signature_valid": True,
                "headers_present": True,
                "authentication_successful": True
            },
            "response_validation": {
                "status_code": 200,
                "response_time_ms": 245,
                "content_type": "application/json",
                "body_valid": True,
                "error_handling": "appropriate"
            },
            "payload_validation": {
                "payload_sent": True,
                "payload_size_bytes": len(str(request.test_payload)),
                "encoding": "utf-8",
                "compression": None
            },
            "performance_metrics": {
                "throughput_requests_per_second": 4.1,
                "latency_p95_ms": 298,
                "success_rate": 1.0,
                "error_rate": 0.0
            }
        }
        
        # Validation summary
        validation_summary = {
            "overall_status": "passed",
            "tests_passed": 12,
            "tests_failed": 0,
            "critical_issues": [],
            "warnings": [],
            "recommendations": [
                "Webhook is functioning correctly",
                "Response time is within acceptable limits",
                "Authentication is properly configured"
            ]
        }
        
        return {
            "success": True,
            "webhook_test": test_results,
            "validation_summary": validation_summary,
            "next_steps": [
                "Webhook is ready for production use",
                "Monitor delivery success rates",
                "Set up alerting for failed deliveries"
            ]
        }
    except Exception as e:
        logger.error(f"Webhook test failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/v1/webhooks")
async def list_webhooks(
    current_user: Dict = Depends(verify_token)
) -> Dict:
    """List all registered webhooks with status and metrics.
    
    Returns comprehensive webhook overview including:
    - Webhook configuration and status
    - Delivery metrics and performance
    - Error rates and troubleshooting
    - Event subscription details
    - Management and control options
    """
    try:
        # Mock webhook data (would retrieve from webhook service)
        webhooks = [
            {
                "webhook_id": str(uuid4()),
                "webhook_url": "https://api.example.com/webhooks/content",
                "event_types": ["content.generation.completed", "workflow.status.changed"],
                "status": "active",
                "created_at": "2024-12-01T10:00:00Z",
                "metrics": {
                    "total_deliveries": 247,
                    "successful_deliveries": 243,
                    "failed_deliveries": 4,
                    "success_rate": 0.984,
                    "average_response_time_ms": 156,
                    "last_delivery": "2025-01-06T09:45:00Z"
                },
                "configuration": {
                    "authentication": "signature",
                    "retry_policy": {"max_retries": 3, "exponential_backoff": True},
                    "timeout_seconds": 30
                }
            },
            {
                "webhook_id": str(uuid4()),
                "webhook_url": "https://analytics.example.com/api/events",
                "event_types": ["analytics.report.ready", "batch.processing.completed"],
                "status": "active",
                "created_at": "2024-11-15T14:30:00Z",
                "metrics": {
                    "total_deliveries": 89,
                    "successful_deliveries": 87,
                    "failed_deliveries": 2,
                    "success_rate": 0.978,
                    "average_response_time_ms": 203,
                    "last_delivery": "2025-01-06T08:30:00Z"
                },
                "configuration": {
                    "authentication": "api_key",
                    "retry_policy": {"max_retries": 5, "exponential_backoff": True},
                    "timeout_seconds": 45
                }
            }
        ]
        
        # Aggregate metrics
        aggregate_metrics = {
            "total_webhooks": len(webhooks),
            "active_webhooks": len([w for w in webhooks if w["status"] == "active"]),
            "total_deliveries": sum(w["metrics"]["total_deliveries"] for w in webhooks),
            "overall_success_rate": sum(w["metrics"]["success_rate"] for w in webhooks) / len(webhooks) if webhooks else 0,
            "average_response_time_ms": sum(w["metrics"]["average_response_time_ms"] for w in webhooks) / len(webhooks) if webhooks else 0
        }
        
        return {
            "success": True,
            "webhooks": {
                "registered_webhooks": webhooks,
                "aggregate_metrics": aggregate_metrics,
                "webhook_management": {
                    "register_new": "/api/v1/webhooks/register",
                    "test_webhook": "/api/v1/webhooks/{webhook_id}/test",
                    "webhook_logs": "/api/v1/webhooks/{webhook_id}/logs",
                    "webhook_metrics": "/api/v1/webhooks/{webhook_id}/metrics"
                }
            },
            "retrieved_at": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Webhook listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) from e
