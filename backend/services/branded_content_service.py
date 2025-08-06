"""Branded Content Service - Integrates Freepik API with BYMB brand consistency system."""

import asyncio
import json
import uuid
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
import io
import base64

from .freepik_client import FreepikClient, SearchFilters, FreepikResource, DownloadResult
from .freepik_client import ContentType as FreepikContentType, Orientation, LicenseType
from .brand_profile import BYMBBrandProfile, PlatformType, ContentType, BrandTone, bymb_brand
from .brand_validator import BrandValidator, ValidationResult, ContentAnalysis, brand_validator
from .brand_template_engine import BrandTemplateEngine, GenerationRequest, GenerationResult, brand_template_engine
from .brand_enforcer import BrandEnforcementEngine, EnforcementResult, brand_enforcer

logger = logging.getLogger(__name__)


class ContentCreationMode(Enum):
    """Content creation modes."""
    TEMPLATE_BASED = "template_based"      # Use branded templates
    FREEPIK_ENHANCED = "freepik_enhanced"  # Freepik images with brand overlay
    HYBRID = "hybrid"                      # Combine both approaches
    BRAND_ONLY = "brand_only"              # Only brand assets


class QualityLevel(Enum):
    """Content quality levels."""
    DRAFT = "draft"          # Quick generation for testing
    STANDARD = "standard"    # Good quality for regular posts
    PREMIUM = "premium"      # High quality for important content
    EXECUTIVE = "executive"  # Highest quality for executive use


@dataclass
class ContentRequest:
    """Comprehensive content generation request."""
    # Content specifications
    text_content: str
    platform: PlatformType
    content_type: ContentType
    quality_level: QualityLevel = QualityLevel.STANDARD
    creation_mode: ContentCreationMode = ContentCreationMode.HYBRID
    
    # Brand specifications  
    brand_tone: Optional[BrandTone] = None
    enforce_brand_compliance: bool = True
    minimum_brand_score: float = 0.8
    
    # Visual preferences
    visual_style: Optional[str] = None  # "professional", "elegant", "modern"
    color_scheme: Optional[str] = None  # "primary", "secondary", "monochrome"
    include_logo: bool = True
    
    # Freepik integration
    freepik_search_terms: Optional[List[str]] = None
    freepik_image_filters: Optional[Dict[str, Any]] = None
    use_freepik_ai: bool = False
    
    # Customizations
    template_id: Optional[str] = None
    custom_dimensions: Optional[Tuple[int, int]] = None
    custom_brand_elements: Optional[Dict[str, Any]] = None
    
    # Output preferences
    output_formats: List[str] = field(default_factory=lambda: ["PNG"])
    include_variations: bool = False
    variation_count: int = 3
    
    # Metadata
    campaign_id: Optional[str] = None
    user_id: str = "default"
    request_metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass 
class BrandedContentResult:
    """Comprehensive branded content result."""
    success: bool
    content_id: str
    
    # Generated content
    primary_image: Optional[bytes] = None
    primary_image_base64: Optional[str] = None
    variations: List[bytes] = field(default_factory=list)
    
    # Brand compliance
    brand_validation: Optional[ValidationResult] = None
    brand_enforcement: Optional[EnforcementResult] = None
    final_brand_score: float = 0.0
    
    # Generation metadata
    generation_method: ContentCreationMode = ContentCreationMode.TEMPLATE_BASED
    template_used: Optional[str] = None
    freepik_resources: List[FreepikResource] = field(default_factory=list)
    
    # Quality metrics
    quality_score: float = 0.0
    processing_time_ms: int = 0
    generation_cost: float = 0.0
    
    # Output files
    output_files: Dict[str, str] = field(default_factory=dict)  # format -> file_path
    
    # Issues and recommendations
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    
    # Metadata
    creation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    generation_metadata: Dict[str, Any] = field(default_factory=dict)


