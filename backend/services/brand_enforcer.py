"""Brand Consistency Enforcer - Automatic brand compliance enforcement and correction."""

import asyncio
import re
import json
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import colorsys

from .brand_profile import BYMBBrandProfile, PlatformType, ContentType, BrandTone, bymb_brand
from .brand_validator import BrandValidator, ValidationResult, ValidationIssue, ValidationSeverity, brand_validator
from .brand_template_engine import BrandTemplateEngine, GenerationRequest, GenerationResult

logger = logging.getLogger(__name__)


class EnforcementLevel(Enum):
    """Brand enforcement strictness levels."""
    STRICT = "strict"          # No deviations allowed
    MODERATE = "moderate"      # Minor deviations with warnings
    FLEXIBLE = "flexible"      # Major deviations with corrections
    ADVISORY = "advisory"      # Only provide recommendations


class CorrectionType(Enum):
    """Types of automatic corrections."""
    COLOR_ADJUSTMENT = "color_adjustment"
    FONT_REPLACEMENT = "font_replacement"
    SIZE_ADJUSTMENT = "size_adjustment"
    LOGO_ADDITION = "logo_addition"
    TEXT_REWRITING = "text_rewriting"
    LAYOUT_CORRECTION = "layout_correction"
    CONTRAST_ENHANCEMENT = "contrast_enhancement"


