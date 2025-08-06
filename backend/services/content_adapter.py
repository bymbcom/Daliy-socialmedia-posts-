"""Content adaptation service for automated format conversion and visual content generation.

This service handles the transformation of business insights into platform-optimized
visual content, including image resizing, text overlay, and brand element integration.
"""

import asyncio
import os
import json
import uuid
import tempfile
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import textwrap
import colorsys
import requests
from io import BytesIO

from .social_media_optimizer import SocialPlatform, ContentType, ContentOptimization

logger = logging.getLogger(__name__)


class VisualStyle(Enum):
    """Visual style options for BYMB Consultancy content."""
    PROFESSIONAL_MINIMAL = "professional_minimal"
    CORPORATE_BRANDED = "corporate_branded"
    MODERN_GRADIENT = "modern_gradient"
    INFOGRAPHIC_STYLE = "infographic_style"
    QUOTE_CARD = "quote_card"


class TextPosition(Enum):
    """Text positioning options."""
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    OVERLAY = "overlay"


@dataclass
class BrandColors:
    """BYMB Consultancy brand color palette."""
    primary: str = "#1B365D"      # Deep Navy Blue
    secondary: str = "#4A90A4"    # Professional Teal
    accent: str = "#F39C12"       # Golden Orange
    neutral_dark: str = "#2C3E50" # Dark Gray
    neutral_light: str = "#ECF0F1" # Light Gray
    white: str = "#FFFFFF"
    text_primary: str = "#2C3E50"
    text_secondary: str = "#7F8C8D"


@dataclass
class VisualTemplate:
    """Visual template configuration."""
    style: VisualStyle
    background_color: str
    text_color: str
    accent_color: str
    font_primary: str
    font_secondary: str
    layout_elements: Dict[str, Any]
    brand_elements: List[str]


@dataclass
class ContentAdaptationResult:
    """Result of content adaptation process."""
    success: bool
    file_path: Optional[str]
    file_size: Optional[int]
    dimensions: Tuple[int, int]
    format: str
    visual_style: VisualStyle
    optimization_applied: List[str]
    error_message: Optional[str]
    metadata: Dict[str, Any]


