"""BYMB Brand Profile System - Comprehensive brand consistency management."""

from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
import re
from datetime import datetime
import colorsys
import logging

logger = logging.getLogger(__name__)


class PlatformType(Enum):
    """Social media platform types."""
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_STORY = "instagram_story"
    LINKEDIN_POST = "linkedin_post"
    LINKEDIN_BANNER = "linkedin_banner"
    TWITTER_POST = "twitter_post"
    FACEBOOK_POST = "facebook_post"
    FACEBOOK_COVER = "facebook_cover"
    GENERAL = "general"


class ContentType(Enum):
    """Content category types."""
    BUSINESS_INSIGHT = "business_insight"
    THOUGHT_LEADERSHIP = "thought_leadership"
    CASE_STUDY = "case_study"
    ACHIEVEMENT = "achievement"
    INDUSTRY_NEWS = "industry_news"
    INSPIRATIONAL = "inspirational"
    EDUCATIONAL = "educational"
    PROMOTIONAL = "promotional"


class BrandTone(Enum):
    """Brand tone variations."""
    AUTHORITATIVE = "authoritative"
    CONVERSATIONAL = "conversational"
    INSPIRATIONAL = "inspirational"
    ANALYTICAL = "analytical"
    STRATEGIC = "strategic"


@dataclass
class ColorSpec:
    """Color specification with multiple formats."""
    name: str
    hex: str
    rgb: Tuple[int, int, int]
    hsl: Tuple[int, int, int]
    pantone: Optional[str] = None
    cmyk: Optional[Tuple[int, int, int, int]] = None
    usage: Optional[str] = None
    
    @classmethod
    def from_hex(cls, name: str, hex_value: str, usage: Optional[str] = None, pantone: Optional[str] = None) -> 'ColorSpec':
        """Create ColorSpec from hex value."""
        # Remove # if present
        hex_clean = hex_value.lstrip('#')
        
        # Convert to RGB
        rgb = tuple(int(hex_clean[i:i+2], 16) for i in (0, 2, 4))
        
        # Convert to HSL
        r, g, b = [x/255.0 for x in rgb]
        h, l, s = colorsys.rgb_to_hls(r, g, b)
        hsl = (int(h*360), int(s*100), int(l*100))
        
        return cls(
            name=name,
            hex=f"#{hex_clean.upper()}",
            rgb=rgb,
            hsl=hsl,
            pantone=pantone,
            usage=usage
        )


@dataclass
class Typography:
    """Typography specification."""
    family: str
    weight: str
    size_px: int
    size_pt: Optional[int] = None
    line_height: Optional[float] = None
    letter_spacing: Optional[float] = None
    usage: Optional[str] = None


@dataclass
class LogoVariant:
    """Logo variant specification."""
    name: str
    file_path: str
    usage: str
    min_size_px: int
    background_requirements: List[str]
    formats: List[str] = field(default_factory=lambda: ["PNG", "SVG"])


@dataclass
class SocialPlatformSpecs:
    """Social media platform specifications."""
    platform: PlatformType
    dimensions: Dict[str, Tuple[int, int]]  # format -> (width, height)
    safe_zones: Dict[str, Dict[str, int]]  # margins, title safe areas
    text_limits: Dict[str, int]  # character limits for different elements
    optimal_image_ratio: Optional[str] = None
    recommended_fonts: Optional[List[str]] = None


@dataclass
class BrandVoiceProfile:
    """Brand voice and messaging profile."""
    personality_traits: List[str]
    tone_guidelines: Dict[BrandTone, str]
    key_messages: List[str]
    value_propositions: List[str]
    avoiding_words: List[str]
    preferred_phrases: List[str]
    call_to_actions: List[str]
    hashtag_strategy: Dict[str, List[str]]  # category -> hashtags


