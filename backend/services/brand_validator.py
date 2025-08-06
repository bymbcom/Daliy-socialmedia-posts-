"""Brand Validation Service - Comprehensive brand compliance scoring and validation."""

import re
import asyncio
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime
import logging
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import colorsys

from .brand_profile import BYMBBrandProfile, PlatformType, ContentType, BrandTone, ColorSpec, bymb_brand

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ValidationCategory(Enum):
    """Validation category types."""
    VISUAL_IDENTITY = "visual_identity"
    CONTENT_VOICE = "content_voice"
    PLATFORM_COMPLIANCE = "platform_compliance"
    BRAND_CONSISTENCY = "brand_consistency"
    ACCESSIBILITY = "accessibility"


@dataclass
class ValidationIssue:
    """Brand validation issue."""
    category: ValidationCategory
    severity: ValidationSeverity
    message: str
    description: str
    suggestion: str
    affected_element: Optional[str] = None
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    score_impact: float = 0.0


@dataclass
class ValidationResult:
    """Comprehensive validation result."""
    overall_score: float
    category_scores: Dict[ValidationCategory, float]
    compliance_level: str
    issues: List[ValidationIssue]
    passed_checks: List[str]
    recommendations: List[str]
    platform_specific_issues: List[str] = field(default_factory=list)
    validation_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ContentAnalysis:
    """Content analysis structure."""
    text_content: str
    visual_elements: Dict[str, Any]
    platform_specs: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class BrandValidator:
    """Comprehensive brand validation service."""
    
    def __init__(self, brand_profile: BYMBBrandProfile = None):
        """Initialize brand validator."""
        self.brand = brand_profile or bymb_brand
        self.compliance_rules = self.brand.get_compliance_rules()
        self.scoring_thresholds = self.brand.scoring_thresholds
        
        # Initialize text analysis components
        self._setup_text_analysis()
        
        logger.info("Brand validator initialized with BYMB profile")
    
    def _setup_text_analysis(self):
        """Setup text analysis tools."""
        # Brand vocabulary for semantic analysis
        brand_vocabulary = (
            self.brand.voice_profile.preferred_phrases +
            self.brand.voice_profile.key_messages +
            self.brand.voice_profile.value_propositions +
            [word.lower() for phrase in self.brand.voice_profile.preferred_phrases for word in phrase.split()]
        )
        
        self.brand_vocabulary = set(brand_vocabulary)
        
        # Initialize TF-IDF vectorizer for content analysis
        self.text_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Pre-fit with brand content
        brand_texts = (
            self.brand.voice_profile.key_messages +
            self.brand.voice_profile.value_propositions +
            [desc for tone, desc in self.brand.voice_profile.tone_guidelines.items()]
        )
        
        try:
            self.text_vectorizer.fit(brand_texts)
            self.brand_text_vectors = self.text_vectorizer.transform(brand_texts)
        except Exception as e:
            logger.warning(f"Failed to initialize text vectorizer: {e}")
            self.text_vectorizer = None
            self.brand_text_vectors = None
    
    async def validate_content(
        self,
        content: ContentAnalysis,
        platform: PlatformType,
        content_type: Optional[ContentType] = None
    ) -> ValidationResult:
        """Comprehensive content validation."""
        logger.info(f"Starting validation for {platform.value} content")
        
        issues = []
        passed_checks = []
        category_scores = {}
        recommendations = []
        
        # Visual identity validation
        visual_score, visual_issues, visual_passed = await self._validate_visual_identity(
            content.visual_elements, platform
        )
        category_scores[ValidationCategory.VISUAL_IDENTITY] = visual_score
        issues.extend(visual_issues)
        passed_checks.extend(visual_passed)
        
        # Content voice validation
        voice_score, voice_issues, voice_passed = await self._validate_content_voice(
            content.text_content, content_type
        )
        category_scores[ValidationCategory.CONTENT_VOICE] = voice_score
        issues.extend(voice_issues)
        passed_checks.extend(voice_passed)
        
        # Platform compliance validation
        platform_score, platform_issues, platform_passed = await self._validate_platform_compliance(
            content, platform
        )
        category_scores[ValidationCategory.PLATFORM_COMPLIANCE] = platform_score
        issues.extend(platform_issues)
        passed_checks.extend(platform_passed)
        
        # Brand consistency validation
        consistency_score, consistency_issues, consistency_passed = await self._validate_brand_consistency(
            content, platform, content_type
        )
        category_scores[ValidationCategory.BRAND_CONSISTENCY] = consistency_score
        issues.extend(consistency_issues)
        passed_checks.extend(consistency_passed)
        
        # Accessibility validation
        accessibility_score, accessibility_issues, accessibility_passed = await self._validate_accessibility(
            content.visual_elements, content.text_content
        )
        category_scores[ValidationCategory.ACCESSIBILITY] = accessibility_score
        issues.extend(accessibility_issues)
        passed_checks.extend(accessibility_passed)
        
        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(category_scores)
        
        # Determine compliance level
        compliance_level = self._determine_compliance_level(overall_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(issues, category_scores)
        
        logger.info(f"Validation completed. Overall score: {overall_score:.2f}, Level: {compliance_level}")
        
        return ValidationResult(
            overall_score=overall_score,
            category_scores=category_scores,
            compliance_level=compliance_level,
            issues=issues,
            passed_checks=passed_checks,
            recommendations=recommendations,
            metadata={
                "platform": platform.value,
                "content_type": content_type.value if content_type else None,
                "total_issues": len(issues),
                "critical_issues": len([i for i in issues if i.severity == ValidationSeverity.CRITICAL]),
                "validation_duration_ms": 0  # Would be calculated in actual implementation
            }
        )
    
    async def _validate_visual_identity(
        self, 
        visual_elements: Dict[str, Any], 
        platform: PlatformType
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Validate visual identity compliance."""
        issues = []
        passed_checks = []
        score_components = []
        
        # Logo presence and compliance
        logo_score, logo_issues, logo_passed = self._check_logo_compliance(visual_elements, platform)
        issues.extend(logo_issues)
        passed_checks.extend(logo_passed)
        score_components.append(("logo", logo_score, 0.3))
        
        # Color palette compliance
        color_score, color_issues, color_passed = self._check_color_compliance(visual_elements)
        issues.extend(color_issues)
        passed_checks.extend(color_passed)
        score_components.append(("color", color_score, 0.35))
        
        # Typography compliance
        typography_score, typography_issues, typography_passed = self._check_typography_compliance(
            visual_elements
        )
        issues.extend(typography_issues)
        passed_checks.extend(typography_passed)
        score_components.append(("typography", typography_score, 0.25))
        
        # Layout and spacing compliance
        layout_score, layout_issues, layout_passed = self._check_layout_compliance(
            visual_elements, platform
        )
        issues.extend(layout_issues)
        passed_checks.extend(layout_passed)
        score_components.append(("layout", layout_score, 0.1))
        
        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in score_components)
        
        return total_score, issues, passed_checks
    
    async def _validate_content_voice(
        self, 
        text_content: str, 
        content_type: Optional[ContentType]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Validate content voice and messaging."""
        issues = []
        passed_checks = []
        score_components = []
        
        if not text_content or not text_content.strip():
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_VOICE,
                severity=ValidationSeverity.HIGH,
                message="No text content provided",
                description="Content must include text to maintain brand voice",
                suggestion="Add meaningful text content that reflects BYMB's voice",
                score_impact=-0.5
            ))
            return 0.0, issues, passed_checks
        
        # Voice tone analysis
        tone_score, tone_issues, tone_passed = self._analyze_voice_tone(text_content, content_type)
        issues.extend(tone_issues)
        passed_checks.extend(tone_passed)
        score_components.append(("tone", tone_score, 0.3))
        
        # Brand vocabulary usage
        vocabulary_score, vocab_issues, vocab_passed = self._check_brand_vocabulary(text_content)
        issues.extend(vocab_issues)
        passed_checks.extend(vocab_passed)
        score_components.append(("vocabulary", vocabulary_score, 0.25))
        
        # Message alignment
        message_score, message_issues, message_passed = self._check_message_alignment(text_content)
        issues.extend(message_issues)
        passed_checks.extend(message_passed)
        score_components.append(("message", message_score, 0.25))
        
        # Prohibited words check
        prohibited_score, prohibited_issues, prohibited_passed = self._check_prohibited_words(text_content)
        issues.extend(prohibited_issues)
        passed_checks.extend(prohibited_passed)
        score_components.append(("prohibited", prohibited_score, 0.2))
        
        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in score_components)
        
        return total_score, issues, passed_checks
    
    async def _validate_platform_compliance(
        self, 
        content: ContentAnalysis, 
        platform: PlatformType
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Validate platform-specific compliance."""
        issues = []
        passed_checks = []
        score_components = []
        
        platform_specs = self.brand.get_platform_specs(platform)
        if not platform_specs:
            issues.append(ValidationIssue(
                category=ValidationCategory.PLATFORM_COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                message=f"No specifications found for platform {platform.value}",
                description="Platform specifications are required for proper validation",
                suggestion="Ensure platform specifications are configured",
                score_impact=-0.2
            ))
            return 0.5, issues, passed_checks
        
        # Dimension compliance
        dimension_score, dimension_issues, dimension_passed = self._check_dimension_compliance(
            content.visual_elements, platform_specs
        )
        issues.extend(dimension_issues)
        passed_checks.extend(dimension_passed)
        score_components.append(("dimensions", dimension_score, 0.4))
        
        # Text length compliance
        text_score, text_issues, text_passed = self._check_text_length_compliance(
            content.text_content, platform_specs
        )
        issues.extend(text_issues)
        passed_checks.extend(text_passed)
        score_components.append(("text_length", text_score, 0.3))
        
        # Safe zone compliance
        safe_zone_score, safe_zone_issues, safe_zone_passed = self._check_safe_zone_compliance(
            content.visual_elements, platform_specs
        )
        issues.extend(safe_zone_issues)
        passed_checks.extend(safe_zone_passed)
        score_components.append(("safe_zones", safe_zone_score, 0.3))
        
        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in score_components)
        
        return total_score, issues, passed_checks
    
    async def _validate_brand_consistency(
        self, 
        content: ContentAnalysis, 
        platform: PlatformType,
        content_type: Optional[ContentType]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Validate overall brand consistency."""
        issues = []
        passed_checks = []
        score_components = []
        
        # Visual-content alignment
        alignment_score, alignment_issues, alignment_passed = self._check_visual_content_alignment(
            content.visual_elements, content.text_content
        )
        issues.extend(alignment_issues)
        passed_checks.extend(alignment_passed)
        score_components.append(("alignment", alignment_score, 0.4))
        
        # Call-to-action appropriateness
        cta_score, cta_issues, cta_passed = self._check_cta_appropriateness(
            content.text_content, content_type
        )
        issues.extend(cta_issues)
        passed_checks.extend(cta_passed)
        score_components.append(("cta", cta_score, 0.3))
        
        # Hashtag strategy compliance
        hashtag_score, hashtag_issues, hashtag_passed = self._check_hashtag_strategy(
            content.text_content, content_type, platform
        )
        issues.extend(hashtag_issues)
        passed_checks.extend(hashtag_passed)
        score_components.append(("hashtags", hashtag_score, 0.3))
        
        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in score_components)
        
        return total_score, issues, passed_checks
    
    async def _validate_accessibility(
        self, 
        visual_elements: Dict[str, Any], 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Validate accessibility compliance."""
        issues = []
        passed_checks = []
        score_components = []
        
        # Color contrast compliance
        contrast_score, contrast_issues, contrast_passed = self._check_color_contrast(visual_elements)
        issues.extend(contrast_issues)
        passed_checks.extend(contrast_passed)
        score_components.append(("contrast", contrast_score, 0.4))
        
        # Text readability
        readability_score, readability_issues, readability_passed = self._check_text_readability(
            visual_elements, text_content
        )
        issues.extend(readability_issues)
        passed_checks.extend(readability_passed)
        score_components.append(("readability", readability_score, 0.4))
        
        # Alternative text compliance
        alt_text_score, alt_text_issues, alt_text_passed = self._check_alternative_text(visual_elements)
        issues.extend(alt_text_issues)
        passed_checks.extend(alt_text_passed)
        score_components.append(("alt_text", alt_text_score, 0.2))
        
        # Calculate weighted score
        total_score = sum(score * weight for _, score, weight in score_components)
        
        return total_score, issues, passed_checks
    
    def _check_logo_compliance(
        self, 
        visual_elements: Dict[str, Any], 
        platform: PlatformType
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check logo presence and compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        logo_info = visual_elements.get("logo", {})
        
        if not logo_info:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.HIGH,
                message="Brand logo missing",
                description="BYMB brand logo must be present on all content",
                suggestion="Add appropriate BYMB logo variant for this content",
                affected_element="logo",
                score_impact=-0.8
            ))
            return 0.2, issues, passed_checks
        
        # Check logo size
        logo_size = logo_info.get("size", {})
        min_size = logo_info.get("min_size_required", 80)
        current_size = min(logo_size.get("width", 0), logo_size.get("height", 0))
        
        if current_size < min_size:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.MEDIUM,
                message="Logo too small",
                description=f"Logo size ({current_size}px) is below minimum requirement ({min_size}px)",
                suggestion=f"Increase logo size to at least {min_size}px",
                current_value=f"{current_size}px",
                expected_value=f"{min_size}px minimum",
                score_impact=-0.3
            ))
            score -= 0.3
        else:
            passed_checks.append("Logo size meets minimum requirements")
        
        # Check logo placement
        logo_placement = logo_info.get("placement", "")
        acceptable_placements = ["top-left", "top-right", "bottom-left", "bottom-right"]
        
        if logo_placement not in acceptable_placements:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.LOW,
                message="Non-standard logo placement",
                description="Logo should be placed in standard positions for better brand recognition",
                suggestion=f"Consider placing logo in: {', '.join(acceptable_placements)}",
                current_value=logo_placement,
                expected_value="Standard corner placement",
                score_impact=-0.1
            ))
            score -= 0.1
        else:
            passed_checks.append("Logo placement follows brand guidelines")
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_color_compliance(
        self, 
        visual_elements: Dict[str, Any]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check color palette compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        colors_used = visual_elements.get("colors", [])
        if not colors_used:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.MEDIUM,
                message="No color information provided",
                description="Color compliance cannot be validated without color data",
                suggestion="Provide color information for validation",
                score_impact=-0.5
            ))
            return 0.5, issues, passed_checks
        
        # Get brand colors
        brand_colors = self.brand.get_color_palette(include_secondary=True)
        brand_color_values = {color.hex.lower() for color in brand_colors}
        
        # Check if colors are from brand palette
        non_brand_colors = []
        for color in colors_used:
            color_hex = color.get("hex", "").lower()
            if color_hex not in brand_color_values:
                non_brand_colors.append(color_hex)
        
        if non_brand_colors:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.HIGH,
                message="Non-brand colors detected",
                description=f"Colors not in brand palette: {', '.join(non_brand_colors)}",
                suggestion="Use only approved BYMB brand colors",
                current_value=f"{len(non_brand_colors)} non-brand colors",
                expected_value="Brand colors only",
                score_impact=-0.6
            ))
            score -= 0.6
        else:
            passed_checks.append("All colors comply with brand palette")
        
        # Check primary color usage
        primary_colors = {color.hex.lower() for color in self.brand.primary_colors}
        primary_color_usage = sum(
            1 for color in colors_used 
            if color.get("hex", "").lower() in primary_colors
        )
        
        if primary_color_usage == 0:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.MEDIUM,
                message="No primary brand colors used",
                description="Content should feature BYMB primary colors (Deep Blue, Gold)",
                suggestion="Incorporate BYMB Deep Blue (#1B365D) or Gold (#D4AF37)",
                score_impact=-0.3
            ))
            score -= 0.3
        else:
            passed_checks.append("Primary brand colors are present")
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_typography_compliance(
        self, 
        visual_elements: Dict[str, Any]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check typography compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        typography_info = visual_elements.get("typography", {})
        if not typography_info:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.MEDIUM,
                message="No typography information provided",
                description="Typography compliance cannot be validated without font data",
                suggestion="Provide typography information for validation",
                score_impact=-0.4
            ))
            return 0.6, issues, passed_checks
        
        # Get brand fonts
        brand_fonts = self.brand.get_brand_fonts()
        approved_font_families = {spec.family.lower() for spec in brand_fonts.values()}
        
        # Check font families
        fonts_used = typography_info.get("fonts_used", [])
        non_brand_fonts = []
        
        for font in fonts_used:
            font_family = font.get("family", "").lower()
            if font_family not in approved_font_families:
                non_brand_fonts.append(font.get("family", "Unknown"))
        
        if non_brand_fonts:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.MEDIUM,
                message="Non-approved fonts detected",
                description=f"Fonts not in brand guidelines: {', '.join(non_brand_fonts)}",
                suggestion="Use approved BYMB fonts: Inter, Playfair Display",
                current_value=f"{len(non_brand_fonts)} non-brand fonts",
                expected_value="Brand fonts only",
                score_impact=-0.4
            ))
            score -= 0.4
        else:
            passed_checks.append("All fonts comply with brand guidelines")
        
        # Check typography hierarchy
        hierarchy_present = typography_info.get("hierarchy_respected", False)
        if not hierarchy_present:
            issues.append(ValidationIssue(
                category=ValidationCategory.VISUAL_IDENTITY,
                severity=ValidationSeverity.LOW,
                message="Typography hierarchy unclear",
                description="Clear visual hierarchy improves brand consistency",
                suggestion="Use distinct font sizes and weights to create clear hierarchy",
                score_impact=-0.2
            ))
            score -= 0.2
        else:
            passed_checks.append("Typography hierarchy is well-established")
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_layout_compliance(
        self, 
        visual_elements: Dict[str, Any], 
        platform: PlatformType
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check layout and spacing compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        layout_info = visual_elements.get("layout", {})
        platform_specs = self.brand.get_platform_specs(platform)
        
        if not platform_specs:
            return 0.5, issues, passed_checks
        
        # Check margin compliance
        margins = layout_info.get("margins", {})
        required_margins = platform_specs.safe_zones.get("margin", {})
        
        for position, required_value in required_margins.items():
            current_value = margins.get(position, 0)
            if current_value < required_value:
                issues.append(ValidationIssue(
                    category=ValidationCategory.VISUAL_IDENTITY,
                    severity=ValidationSeverity.LOW,
                    message=f"Insufficient {position} margin",
                    description=f"Margin should be at least {required_value}px for optimal presentation",
                    suggestion=f"Increase {position} margin to {required_value}px",
                    current_value=f"{current_value}px",
                    expected_value=f"{required_value}px minimum",
                    score_impact=-0.1
                ))
                score -= 0.1
        
        if score == 1.0:
            passed_checks.append("Layout margins meet platform requirements")
        
        return max(score, 0.0), issues, passed_checks
    
    def _analyze_voice_tone(
        self, 
        text_content: str, 
        content_type: Optional[ContentType]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Analyze voice tone compliance."""
        issues = []
        passed_checks = []
        score = 0.8  # Default good score
        
        if not text_content.strip():
            return 0.0, issues, passed_checks
        
        # Analyze tone characteristics
        text_lower = text_content.lower()
        
        # Check for authoritative language
        authoritative_indicators = [
            "proven", "expertise", "experience", "results", "strategy", 
            "transform", "achieve", "deliver", "success", "professional"
        ]
        authoritative_count = sum(1 for indicator in authoritative_indicators if indicator in text_lower)
        
        # Check for conversational elements
        conversational_indicators = ["?", "you", "your", "we", "our", "let's", "ready"]
        conversational_count = sum(1 for indicator in conversational_indicators if indicator in text_lower)
        
        # Check for inspirational language
        inspirational_indicators = [
            "beautiful", "potential", "growth", "excellence", "opportunity",
            "future", "vision", "dream", "aspire"
        ]
        inspirational_count = sum(1 for indicator in inspirational_indicators if indicator in text_lower)
        
        # Evaluate tone appropriateness
        total_indicators = authoritative_count + conversational_count + inspirational_count
        
        if total_indicators == 0:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_VOICE,
                severity=ValidationSeverity.MEDIUM,
                message="Neutral tone detected",
                description="Content lacks distinctive BYMB brand voice characteristics",
                suggestion="Incorporate authoritative, conversational, or inspirational language",
                score_impact=-0.3
            ))
            score -= 0.3
        else:
            passed_checks.append("Brand voice characteristics detected in content")
        
        # Check for appropriate content type alignment
        if content_type:
            if content_type in [ContentType.THOUGHT_LEADERSHIP, ContentType.BUSINESS_INSIGHT]:
                if authoritative_count < 2:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.CONTENT_VOICE,
                        severity=ValidationSeverity.LOW,
                        message="Insufficient authoritative tone",
                        description="Thought leadership content should demonstrate expertise",
                        suggestion="Include more authoritative language showing proven expertise",
                        score_impact=-0.1
                    ))
                    score -= 0.1
            
            elif content_type == ContentType.INSPIRATIONAL:
                if inspirational_count < 2:
                    issues.append(ValidationIssue(
                        category=ValidationCategory.CONTENT_VOICE,
                        severity=ValidationSeverity.LOW,
                        message="Insufficient inspirational tone",
                        description="Inspirational content should uplift and motivate",
                        suggestion="Include more inspirational and empowering language",
                        score_impact=-0.1
                    ))
                    score -= 0.1
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_brand_vocabulary(
        self, 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check brand vocabulary usage."""
        issues = []
        passed_checks = []
        score = 0.7  # Default score
        
        if not text_content.strip():
            return 0.0, issues, passed_checks
        
        text_lower = text_content.lower()
        words_in_content = set(re.findall(r'\b\w+\b', text_lower))
        
        # Check for brand vocabulary usage
        brand_words_found = words_in_content.intersection(self.brand_vocabulary)
        brand_word_ratio = len(brand_words_found) / max(len(words_in_content), 1)
        
        if brand_word_ratio >= 0.15:  # 15% brand vocabulary
            passed_checks.append("Strong brand vocabulary presence")
            score = 1.0
        elif brand_word_ratio >= 0.10:  # 10% brand vocabulary
            passed_checks.append("Adequate brand vocabulary presence")
            score = 0.8
        elif brand_word_ratio >= 0.05:  # 5% brand vocabulary
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_VOICE,
                severity=ValidationSeverity.LOW,
                message="Limited brand vocabulary usage",
                description="Consider incorporating more BYMB-specific terminology",
                suggestion="Include words like 'transformation', 'excellence', 'strategic', 'beautiful'",
                current_value=f"{brand_word_ratio:.1%} brand vocabulary",
                expected_value="10%+ brand vocabulary",
                score_impact=-0.2
            ))
            score = 0.6
        else:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_VOICE,
                severity=ValidationSeverity.MEDIUM,
                message="Insufficient brand vocabulary",
                description="Content lacks distinctive BYMB terminology",
                suggestion="Incorporate brand-specific language and preferred phrases",
                current_value=f"{brand_word_ratio:.1%} brand vocabulary",
                expected_value="10%+ brand vocabulary",
                score_impact=-0.4
            ))
            score = 0.4
        
        return score, issues, passed_checks
    
    def _check_message_alignment(
        self, 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check message alignment with brand values."""
        issues = []
        passed_checks = []
        score = 0.7  # Default score
        
        if not self.text_vectorizer or not text_content.strip():
            return score, issues, passed_checks
        
        try:
            # Vectorize the content
            content_vector = self.text_vectorizer.transform([text_content])
            
            # Calculate similarity with brand messages
            similarities = cosine_similarity(content_vector, self.brand_text_vectors)
            max_similarity = np.max(similarities)
            
            if max_similarity >= 0.3:  # High similarity threshold
                passed_checks.append("Content aligns well with brand messaging")
                score = 1.0
            elif max_similarity >= 0.2:  # Medium similarity
                passed_checks.append("Content shows reasonable brand alignment")
                score = 0.8
            elif max_similarity >= 0.1:  # Low similarity
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_VOICE,
                    severity=ValidationSeverity.LOW,
                    message="Weak brand message alignment",
                    description="Content could better reflect core BYMB messages",
                    suggestion="Align content with key brand values and propositions",
                    score_impact=-0.2
                ))
                score = 0.6
            else:
                issues.append(ValidationIssue(
                    category=ValidationCategory.CONTENT_VOICE,
                    severity=ValidationSeverity.MEDIUM,
                    message="Poor brand message alignment",
                    description="Content does not strongly reflect BYMB brand messaging",
                    suggestion="Incorporate key messages about expertise, results, and transformation",
                    score_impact=-0.4
                ))
                score = 0.4
                
        except Exception as e:
            logger.warning(f"Message alignment analysis failed: {e}")
        
        return score, issues, passed_checks
    
    def _check_prohibited_words(
        self, 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check for prohibited words."""
        issues = []
        passed_checks = []
        score = 1.0
        
        text_lower = text_content.lower()
        avoiding_words = self.brand.voice_profile.avoiding_words
        
        found_prohibited = []
        for word in avoiding_words:
            if word.lower() in text_lower:
                found_prohibited.append(word)
        
        if found_prohibited:
            issues.append(ValidationIssue(
                category=ValidationCategory.CONTENT_VOICE,
                severity=ValidationSeverity.HIGH,
                message="Prohibited words detected",
                description=f"Found words that contradict brand voice: {', '.join(found_prohibited)}",
                suggestion="Remove or replace prohibited words with brand-appropriate alternatives",
                current_value=f"{len(found_prohibited)} prohibited words",
                expected_value="No prohibited words",
                score_impact=-0.6
            ))
            score = 0.4
        else:
            passed_checks.append("No prohibited words detected")
        
        return score, issues, passed_checks
    
    def _check_dimension_compliance(
        self, 
        visual_elements: Dict[str, Any], 
        platform_specs: Any
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check dimension compliance for platform."""
        issues = []
        passed_checks = []
        score = 1.0
        
        dimensions = visual_elements.get("dimensions", {})
        width = dimensions.get("width", 0)
        height = dimensions.get("height", 0)
        
        if width == 0 or height == 0:
            issues.append(ValidationIssue(
                category=ValidationCategory.PLATFORM_COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                message="No dimension information provided",
                description="Cannot validate platform dimension requirements",
                suggestion="Provide image dimensions for validation",
                score_impact=-0.3
            ))
            return 0.7, issues, passed_checks
        
        # Check against platform specifications
        platform_dimensions = platform_specs.dimensions
        matching_format = None
        
        for format_name, (req_width, req_height) in platform_dimensions.items():
            if width == req_width and height == req_height:
                matching_format = format_name
                break
        
        if matching_format:
            passed_checks.append(f"Dimensions match {matching_format} format perfectly")
        else:
            # Check for close matches (within 5% tolerance)
            close_matches = []
            for format_name, (req_width, req_height) in platform_dimensions.items():
                width_diff = abs(width - req_width) / req_width
                height_diff = abs(height - req_height) / req_height
                
                if width_diff <= 0.05 and height_diff <= 0.05:
                    close_matches.append((format_name, req_width, req_height))
            
            if close_matches:
                format_name, req_width, req_height = close_matches[0]
                issues.append(ValidationIssue(
                    category=ValidationCategory.PLATFORM_COMPLIANCE,
                    severity=ValidationSeverity.LOW,
                    message="Dimensions close to standard format",
                    description=f"Current: {width}x{height}, {format_name}: {req_width}x{req_height}",
                    suggestion=f"Adjust to exact {format_name} dimensions: {req_width}x{req_height}",
                    current_value=f"{width}x{height}",
                    expected_value=f"{req_width}x{req_height}",
                    score_impact=-0.1
                ))
                score = 0.9
            else:
                issues.append(ValidationIssue(
                    category=ValidationCategory.PLATFORM_COMPLIANCE,
                    severity=ValidationSeverity.MEDIUM,
                    message="Non-standard dimensions",
                    description=f"Dimensions {width}x{height} don't match platform requirements",
                    suggestion=f"Use standard dimensions: {list(platform_dimensions.values())}",
                    current_value=f"{width}x{height}",
                    expected_value="Standard platform dimensions",
                    score_impact=-0.4
                ))
                score = 0.6
        
        return score, issues, passed_checks
    
    def _check_text_length_compliance(
        self, 
        text_content: str, 
        platform_specs: Any
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check text length compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        if not text_content:
            return score, issues, passed_checks
        
        text_limits = platform_specs.text_limits
        content_length = len(text_content)
        
        # Check against various text limits
        for limit_type, max_length in text_limits.items():
            if limit_type == "optimal_post" and "post" in limit_type:
                # Check optimal length vs absolute limit
                if content_length <= max_length:
                    passed_checks.append(f"Text length optimal for {limit_type}")
                elif content_length <= text_limits.get("post", max_length * 2):
                    issues.append(ValidationIssue(
                        category=ValidationCategory.PLATFORM_COMPLIANCE,
                        severity=ValidationSeverity.LOW,
                        message="Text longer than optimal",
                        description=f"Text length ({content_length}) exceeds optimal length ({max_length})",
                        suggestion=f"Consider shortening to under {max_length} characters for better engagement",
                        current_value=f"{content_length} characters",
                        expected_value=f"Under {max_length} characters (optimal)",
                        score_impact=-0.1
                    ))
                    score -= 0.1
            
            elif limit_type in ["post", "caption", "tweet"] and content_length > max_length:
                severity = ValidationSeverity.HIGH if content_length > max_length * 1.1 else ValidationSeverity.MEDIUM
                issues.append(ValidationIssue(
                    category=ValidationCategory.PLATFORM_COMPLIANCE,
                    severity=severity,
                    message=f"Text exceeds {limit_type} limit",
                    description=f"Content length ({content_length}) exceeds platform limit ({max_length})",
                    suggestion=f"Shorten content to under {max_length} characters",
                    current_value=f"{content_length} characters",
                    expected_value=f"Under {max_length} characters",
                    score_impact=-0.3 if severity == ValidationSeverity.HIGH else -0.2
                ))
                score -= 0.3 if severity == ValidationSeverity.HIGH else 0.2
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_safe_zone_compliance(
        self, 
        visual_elements: Dict[str, Any], 
        platform_specs: Any
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check safe zone compliance."""
        issues = []
        passed_checks = []
        score = 1.0
        
        layout_info = visual_elements.get("layout", {})
        safe_zones = platform_specs.safe_zones
        
        # This is a simplified check - in a real implementation,
        # you would analyze the actual image layout
        margins_respected = layout_info.get("safe_zones_respected", True)
        
        if margins_respected:
            passed_checks.append("Safe zones respected in layout")
        else:
            issues.append(ValidationIssue(
                category=ValidationCategory.PLATFORM_COMPLIANCE,
                severity=ValidationSeverity.MEDIUM,
                message="Safe zone violations detected",
                description="Important content may be cut off on some devices",
                suggestion="Keep text and key elements within platform safe zones",
                score_impact=-0.3
            ))
            score = 0.7
        
        return score, issues, passed_checks
    
    def _check_visual_content_alignment(
        self, 
        visual_elements: Dict[str, Any], 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check visual-content alignment."""
        issues = []
        passed_checks = []
        score = 0.8  # Default good score
        
        # This would require more sophisticated analysis in practice
        # For now, we'll do basic checks
        
        if not text_content.strip():
            issues.append(ValidationIssue(
                category=ValidationCategory.BRAND_CONSISTENCY,
                severity=ValidationSeverity.MEDIUM,
                message="No text content for visual alignment check",
                description="Text and visuals should work together to reinforce brand message",
                suggestion="Ensure text complements visual elements",
                score_impact=-0.2
            ))
            score = 0.6
        else:
            passed_checks.append("Text content present for visual alignment")
        
        # Check for emotional alignment
        text_sentiment = self._analyze_text_sentiment(text_content)
        visual_mood = visual_elements.get("mood", "neutral")
        
        if text_sentiment == "positive" and visual_mood in ["professional", "inspirational", "success"]:
            passed_checks.append("Visual mood aligns with positive text sentiment")
        elif text_sentiment == "professional" and visual_mood in ["professional", "authoritative"]:
            passed_checks.append("Visual mood aligns with professional text tone")
        
        return score, issues, passed_checks
    
    def _check_cta_appropriateness(
        self, 
        text_content: str, 
        content_type: Optional[ContentType]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check call-to-action appropriateness."""
        issues = []
        passed_checks = []
        score = 0.8  # Default score
        
        if not text_content.strip():
            return score, issues, passed_checks
        
        # Check for CTA presence
        brand_ctas = self.brand.voice_profile.call_to_actions
        text_lower = text_content.lower()
        
        cta_found = False
        for cta in brand_ctas:
            if any(word in text_lower for word in cta.lower().split()):
                cta_found = True
                break
        
        # Generic CTA indicators
        cta_indicators = [
            "contact", "call", "visit", "learn more", "discover", "start", 
            "begin", "transform", "achieve", "unlock", "ready", "let's"
        ]
        
        generic_cta = any(indicator in text_lower for indicator in cta_indicators)
        
        if cta_found:
            passed_checks.append("Brand-aligned call-to-action present")
            score = 1.0
        elif generic_cta:
            passed_checks.append("Call-to-action present")
            score = 0.9
        else:
            # Not all content needs CTAs
            if content_type in [ContentType.THOUGHT_LEADERSHIP, ContentType.EDUCATIONAL]:
                passed_checks.append("No CTA required for this content type")
            else:
                issues.append(ValidationIssue(
                    category=ValidationCategory.BRAND_CONSISTENCY,
                    severity=ValidationSeverity.LOW,
                    message="No clear call-to-action",
                    description="Content could benefit from a clear next step for audience",
                    suggestion="Consider adding a relevant call-to-action from BYMB's approved list",
                    score_impact=-0.2
                ))
                score = 0.6
        
        return score, issues, passed_checks
    
    def _check_hashtag_strategy(
        self, 
        text_content: str, 
        content_type: Optional[ContentType],
        platform: PlatformType
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check hashtag strategy compliance."""
        issues = []
        passed_checks = []
        score = 0.8  # Default score
        
        # Extract hashtags from content
        hashtags = re.findall(r'#\w+', text_content)
        
        if not hashtags:
            if platform in [PlatformType.INSTAGRAM_POST, PlatformType.TWITTER_POST]:
                issues.append(ValidationIssue(
                    category=ValidationCategory.BRAND_CONSISTENCY,
                    severity=ValidationSeverity.LOW,
                    message="No hashtags found",
                    description=f"Hashtags improve discoverability on {platform.value}",
                    suggestion="Consider adding relevant brand and industry hashtags",
                    score_impact=-0.2
                ))
                score = 0.6
            else:
                passed_checks.append("No hashtags needed for this platform")
            
            return score, issues, passed_checks
        
        # Check brand hashtag presence
        brand_hashtags = self.brand.voice_profile.hashtag_strategy.get("brand", [])
        brand_hashtag_found = any(
            hashtag.lower() in [bh.lower() for bh in brand_hashtags] 
            for hashtag in hashtags
        )
        
        if brand_hashtag_found:
            passed_checks.append("Brand hashtags present")
            score = 1.0
        else:
            issues.append(ValidationIssue(
                category=ValidationCategory.BRAND_CONSISTENCY,
                severity=ValidationSeverity.MEDIUM,
                message="No brand hashtags found",
                description="Content should include at least one BYMB brand hashtag",
                suggestion="Add #BYMBConsultancy or #BeYourMostBeautiful",
                score_impact=-0.3
            ))
            score = 0.5
        
        # Check hashtag count for platform
        hashtag_count = len(hashtags)
        if platform == PlatformType.INSTAGRAM_POST and hashtag_count > 30:
            issues.append(ValidationIssue(
                category=ValidationCategory.PLATFORM_COMPLIANCE,
                severity=ValidationSeverity.LOW,
                message="Too many hashtags for Instagram",
                description=f"Using {hashtag_count} hashtags, Instagram limit is 30",
                suggestion="Reduce to maximum 30 hashtags",
                current_value=f"{hashtag_count} hashtags",
                expected_value="30 hashtags maximum",
                score_impact=-0.1
            ))
            score -= 0.1
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_color_contrast(
        self, 
        visual_elements: Dict[str, Any]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check color contrast for accessibility."""
        issues = []
        passed_checks = []
        score = 1.0
        
        contrast_info = visual_elements.get("contrast", {})
        min_contrast_ratio = contrast_info.get("min_ratio", 4.5)  # WCAG AA standard
        
        if min_contrast_ratio >= 4.5:
            passed_checks.append("Color contrast meets WCAG AA standards")
        elif min_contrast_ratio >= 3.0:
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.MEDIUM,
                message="Low color contrast",
                description=f"Contrast ratio {min_contrast_ratio:.1f} is below WCAG AA standard (4.5:1)",
                suggestion="Increase contrast between text and background colors",
                current_value=f"{min_contrast_ratio:.1f}:1",
                expected_value="4.5:1 minimum",
                score_impact=-0.3
            ))
            score = 0.7
        else:
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.HIGH,
                message="Poor color contrast",
                description=f"Contrast ratio {min_contrast_ratio:.1f} may make text difficult to read",
                suggestion="Significantly increase contrast between text and background",
                current_value=f"{min_contrast_ratio:.1f}:1",
                expected_value="4.5:1 minimum",
                score_impact=-0.6
            ))
            score = 0.4
        
        return score, issues, passed_checks
    
    def _check_text_readability(
        self, 
        visual_elements: Dict[str, Any], 
        text_content: str
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check text readability."""
        issues = []
        passed_checks = []
        score = 0.8  # Default score
        
        typography_info = visual_elements.get("typography", {})
        
        # Check font size
        min_font_size = typography_info.get("min_font_size", 14)
        
        if min_font_size >= 16:
            passed_checks.append("Font size excellent for readability")
            score = 1.0
        elif min_font_size >= 14:
            passed_checks.append("Font size adequate for readability")
        else:
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.MEDIUM,
                message="Small font size may affect readability",
                description=f"Minimum font size is {min_font_size}px",
                suggestion="Use at least 14px for body text, preferably 16px+",
                current_value=f"{min_font_size}px",
                expected_value="14px minimum, 16px+ preferred",
                score_impact=-0.3
            ))
            score = 0.5
        
        # Check line length and spacing
        line_height = typography_info.get("line_height", 1.5)
        if line_height < 1.2:
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.LOW,
                message="Tight line spacing may affect readability",
                description=f"Line height is {line_height}",
                suggestion="Use line height of 1.4-1.6 for better readability",
                current_value=f"{line_height}",
                expected_value="1.4-1.6",
                score_impact=-0.1
            ))
            score -= 0.1
        
        return max(score, 0.0), issues, passed_checks
    
    def _check_alternative_text(
        self, 
        visual_elements: Dict[str, Any]
    ) -> Tuple[float, List[ValidationIssue], List[str]]:
        """Check alternative text for accessibility."""
        issues = []
        passed_checks = []
        score = 1.0
        
        alt_text = visual_elements.get("alt_text", "")
        
        if not alt_text or not alt_text.strip():
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.MEDIUM,
                message="Missing alternative text",
                description="Alt text is important for screen readers and accessibility",
                suggestion="Provide descriptive alt text for all images",
                score_impact=-0.5
            ))
            score = 0.5
        elif len(alt_text) < 10:
            issues.append(ValidationIssue(
                category=ValidationCategory.ACCESSIBILITY,
                severity=ValidationSeverity.LOW,
                message="Alt text too brief",
                description="Alt text should be descriptive enough to convey image meaning",
                suggestion="Expand alt text to better describe the image content",
                current_value=f"{len(alt_text)} characters",
                expected_value="50-150 characters recommended",
                score_impact=-0.2
            ))
            score = 0.8
        else:
            passed_checks.append("Descriptive alternative text provided")
        
        return score, issues, passed_checks
    
    def _analyze_text_sentiment(self, text_content: str) -> str:
        """Simple sentiment analysis."""
        positive_words = [
            "success", "achieve", "excellent", "beautiful", "growth", "opportunity",
            "positive", "great", "amazing", "wonderful", "fantastic", "outstanding"
        ]
        
        professional_words = [
            "strategy", "professional", "business", "expertise", "proven", 
            "results", "transformation", "consulting", "strategic", "analysis"
        ]
        
        text_lower = text_content.lower()
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        professional_count = sum(1 for word in professional_words if word in text_lower)
        
        if positive_count > professional_count:
            return "positive"
        elif professional_count > 0:
            return "professional"
        else:
            return "neutral"
    
    def _calculate_overall_score(self, category_scores: Dict[ValidationCategory, float]) -> float:
        """Calculate weighted overall score."""
        # Category weights based on business importance
        weights = {
            ValidationCategory.VISUAL_IDENTITY: 0.25,
            ValidationCategory.CONTENT_VOICE: 0.25,
            ValidationCategory.PLATFORM_COMPLIANCE: 0.20,
            ValidationCategory.BRAND_CONSISTENCY: 0.20,
            ValidationCategory.ACCESSIBILITY: 0.10
        }
        
        total_score = sum(
            category_scores.get(category, 0.0) * weight
            for category, weight in weights.items()
        )
        
        return min(max(total_score, 0.0), 1.0)  # Clamp between 0 and 1
    
    def _determine_compliance_level(self, score: float) -> str:
        """Determine compliance level from score."""
        for level, threshold in sorted(self.scoring_thresholds.items(), key=lambda x: x[1], reverse=True):
            if score >= threshold:
                return level
        return "non_compliant"
    
    def _generate_recommendations(
        self, 
        issues: List[ValidationIssue], 
        category_scores: Dict[ValidationCategory, float]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # High-impact recommendations based on scores
        lowest_category = min(category_scores.items(), key=lambda x: x[1])
        if lowest_category[1] < 0.7:
            recommendations.append(
                f"Priority: Improve {lowest_category[0].value.replace('_', ' ')} (score: {lowest_category[1]:.1%})"
            )
        
        # Critical issue recommendations
        critical_issues = [issue for issue in issues if issue.severity == ValidationSeverity.CRITICAL]
        if critical_issues:
            recommendations.append(f"Address {len(critical_issues)} critical issues immediately")
        
        # Common issue patterns
        visual_issues = [issue for issue in issues if issue.category == ValidationCategory.VISUAL_IDENTITY]
        if len(visual_issues) >= 3:
            recommendations.append("Review and standardize visual brand elements")
        
        voice_issues = [issue for issue in issues if issue.category == ValidationCategory.CONTENT_VOICE]
        if len(voice_issues) >= 3:
            recommendations.append("Align content more closely with BYMB brand voice guidelines")
        
        # Specific actionable items
        if category_scores.get(ValidationCategory.PLATFORM_COMPLIANCE, 1.0) < 0.8:
            recommendations.append("Optimize content dimensions and formatting for target platform")
        
        if category_scores.get(ValidationCategory.ACCESSIBILITY, 1.0) < 0.8:
            recommendations.append("Improve accessibility with better contrast and alt text")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def get_validation_summary(self, result: ValidationResult) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            "overall_assessment": {
                "score": result.overall_score,
                "level": result.compliance_level,
                "grade": self._score_to_grade(result.overall_score)
            },
            "category_breakdown": {
                category.value: {
                    "score": score,
                    "grade": self._score_to_grade(score),
                    "status": "pass" if score >= 0.7 else "needs_improvement" if score >= 0.5 else "fail"
                }
                for category, score in result.category_scores.items()
            },
            "issue_summary": {
                "total": len(result.issues),
                "by_severity": {
                    severity.value: len([i for i in result.issues if i.severity == severity])
                    for severity in ValidationSeverity
                },
                "by_category": {
                    category.value: len([i for i in result.issues if i.category == category])
                    for category in ValidationCategory
                }
            },
            "success_metrics": {
                "passed_checks": len(result.passed_checks),
                "compliance_percentage": result.overall_score * 100,
                "ready_for_publication": result.overall_score >= 0.8 and len([
                    i for i in result.issues if i.severity == ValidationSeverity.CRITICAL
                ]) == 0
            },
            "next_steps": result.recommendations[:3]  # Top 3 recommendations
        }
    
    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
        if score >= 0.95:
            return "A+"
        elif score >= 0.90:
            return "A"
        elif score >= 0.85:
            return "A-"
        elif score >= 0.80:
            return "B+"
        elif score >= 0.75:
            return "B"
        elif score >= 0.70:
            return "B-"
        elif score >= 0.65:
            return "C+"
        elif score >= 0.60:
            return "C"
        elif score >= 0.50:
            return "C-"
        else:
            return "F"


# Global validator instance
brand_validator = BrandValidator()