class BrandedContentService:
    """Comprehensive branded content generation service."""
    
    def __init__(
        self,
        freepik_client: Optional[FreepikClient] = None,
        brand_profile: Optional[BYMBBrandProfile] = None,
        template_engine: Optional[BrandTemplateEngine] = None,
        validator: Optional[BrandValidator] = None,
        enforcer: Optional[BrandEnforcementEngine] = None,
        output_directory: str = "generated_content"
    ):
        """Initialize branded content service."""
        self.freepik_client = freepik_client
        self.brand = brand_profile or bymb_brand
        self.template_engine = template_engine or brand_template_engine
        self.validator = validator or brand_validator
        self.enforcer = enforcer or brand_enforcer
        
        # Output management
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.generation_stats = {
            "total_requests": 0,
            "successful_generations": 0,
            "average_brand_score": 0.0,
            "average_processing_time": 0.0
        }
        
        logger.info("Branded content service initialized")
    
    async def generate_branded_content(self, request: ContentRequest) -> BrandedContentResult:
        """Generate branded content based on request specifications."""
        start_time = datetime.now()
        content_id = str(uuid.uuid4())
        
        logger.info(f"Starting branded content generation: {content_id}")
        
        try:
            self.generation_stats["total_requests"] += 1
            
            # Validate and prepare request
            validated_request = await self._validate_request(request)
            if not validated_request:
                return BrandedContentResult(
                    success=False,
                    content_id=content_id,
                    errors=["Invalid content request"]
                )
            
            # Choose generation strategy based on mode
            if request.creation_mode == ContentCreationMode.TEMPLATE_BASED:
                result = await self._generate_template_based_content(validated_request, content_id)
            elif request.creation_mode == ContentCreationMode.FREEPIK_ENHANCED:
                result = await self._generate_freepik_enhanced_content(validated_request, content_id)
            elif request.creation_mode == ContentCreationMode.HYBRID:
                result = await self._generate_hybrid_content(validated_request, content_id)
            else:  # BRAND_ONLY
                result = await self._generate_brand_only_content(validated_request, content_id)
            
            # Apply brand enforcement if requested
            if request.enforce_brand_compliance and result.primary_image:
                enforcement_result = await self._enforce_brand_compliance(result, request)
                result.brand_enforcement = enforcement_result
                
                # Update final score
                if enforcement_result.success:
                    result.final_brand_score = enforcement_result.corrected_score
                    if enforcement_result.corrected_image_data:
                        result.primary_image = enforcement_result.corrected_image_data
                        result.primary_image_base64 = base64.b64encode(enforcement_result.corrected_image_data).decode('utf-8')
            
            # Generate variations if requested
            if request.include_variations and result.success:
                variations = await self._generate_variations(result, request)
                result.variations = variations
            
            # Save output files
            if result.primary_image:
                await self._save_output_files(result, request)
            
            # Calculate final metrics
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            result.processing_time_ms = int(processing_time)
            
            # Update statistics
            if result.success:
                self.generation_stats["successful_generations"] += 1
                self.generation_stats["average_brand_score"] = (
                    (self.generation_stats["average_brand_score"] * (self.generation_stats["successful_generations"] - 1) +
                     result.final_brand_score) / self.generation_stats["successful_generations"]
                )
            
            self.generation_stats["average_processing_time"] = (
                (self.generation_stats["average_processing_time"] * (self.generation_stats["total_requests"] - 1) +
                 processing_time) / self.generation_stats["total_requests"]
            )
            
            logger.info(
                f"Content generation completed: {content_id} - "
                f"Success: {result.success}, Score: {result.final_brand_score:.2f}, "
                f"Time: {processing_time:.0f}ms"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed for {content_id}: {e}")
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return BrandedContentResult(
                success=False,
                content_id=content_id,
                processing_time_ms=int(processing_time),
                errors=[f"Generation failed: {str(e)}"]
            )
    
    async def _validate_request(self, request: ContentRequest) -> Optional[ContentRequest]:
        """Validate and prepare content request."""
        if not request.text_content.strip():
            logger.error("Empty text content in request")
            return None
        
        if not request.platform:
            logger.error("Platform not specified in request")
            return None
        
        # Set default brand tone based on content type
        if not request.brand_tone:
            tone_mapping = {
                ContentType.THOUGHT_LEADERSHIP: BrandTone.AUTHORITATIVE,
                ContentType.BUSINESS_INSIGHT: BrandTone.ANALYTICAL,
                ContentType.INSPIRATIONAL: BrandTone.INSPIRATIONAL,
                ContentType.EDUCATIONAL: BrandTone.CONVERSATIONAL,
                ContentType.PROMOTIONAL: BrandTone.STRATEGIC
            }
            request.brand_tone = tone_mapping.get(request.content_type, BrandTone.AUTHORITATIVE)
        
        # Set default visual style based on quality level
        if not request.visual_style:
            style_mapping = {
                QualityLevel.DRAFT: "minimal",
                QualityLevel.STANDARD: "professional", 
                QualityLevel.PREMIUM: "elegant",
                QualityLevel.EXECUTIVE: "executive"
            }
            request.visual_style = style_mapping[request.quality_level]
        
        return request
    
    async def _generate_template_based_content(
        self, 
        request: ContentRequest, 
        content_id: str
    ) -> BrandedContentResult:
        """Generate content using brand templates."""
        result = BrandedContentResult(
            success=False,
            content_id=content_id,
            generation_method=ContentCreationMode.TEMPLATE_BASED
        )
        
        try:
            # Find or select appropriate template
            template_id = await self._select_template(request)
            if not template_id:
                result.errors.append("No suitable template found")
                return result
            
            # Prepare template generation request
            template_request = GenerationRequest(
                template_id=template_id,
                content=self._extract_template_variables(request),
                platform=request.platform,
                content_type=request.content_type,
                customizations=self._build_template_customizations(request),
                brand_validation_required=True
            )
            
            # Generate content using template engine
            generation_result = await self.template_engine.generate_content(template_request)
            
            if generation_result.success:
                result.success = True
                result.primary_image = generation_result.image_data
                result.primary_image_base64 = generation_result.image_base64
                result.template_used = template_id
                result.brand_validation = generation_result.validation_result
                
                if result.brand_validation:
                    result.final_brand_score = result.brand_validation.overall_score
                
                # Calculate quality score based on brand compliance and template quality
                result.quality_score = self._calculate_quality_score(
                    result.brand_validation, request.quality_level
                )
                
                # Add any warnings from generation
                result.warnings.extend(generation_result.warnings)
                
            else:
                result.errors.append(f"Template generation failed: {generation_result.error_message}")
            
            return result
            
        except Exception as e:
            logger.error(f"Template-based generation failed: {e}")
            result.errors.append(f"Template generation error: {str(e)}")
            return result
    
    async def _generate_freepik_enhanced_content(
        self, 
        request: ContentRequest, 
        content_id: str
    ) -> BrandedContentResult:
        """Generate content using Freepik images with brand enhancements."""
        result = BrandedContentResult(
            success=False,
            content_id=content_id,
            generation_method=ContentCreationMode.FREEPIK_ENHANCED
        )
        
        if not self.freepik_client:
            result.errors.append("Freepik client not configured")
            return result
        
        try:
            # Search for relevant Freepik images
            search_terms = request.freepik_search_terms or self._generate_search_terms(request)
            freepik_resources = await self._search_brand_appropriate_images(search_terms, request)
            
            if not freepik_resources:
                result.errors.append("No suitable Freepik images found")
                return result
            
            # Select best image for branding
            selected_resource = await self._select_best_freepik_image(freepik_resources, request)
            result.freepik_resources = [selected_resource]
            
            # Download the image
            download_result = await self._download_and_prepare_image(selected_resource, content_id)
            if not download_result.success:
                result.errors.append(f"Image download failed: {download_result.error_message}")
                return result
            
            # Apply brand enhancements
            branded_image = await self._apply_brand_enhancements(
                download_result.file_path, request
            )
            
            if branded_image:
                result.success = True
                result.primary_image = branded_image
                result.primary_image_base64 = base64.b64encode(branded_image).decode('utf-8')
                
                # Validate brand compliance
                result.brand_validation = await self._validate_freepik_enhanced_content(
                    branded_image, request
                )
                
                if result.brand_validation:
                    result.final_brand_score = result.brand_validation.overall_score
                
                result.quality_score = self._calculate_freepik_quality_score(
                    selected_resource, result.brand_validation, request.quality_level
                )
                
            else:
                result.errors.append("Failed to apply brand enhancements to Freepik image")
            
            return result
            
        except Exception as e:
            logger.error(f"Freepik-enhanced generation failed: {e}")
            result.errors.append(f"Freepik enhancement error: {str(e)}")
            return result
    
    async def _generate_hybrid_content(
        self, 
        request: ContentRequest, 
        content_id: str
    ) -> BrandedContentResult:
        """Generate content using hybrid approach (templates + Freepik)."""
        result = BrandedContentResult(
            success=False,
            content_id=content_id,
            generation_method=ContentCreationMode.HYBRID
        )
        
        try:
            # Try template-based approach first
            template_result = await self._generate_template_based_content(request, content_id)
            
            # If template approach succeeds and meets quality threshold, use it
            if (template_result.success and 
                template_result.final_brand_score >= request.minimum_brand_score):
                result = template_result
                result.generation_method = ContentCreationMode.HYBRID
                result.generation_metadata["primary_method"] = "template"
                return result
            
            # Otherwise, try Freepik-enhanced approach
            freepik_result = await self._generate_freepik_enhanced_content(request, content_id)
            
            if freepik_result.success:
                result = freepik_result
                result.generation_method = ContentCreationMode.HYBRID
                result.generation_metadata["primary_method"] = "freepik"
                
                # Add template warnings if template failed
                if not template_result.success:
                    result.warnings.append("Template generation failed, used Freepik approach")
                else:
                    result.warnings.append(f"Template score ({template_result.final_brand_score:.2f}) below threshold, used Freepik approach")
                
                return result
            
            # If both fail, return template result with additional errors
            result = template_result
            result.generation_method = ContentCreationMode.HYBRID
            result.errors.extend(freepik_result.errors)
            result.warnings.append("Both template and Freepik approaches had issues")
            
            return result
            
        except Exception as e:
            logger.error(f"Hybrid generation failed: {e}")
            result.errors.append(f"Hybrid generation error: {str(e)}")
            return result
    
    async def _generate_brand_only_content(
        self, 
        request: ContentRequest, 
        content_id: str
    ) -> BrandedContentResult:
        """Generate content using only brand assets (no external images)."""
        result = BrandedContentResult(
            success=False,
            content_id=content_id,
            generation_method=ContentCreationMode.BRAND_ONLY
        )
        
        try:
            # Force template-based generation without external assets
            modified_request = request
            modified_request.freepik_search_terms = None
            
            # Use simple, brand-focused templates
            template_result = await self._generate_template_based_content(modified_request, content_id)
            
            if template_result.success:
                result = template_result
                result.generation_method = ContentCreationMode.BRAND_ONLY
                result.generation_metadata["assets_used"] = "brand_only"
            else:
                result.errors.extend(template_result.errors)
            
            return result
            
        except Exception as e:
            logger.error(f"Brand-only generation failed: {e}")
            result.errors.append(f"Brand-only generation error: {str(e)}")
            return result
    
    async def _select_template(self, request: ContentRequest) -> Optional[str]:
        """Select appropriate template for request."""
        if request.template_id:
            return request.template_id
        
        # Get available templates for platform and content type
        available_templates = self.template_engine.get_available_templates(
            platform=request.platform,
            category=None  # Will be mapped from content_type
        )
        
        if not available_templates:
            return None
        
        # Score templates based on request criteria
        scored_templates = []
        
        for template in available_templates:
            score = 0.0
            
            # Brand compliance score
            score += template["brand_compliance_score"] * 0.4
            
            # Visual style match
            if request.visual_style and request.visual_style in template.get("layout_style", "").lower():
                score += 0.3
            
            # Quality level appropriateness  
            quality_bonus = {
                QualityLevel.DRAFT: 0.1,
                QualityLevel.STANDARD: 0.2,
                QualityLevel.PREMIUM: 0.3,
                QualityLevel.EXECUTIVE: 0.4
            }
            score += quality_bonus[request.quality_level]
            
            scored_templates.append((template["id"], score))
        
        # Return highest scoring template
        if scored_templates:
            scored_templates.sort(key=lambda x: x[1], reverse=True)
            return scored_templates[0][0]
        
        return None
    
    def _extract_template_variables(self, request: ContentRequest) -> Dict[str, str]:
        """Extract template variables from request."""
        variables = {
            "main_text": request.text_content,
            "author": self.brand.founder,
            "company": self.brand.brand_name,
            "tagline": self.brand.tagline,
            "location": self.brand.location,
            "experience": self.brand.experience
        }
        
        # Add content-type specific variables
        if request.content_type == ContentType.BUSINESS_INSIGHT:
            variables.update({
                "insight_title": "Strategic Business Insight",
                "insight_content": request.text_content,
                "expertise_note": f"Based on {self.brand.experience} of consultancy experience"
            })
        
        elif request.content_type == ContentType.ACHIEVEMENT:
            variables.update({
                "achievement_title": "Milestone Achievement",
                "achievement_content": request.text_content,
                "results_note": self.brand.client_results
            })
        
        # Add any custom variables from request
        if request.custom_brand_elements:
            variables.update(request.custom_brand_elements)
        
        return variables
    
    def _build_template_customizations(self, request: ContentRequest) -> Dict[str, Any]:
        """Build template customizations from request."""
        customizations = {}
        
        # Quality level adjustments
        if request.quality_level == QualityLevel.PREMIUM:
            customizations["filter"] = "enhance"
            customizations["contrast"] = 1.1
        elif request.quality_level == QualityLevel.EXECUTIVE:
            customizations["filter"] = "sharpen"
            customizations["contrast"] = 1.2
            customizations["brightness"] = 1.05
        
        # Color scheme preferences
        if request.color_scheme:
            customizations["color_scheme"] = request.color_scheme
        
        # Visual style adjustments
        if request.visual_style == "elegant":
            customizations["elegance_boost"] = True
        
        return customizations
    
    async def _search_brand_appropriate_images(
        self, 
        search_terms: List[str], 
        request: ContentRequest
    ) -> List[FreepikResource]:
        """Search for brand-appropriate images from Freepik."""
        if not self.freepik_client:
            return []
        
        resources = []
        
        for term in search_terms[:3]:  # Limit search terms
            # Build search filters
            filters = SearchFilters(
                query=term,
                content_type=FreepikContentType.PHOTO,  # Prefer photos for professional content
                orientation=self._get_orientation_for_platform(request.platform),
                license_type=LicenseType.ALL,
                limit=10,
                order_by="popular"
            )
            
            # Apply platform-specific filters
            platform_specs = self.brand.get_platform_specs(request.platform)
            if platform_specs and "square" in platform_specs.dimensions:
                filters.orientation = Orientation.SQUARE
            
            # Apply quality filters
            if request.quality_level in [QualityLevel.PREMIUM, QualityLevel.EXECUTIVE]:
                filters.min_width = 1080
                filters.min_height = 1080
            
            # Apply custom filters if provided
            if request.freepik_image_filters:
                for key, value in request.freepik_image_filters.items():
                    if hasattr(filters, key):
                        setattr(filters, key, value)
            
            try:
                search_result = await self.freepik_client.search_resources(filters, request.user_id)
                
                # Filter for brand appropriateness
                appropriate_resources = []
                for resource in search_result.get("resources", []):
                    if await self._is_brand_appropriate_image(resource, request):
                        appropriate_resources.append(resource)
                
                resources.extend(appropriate_resources)
                
            except Exception as e:
                logger.warning(f"Freepik search failed for term '{term}': {e}")
        
        return resources
    
    def _generate_search_terms(self, request: ContentRequest) -> List[str]:
        """Generate Freepik search terms based on content."""
        base_terms = []
        
        # Content type based terms
        content_terms = {
            ContentType.BUSINESS_INSIGHT: ["business", "strategy", "professional", "corporate", "consulting"],
            ContentType.THOUGHT_LEADERSHIP: ["leadership", "executive", "vision", "innovation", "growth"],
            ContentType.ACHIEVEMENT: ["success", "achievement", "celebration", "milestone", "trophy"],
            ContentType.EDUCATIONAL: ["learning", "education", "training", "development", "knowledge"],
            ContentType.PROMOTIONAL: ["marketing", "promotion", "brand", "advertising", "campaign"],
            ContentType.INSPIRATIONAL: ["inspiration", "motivation", "aspiration", "dreams", "goals"]
        }
        
        base_terms.extend(content_terms.get(request.content_type, ["business", "professional"]))
        
        # Platform specific terms
        if request.platform in [PlatformType.LINKEDIN_POST, PlatformType.LINKEDIN_BANNER]:
            base_terms.extend(["linkedin", "professional", "networking", "corporate"])
        elif request.platform in [PlatformType.INSTAGRAM_POST, PlatformType.INSTAGRAM_STORY]:
            base_terms.extend(["modern", "stylish", "visual", "aesthetic"])
        
        # Industry specific terms
        base_terms.extend(["consulting", "business transformation", "Gulf region", "professional services"])
        
        # Quality and style terms
        if request.quality_level in [QualityLevel.PREMIUM, QualityLevel.EXECUTIVE]:
            base_terms.extend(["premium", "luxury", "elegant", "sophisticated"])
        
        return base_terms[:10]  # Limit to top 10 terms
    
    def _get_orientation_for_platform(self, platform: PlatformType) -> Orientation:
        """Get preferred orientation for platform."""
        orientation_mapping = {
            PlatformType.INSTAGRAM_STORY: Orientation.VERTICAL,
            PlatformType.TWITTER_POST: Orientation.HORIZONTAL,
            PlatformType.FACEBOOK_COVER: Orientation.HORIZONTAL,
            PlatformType.LINKEDIN_BANNER: Orientation.HORIZONTAL
        }
        
        return orientation_mapping.get(platform, Orientation.SQUARE)
    
    async def _is_brand_appropriate_image(
        self, 
        resource: FreepikResource, 
        request: ContentRequest
    ) -> bool:
        """Check if image is appropriate for BYMB brand."""
        # Check tags for inappropriate content
        inappropriate_tags = [
            "cartoon", "childish", "comic", "funny", "casual", "messy",
            "unprofessional", "amateur", "low-quality", "grainy"
        ]
        
        resource_tags = [tag.lower() for tag in resource.tags]
        
        if any(tag in resource_tags for tag in inappropriate_tags):
            return False
        
        # Check for professional/business relevance
        professional_tags = [
            "business", "professional", "corporate", "executive", "office",
            "meeting", "strategy", "success", "growth", "consulting",
            "leadership", "professional", "elegant", "modern", "clean"
        ]
        
        professional_match = sum(1 for tag in professional_tags if tag in resource_tags)
        
        # Require at least some professional relevance
        if professional_match < 1:
            return False
        
        # Check image quality requirements
        if request.quality_level in [QualityLevel.PREMIUM, QualityLevel.EXECUTIVE]:
            if resource.width < 1080 or resource.height < 1080:
                return False
        
        return True
    
    async def _select_best_freepik_image(
        self, 
        resources: List[FreepikResource], 
        request: ContentRequest
    ) -> FreepikResource:
        """Select the best Freepik image for branding."""
        if len(resources) == 1:
            return resources[0]
        
        # Score resources
        scored_resources = []
        
        for resource in resources:
            score = 0.0
            
            # Image quality score (dimensions, etc.)
            quality_score = min(resource.width / 1080, 1.0) * min(resource.height / 1080, 1.0)
            score += quality_score * 0.3
            
            # Professional relevance score
            professional_tags = [
                "business", "professional", "corporate", "executive", 
                "consulting", "strategy", "success", "leadership"
            ]
            resource_tags = [tag.lower() for tag in resource.tags]
            relevance_score = sum(1 for tag in professional_tags if tag in resource_tags) / len(professional_tags)
            score += relevance_score * 0.4
            
            # Brand color compatibility (simplified)
            # This would be more sophisticated in a real implementation
            brand_friendly_colors = ["blue", "gold", "white", "gray", "teal"]
            color_tags = [tag for tag in resource_tags if any(color in tag for color in brand_friendly_colors)]
            color_score = len(color_tags) * 0.1
            score += color_score * 0.3
            
            scored_resources.append((resource, score))
        
        # Return highest scoring resource
        scored_resources.sort(key=lambda x: x[1], reverse=True)
        return scored_resources[0][0]
    
    async def _download_and_prepare_image(
        self, 
        resource: FreepikResource, 
        content_id: str
    ) -> DownloadResult:
        """Download and prepare Freepik image."""
        if not self.freepik_client:
            return DownloadResult(
                success=False,
                file_path=None,
                file_size=None,
                download_url=None,
                error_message="Freepik client not configured",
                metadata={}
            )
        
        # Prepare download path
        download_path = self.output_directory / "freepik" / f"{content_id}_{resource.id}.jpg"
        download_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download image
        try:
            download_result = await self.freepik_client.download_resource(
                resource.id, str(download_path)
            )
            
            if download_result.success:
                logger.info(f"Downloaded Freepik image: {resource.id}")
            
            return download_result
            
        except Exception as e:
            logger.error(f"Failed to download Freepik image {resource.id}: {e}")
            return DownloadResult(
                success=False,
                file_path=None,
                file_size=None,
                download_url=None,
                error_message=str(e),
                metadata={}
            )
    
    async def _apply_brand_enhancements(
        self, 
        image_path: str, 
        request: ContentRequest
    ) -> Optional[bytes]:
        """Apply BYMB brand enhancements to image."""
        try:
            # Load image
            image = Image.open(image_path).convert("RGBA")
            
            # Get platform dimensions
            platform_specs = self.brand.get_platform_specs(request.platform)
            if platform_specs and request.custom_dimensions:
                target_dimensions = request.custom_dimensions
            elif platform_specs and "square" in platform_specs.dimensions:
                target_dimensions = platform_specs.dimensions["square"]
            else:
                target_dimensions = (1080, 1080)  # Default
            
            # Resize image
            image = image.resize(target_dimensions, Image.Resampling.LANCZOS)
            
            # Create overlay for brand elements
            overlay = Image.new("RGBA", target_dimensions, (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)
            
            # Add brand color overlay if needed
            if request.color_scheme == "primary":
                # Add subtle brand color overlay
                overlay_color = (*self.brand.primary_colors[0].rgb, 30)  # Very transparent
                draw.rectangle([0, 0, target_dimensions[0], target_dimensions[1]], fill=overlay_color)
            
            # Add logo if requested
            if request.include_logo:
                await self._add_logo_to_image(overlay, target_dimensions, request)
            
            # Add text overlay with brand styling
            await self._add_text_overlay(overlay, request.text_content, target_dimensions, request)
            
            # Composite the images
            final_image = Image.alpha_composite(image, overlay)
            
            # Convert to RGB for JPEG output
            final_image = final_image.convert("RGB")
            
            # Apply quality enhancements based on quality level
            if request.quality_level in [QualityLevel.PREMIUM, QualityLevel.EXECUTIVE]:
                final_image = final_image.filter(ImageFilter.SHARPEN)
                enhancer = ImageEnhance.Contrast(final_image)
                final_image = enhancer.enhance(1.1)
            
            # Convert to bytes
            buffer = io.BytesIO()
            final_image.save(buffer, format='PNG', quality=95)
            return buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to apply brand enhancements: {e}")
            return None
    
    async def _add_logo_to_image(
        self, 
        overlay: Image.Image, 
        dimensions: Tuple[int, int], 
        request: ContentRequest
    ):
        """Add BYMB logo to image overlay."""
        # This would load and composite the actual logo
        # For now, create a placeholder
        draw = ImageDraw.Draw(overlay)
        
        logo_width, logo_height = 120, 45
        logo_x, logo_y = 50, 50
        
        # Draw logo background
        logo_bg_color = (*self.brand.primary_colors[0].rgb, 180)  # Semi-transparent
        draw.rectangle([
            logo_x - 10, logo_y - 5,
            logo_x + logo_width + 10, logo_y + logo_height + 5
        ], fill=logo_bg_color)
        
        # Add logo text (simplified)
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        draw.text((logo_x, logo_y), "BYMB", fill=self.brand.primary_colors[1].hex, font=font)
    
    async def _add_text_overlay(
        self, 
        overlay: Image.Image, 
        text: str, 
        dimensions: Tuple[int, int], 
        request: ContentRequest
    ):
        """Add branded text overlay to image."""
        if len(text) > 150:  # Don't overlay very long text
            return
        
        draw = ImageDraw.Draw(overlay)
        
        # Position text in bottom area
        text_area_height = dimensions[1] // 3
        text_y = dimensions[1] - text_area_height - 50
        
        # Create text background
        bg_color = (*self.brand.primary_colors[0].rgb, 150)  # Semi-transparent
        draw.rectangle([
            0, text_y - 20,
            dimensions[0], dimensions[1]
        ], fill=bg_color)
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 18)
        except:
            font = ImageFont.load_default()
        
        # Simple text wrapping
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] <= dimensions[0] - 100:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw text lines
        line_height = 25
        for i, line in enumerate(lines[:4]):  # Max 4 lines
            draw.text((
                50, text_y + i * line_height
            ), line, fill="#FFFFFF", font=font)
    
    async def _validate_freepik_enhanced_content(
        self, 
        image_data: bytes, 
        request: ContentRequest
    ) -> Optional[ValidationResult]:
        """Validate Freepik-enhanced content for brand compliance."""
        try:
            # Prepare content analysis
            text_content = request.text_content
            
            # Analyze the generated image (simplified)
            visual_elements = {
                "dimensions": {"width": 1080, "height": 1080},  # Would be extracted from actual image
                "colors": [
                    {"hex": self.brand.primary_colors[0].hex, "name": "Primary"},
                    {"hex": "#FFFFFF", "name": "White"}
                ],
                "typography": {
                    "fonts_used": [{"family": "Arial"}],  # Would be detected
                    "min_font_size": 18,
                    "hierarchy_respected": True
                },
                "logo": {
                    "present": request.include_logo,
                    "size": {"width": 120, "height": 45},
                    "placement": "top-left"
                },
                "layout": {
                    "margins": {"top": 50, "bottom": 50, "left": 50, "right": 50},
                    "safe_zones_respected": True
                },
                "contrast": {"min_ratio": 4.5},
                "alt_text": f"BYMB branded {request.content_type.value} content"
            }
            
            content_analysis = ContentAnalysis(
                text_content=text_content,
                visual_elements=visual_elements,
                platform_specs={},
                metadata={"generation_method": "freepik_enhanced"}
            )
            
            return await self.validator.validate_content(
                content_analysis, request.platform, request.content_type
            )
            
        except Exception as e:
            logger.error(f"Validation of Freepik content failed: {e}")
            return None
    
    def _calculate_quality_score(
        self, 
        validation_result: Optional[ValidationResult], 
        quality_level: QualityLevel
    ) -> float:
        """Calculate quality score for template-based content."""
        base_score = 0.7  # Default score
        
        if validation_result:
            base_score = validation_result.overall_score
        
        # Apply quality level bonus
        quality_bonus = {
            QualityLevel.DRAFT: 0.0,
            QualityLevel.STANDARD: 0.1,
            QualityLevel.PREMIUM: 0.15,
            QualityLevel.EXECUTIVE: 0.2
        }
        
        return min(base_score + quality_bonus[quality_level], 1.0)
    
    def _calculate_freepik_quality_score(
        self, 
        resource: FreepikResource, 
        validation_result: Optional[ValidationResult], 
        quality_level: QualityLevel
    ) -> float:
        """Calculate quality score for Freepik-enhanced content."""
        # Base score from brand validation
        brand_score = validation_result.overall_score if validation_result else 0.7
        
        # Image quality score
        image_score = min(resource.width / 1080, 1.0) * min(resource.height / 1080, 1.0)
        
        # Combined score
        combined_score = (brand_score * 0.7) + (image_score * 0.3)
        
        # Quality level adjustment
        quality_multipliers = {
            QualityLevel.DRAFT: 0.9,
            QualityLevel.STANDARD: 1.0,
            QualityLevel.PREMIUM: 1.1,
            QualityLevel.EXECUTIVE: 1.2
        }
        
        return min(combined_score * quality_multipliers[quality_level], 1.0)
    
    async def _enforce_brand_compliance(
        self, 
        result: BrandedContentResult, 
        request: ContentRequest
    ) -> Optional[EnforcementResult]:
        """Enforce brand compliance on generated content."""
        if not result.primary_image:
            return None
        
        try:
            # Prepare content for enforcement
            content = {
                "text": request.text_content,
                "visual_elements": {
                    "dimensions": {"width": 1080, "height": 1080},  # Would be extracted
                    "colors": [{"hex": self.brand.primary_colors[0].hex}],
                    "typography": {"fonts_used": [{"family": "Arial"}]},
                    "logo": {"present": request.include_logo}
                },
                "platform_specs": {},
                "metadata": {"content_id": result.content_id}
            }
            
            return await self.enforcer.enforce_brand_compliance(
                content, request.platform, request.content_type
            )
            
        except Exception as e:
            logger.error(f"Brand enforcement failed: {e}")
            return None
    
    async def _generate_variations(
        self, 
        base_result: BrandedContentResult, 
        request: ContentRequest
    ) -> List[bytes]:
        """Generate variations of the base content."""
        variations = []
        
        try:
            for i in range(min(request.variation_count, 5)):  # Max 5 variations
                # Create slight variations in the content
                variation_request = ContentRequest(
                    text_content=request.text_content,
                    platform=request.platform,
                    content_type=request.content_type,
                    quality_level=request.quality_level,
                    creation_mode=request.creation_mode,
                    brand_tone=request.brand_tone,
                    visual_style=request.visual_style,
                    color_scheme="secondary" if i % 2 == 0 else request.color_scheme,
                    include_logo=request.include_logo,
                    template_id=request.template_id,
                    user_id=request.user_id
                )
                
                # Generate variation (simplified - would use different approaches)
                if base_result.primary_image:
                    # For now, just return the base image with slight modifications
                    # In a real implementation, this would create actual variations
                    variations.append(base_result.primary_image)
        
        except Exception as e:
            logger.error(f"Failed to generate variations: {e}")
        
        return variations
    
    async def _save_output_files(
        self, 
        result: BrandedContentResult, 
        request: ContentRequest
    ):
        """Save generated content to output files."""
        try:
            output_files = {}
            
            for format_type in request.output_formats:
                filename = f"{result.content_id}_{request.platform.value}.{format_type.lower()}"
                file_path = self.output_directory / filename
                
                if format_type.upper() == "PNG" and result.primary_image:
                    with open(file_path, "wb") as f:
                        f.write(result.primary_image)
                    output_files[format_type] = str(file_path)
                
                elif format_type.upper() == "JPG" and result.primary_image:
                    # Convert PNG to JPG
                    image = Image.open(io.BytesIO(result.primary_image))
                    if image.mode in ('RGBA', 'LA', 'P'):
                        # Convert to RGB for JPEG
                        rgb_image = Image.new('RGB', image.size, (255, 255, 255))
                        if image.mode == 'P':
                            image = image.convert('RGBA')
                        rgb_image.paste(image, mask=image.split()[-1])
                        image = rgb_image
                    
                    image.save(file_path, "JPEG", quality=95)
                    output_files[format_type] = str(file_path)
            
            result.output_files = output_files
            
        except Exception as e:
            logger.error(f"Failed to save output files: {e}")
            result.warnings.append(f"Could not save some output files: {str(e)}")
    
    async def get_generation_statistics(self) -> Dict[str, Any]:
        """Get content generation statistics."""
        return {
            **self.generation_stats,
            "statistics_timestamp": datetime.now().isoformat(),
            "output_directory": str(self.output_directory),
            "services_status": {
                "freepik_client": self.freepik_client is not None,
                "template_engine": self.template_engine is not None,
                "validator": self.validator is not None,
                "enforcer": self.enforcer is not None
            }
        }
    
    async def batch_generate_content(
        self, 
        requests: List[ContentRequest]
    ) -> List[BrandedContentResult]:
        """Generate multiple branded content items in batch."""
        results = []
        
        batch_start = datetime.now()
        logger.info(f"Starting batch generation of {len(requests)} items")
        
        for i, request in enumerate(requests):
            try:
                result = await self.generate_branded_content(request)
                results.append(result)
                
                if i % 5 == 0:  # Log progress every 5 items
                    logger.info(f"Batch progress: {i+1}/{len(requests)} completed")
                    
            except Exception as e:
                logger.error(f"Batch item {i} failed: {e}")
                results.append(BrandedContentResult(
                    success=False,
                    content_id=str(uuid.uuid4()),
                    errors=[f"Batch generation failed: {str(e)}"]
                ))
        
        batch_duration = (datetime.now() - batch_start).total_seconds()
        successful_count = len([r for r in results if r.success])
        
        logger.info(
            f"Batch generation completed: {successful_count}/{len(requests)} successful, "
            f"Duration: {batch_duration:.1f}s"
        )
        
        return results
    
    def cleanup_old_files(self, days_old: int = 7):
        """Clean up old generated content files."""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            
            cleaned_count = 0
            for file_path in self.output_directory.rglob("*"):
                if file_path.is_file() and file_path.stat().st_mtime < cutoff_time:
                    file_path.unlink()
                    cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} old files (older than {days_old} days)")
            
        except Exception as e:
            logger.error(f"Failed to clean up old files: {e}")


# Global branded content service instance  
branded_content_service = BrandedContentService()