class BYMBBrandProfile:
    """Comprehensive BYMB Brand Profile System."""
    
    def __init__(self):
        """Initialize BYMB brand profile with all specifications."""
        self._initialize_brand_identity()
        self._initialize_visual_system()
        self._initialize_voice_guidelines()
        self._initialize_platform_specs()
        self._initialize_compliance_rules()
    
    def _initialize_brand_identity(self):
        """Initialize core brand identity elements."""
        self.brand_name = "BYMB Consultancy"
        self.founder = "Bader Abdulrahim"
        self.location = "Manama, Kingdom of Bahrain"
        self.experience = "23+ years"
        self.client_results = "$35M+ client results"
        self.tagline = "Be Your Most Beautiful - In Business & Beyond"
        
        self.brand_essence = {
            "mission": "Empowering businesses to achieve their most beautiful potential through strategic transformation",
            "vision": "To be the premier consultancy driving meaningful business transformation in the Gulf region",
            "values": [
                "Excellence in execution",
                "Strategic thinking",
                "Authentic relationships",
                "Continuous innovation",
                "Results-driven approach",
                "Cultural sensitivity"
            ],
            "positioning": "Premium business consultancy with proven track record and deep regional expertise"
        }
    
    def _initialize_visual_system(self):
        """Initialize visual identity system."""
        # Primary color palette
        self.primary_colors = [
            ColorSpec.from_hex(
                "BYMB Deep Blue", 
                "#1B365D", 
                "Primary brand color - authority, trust, professionalism",
                "PANTONE 7546 C"
            ),
            ColorSpec.from_hex(
                "BYMB Gold", 
                "#D4AF37", 
                "Accent color - premium, achievement, success",
                "PANTONE 871 C"
            ),
            ColorSpec.from_hex(
                "BYMB White", 
                "#FFFFFF", 
                "Clean background, clarity, space"
            )
        ]
        
        # Secondary color palette
        self.secondary_colors = [
            ColorSpec.from_hex(
                "Gulf Teal", 
                "#2E8B8B", 
                "Regional connection, stability"
            ),
            ColorSpec.from_hex(
                "Warm Gray", 
                "#6B7280", 
                "Supporting text, subtle backgrounds"
            ),
            ColorSpec.from_hex(
                "Success Green", 
                "#059669", 
                "Growth, positive results"
            ),
            ColorSpec.from_hex(
                "Alert Red", 
                "#DC2626", 
                "Urgent calls to action, warnings"
            )
        ]
        
        # Typography system
        self.typography = {
            "primary": Typography(
                family="Inter",
                weight="600",
                size_px=28,
                size_pt=21,
                line_height=1.3,
                letter_spacing=-0.02,
                usage="Headlines, main titles"
            ),
            "secondary": Typography(
                family="Inter",
                weight="500",
                size_px=18,
                size_pt=14,
                line_height=1.5,
                usage="Subheadings, important text"
            ),
            "body": Typography(
                family="Inter",
                weight="400",
                size_px=14,
                size_pt=11,
                line_height=1.6,
                usage="Body text, descriptions"
            ),
            "accent": Typography(
                family="Playfair Display",
                weight="400",
                size_px=24,
                size_pt=18,
                line_height=1.4,
                usage="Quotes, elegant emphasis"
            )
        }
        
        # Logo variants
        self.logo_variants = [
            LogoVariant(
                name="Primary Logo",
                file_path="assets/brand/logo-primary.svg",
                usage="Main brand applications, light backgrounds",
                min_size_px=120,
                background_requirements=["light", "white"]
            ),
            LogoVariant(
                name="Reverse Logo",
                file_path="assets/brand/logo-reverse.svg",
                usage="Dark backgrounds, overlays",
                min_size_px=120,
                background_requirements=["dark", "colored"]
            ),
            LogoVariant(
                name="Icon Mark",
                file_path="assets/brand/icon-mark.svg",
                usage="Small spaces, social profiles",
                min_size_px=32,
                background_requirements=["any"]
            ),
            LogoVariant(
                name="Horizontal Lock-up",
                file_path="assets/brand/logo-horizontal.svg",
                usage="Wide formats, headers",
                min_size_px=180,
                background_requirements=["light", "white"]
            )
        ]
    
    def _initialize_voice_guidelines(self):
        """Initialize brand voice and messaging guidelines."""
        self.voice_profile = BrandVoiceProfile(
            personality_traits=[
                "Authoritative yet approachable",
                "Strategic and insightful",
                "Culturally aware",
                "Results-focused",
                "Professionally warm",
                "Confidently humble"
            ],
            tone_guidelines={
                BrandTone.AUTHORITATIVE: "Use when sharing industry insights, thought leadership. Confident, expert, backed by experience.",
                BrandTone.CONVERSATIONAL: "Use for engagement posts, questions. Warm, accessible, inviting dialogue.",
                BrandTone.INSPIRATIONAL: "Use for motivational content, success stories. Uplifting, empowering, forward-looking.",
                BrandTone.ANALYTICAL: "Use for data-driven content, case studies. Precise, logical, evidence-based.",
                BrandTone.STRATEGIC: "Use for business advice, planning content. Thoughtful, comprehensive, long-term focused."
            },
            key_messages=[
                "23+ years of proven business transformation expertise",
                "Driving $35M+ in measurable client results",
                "Strategic excellence rooted in Gulf region insights",
                "Your partner in achieving business beauty and success",
                "Transforming challenges into competitive advantages"
            ],
            value_propositions=[
                "Proven track record with measurable results",
                "Deep understanding of Gulf business culture",
                "Strategic approach tailored to your unique needs",
                "End-to-end transformation support",
                "Premium consultancy accessible to ambitious businesses"
            ],
            avoiding_words=[
                "cheap", "basic", "simple", "easy fix", "overnight success",
                "guaranteed", "one-size-fits-all", "generic", "amateur"
            ],
            preferred_phrases=[
                "strategic transformation", "measurable results", "proven expertise",
                "business excellence", "competitive advantage", "sustainable growth",
                "cultural intelligence", "premium partnership", "authentic success"
            ],
            call_to_actions=[
                "Transform your business potential today",
                "Discover your path to sustainable growth",
                "Let's craft your success strategy",
                "Ready to achieve business excellence?",
                "Start your transformation journey",
                "Unlock your competitive advantage"
            ],
            hashtag_strategy={
                "brand": ["#BYMBConsultancy", "#BeYourMostBeautiful", "#BaderAbdulrahim"],
                "business": ["#BusinessTransformation", "#StrategicConsulting", "#GulfBusiness"],
                "results": ["#ProvenResults", "#BusinessGrowth", "#CompetitiveAdvantage"],
                "location": ["#BahrainBusiness", "#GCCConsulting", "#MiddleEastStrategy"],
                "expertise": ["#23YearsExperience", "#BusinessExcellence", "#TransformationExpert"]
            }
        )
    
    def _initialize_platform_specs(self):
        """Initialize social media platform specifications."""
        self.platform_specs = {
            PlatformType.INSTAGRAM_POST: SocialPlatformSpecs(
                platform=PlatformType.INSTAGRAM_POST,
                dimensions={
                    "square": (1080, 1080),
                    "portrait": (1080, 1350),
                    "landscape": (1080, 566)
                },
                safe_zones={
                    "margin": {"top": 100, "bottom": 100, "left": 80, "right": 80},
                    "logo_area": {"top": 50, "left": 50, "width": 200, "height": 80}
                },
                text_limits={
                    "caption": 2200,
                    "hashtags": 30,
                    "overlay_text": 50
                },
                optimal_image_ratio="1:1",
                recommended_fonts=["Inter", "Playfair Display"]
            ),
            PlatformType.INSTAGRAM_STORY: SocialPlatformSpecs(
                platform=PlatformType.INSTAGRAM_STORY,
                dimensions={
                    "story": (1080, 1920)
                },
                safe_zones={
                    "margin": {"top": 200, "bottom": 300, "left": 80, "right": 80},
                    "interactive_area": {"bottom": 250}
                },
                text_limits={
                    "overlay_text": 30
                },
                optimal_image_ratio="9:16"
            ),
            PlatformType.LINKEDIN_POST: SocialPlatformSpecs(
                platform=PlatformType.LINKEDIN_POST,
                dimensions={
                    "landscape": (1200, 628),
                    "square": (1080, 1080),
                    "vertical": (1080, 1350)
                },
                safe_zones={
                    "margin": {"top": 80, "bottom": 80, "left": 60, "right": 60}
                },
                text_limits={
                    "post": 3000,
                    "headline": 150,
                    "overlay_text": 60
                },
                optimal_image_ratio="1.91:1"
            ),
            PlatformType.TWITTER_POST: SocialPlatformSpecs(
                platform=PlatformType.TWITTER_POST,
                dimensions={
                    "landscape": (1200, 675),
                    "square": (1080, 1080)
                },
                safe_zones={
                    "margin": {"top": 60, "bottom": 60, "left": 50, "right": 50}
                },
                text_limits={
                    "tweet": 280,
                    "overlay_text": 40
                },
                optimal_image_ratio="16:9"
            ),
            PlatformType.FACEBOOK_POST: SocialPlatformSpecs(
                platform=PlatformType.FACEBOOK_POST,
                dimensions={
                    "landscape": (1200, 628),
                    "square": (1080, 1080)
                },
                safe_zones={
                    "margin": {"top": 80, "bottom": 80, "left": 60, "right": 60}
                },
                text_limits={
                    "post": 63206,  # Technical limit, but 500-600 is optimal
                    "optimal_post": 600,
                    "overlay_text": 50
                },
                optimal_image_ratio="1.91:1"
            )
        }
    
    def _initialize_compliance_rules(self):
        """Initialize brand compliance rules and scoring system."""
        self.compliance_rules = {
            "visual": {
                "logo_presence": {
                    "weight": 0.15,
                    "description": "Brand logo must be present and properly sized",
                    "requirements": {
                        "min_size_px": 80,
                        "clear_space": "2x logo height",
                        "placement": ["top-left", "top-right", "bottom-left", "bottom-right"]
                    }
                },
                "color_compliance": {
                    "weight": 0.20,
                    "description": "Colors must align with brand palette",
                    "requirements": {
                        "primary_color_usage": 0.4,  # At least 40% primary colors
                        "brand_color_only": True,
                        "contrast_ratio": 4.5  # WCAG AA standard
                    }
                },
                "typography_compliance": {
                    "weight": 0.15,
                    "description": "Typography must follow brand guidelines",
                    "requirements": {
                        "approved_fonts_only": True,
                        "hierarchy_respected": True,
                        "readability_score": 0.7
                    }
                },
                "layout_consistency": {
                    "weight": 0.10,
                    "description": "Layout follows brand grid and spacing",
                    "requirements": {
                        "margin_compliance": True,
                        "safe_zone_respected": True,
                        "visual_hierarchy": True
                    }
                }
            },
            "content": {
                "voice_alignment": {
                    "weight": 0.15,
                    "description": "Content matches brand voice and tone",
                    "requirements": {
                        "tone_consistency": True,
                        "brand_words_present": 0.2,  # 20% brand vocabulary
                        "avoiding_words_absent": True
                    }
                },
                "message_consistency": {
                    "weight": 0.15,
                    "description": "Messaging aligns with brand values",
                    "requirements": {
                        "value_prop_present": True,
                        "key_message_alignment": 0.6,
                        "cta_appropriate": True
                    }
                },
                "platform_optimization": {
                    "weight": 0.10,
                    "description": "Content optimized for specific platform",
                    "requirements": {
                        "dimension_compliance": True,
                        "text_length_optimal": True,
                        "hashtag_strategy": True
                    }
                }
            }
        }
        
        # Scoring thresholds
        self.scoring_thresholds = {
            "excellent": 0.90,
            "good": 0.80,
            "acceptable": 0.70,
            "needs_improvement": 0.60,
            "non_compliant": 0.50
        }
    
    def get_platform_specs(self, platform: PlatformType) -> SocialPlatformSpecs:
        """Get specifications for a specific platform."""
        return self.platform_specs.get(platform)
    
    def get_color_palette(self, include_secondary: bool = True) -> List[ColorSpec]:
        """Get brand color palette."""
        colors = self.primary_colors.copy()
        if include_secondary:
            colors.extend(self.secondary_colors)
        return colors
    
    def get_brand_fonts(self) -> Dict[str, Typography]:
        """Get brand typography specifications."""
        return self.typography
    
    def get_voice_guidelines(self, tone: Optional[BrandTone] = None) -> Union[BrandVoiceProfile, str]:
        """Get brand voice guidelines."""
        if tone:
            return self.voice_profile.tone_guidelines.get(tone, "")
        return self.voice_profile
    
    def get_compliance_rules(self) -> Dict[str, Any]:
        """Get brand compliance rules."""
        return self.compliance_rules
    
    def get_logo_for_context(self, background_type: str, size_requirement: int) -> Optional[LogoVariant]:
        """Get appropriate logo variant for specific context."""
        suitable_logos = [
            logo for logo in self.logo_variants
            if (background_type in logo.background_requirements or "any" in logo.background_requirements)
            and logo.min_size_px <= size_requirement
        ]
        
        if suitable_logos:
            # Return the most appropriate logo (prefer primary, then by size)
            return min(suitable_logos, key=lambda x: (x.name != "Primary Logo", x.min_size_px))
        
        return None
    
    def get_hashtag_strategy(self, content_category: Optional[str] = None) -> Union[List[str], Dict[str, List[str]]]:
        """Get hashtag strategy for content."""
        if content_category and content_category in self.voice_profile.hashtag_strategy:
            return self.voice_profile.hashtag_strategy[content_category]
        return self.voice_profile.hashtag_strategy
    
    def export_brand_guide(self) -> Dict[str, Any]:
        """Export complete brand guidelines as structured data."""
        return {
            "brand_identity": {
                "name": self.brand_name,
                "founder": self.founder,
                "location": self.location,
                "experience": self.experience,
                "results": self.client_results,
                "tagline": self.tagline,
                "essence": self.brand_essence
            },
            "visual_system": {
                "primary_colors": [
                    {
                        "name": color.name,
                        "hex": color.hex,
                        "rgb": color.rgb,
                        "hsl": color.hsl,
                        "usage": color.usage,
                        "pantone": color.pantone
                    }
                    for color in self.primary_colors
                ],
                "secondary_colors": [
                    {
                        "name": color.name,
                        "hex": color.hex,
                        "rgb": color.rgb,
                        "hsl": color.hsl,
                        "usage": color.usage
                    }
                    for color in self.secondary_colors
                ],
                "typography": {
                    name: {
                        "family": spec.family,
                        "weight": spec.weight,
                        "size_px": spec.size_px,
                        "size_pt": spec.size_pt,
                        "line_height": spec.line_height,
                        "letter_spacing": spec.letter_spacing,
                        "usage": spec.usage
                    }
                    for name, spec in self.typography.items()
                },
                "logos": [
                    {
                        "name": logo.name,
                        "file_path": logo.file_path,
                        "usage": logo.usage,
                        "min_size_px": logo.min_size_px,
                        "background_requirements": logo.background_requirements,
                        "formats": logo.formats
                    }
                    for logo in self.logo_variants
                ]
            },
            "voice_guidelines": {
                "personality_traits": self.voice_profile.personality_traits,
                "tone_guidelines": {tone.value: guideline for tone, guideline in self.voice_profile.tone_guidelines.items()},
                "key_messages": self.voice_profile.key_messages,
                "value_propositions": self.voice_profile.value_propositions,
                "avoiding_words": self.voice_profile.avoiding_words,
                "preferred_phrases": self.voice_profile.preferred_phrases,
                "call_to_actions": self.voice_profile.call_to_actions,
                "hashtag_strategy": self.voice_profile.hashtag_strategy
            },
            "platform_specifications": {
                platform.value: {
                    "dimensions": spec.dimensions,
                    "safe_zones": spec.safe_zones,
                    "text_limits": spec.text_limits,
                    "optimal_image_ratio": spec.optimal_image_ratio,
                    "recommended_fonts": spec.recommended_fonts
                }
                for platform, spec in self.platform_specs.items()
            },
            "compliance_rules": self.compliance_rules,
            "scoring_thresholds": self.scoring_thresholds,
            "export_timestamp": datetime.now().isoformat()
        }


# Global brand profile instance
bymb_brand = BYMBBrandProfile()