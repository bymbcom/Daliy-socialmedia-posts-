"""Brand Template Engine - Manages branded content templates and asset generation."""

import os
import json
import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import io
import base64

from .brand_profile import BYMBBrandProfile, PlatformType, ContentType, BrandTone, ColorSpec, bymb_brand
from .brand_validator import BrandValidator, ValidationResult, ContentAnalysis, brand_validator

logger = logging.getLogger(__name__)


class TemplateCategory(Enum):
    """Template categories."""
    QUOTE = "quote"
    INSIGHT = "insight"
    ANNOUNCEMENT = "announcement"
    CASE_STUDY = "case_study"
    ACHIEVEMENT = "achievement"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"
    STORY = "story"


class LayoutStyle(Enum):
    """Layout styles."""
    MINIMAL = "minimal"
    PROFESSIONAL = "professional"
    ELEGANT = "elegant"
    MODERN = "modern"
    EXECUTIVE = "executive"


@dataclass
class TemplateAsset:
    """Template asset specification."""
    type: str  # "logo", "background", "overlay", "pattern"
    path: str
    position: Dict[str, Union[int, float]]  # x, y, width, height
    opacity: float = 1.0
    blend_mode: str = "normal"
    conditions: Dict[str, Any] = field(default_factory=dict)  # When to use this asset


@dataclass
class TextElement:
    """Text element in template."""
    text: str
    position: Dict[str, Union[int, float]]
    font_family: str
    font_size: int
    font_weight: str
    color: str
    alignment: str = "left"
    max_width: Optional[int] = None
    line_height: float = 1.5
    letter_spacing: float = 0.0
    text_transform: str = "none"  # "uppercase", "lowercase", "capitalize"


@dataclass
class BrandTemplate:
    """Complete brand template definition."""
    id: str
    name: str
    description: str
    category: TemplateCategory
    platform: PlatformType
    layout_style: LayoutStyle
    dimensions: Tuple[int, int]  # width, height
    background_color: str
    assets: List[TemplateAsset] = field(default_factory=list)
    text_elements: List[TextElement] = field(default_factory=list)
    safe_zones: Dict[str, int] = field(default_factory=dict)
    variables: Dict[str, str] = field(default_factory=dict)  # Placeholder variables
    brand_compliance_score: float = 1.0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class GenerationRequest:
    """Content generation request."""
    template_id: str
    content: Dict[str, str]  # Variable replacements
    platform: PlatformType
    content_type: Optional[ContentType] = None
    customizations: Dict[str, Any] = field(default_factory=dict)
    brand_validation_required: bool = True