@dataclass
class BrandCorrection:
    """Brand correction action."""
    type: CorrectionType
    severity: ValidationSeverity
    description: str
    original_value: str
    corrected_value: str
    confidence: float  # 0.0 to 1.0
    automatic: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EnforcementResult:
    """Brand enforcement result."""
    success: bool
    original_score: float
    corrected_score: float
    corrections_applied: List[BrandCorrection]
    recommendations: List[str]
    corrected_content: Optional[Dict[str, Any]] = None
    corrected_image_data: Optional[bytes] = None
    enforcement_metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class BrandEnforcementEngine:
    """Automatic brand compliance enforcement system."""
    
    def __init__(
        self, 
        brand_profile: BYMBBrandProfile = None,
        validator: BrandValidator = None,
        enforcement_level: EnforcementLevel = EnforcementLevel.MODERATE
    ):
        """Initialize brand enforcement engine."""
        self.brand = brand_profile or bymb_brand
        self.validator = validator or brand_validator
        self.enforcement_level = enforcement_level
        
        # Correction thresholds
        self.correction_thresholds = {
            EnforcementLevel.STRICT: 0.95,      # Correct anything below 95%
            EnforcementLevel.MODERATE: 0.80,    # Correct anything below 80%
            EnforcementLevel.FLEXIBLE: 0.60,    # Correct anything below 60%
            EnforcementLevel.ADVISORY: 0.40     # Only recommend corrections
        }
        
        # Initialize correction strategies
        self._init_correction_strategies()
        
        logger.info(f"Brand enforcement engine initialized with {enforcement_level.value} level")
    
    def _init_correction_strategies(self):
        """Initialize correction strategies for different issues."""
        self.color_corrections = {
            "non_brand_colors": self._correct_non_brand_colors,
            "insufficient_contrast": self._correct_color_contrast,
            "missing_primary_colors": self._add_primary_colors
        }
        
        self.text_corrections = {
            "prohibited_words": self._correct_prohibited_words,
            "weak_brand_vocabulary": self._enhance_brand_vocabulary,
            "inappropriate_tone": self._adjust_content_tone,
            "missing_cta": self._add_call_to_action
        }
        
        self.visual_corrections = {
            "missing_logo": self._add_brand_logo,
            "incorrect_typography": self._correct_typography,
            "poor_layout": self._improve_layout,
            "dimension_issues": self._correct_dimensions
        }
        
        self.platform_corrections = {
            "text_too_long": self._shorten_text,
            "dimension_mismatch": self._adjust_dimensions,
            "safe_zone_violations": self._fix_safe_zones
        }
    
    async def enforce_brand_compliance(
        self, 
        content: Dict[str, Any],
        platform: PlatformType,
        content_type: Optional[ContentType] = None
    ) -> EnforcementResult:
        """Enforce brand compliance on content."""
        logger.info(f"Starting brand enforcement for {platform.value} content")
        
        try:
            # Initial validation
            initial_validation = await self._validate_content(content, platform, content_type)
            original_score = initial_validation.overall_score
            
            # Check if enforcement is needed
            threshold = self.correction_thresholds[self.enforcement_level]
            
            if original_score >= threshold:
                logger.info(f"Content already compliant (score: {original_score:.2f})")
                return EnforcementResult(
                    success=True,
                    original_score=original_score,
                    corrected_score=original_score,
                    corrections_applied=[],
                    recommendations=[],
                    enforcement_metadata={
                        "enforcement_needed": False,
                        "original_compliant": True
                    }
                )
            
            # Apply corrections based on validation issues
            corrections_applied = []
            corrected_content = content.copy()
            warnings = []
            errors = []
            
            for issue in initial_validation.issues:
                correction_result = await self._apply_correction(
                    issue, corrected_content, platform, content_type
                )
                
                if correction_result:
                    corrections_applied.append(correction_result)
                    
                    if not correction_result.automatic:
                        warnings.append(f"Manual correction required: {correction_result.description}")
                else:
                    # Could not correct automatically
                    if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
                        errors.append(f"Could not auto-correct critical issue: {issue.message}")
                    else:
                        warnings.append(f"Could not auto-correct: {issue.message}")
            
            # Re-validate corrected content
            final_validation = await self._validate_content(corrected_content, platform, content_type)
            corrected_score = final_validation.overall_score
            
            # Generate recommendations for remaining issues
            recommendations = []
            for issue in final_validation.issues:
                if issue.severity in [ValidationSeverity.CRITICAL, ValidationSeverity.HIGH]:
                    recommendations.append(f"Priority: {issue.suggestion}")
                else:
                    recommendations.append(issue.suggestion)
            
            # Generate corrected image if applicable
            corrected_image_data = None
            if corrected_content.get("image_generation_needed"):
                corrected_image_data = await self._generate_corrected_image(
                    corrected_content, platform
                )
            
            success = corrected_score > original_score or len(errors) == 0
            
            logger.info(
                f"Brand enforcement completed. Score: {original_score:.2f} -> {corrected_score:.2f}, "
                f"Corrections: {len(corrections_applied)}"
            )
            
            return EnforcementResult(
                success=success,
                original_score=original_score,
                corrected_score=corrected_score,
                corrections_applied=corrections_applied,
                recommendations=recommendations[:10],  # Limit recommendations
                corrected_content=corrected_content,
                corrected_image_data=corrected_image_data,
                warnings=warnings,
                errors=errors,
                enforcement_metadata={
                    "enforcement_level": self.enforcement_level.value,
                    "threshold": threshold,
                    "total_issues_found": len(initial_validation.issues),
                    "issues_corrected": len(corrections_applied),
                    "enforcement_timestamp": datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Brand enforcement failed: {e}")
            return EnforcementResult(
                success=False,
                original_score=0.0,
                corrected_score=0.0,
                corrections_applied=[],
                recommendations=[],
                errors=[f"Enforcement failed: {str(e)}"]
            )
    
    async def _validate_content(
        self, 
        content: Dict[str, Any], 
        platform: PlatformType, 
        content_type: Optional[ContentType]
    ) -> ValidationResult:
        """Validate content using the brand validator."""
        from .brand_validator import ContentAnalysis
        
        # Prepare content analysis
        text_content = content.get("text", "")
        visual_elements = content.get("visual_elements", {})
        
        content_analysis = ContentAnalysis(
            text_content=text_content,
            visual_elements=visual_elements,
            platform_specs=content.get("platform_specs", {}),
            metadata=content.get("metadata", {})
        )
        
        return await self.validator.validate_content(content_analysis, platform, content_type)
    
    async def _apply_correction(
        self, 
        issue: ValidationIssue, 
        content: Dict[str, Any], 
        platform: PlatformType,
        content_type: Optional[ContentType]
    ) -> Optional[BrandCorrection]:
        """Apply correction for a specific validation issue."""
        try:
            # Determine correction strategy based on issue
            if "color" in issue.message.lower():
                return await self._apply_color_correction(issue, content)
            elif "font" in issue.message.lower() or "typography" in issue.message.lower():
                return await self._apply_typography_correction(issue, content)
            elif "logo" in issue.message.lower():
                return await self._apply_logo_correction(issue, content)
            elif "text" in issue.message.lower() and "length" in issue.message.lower():
                return await self._apply_text_length_correction(issue, content, platform)
            elif "prohibited" in issue.message.lower() or "vocabulary" in issue.message.lower():
                return await self._apply_text_content_correction(issue, content, content_type)
            elif "dimension" in issue.message.lower():
                return await self._apply_dimension_correction(issue, content, platform)
            elif "contrast" in issue.message.lower():
                return await self._apply_contrast_correction(issue, content)
            elif "call-to-action" in issue.message.lower():
                return await self._apply_cta_correction(issue, content, content_type)
            else:
                logger.warning(f"No correction strategy for issue: {issue.message}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to apply correction for {issue.message}: {e}")
            return None
    
    async def _apply_color_correction(self, issue: ValidationIssue, content: Dict[str, Any]) -> BrandCorrection:
        """Apply color corrections."""
        visual_elements = content.get("visual_elements", {})
        colors = visual_elements.get("colors", [])
        
        if "non-brand colors" in issue.message.lower():
            # Replace non-brand colors with brand colors
            corrected_colors = []
            brand_colors = self.brand.get_color_palette(include_secondary=True)
            brand_hex_values = [color.hex.lower() for color in brand_colors]
            
            for color in colors:
                color_hex = color.get("hex", "").lower()
                if color_hex not in brand_hex_values:
                    # Replace with closest brand color
                    closest_brand_color = self._find_closest_brand_color(color_hex)
                    corrected_colors.append({"hex": closest_brand_color.hex, "name": closest_brand_color.name})
                else:
                    corrected_colors.append(color)
            
            visual_elements["colors"] = corrected_colors
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.COLOR_ADJUSTMENT,
                severity=issue.severity,
                description="Replaced non-brand colors with approved brand colors",
                original_value=f"{len([c for c in colors if c.get('hex', '').lower() not in brand_hex_values])} non-brand colors",
                corrected_value="All brand-approved colors",
                confidence=0.9
            )
        
        elif "missing primary colors" in issue.message.lower():
            # Add primary brand color to palette
            primary_color = self.brand.primary_colors[0]  # Deep Blue
            colors.append({"hex": primary_color.hex, "name": primary_color.name, "usage": "primary"})
            visual_elements["colors"] = colors
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.COLOR_ADJUSTMENT,
                severity=issue.severity,
                description="Added primary brand color to content",
                original_value="No primary colors",
                corrected_value=f"Added {primary_color.name}",
                confidence=0.95
            )
        
        return None
    
    async def _apply_typography_correction(self, issue: ValidationIssue, content: Dict[str, Any]) -> BrandCorrection:
        """Apply typography corrections."""
        visual_elements = content.get("visual_elements", {})
        typography = visual_elements.get("typography", {})
        
        if "non-approved fonts" in issue.message.lower():
            # Replace fonts with brand fonts
            brand_fonts = self.brand.get_brand_fonts()
            approved_families = [spec.family for spec in brand_fonts.values()]
            
            fonts_used = typography.get("fonts_used", [])
            corrected_fonts = []
            
            for font in fonts_used:
                font_family = font.get("family", "")
                if font_family not in approved_families:
                    # Replace with primary brand font
                    replacement_font = brand_fonts["primary"]
                    corrected_fonts.append({"family": replacement_font.family})
                else:
                    corrected_fonts.append(font)
            
            typography["fonts_used"] = corrected_fonts
            visual_elements["typography"] = typography
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.FONT_REPLACEMENT,
                severity=issue.severity,
                description="Replaced non-approved fonts with brand fonts",
                original_value=f"Non-brand fonts detected",
                corrected_value="Brand-approved fonts only",
                confidence=0.85
            )
        
        return None
    
    async def _apply_logo_correction(self, issue: ValidationIssue, content: Dict[str, Any]) -> BrandCorrection:
        """Apply logo corrections."""
        visual_elements = content.get("visual_elements", {})
        
        if "missing" in issue.message.lower():
            # Add brand logo
            logo_variant = self.brand.logo_variants[0]  # Primary logo
            visual_elements["logo"] = {
                "present": True,
                "variant": logo_variant.name,
                "size": {"width": 120, "height": 45},
                "placement": "top-left"
            }
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.LOGO_ADDITION,
                severity=issue.severity,
                description="Added BYMB brand logo to content",
                original_value="No logo",
                corrected_value=f"Added {logo_variant.name}",
                confidence=0.95
            )
        
        elif "too small" in issue.message.lower():
            # Increase logo size
            logo = visual_elements.get("logo", {})
            size = logo.get("size", {})
            
            min_size = 80  # Minimum recommended size
            current_size = min(size.get("width", 0), size.get("height", 0))
            new_size = max(min_size, current_size * 1.5)
            
            logo["size"] = {
                "width": int(new_size * 2.67),  # Maintain aspect ratio
                "height": int(new_size)
            }
            visual_elements["logo"] = logo
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.SIZE_ADJUSTMENT,
                severity=issue.severity,
                description="Increased logo size to meet minimum requirements",
                original_value=f"{current_size}px",
                corrected_value=f"{new_size}px",
                confidence=0.9
            )
        
        return None
    
    async def _apply_text_length_correction(
        self, 
        issue: ValidationIssue, 
        content: Dict[str, Any], 
        platform: PlatformType
    ) -> BrandCorrection:
        """Apply text length corrections."""
        text_content = content.get("text", "")
        
        if "exceeds" in issue.message.lower():
            platform_specs = self.brand.get_platform_specs(platform)
            text_limits = platform_specs.text_limits if platform_specs else {}
            
            # Determine appropriate limit
            if "post" in text_limits:
                max_length = text_limits["post"]
            elif "tweet" in text_limits:
                max_length = text_limits["tweet"]
            elif "caption" in text_limits:
                max_length = text_limits["caption"]
            else:
                max_length = 280  # Default Twitter-like limit
            
            # Shorten text while preserving key messages
            shortened_text = await self._shorten_text_intelligently(text_content, max_length)
            content["text"] = shortened_text
            
            return BrandCorrection(
                type=CorrectionType.TEXT_REWRITING,
                severity=issue.severity,
                description=f"Shortened text to meet {platform.value} requirements",
                original_value=f"{len(text_content)} characters",
                corrected_value=f"{len(shortened_text)} characters",
                confidence=0.8
            )
        
        return None
    
    async def _apply_text_content_correction(
        self, 
        issue: ValidationIssue, 
        content: Dict[str, Any],
        content_type: Optional[ContentType]
    ) -> BrandCorrection:
        """Apply text content corrections."""
        text_content = content.get("text", "")
        
        if "prohibited words" in issue.message.lower():
            # Remove/replace prohibited words
            corrected_text = text_content
            avoided_words = self.brand.voice_profile.avoiding_words
            
            replacements = {
                "cheap": "cost-effective",
                "basic": "essential",
                "simple": "streamlined",
                "easy": "straightforward",
                "guaranteed": "proven approach to"
            }
            
            for avoided_word in avoided_words:
                if avoided_word.lower() in corrected_text.lower():
                    replacement = replacements.get(avoided_word.lower(), "")
                    if replacement:
                        pattern = re.compile(re.escape(avoided_word), re.IGNORECASE)
                        corrected_text = pattern.sub(replacement, corrected_text)
                    else:
                        # Remove the word entirely
                        pattern = re.compile(r'\b' + re.escape(avoided_word) + r'\b', re.IGNORECASE)
                        corrected_text = pattern.sub("", corrected_text)
                        # Clean up extra spaces
                        corrected_text = re.sub(r'\s+', ' ', corrected_text).strip()
            
            content["text"] = corrected_text
            
            return BrandCorrection(
                type=CorrectionType.TEXT_REWRITING,
                severity=issue.severity,
                description="Removed/replaced prohibited words with brand-appropriate alternatives",
                original_value="Contains prohibited words",
                corrected_value="Brand-compliant vocabulary",
                confidence=0.75
            )
        
        elif "insufficient brand vocabulary" in issue.message.lower():
            # Enhance with brand vocabulary
            enhanced_text = await self._enhance_brand_vocabulary(text_content, content_type)
            content["text"] = enhanced_text
            
            return BrandCorrection(
                type=CorrectionType.TEXT_REWRITING,
                severity=issue.severity,
                description="Enhanced text with BYMB brand vocabulary",
                original_value="Limited brand language",
                corrected_value="Enhanced brand vocabulary",
                confidence=0.7
            )
        
        return None
    
    async def _apply_dimension_correction(
        self, 
        issue: ValidationIssue, 
        content: Dict[str, Any], 
        platform: PlatformType
    ) -> BrandCorrection:
        """Apply dimension corrections."""
        visual_elements = content.get("visual_elements", {})
        dimensions = visual_elements.get("dimensions", {})
        
        platform_specs = self.brand.get_platform_specs(platform)
        if not platform_specs:
            return None
        
        current_width = dimensions.get("width", 0)
        current_height = dimensions.get("height", 0)
        
        # Find best matching platform dimension
        best_format = None
        min_diff = float('inf')
        
        for format_name, (req_width, req_height) in platform_specs.dimensions.items():
            # Calculate difference
            width_diff = abs(current_width - req_width) / req_width
            height_diff = abs(current_height - req_height) / req_height
            total_diff = width_diff + height_diff
            
            if total_diff < min_diff:
                min_diff = total_diff
                best_format = format_name
                corrected_width, corrected_height = req_width, req_height
        
        if best_format:
            dimensions["width"] = corrected_width
            dimensions["height"] = corrected_height
            visual_elements["dimensions"] = dimensions
            content["image_generation_needed"] = True
            
            return BrandCorrection(
                type=CorrectionType.SIZE_ADJUSTMENT,
                severity=issue.severity,
                description=f"Adjusted dimensions to {best_format} format",
                original_value=f"{current_width}x{current_height}",
                corrected_value=f"{corrected_width}x{corrected_height}",
                confidence=0.9
            )
        
        return None
    
    async def _apply_contrast_correction(self, issue: ValidationIssue, content: Dict[str, Any]) -> BrandCorrection:
        """Apply contrast corrections."""
        visual_elements = content.get("visual_elements", {})
        
        # Enhance contrast by adjusting colors
        visual_elements["contrast_enhanced"] = True
        visual_elements["contrast"] = {"min_ratio": 4.5}  # WCAG AA standard
        content["image_generation_needed"] = True
        
        return BrandCorrection(
            type=CorrectionType.CONTRAST_ENHANCEMENT,
            severity=issue.severity,
            description="Enhanced color contrast to meet accessibility standards",
            original_value="Low contrast",
            corrected_value="WCAG AA compliant contrast",
            confidence=0.8
        )
    
    async def _apply_cta_correction(
        self, 
        issue: ValidationIssue, 
        content: Dict[str, Any],
        content_type: Optional[ContentType]
    ) -> BrandCorrection:
        """Apply call-to-action corrections."""
        text_content = content.get("text", "")
        
        # Add appropriate CTA based on content type
        brand_ctas = self.brand.voice_profile.call_to_actions
        
        if content_type == ContentType.PROMOTIONAL:
            cta = "Transform your business potential today"
        elif content_type == ContentType.EDUCATIONAL:
            cta = "Ready to achieve business excellence?"
        elif content_type == ContentType.THOUGHT_LEADERSHIP:
            cta = "Let's craft your success strategy"
        else:
            cta = brand_ctas[0]  # Default CTA
        
        # Add CTA to text
        enhanced_text = f"{text_content.rstrip('.')}. {cta}"
        content["text"] = enhanced_text
        
        return BrandCorrection(
            type=CorrectionType.TEXT_REWRITING,
            severity=issue.severity,
            description="Added brand-appropriate call-to-action",
            original_value="No CTA",
            corrected_value=f"Added: {cta}",
            confidence=0.85
        )
    
    def _find_closest_brand_color(self, target_hex: str) -> Any:
        """Find closest brand color to target color."""
        target_rgb = self._hex_to_rgb(target_hex)
        brand_colors = self.brand.get_color_palette(include_secondary=True)
        
        min_distance = float('inf')
        closest_color = brand_colors[0]  # Default to first brand color
        
        for color in brand_colors:
            color_rgb = color.rgb
            distance = self._color_distance(target_rgb, color_rgb)
            
            if distance < min_distance:
                min_distance = distance
                closest_color = color
        
        return closest_color
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """Convert hex color to RGB."""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    def _color_distance(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> float:
        """Calculate distance between two RGB colors."""
        return sum((a - b) ** 2 for a, b in zip(color1, color2)) ** 0.5
    
    async def _shorten_text_intelligently(self, text: str, max_length: int) -> str:
        """Shorten text while preserving key brand messages."""
        if len(text) <= max_length:
            return text
        
        # Preserve brand keywords and key messages
        brand_keywords = [
            "BYMB", "transformation", "strategic", "excellence", "results",
            "Bader Abdulrahim", "consultancy", "beautiful", "business"
        ]
        
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Score sentences by brand keyword presence
        scored_sentences = []
        for sentence in sentences:
            score = sum(1 for keyword in brand_keywords if keyword.lower() in sentence.lower())
            scored_sentences.append((sentence, score))
        
        # Sort by score (keep most brand-relevant sentences)
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        
        # Build shortened text
        shortened = ""
        for sentence, score in scored_sentences:
            test_length = len(shortened) + len(sentence) + 2  # +2 for ". "
            if test_length <= max_length:
                if shortened:
                    shortened += ". "
                shortened += sentence
            else:
                break
        
        # Ensure we have some content
        if not shortened and sentences:
            # Take first sentence and truncate if needed
            shortened = sentences[0][:max_length-3] + "..."
        
        return shortened.strip()
    
    async def _enhance_brand_vocabulary(self, text: str, content_type: Optional[ContentType]) -> str:
        """Enhance text with brand vocabulary."""
        # Simple word replacements to improve brand alignment
        replacements = {
            "company": "consultancy",
            "help": "transform",
            "good": "excellent",
            "work": "strategic partnership",
            "improve": "optimize",
            "change": "transformation",
            "success": "measurable results",
            "experience": "proven expertise"
        }
        
        enhanced_text = text
        for original, replacement in replacements.items():
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
            enhanced_text = pattern.sub(replacement, enhanced_text)
        
        # Add brand-specific context if appropriate
        if content_type == ContentType.BUSINESS_INSIGHT:
            if "years" not in enhanced_text.lower() and "experience" not in enhanced_text.lower():
                enhanced_text += " Based on 23+ years of proven consultancy expertise."
        
        return enhanced_text
    
    async def _generate_corrected_image(self, content: Dict[str, Any], platform: PlatformType) -> Optional[bytes]:
        """Generate corrected image using template engine."""
        try:
            # This would integrate with the template engine
            # For now, return None as placeholder
            logger.info("Image generation requested for corrected content")
            return None
        except Exception as e:
            logger.error(f"Failed to generate corrected image: {e}")
            return None
    
    async def batch_enforce_compliance(
        self, 
        content_batch: List[Dict[str, Any]], 
        platforms: List[PlatformType]
    ) -> List[EnforcementResult]:
        """Batch enforce compliance on multiple content items."""
        results = []
        
        for i, content in enumerate(content_batch):
            platform = platforms[i] if i < len(platforms) else platforms[0]
            
            try:
                result = await self.enforce_brand_compliance(content, platform)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch enforcement failed for item {i}: {e}")
                results.append(EnforcementResult(
                    success=False,
                    original_score=0.0,
                    corrected_score=0.0,
                    corrections_applied=[],
                    recommendations=[],
                    errors=[f"Enforcement failed: {str(e)}"]
                ))
        
        return results
    
    def get_enforcement_statistics(self, results: List[EnforcementResult]) -> Dict[str, Any]:
        """Generate enforcement statistics."""
        if not results:
            return {"total_items": 0}
        
        successful_results = [r for r in results if r.success]
        
        return {
            "total_items": len(results),
            "successful_enforcements": len(successful_results),
            "average_original_score": sum(r.original_score for r in results) / len(results),
            "average_corrected_score": sum(r.corrected_score for r in results) / len(results),
            "total_corrections": sum(len(r.corrections_applied) for r in results),
            "correction_types": self._count_correction_types(results),
            "improvement_rate": len([r for r in results if r.corrected_score > r.original_score]) / len(results),
            "enforcement_level": self.enforcement_level.value,
            "statistics_timestamp": datetime.now().isoformat()
        }
    
    def _count_correction_types(self, results: List[EnforcementResult]) -> Dict[str, int]:
        """Count correction types across results."""
        correction_counts = {}
        
        for result in results:
            for correction in result.corrections_applied:
                correction_type = correction.type.value
                correction_counts[correction_type] = correction_counts.get(correction_type, 0) + 1
        
        return correction_counts
    
    async def preview_corrections(
        self, 
        content: Dict[str, Any], 
        platform: PlatformType
    ) -> Dict[str, Any]:
        """Preview what corrections would be applied without actually applying them."""
        # Validate content
        validation_result = await self._validate_content(content, platform)
        
        # Predict corrections for each issue
        predicted_corrections = []
        
        for issue in validation_result.issues:
            correction_preview = {
                "issue": issue.message,
                "severity": issue.severity.value,
                "suggested_correction": issue.suggestion,
                "auto_correctable": self._is_auto_correctable(issue),
                "confidence": self._predict_correction_confidence(issue)
            }
            predicted_corrections.append(correction_preview)
        
        return {
            "current_score": validation_result.overall_score,
            "predicted_corrections": predicted_corrections,
            "enforcement_needed": validation_result.overall_score < self.correction_thresholds[self.enforcement_level],
            "enforcement_level": self.enforcement_level.value,
            "total_issues": len(validation_result.issues),
            "auto_correctable_issues": len([c for c in predicted_corrections if c["auto_correctable"]])
        }
    
    def _is_auto_correctable(self, issue: ValidationIssue) -> bool:
        """Determine if an issue can be automatically corrected."""
        auto_correctable_keywords = [
            "color", "font", "logo", "dimension", "contrast", 
            "prohibited", "length", "call-to-action"
        ]
        
        return any(keyword in issue.message.lower() for keyword in auto_correctable_keywords)
    
    def _predict_correction_confidence(self, issue: ValidationIssue) -> float:
        """Predict confidence level for correction."""
        if issue.severity == ValidationSeverity.CRITICAL:
            return 0.9
        elif issue.severity == ValidationSeverity.HIGH:
            return 0.8
        elif issue.severity == ValidationSeverity.MEDIUM:
            return 0.7
        else:
            return 0.6


# Global enforcement engine instance
brand_enforcer = BrandEnforcementEngine()