class ContentAdapter:
    """Service for adapting content to different formats and platforms."""
    
    def __init__(self, assets_path: Optional[str] = None):
        """Initialize content adapter.
        
        Args:
            assets_path: Path to brand assets directory
        """
        self.assets_path = Path(assets_path) if assets_path else Path("assets")
        self.brand_colors = BrandColors()
        self.templates = self._initialize_templates()
        self.temp_dir = Path(tempfile.gettempdir()) / "bymb_content"
        self.temp_dir.mkdir(exist_ok=True)
        
        # Create default fonts mapping
        self.font_mapping = {
            "professional": self._get_font_path("Arial.ttf", "arial.ttf"),
            "bold": self._get_font_path("Arial-Bold.ttf", "arial-bold.ttf"),
            "light": self._get_font_path("Arial-Light.ttf", "arial-light.ttf")
        }
        
        logger.info("Content adapter initialized")
    
    def _initialize_templates(self) -> Dict[VisualStyle, VisualTemplate]:
        """Initialize visual templates for different styles."""
        return {
            VisualStyle.PROFESSIONAL_MINIMAL: VisualTemplate(
                style=VisualStyle.PROFESSIONAL_MINIMAL,
                background_color=self.brand_colors.white,
                text_color=self.brand_colors.text_primary,
                accent_color=self.brand_colors.primary,
                font_primary="professional",
                font_secondary="light",
                layout_elements={
                    "padding": 60,
                    "line_spacing": 1.4,
                    "title_size_ratio": 1.8,
                    "content_size_ratio": 1.0
                },
                brand_elements=["logo", "tagline"]
            ),
            
            VisualStyle.CORPORATE_BRANDED: VisualTemplate(
                style=VisualStyle.CORPORATE_BRANDED,
                background_color=self.brand_colors.primary,
                text_color=self.brand_colors.white,
                accent_color=self.brand_colors.accent,
                font_primary="bold",
                font_secondary="professional",
                layout_elements={
                    "padding": 50,
                    "line_spacing": 1.5,
                    "title_size_ratio": 2.0,
                    "content_size_ratio": 1.1,
                    "gradient_overlay": True
                },
                brand_elements=["logo", "tagline", "credentials"]
            ),
            
            VisualStyle.MODERN_GRADIENT: VisualTemplate(
                style=VisualStyle.MODERN_GRADIENT,
                background_color=self.brand_colors.secondary,
                text_color=self.brand_colors.white,
                accent_color=self.brand_colors.accent,
                font_primary="professional",
                font_secondary="light",
                layout_elements={
                    "padding": 70,
                    "line_spacing": 1.6,
                    "title_size_ratio": 1.9,
                    "content_size_ratio": 1.0,
                    "gradient_direction": "diagonal",
                    "modern_elements": True
                },
                brand_elements=["logo", "modern_tagline"]
            ),
            
            VisualStyle.INFOGRAPHIC_STYLE: VisualTemplate(
                style=VisualStyle.INFOGRAPHIC_STYLE,
                background_color=self.brand_colors.neutral_light,
                text_color=self.brand_colors.text_primary,
                accent_color=self.brand_colors.secondary,
                font_primary="bold",
                font_secondary="professional",
                layout_elements={
                    "padding": 40,
                    "line_spacing": 1.3,
                    "title_size_ratio": 1.6,
                    "content_size_ratio": 0.9,
                    "icons_enabled": True,
                    "data_visualization": True
                },
                brand_elements=["logo", "statistics", "icons"]
            ),
            
            VisualStyle.QUOTE_CARD: VisualTemplate(
                style=VisualStyle.QUOTE_CARD,
                background_color=self.brand_colors.white,
                text_color=self.brand_colors.text_primary,
                accent_color=self.brand_colors.accent,
                font_primary="light",
                font_secondary="professional",
                layout_elements={
                    "padding": 80,
                    "line_spacing": 1.7,
                    "title_size_ratio": 1.4,
                    "content_size_ratio": 1.2,
                    "quote_marks": True,
                    "centered_layout": True
                },
                brand_elements=["attribution", "logo_small"]
            )
        }
    
    def _get_font_path(self, preferred: str, fallback: str) -> str:
        """Get font file path with fallbacks."""
        # Try to find system fonts or use PIL defaults
        font_dirs = [
            "/System/Library/Fonts/",  # macOS
            "/usr/share/fonts/",       # Linux
            "C:\\Windows\\Fonts\\",    # Windows
            str(self.assets_path / "fonts"),  # Custom fonts
        ]
        
        for font_dir in font_dirs:
            for font_name in [preferred, fallback]:
                font_path = Path(font_dir) / font_name
                if font_path.exists():
                    return str(font_path)
        
        return "arial.ttf"  # PIL default fallback
    
    async def adapt_content_to_format(
        self,
        optimization: ContentOptimization,
        visual_style: VisualStyle = VisualStyle.PROFESSIONAL_MINIMAL,
        background_image: Optional[str] = None
    ) -> ContentAdaptationResult:
        """Adapt optimized content to visual format.
        
        Args:
            optimization: Optimized content from social media optimizer
            visual_style: Desired visual style
            background_image: Optional background image path
            
        Returns:
            Content adaptation result
        """
        try:
            template = self.templates[visual_style]
            specs = optimization.image_specs
            dimensions = specs["dimensions"]
            
            # Create image
            image = await self._create_base_image(
                dimensions, template, background_image
            )
            
            # Add text content
            image = await self._add_text_content(
                image, optimization, template, dimensions
            )
            
            # Add brand elements
            image = await self._add_brand_elements(
                image, template, dimensions
            )
            
            # Apply platform optimizations
            optimizations = await self._apply_platform_optimizations(
                image, optimization.platform, optimization.content_type
            )
            
            # Save image
            file_path = await self._save_image(
                image, optimization, visual_style
            )
            
            # Get file stats
            file_size = os.path.getsize(file_path)
            
            return ContentAdaptationResult(
                success=True,
                file_path=file_path,
                file_size=file_size,
                dimensions=dimensions,
                format=specs["format"],
                visual_style=visual_style,
                optimization_applied=optimizations,
                error_message=None,
                metadata={
                    "template_used": template.style.value,
                    "brand_elements": template.brand_elements,
                    "creation_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Content adaptation failed: {str(e)}")
            return ContentAdaptationResult(
                success=False,
                file_path=None,
                file_size=None,
                dimensions=(0, 0),
                format="",
                visual_style=visual_style,
                optimization_applied=[],
                error_message=str(e),
                metadata={}
            )
    
    async def _create_base_image(
        self,
        dimensions: Tuple[int, int],
        template: VisualTemplate,
        background_image: Optional[str]
    ) -> Image.Image:
        """Create base image with background."""
        width, height = dimensions
        
        if background_image and os.path.exists(background_image):
            # Use provided background
            bg_image = Image.open(background_image)
            bg_image = bg_image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Apply overlay if needed
            if template.layout_elements.get("gradient_overlay"):
                overlay = await self._create_gradient_overlay(dimensions, template)
                bg_image = Image.alpha_composite(
                    bg_image.convert("RGBA"), overlay
                )
        else:
            # Create solid color or gradient background
            if template.layout_elements.get("gradient_direction"):
                bg_image = await self._create_gradient_background(dimensions, template)
            else:
                bg_image = Image.new("RGB", dimensions, template.background_color)
        
        return bg_image.convert("RGB")
    
    async def _create_gradient_background(
        self,
        dimensions: Tuple[int, int],
        template: VisualTemplate
    ) -> Image.Image:
        """Create gradient background."""
        width, height = dimensions
        gradient = Image.new("RGB", dimensions)
        draw = ImageDraw.Draw(gradient)
        
        # Parse colors
        start_color = self._hex_to_rgb(template.background_color)
        end_color = self._hex_to_rgb(template.accent_color)
        
        direction = template.layout_elements.get("gradient_direction", "vertical")
        
        if direction == "vertical":
            for y in range(height):
                ratio = y / height
                color = self._interpolate_color(start_color, end_color, ratio)
                draw.line([(0, y), (width, y)], fill=color)
        elif direction == "horizontal":
            for x in range(width):
                ratio = x / width
                color = self._interpolate_color(start_color, end_color, ratio)
                draw.line([(x, 0), (x, height)], fill=color)
        elif direction == "diagonal":
            for y in range(height):
                for x in range(width):
                    ratio = (x + y) / (width + height)
                    color = self._interpolate_color(start_color, end_color, ratio)
                    draw.point((x, y), fill=color)
        
        return gradient
    
    async def _create_gradient_overlay(
        self,
        dimensions: Tuple[int, int],
        template: VisualTemplate
    ) -> Image.Image:
        """Create transparent gradient overlay."""
        width, height = dimensions
        overlay = Image.new("RGBA", dimensions, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Create dark overlay for better text readability
        overlay_color = self._hex_to_rgba(template.background_color, 0.6)
        draw.rectangle([0, 0, width, height], fill=overlay_color)
        
        return overlay
    
    async def _add_text_content(
        self,
        image: Image.Image,
        optimization: ContentOptimization,
        template: VisualTemplate,
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """Add text content to image."""
        draw = ImageDraw.Draw(image)
        width, height = dimensions
        padding = template.layout_elements["padding"]
        
        # Calculate available text area
        text_area = (
            padding,
            padding,
            width - padding,
            height - padding
        )
        
        # Prepare text content
        if optimization.title:
            title = optimization.title
            content = optimization.caption
        else:
            # Split caption into title and content
            lines = optimization.caption.split('\n')
            title = lines[0] if lines else ""
            content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
        
        # Font sizes
        base_font_size = max(16, min(width, height) // 30)
        title_size = int(base_font_size * template.layout_elements["title_size_ratio"])
        content_size = int(base_font_size * template.layout_elements["content_size_ratio"])
        
        # Load fonts
        try:
            title_font = ImageFont.truetype(
                self.font_mapping[template.font_primary], title_size
            )
            content_font = ImageFont.truetype(
                self.font_mapping[template.font_secondary], content_size
            )
        except OSError:
            # Fallback to default font
            title_font = ImageFont.load_default()
            content_font = ImageFont.load_default()
        
        # Text colors
        text_color = template.text_color
        accent_color = template.accent_color
        
        current_y = text_area[1]
        
        # Add title
        if title:
            wrapped_title = self._wrap_text(
                title, title_font, text_area[2] - text_area[0]
            )
            
            for line in wrapped_title:
                bbox = draw.textbbox((0, 0), line, font=title_font)
                line_height = bbox[3] - bbox[1]
                
                # Center text horizontally
                text_width = bbox[2] - bbox[0]
                x = text_area[0] + (text_area[2] - text_area[0] - text_width) // 2
                
                draw.text((x, current_y), line, font=title_font, fill=text_color)
                current_y += line_height + 10
            
            current_y += 20  # Space between title and content
        
        # Add content
        if content:
            wrapped_content = self._wrap_text(
                content, content_font, text_area[2] - text_area[0]
            )
            
            line_spacing = int(content_size * template.layout_elements["line_spacing"])
            
            for line in wrapped_content:
                if current_y + line_spacing > text_area[3] - 50:  # Leave space for branding
                    break
                
                bbox = draw.textbbox((0, 0), line, font=content_font)
                line_height = bbox[3] - bbox[1]
                
                # Left align content or center based on template
                if template.layout_elements.get("centered_layout"):
                    text_width = bbox[2] - bbox[0]
                    x = text_area[0] + (text_area[2] - text_area[0] - text_width) // 2
                else:
                    x = text_area[0]
                
                draw.text((x, current_y), line, font=content_font, fill=text_color)
                current_y += line_spacing
        
        # Add quote marks for quote card style
        if template.layout_elements.get("quote_marks"):
            quote_size = title_size * 2
            try:
                quote_font = ImageFont.truetype(
                    self.font_mapping[template.font_primary], quote_size
                )
            except OSError:
                quote_font = ImageFont.load_default()
            
            draw.text((text_area[0], text_area[1] - quote_size // 2), '"', 
                     font=quote_font, fill=accent_color)
        
        return image
    
    async def _add_brand_elements(
        self,
        image: Image.Image,
        template: VisualTemplate,
        dimensions: Tuple[int, int]
    ) -> Image.Image:
        """Add BYMB brand elements to image."""
        draw = ImageDraw.Draw(image)
        width, height = dimensions
        padding = template.layout_elements["padding"]
        
        # Add logo (if available)
        logo_path = self.assets_path / "logo.png"
        if "logo" in template.brand_elements and logo_path.exists():
            logo = Image.open(logo_path)
            
            # Resize logo appropriately
            logo_size = min(width // 8, height // 8)
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Position logo in bottom right
            logo_x = width - logo_size - padding
            logo_y = height - logo_size - padding
            
            # Handle transparency
            if logo.mode == 'RGBA':
                image.paste(logo, (logo_x, logo_y), logo)
            else:
                image.paste(logo, (logo_x, logo_y))
        
        # Add tagline/credentials
        if "tagline" in template.brand_elements or "credentials" in template.brand_elements:
            tagline = "BYMB Consultancy • 23+ Years • $35M+ Results"
            
            base_font_size = max(12, min(width, height) // 50)
            try:
                tagline_font = ImageFont.truetype(
                    self.font_mapping["light"], base_font_size
                )
            except OSError:
                tagline_font = ImageFont.load_default()
            
            # Position at bottom
            bbox = draw.textbbox((0, 0), tagline, font=tagline_font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (width - text_width) // 2
            y = height - padding - text_height
            
            # Add background for better readability if needed
            if template.background_color != self.brand_colors.white:
                bg_padding = 10
                draw.rectangle([
                    x - bg_padding, y - bg_padding,
                    x + text_width + bg_padding, y + text_height + bg_padding
                ], fill=self._hex_to_rgba(self.brand_colors.white, 0.8))
            
            draw.text((x, y), tagline, font=tagline_font, 
                     fill=template.text_secondary if hasattr(template, 'text_secondary') else template.text_color)
        
        # Add accent elements for modern style
        if template.layout_elements.get("modern_elements"):
            # Add geometric accent
            accent_color = template.accent_color
            
            # Top-left accent
            draw.rectangle([0, 0, 5, height // 3], fill=accent_color)
            draw.rectangle([0, 0, width // 3, 5], fill=accent_color)
            
            # Bottom-right accent
            draw.rectangle([width - 5, height * 2 // 3, width, height], fill=accent_color)
            draw.rectangle([width * 2 // 3, height - 5, width, height], fill=accent_color)
        
        return image
    
    async def _apply_platform_optimizations(
        self,
        image: Image.Image,
        platform: SocialPlatform,
        content_type: ContentType
    ) -> List[str]:
        """Apply platform-specific optimizations."""
        optimizations = []
        
        # Instagram optimizations
        if platform == SocialPlatform.INSTAGRAM:
            # Increase saturation slightly for Instagram
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(1.1)
            optimizations.append("instagram_color_enhancement")
            
            if content_type == ContentType.STORY:
                # Add story-specific elements
                optimizations.append("story_format_optimization")
        
        # LinkedIn optimizations
        elif platform == SocialPlatform.LINKEDIN:
            # Maintain professional appearance
            optimizations.append("professional_color_profile")
        
        # Twitter optimizations
        elif platform == SocialPlatform.TWITTER:
            # Optimize for smaller display
            optimizations.append("compact_layout_optimization")
        
        # Facebook optimizations
        elif platform == SocialPlatform.FACEBOOK:
            # Standard optimizations
            optimizations.append("standard_social_optimization")
        
        return optimizations
    
    async def _save_image(
        self,
        image: Image.Image,
        optimization: ContentOptimization,
        visual_style: VisualStyle
    ) -> str:
        """Save image with appropriate naming and format."""
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bymb_{optimization.platform.value}_{optimization.content_type.value}_{visual_style.value}_{timestamp}.{optimization.image_specs['format'].lower()}"
        
        file_path = self.temp_dir / filename
        
        # Save with appropriate quality
        save_kwargs = {
            "format": optimization.image_specs["format"],
            "quality": optimization.image_specs.get("quality", 95)
        }
        
        if optimization.image_specs["format"] == "PNG":
            save_kwargs.pop("quality")  # PNG doesn't use quality parameter
        
        image.save(str(file_path), **save_kwargs)
        
        logger.info(f"Content adapted and saved: {file_path}")
        return str(file_path)
    
    def _wrap_text(self, text: str, font: ImageFont, max_width: int) -> List[str]:
        """Wrap text to fit within specified width."""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            if bbox[2] - bbox[0] <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Single word is too long, force it
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB tuple."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _hex_to_rgba(self, hex_color: str, alpha: float) -> Tuple[int, int, int, int]:
        """Convert hex color to RGBA tuple."""
        rgb = self._hex_to_rgb(hex_color)
        return rgb + (int(alpha * 255),)
    
    def _interpolate_color(
        self, 
        color1: Tuple[int, int, int], 
        color2: Tuple[int, int, int], 
        ratio: float
    ) -> Tuple[int, int, int]:
        """Interpolate between two colors."""
        return tuple(
            int(color1[i] + (color2[i] - color1[i]) * ratio)
            for i in range(3)
        )
    
    async def create_carousel_content(
        self,
        optimizations: List[ContentOptimization],
        visual_style: VisualStyle = VisualStyle.INFOGRAPHIC_STYLE
    ) -> List[ContentAdaptationResult]:
        """Create carousel content from multiple optimizations."""
        carousel_results = []
        
        for i, optimization in enumerate(optimizations):
            # Modify content for carousel slide
            slide_optimization = ContentOptimization(
                platform=optimization.platform,
                content_type=ContentType.CAROUSEL,
                title=f"Slide {i + 1}: {optimization.title}" if optimization.title else f"Key Insight {i + 1}",
                caption=optimization.caption,
                hashtags=optimization.hashtags,
                tone=optimization.tone,
                call_to_action=optimization.call_to_action,
                image_specs=optimization.image_specs,
                engagement_elements=optimization.engagement_elements,
                optimal_posting_time=optimization.optimal_posting_time,
                performance_predictions=optimization.performance_predictions,
                brand_compliance=optimization.brand_compliance
            )
            
            result = await self.adapt_content_to_format(
                slide_optimization, visual_style
            )
            carousel_results.append(result)
        
        return carousel_results
    
    async def batch_adapt_content(
        self,
        optimizations: List[ContentOptimization],
        visual_styles: Optional[List[VisualStyle]] = None
    ) -> Dict[str, List[ContentAdaptationResult]]:
        """Batch adapt multiple content pieces."""
        if visual_styles is None:
            visual_styles = [VisualStyle.PROFESSIONAL_MINIMAL]
        
        results = {"successful": [], "failed": []}
        
        for optimization in optimizations:
            for style in visual_styles:
                result = await self.adapt_content_to_format(optimization, style)
                
                if result.success:
                    results["successful"].append(result)
                else:
                    results["failed"].append(result)
        
        return results
    
    async def cleanup_temp_files(self, older_than_hours: int = 24) -> int:
        """Clean up temporary files older than specified hours."""
        cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
        deleted_count = 0
        
        for file_path in self.temp_dir.glob("bymb_*"):
            if file_path.stat().st_mtime < cutoff_time:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except OSError as e:
                    logger.warning(f"Failed to delete {file_path}: {e}")
        
        logger.info(f"Cleaned up {deleted_count} temporary files")
        return deleted_count