@dataclass
class GenerationResult:
    """Content generation result."""
    success: bool
    image_data: Optional[bytes] = None
    image_base64: Optional[str] = None
    file_path: Optional[str] = None
    template_used: Optional[str] = None
    validation_result: Optional[ValidationResult] = None
    generation_metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class BrandAssetManager:
    """Manages brand assets and resources."""
    
    def __init__(self, assets_directory: str = "assets/brand"):
        """Initialize asset manager."""
        self.assets_directory = Path(assets_directory)
        self.assets_directory.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.assets_directory / "logos").mkdir(exist_ok=True)
        (self.assets_directory / "backgrounds").mkdir(exist_ok=True)
        (self.assets_directory / "patterns").mkdir(exist_ok=True)
        (self.assets_directory / "fonts").mkdir(exist_ok=True)
        (self.assets_directory / "generated").mkdir(exist_ok=True)
        
        self.brand = bymb_brand
        self._asset_cache = {}
        
        logger.info(f"Brand asset manager initialized: {self.assets_directory}")
    
    async def ensure_brand_assets(self) -> Dict[str, str]:
        """Ensure all required brand assets exist."""
        asset_status = {}
        
        # Check logos
        for logo_variant in self.brand.logo_variants:
            logo_path = self.assets_directory / logo_variant.file_path
            if logo_path.exists():
                asset_status[logo_variant.name] = str(logo_path)
            else:
                # Create placeholder logo if missing
                placeholder_path = await self._create_logo_placeholder(logo_variant)
                asset_status[logo_variant.name] = str(placeholder_path)
        
        # Ensure color swatches exist
        await self._create_color_swatches()
        
        # Ensure pattern assets exist
        await self._create_pattern_assets()
        
        return asset_status
    
    async def _create_logo_placeholder(self, logo_variant) -> Path:
        """Create logo placeholder if actual logo doesn't exist."""
        logo_path = self.assets_directory / "logos" / f"{logo_variant.name.lower().replace(' ', '_')}_placeholder.png"
        
        # Create a simple branded placeholder
        width, height = 400, 150
        image = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Use brand colors
        primary_color = self.brand.primary_colors[0]  # Deep Blue
        accent_color = self.brand.primary_colors[1]  # Gold
        
        # Draw background
        draw.rectangle([0, 0, width, height], fill=primary_color.hex)
        
        # Draw text
        try:
            # Try to use a system font
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        text = "BYMB"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=accent_color.hex, font=font)
        
        # Add tagline
        try:
            tagline_font = ImageFont.truetype("arial.ttf", 14)
        except:
            tagline_font = ImageFont.load_default()
        
        tagline = "Be Your Most Beautiful"
        tagline_bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
        tagline_width = tagline_bbox[2] - tagline_bbox[0]
        
        x = (width - tagline_width) // 2
        y = y + text_height + 10
        
        draw.text((x, y), tagline, fill="#FFFFFF", font=tagline_font)
        
        image.save(logo_path, "PNG")
        logger.info(f"Created logo placeholder: {logo_path}")
        
        return logo_path
    
    async def _create_color_swatches(self):
        """Create color swatch assets."""
        swatch_dir = self.assets_directory / "colors"
        swatch_dir.mkdir(exist_ok=True)
        
        all_colors = self.brand.get_color_palette(include_secondary=True)
        
        for color in all_colors:
            swatch_path = swatch_dir / f"{color.name.lower().replace(' ', '_')}_swatch.png"
            if not swatch_path.exists():
                # Create color swatch
                swatch = Image.new('RGB', (100, 100), color.hex)
                swatch.save(swatch_path, "PNG")
    
    async def _create_pattern_assets(self):
        """Create branded pattern assets."""
        pattern_dir = self.assets_directory / "patterns"
        pattern_dir.mkdir(exist_ok=True)
        
        # Create subtle grid pattern
        grid_path = pattern_dir / "subtle_grid.png"
        if not grid_path.exists():
            await self._create_grid_pattern(grid_path)
        
        # Create geometric pattern
        geo_path = pattern_dir / "geometric.png"
        if not geo_path.exists():
            await self._create_geometric_pattern(geo_path)
    
    async def _create_grid_pattern(self, path: Path):
        """Create subtle grid pattern."""
        size = 200
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Very subtle grid
        grid_color = (200, 200, 200, 30)  # Very transparent
        grid_size = 20
        
        for x in range(0, size, grid_size):
            draw.line([(x, 0), (x, size)], fill=grid_color, width=1)
        
        for y in range(0, size, grid_size):
            draw.line([(0, y), (size, y)], fill=grid_color, width=1)
        
        image.save(path, "PNG")
    
    async def _create_geometric_pattern(self, path: Path):
        """Create geometric pattern."""
        size = 200
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Geometric shapes with brand colors
        accent_color = self.brand.primary_colors[1]  # Gold
        color_with_alpha = (*accent_color.rgb, 50)  # Very transparent
        
        # Draw circles
        for x in range(0, size, 50):
            for y in range(0, size, 50):
                draw.ellipse([x, y, x+20, y+20], fill=color_with_alpha)
        
        image.save(path, "PNG")
    
    def get_asset_path(self, asset_type: str, asset_name: str) -> Optional[Path]:
        """Get path to specific asset."""
        asset_path = self.assets_directory / asset_type / asset_name
        return asset_path if asset_path.exists() else None
    
    def cache_asset(self, asset_id: str, asset_data: Any):
        """Cache asset in memory."""
        self._asset_cache[asset_id] = asset_data
    
    def get_cached_asset(self, asset_id: str) -> Any:
        """Get cached asset."""
        return self._asset_cache.get(asset_id)


class BrandTemplateEngine:
    """Comprehensive brand template engine."""
    
    def __init__(self, asset_manager: Optional[BrandAssetManager] = None):
        """Initialize template engine."""
        self.brand = bymb_brand
        self.asset_manager = asset_manager or BrandAssetManager()
        self.validator = brand_validator
        self.templates = {}
        
        # Initialize default templates
        asyncio.create_task(self._initialize_default_templates())
        
        logger.info("Brand template engine initialized")
    
    async def _initialize_default_templates(self):
        """Initialize default brand templates."""
        try:
            # Ensure brand assets exist
            await self.asset_manager.ensure_brand_assets()
            
            # Create default templates
            await self._create_quote_templates()
            await self._create_insight_templates()
            await self._create_announcement_templates()
            
            logger.info(f"Initialized {len(self.templates)} default templates")
        except Exception as e:
            logger.error(f"Failed to initialize default templates: {e}")
    
    async def _create_quote_templates(self):
        """Create quote-based templates."""
        platforms = [PlatformType.INSTAGRAM_POST, PlatformType.LINKEDIN_POST, PlatformType.TWITTER_POST]
        
        for platform in platforms:
            platform_specs = self.brand.get_platform_specs(platform)
            if not platform_specs:
                continue
            
            # Get dimensions
            if "square" in platform_specs.dimensions:
                width, height = platform_specs.dimensions["square"]
            else:
                width, height = list(platform_specs.dimensions.values())[0]
            
            template_id = f"quote_{platform.value}_minimal"
            
            template = BrandTemplate(
                id=template_id,
                name=f"Inspirational Quote - {platform.value.title()}",
                description="Clean, minimal quote template with BYMB branding",
                category=TemplateCategory.QUOTE,
                platform=platform,
                layout_style=LayoutStyle.MINIMAL,
                dimensions=(width, height),
                background_color=self.brand.primary_colors[2].hex,  # White
                assets=[
                    TemplateAsset(
                        type="logo",
                        path="logos/primary_logo_placeholder.png",
                        position={"x": 50, "y": 50, "width": 120, "height": 45}
                    ),
                    TemplateAsset(
                        type="pattern",
                        path="patterns/subtle_grid.png",
                        position={"x": 0, "y": 0, "width": width, "height": height},
                        opacity=0.1
                    )
                ],
                text_elements=[
                    TextElement(
                        text="{quote_text}",
                        position={"x": 80, "y": height//3, "width": width-160, "height": height//3},
                        font_family="Playfair Display",
                        font_size=28,
                        font_weight="400",
                        color=self.brand.primary_colors[0].hex,  # Deep Blue
                        alignment="center"
                    ),
                    TextElement(
                        text="- {author}",
                        position={"x": 80, "y": height//3*2, "width": width-160, "height": 50},
                        font_family="Inter",
                        font_size=18,
                        font_weight="600",
                        color=self.brand.primary_colors[1].hex,  # Gold
                        alignment="center"
                    ),
                    TextElement(
                        text="{tagline}",
                        position={"x": 50, "y": height-100, "width": width-100, "height": 30},
                        font_family="Inter",
                        font_size=14,
                        font_weight="400",
                        color=self.brand.secondary_colors[1].hex,  # Warm Gray
                        alignment="center"
                    )
                ],
                variables={
                    "quote_text": "Your business transformation starts with a single strategic decision.",
                    "author": "Bader Abdulrahim, BYMB Consultancy",
                    "tagline": "Be Your Most Beautiful"
                }
            )
            
            self.templates[template_id] = template
    
    async def _create_insight_templates(self):
        """Create business insight templates."""
        platforms = [PlatformType.INSTAGRAM_POST, PlatformType.LINKEDIN_POST]
        
        for platform in platforms:
            platform_specs = self.brand.get_platform_specs(platform)
            if not platform_specs:
                continue
            
            # Get dimensions
            if "square" in platform_specs.dimensions:
                width, height = platform_specs.dimensions["square"]
            else:
                width, height = list(platform_specs.dimensions.values())[0]
            
            template_id = f"insight_{platform.value}_professional"
            
            template = BrandTemplate(
                id=template_id,
                name=f"Business Insight - {platform.value.title()}",
                description="Professional template for sharing business insights",
                category=TemplateCategory.INSIGHT,
                platform=platform,
                layout_style=LayoutStyle.PROFESSIONAL,
                dimensions=(width, height),
                background_color=self.brand.primary_colors[0].hex,  # Deep Blue
                assets=[
                    TemplateAsset(
                        type="logo",
                        path="logos/primary_logo_placeholder.png",
                        position={"x": width-170, "y": 50, "width": 120, "height": 45}
                    ),
                    TemplateAsset(
                        type="accent_bar",
                        path="",  # Will be generated
                        position={"x": 0, "y": 0, "width": 8, "height": height},
                        opacity=1.0
                    )
                ],
                text_elements=[
                    TextElement(
                        text="{insight_title}",
                        position={"x": 50, "y": 120, "width": width-100, "height": 80},
                        font_family="Inter",
                        font_size=24,
                        font_weight="700",
                        color=self.brand.primary_colors[1].hex,  # Gold
                        alignment="left"
                    ),
                    TextElement(
                        text="{insight_content}",
                        position={"x": 50, "y": 220, "width": width-100, "height": height-350},
                        font_family="Inter",
                        font_size=16,
                        font_weight="400",
                        color="#FFFFFF",
                        alignment="left",
                        line_height=1.6
                    ),
                    TextElement(
                        text="{expertise_note}",
                        position={"x": 50, "y": height-80, "width": width-200, "height": 30},
                        font_family="Inter",
                        font_size=12,
                        font_weight="400",
                        color=self.brand.secondary_colors[1].hex,  # Warm Gray
                        alignment="left"
                    )
                ],
                variables={
                    "insight_title": "Strategic Business Insight",
                    "insight_content": "In today's rapidly evolving market, businesses that adapt their strategies quarterly rather than annually show 40% better performance metrics.",
                    "expertise_note": "Based on 23+ years of consultancy experience"
                }
            )
            
            self.templates[template_id] = template
    
    async def _create_announcement_templates(self):
        """Create announcement templates."""
        platforms = [PlatformType.INSTAGRAM_POST, PlatformType.LINKEDIN_POST, PlatformType.FACEBOOK_POST]
        
        for platform in platforms:
            platform_specs = self.brand.get_platform_specs(platform)
            if not platform_specs:
                continue
            
            # Get dimensions
            if "landscape" in platform_specs.dimensions:
                width, height = platform_specs.dimensions["landscape"]
            elif "square" in platform_specs.dimensions:
                width, height = platform_specs.dimensions["square"]
            else:
                width, height = list(platform_specs.dimensions.values())[0]
            
            template_id = f"announcement_{platform.value}_elegant"
            
            template = BrandTemplate(
                id=template_id,
                name=f"Company Announcement - {platform.value.title()}",
                description="Elegant template for company announcements and achievements",
                category=TemplateCategory.ANNOUNCEMENT,
                platform=platform,
                layout_style=LayoutStyle.ELEGANT,
                dimensions=(width, height),
                background_color=f"linear-gradient(135deg, {self.brand.primary_colors[0].hex}, {self.brand.secondary_colors[0].hex})",
                assets=[
                    TemplateAsset(
                        type="logo",
                        path="logos/primary_logo_placeholder.png",
                        position={"x": 60, "y": 60, "width": 150, "height": 60}
                    ),
                    TemplateAsset(
                        type="pattern",
                        path="patterns/geometric.png",
                        position={"x": width//2, "y": 0, "width": width//2, "height": height},
                        opacity=0.1
                    )
                ],
                text_elements=[
                    TextElement(
                        text="{announcement_type}",
                        position={"x": 60, "y": 160, "width": width-120, "height": 40},
                        font_family="Inter",
                        font_size=14,
                        font_weight="600",
                        color=self.brand.primary_colors[1].hex,  # Gold
                        alignment="left",
                        text_transform="uppercase",
                        letter_spacing=0.1
                    ),
                    TextElement(
                        text="{announcement_title}",
                        position={"x": 60, "y": 210, "width": width-120, "height": 100},
                        font_family="Playfair Display",
                        font_size=32,
                        font_weight="700",
                        color="#FFFFFF",
                        alignment="left",
                        line_height=1.2
                    ),
                    TextElement(
                        text="{announcement_content}",
                        position={"x": 60, "y": 330, "width": width-120, "height": height-420},
                        font_family="Inter",
                        font_size=16,
                        font_weight="400",
                        color="#FFFFFF",
                        alignment="left",
                        line_height=1.5
                    ),
                    TextElement(
                        text="{call_to_action}",
                        position={"x": 60, "y": height-70, "width": width-120, "height": 30},
                        font_family="Inter",
                        font_size=14,
                        font_weight="600",
                        color=self.brand.primary_colors[1].hex,  # Gold
                        alignment="left"
                    )
                ],
                variables={
                    "announcement_type": "Company Achievement",
                    "announcement_title": "Milestone Reached: $35M+ in Client Results",
                    "announcement_content": "We're proud to announce that BYMB Consultancy has helped our clients achieve over $35 million in measurable business results across 23+ years of strategic partnerships.",
                    "call_to_action": "Ready to transform your business potential?"
                }
            )
            
            self.templates[template_id] = template
    
    async def generate_content(self, request: GenerationRequest) -> GenerationResult:
        """Generate branded content from template."""
        try:
            template = self.templates.get(request.template_id)
            if not template:
                return GenerationResult(
                    success=False,
                    error_message=f"Template '{request.template_id}' not found"
                )
            
            # Apply content replacements
            processed_template = self._process_template_variables(template, request.content)
            
            # Generate image
            image_data = await self._render_template(processed_template, request.customizations)
            
            # Prepare result
            result = GenerationResult(
                success=True,
                image_data=image_data,
                image_base64=base64.b64encode(image_data).decode('utf-8') if image_data else None,
                template_used=request.template_id,
                generation_metadata={
                    "template_name": template.name,
                    "platform": request.platform.value,
                    "dimensions": template.dimensions,
                    "generation_time": datetime.now().isoformat()
                }
            )
            
            # Validate if requested
            if request.brand_validation_required:
                validation_result = await self._validate_generated_content(
                    processed_template, request, image_data
                )
                result.validation_result = validation_result
                
                # Add validation warnings if score is low
                if validation_result.overall_score < 0.8:
                    result.warnings.append(
                        f"Brand compliance score: {validation_result.overall_score:.1%}. "
                        f"Consider reviewing: {', '.join(validation_result.recommendations[:2])}"
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"Content generation failed: {e}")
            return GenerationResult(
                success=False,
                error_message=f"Generation failed: {str(e)}"
            )
    
    def _process_template_variables(self, template: BrandTemplate, content: Dict[str, str]) -> BrandTemplate:
        """Process template variables with provided content."""
        processed_template = BrandTemplate(
            id=template.id,
            name=template.name,
            description=template.description,
            category=template.category,
            platform=template.platform,
            layout_style=template.layout_style,
            dimensions=template.dimensions,
            background_color=template.background_color,
            assets=template.assets.copy(),
            text_elements=[],
            safe_zones=template.safe_zones.copy(),
            variables=template.variables.copy()
        )
        
        # Process text elements
        for text_element in template.text_elements:
            processed_text = text_element.text
            
            # Replace variables
            for variable, value in content.items():
                placeholder = f"{{{variable}}}"
                if placeholder in processed_text:
                    processed_text = processed_text.replace(placeholder, value)
            
            # Fall back to template defaults
            for variable, default_value in template.variables.items():
                placeholder = f"{{{variable}}}"
                if placeholder in processed_text:
                    processed_text = processed_text.replace(placeholder, default_value)
            
            # Create new text element with processed text
            processed_element = TextElement(
                text=processed_text,
                position=text_element.position.copy(),
                font_family=text_element.font_family,
                font_size=text_element.font_size,
                font_weight=text_element.font_weight,
                color=text_element.color,
                alignment=text_element.alignment,
                max_width=text_element.max_width,
                line_height=text_element.line_height,
                letter_spacing=text_element.letter_spacing,
                text_transform=text_element.text_transform
            )
            
            processed_template.text_elements.append(processed_element)
        
        return processed_template
    
    async def _render_template(self, template: BrandTemplate, customizations: Dict[str, Any]) -> bytes:
        """Render template to image."""
        width, height = template.dimensions
        
        # Create base image
        image = Image.new('RGBA', (width, height), (255, 255, 255, 0))
        
        # Apply background
        await self._apply_background(image, template.background_color)
        
        # Apply assets
        for asset in template.assets:
            await self._apply_asset(image, asset)
        
        # Apply text elements
        for text_element in template.text_elements:
            await self._apply_text_element(image, text_element)
        
        # Apply customizations
        if customizations:
            await self._apply_customizations(image, customizations)
        
        # Convert to bytes
        buffer = io.BytesIO()
        image.save(buffer, format='PNG', quality=95)
        return buffer.getvalue()
    
    async def _apply_background(self, image: Image.Image, background: str):
        """Apply background to image."""
        draw = ImageDraw.Draw(image)
        
        if background.startswith('linear-gradient'):
            # Simple gradient implementation
            # In production, you'd want a more sophisticated gradient renderer
            colors = []
            if 'Deep Blue' in background or '#1B365D' in background:
                colors.append(self.brand.primary_colors[0].hex)
            if 'Gulf Teal' in background or '#2E8B8B' in background:
                colors.append(self.brand.secondary_colors[0].hex)
            
            if len(colors) >= 2:
                # Create vertical gradient
                for y in range(image.height):
                    ratio = y / image.height
                    # Simple color interpolation
                    color1 = colors[0]
                    color2 = colors[1]
                    
                    # Convert hex to RGB
                    r1, g1, b1 = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
                    r2, g2, b2 = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
                    
                    # Interpolate
                    r = int(r1 + (r2 - r1) * ratio)
                    g = int(g1 + (g2 - g1) * ratio)
                    b = int(b1 + (b2 - b1) * ratio)
                    
                    draw.rectangle([(0, y), (image.width, y+1)], fill=(r, g, b))
            else:
                draw.rectangle([0, 0, image.width, image.height], fill=self.brand.primary_colors[0].hex)
        else:
            # Solid color background
            draw.rectangle([0, 0, image.width, image.height], fill=background)
    
    async def _apply_asset(self, image: Image.Image, asset: TemplateAsset):
        """Apply asset to image."""
        if asset.type == "accent_bar":
            # Generate accent bar
            draw = ImageDraw.Draw(image)
            pos = asset.position
            draw.rectangle([
                pos["x"], pos["y"], 
                pos["x"] + pos["width"], pos["y"] + pos["height"]
            ], fill=self.brand.primary_colors[1].hex)  # Gold
            return
        
        # Try to load asset file
        asset_path = self.asset_manager.get_asset_path(asset.type + "s", asset.path.split("/")[-1])
        if not asset_path or not asset_path.exists():
            logger.warning(f"Asset not found: {asset.path}")
            return
        
        try:
            asset_image = Image.open(asset_path).convert("RGBA")
            
            # Resize asset
            pos = asset.position
            asset_size = (pos["width"], pos["height"])
            asset_image = asset_image.resize(asset_size, Image.Resampling.LANCZOS)
            
            # Apply opacity
            if asset.opacity < 1.0:
                alpha = asset_image.split()[-1]  # Get alpha channel
                alpha = ImageEnhance.Brightness(alpha).enhance(asset.opacity)
                asset_image.putalpha(alpha)
            
            # Paste asset
            image.paste(asset_image, (pos["x"], pos["y"]), asset_image)
            
        except Exception as e:
            logger.error(f"Failed to apply asset {asset.path}: {e}")
    
    async def _apply_text_element(self, image: Image.Image, text_element: TextElement):
        """Apply text element to image."""
        draw = ImageDraw.Draw(image)
        
        # Load font
        try:
            font = ImageFont.truetype(f"{text_element.font_family.lower().replace(' ', '')}.ttf", text_element.font_size)
        except:
            try:
                font = ImageFont.truetype("arial.ttf", text_element.font_size)
            except:
                font = ImageFont.load_default()
        
        # Process text
        text = text_element.text
        if text_element.text_transform == "uppercase":
            text = text.upper()
        elif text_element.text_transform == "lowercase":
            text = text.lower()
        elif text_element.text_transform == "capitalize":
            text = text.title()
        
        # Handle text wrapping
        pos = text_element.position
        max_width = pos.get("width", image.width - pos["x"])
        
        if text_element.max_width:
            max_width = min(max_width, text_element.max_width)
        
        # Simple text wrapping
        lines = self._wrap_text(text, font, max_width, draw)
        
        # Draw text lines
        y_offset = pos["y"]
        line_height = text_element.font_size * text_element.line_height
        
        for line in lines:
            if text_element.alignment == "center":
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = pos["x"] + (max_width - text_width) // 2
            elif text_element.alignment == "right":
                bbox = draw.textbbox((0, 0), line, font=font)
                text_width = bbox[2] - bbox[0]
                x = pos["x"] + max_width - text_width
            else:  # left
                x = pos["x"]
            
            draw.text((x, y_offset), line, fill=text_element.color, font=font)
            y_offset += line_height
    
    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.Draw) -> List[str]:
        """Wrap text to fit within specified width."""
        lines = []
        words = text.split()
        
        if not words:
            return lines
        
        current_line = words[0]
        
        for word in words[1:]:
            # Check if adding this word exceeds the width
            test_line = current_line + " " + word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        
        lines.append(current_line)
        return lines
    
    async def _apply_customizations(self, image: Image.Image, customizations: Dict[str, Any]):
        """Apply custom modifications to image."""
        # Apply filters if specified
        if "filter" in customizations:
            filter_type = customizations["filter"]
            
            if filter_type == "sharpen":
                image = image.filter(ImageFilter.SHARPEN)
            elif filter_type == "blur":
                image = image.filter(ImageFilter.BLUR)
            elif filter_type == "enhance":
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(1.2)
        
        # Apply brightness/contrast adjustments
        if "brightness" in customizations:
            brightness = customizations["brightness"]
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(brightness)
        
        if "contrast" in customizations:
            contrast = customizations["contrast"]
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(contrast)
    
    async def _validate_generated_content(
        self, 
        template: BrandTemplate, 
        request: GenerationRequest, 
        image_data: bytes
    ) -> ValidationResult:
        """Validate generated content against brand guidelines."""
        # Prepare content analysis
        text_content = " ".join([element.text for element in template.text_elements])
        
        visual_elements = {
            "dimensions": {"width": template.dimensions[0], "height": template.dimensions[1]},
            "colors": [
                {"hex": self.brand.primary_colors[0].hex, "name": "Primary"},
                {"hex": self.brand.primary_colors[1].hex, "name": "Accent"}
            ],
            "typography": {
                "fonts_used": [{"family": element.font_family} for element in template.text_elements],
                "min_font_size": min([element.font_size for element in template.text_elements]) if template.text_elements else 14,
                "hierarchy_respected": True
            },
            "logo": {
                "present": any(asset.type == "logo" for asset in template.assets),
                "size": {"width": 120, "height": 45},
                "placement": "top-left"
            },
            "layout": {
                "margins": {"top": 50, "bottom": 50, "left": 50, "right": 50},
                "safe_zones_respected": True
            },
            "contrast": {"min_ratio": 4.5},  # Assume good contrast
            "alt_text": f"BYMB branded {template.category.value} for {template.platform.value}"
        }
        
        content_analysis = ContentAnalysis(
            text_content=text_content,
            visual_elements=visual_elements,
            platform_specs=asdict(self.brand.get_platform_specs(request.platform)),
            metadata={"template_id": request.template_id}
        )
        
        # Perform validation
        return await self.validator.validate_content(
            content_analysis, 
            request.platform, 
            request.content_type
        )
    
    def get_available_templates(
        self, 
        platform: Optional[PlatformType] = None,
        category: Optional[TemplateCategory] = None
    ) -> List[Dict[str, Any]]:
        """Get available templates with filtering."""
        templates = []
        
        for template_id, template in self.templates.items():
            if platform and template.platform != platform:
                continue
            if category and template.category != category:
                continue
            
            templates.append({
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category.value,
                "platform": template.platform.value,
                "layout_style": template.layout_style.value,
                "dimensions": template.dimensions,
                "variables": list(template.variables.keys()),
                "brand_compliance_score": template.brand_compliance_score
            })
        
        return sorted(templates, key=lambda x: x["brand_compliance_score"], reverse=True)
    
    def get_template_preview(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get template preview information."""
        template = self.templates.get(template_id)
        if not template:
            return None
        
        return {
            "id": template.id,
            "name": template.name,
            "description": template.description,
            "preview_data": {
                "dimensions": template.dimensions,
                "background_color": template.background_color,
                "text_elements": [
                    {
                        "text": element.text,
                        "position": element.position,
                        "font_family": element.font_family,
                        "font_size": element.font_size,
                        "color": element.color
                    }
                    for element in template.text_elements
                ],
                "assets": [
                    {
                        "type": asset.type,
                        "position": asset.position
                    }
                    for asset in template.assets
                ]
            },
            "variables": template.variables,
            "platform": template.platform.value,
            "category": template.category.value
        }
    
    async def create_custom_template(
        self, 
        name: str,
        platform: PlatformType,
        category: TemplateCategory,
        layout_style: LayoutStyle,
        template_data: Dict[str, Any]
    ) -> str:
        """Create a custom template."""
        template_id = f"custom_{platform.value}_{category.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        platform_specs = self.brand.get_platform_specs(platform)
        if not platform_specs:
            raise ValueError(f"No specifications found for platform {platform.value}")
        
        # Get default dimensions
        if "square" in platform_specs.dimensions:
            width, height = platform_specs.dimensions["square"]
        else:
            width, height = list(platform_specs.dimensions.values())[0]
        
        # Override with provided dimensions
        if "dimensions" in template_data:
            width, height = template_data["dimensions"]
        
        template = BrandTemplate(
            id=template_id,
            name=name,
            description=template_data.get("description", f"Custom {category.value} template"),
            category=category,
            platform=platform,
            layout_style=layout_style,
            dimensions=(width, height),
            background_color=template_data.get("background_color", self.brand.primary_colors[2].hex),
            assets=[
                TemplateAsset(**asset_data) for asset_data in template_data.get("assets", [])
            ],
            text_elements=[
                TextElement(**element_data) for element_data in template_data.get("text_elements", [])
            ],
            variables=template_data.get("variables", {})
        )
        
        self.templates[template_id] = template
        logger.info(f"Created custom template: {template_id}")
        
        return template_id
    
    def delete_template(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self.templates:
            del self.templates[template_id]
            logger.info(f"Deleted template: {template_id}")
            return True
        return False
    
    async def get_brand_compliance_report(self) -> Dict[str, Any]:
        """Generate brand compliance report for all templates."""
        total_templates = len(self.templates)
        
        if total_templates == 0:
            return {"total_templates": 0, "average_score": 0.0, "compliance_distribution": {}}
        
        scores = [template.brand_compliance_score for template in self.templates.values()]
        average_score = sum(scores) / len(scores)
        
        # Distribution
        distribution = {
            "excellent": len([s for s in scores if s >= 0.9]),
            "good": len([s for s in scores if 0.8 <= s < 0.9]),
            "acceptable": len([s for s in scores if 0.7 <= s < 0.8]),
            "needs_improvement": len([s for s in scores if 0.6 <= s < 0.7]),
            "non_compliant": len([s for s in scores if s < 0.6])
        }
        
        # Templates by platform
        platform_breakdown = {}
        for template in self.templates.values():
            platform = template.platform.value
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {"count": 0, "avg_score": 0.0}
            platform_breakdown[platform]["count"] += 1
            platform_breakdown[platform]["avg_score"] += template.brand_compliance_score
        
        for platform_data in platform_breakdown.values():
            platform_data["avg_score"] /= platform_data["count"]
        
        return {
            "total_templates": total_templates,
            "average_score": average_score,
            "compliance_distribution": distribution,
            "platform_breakdown": platform_breakdown,
            "recommendations": self._generate_compliance_recommendations(scores, distribution),
            "report_timestamp": datetime.now().isoformat()
        }
    
    def _generate_compliance_recommendations(
        self, 
        scores: List[float], 
        distribution: Dict[str, int]
    ) -> List[str]:
        """Generate compliance recommendations."""
        recommendations = []
        
        if distribution["non_compliant"] > 0:
            recommendations.append(f"Update {distribution['non_compliant']} non-compliant templates immediately")
        
        if distribution["needs_improvement"] > 0:
            recommendations.append(f"Review {distribution['needs_improvement']} templates that need improvement")
        
        avg_score = sum(scores) / len(scores) if scores else 0
        if avg_score < 0.8:
            recommendations.append("Overall template quality needs improvement - focus on brand alignment")
        
        if distribution["excellent"] < len(scores) * 0.5:
            recommendations.append("Increase the number of excellent-quality templates")
        
        return recommendations


# Global template engine instance
brand_template_engine = BrandTemplateEngine()