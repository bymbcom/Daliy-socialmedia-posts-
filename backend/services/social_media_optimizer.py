"""Multi-platform social media optimization service for BYMB Consultancy.

This service provides comprehensive social media content optimization across 
Instagram, LinkedIn, Twitter, and Facebook platforms, specifically designed
for business consultancy content.
"""

import asyncio
import re
import json
from typing import Dict, List, Optional, Tuple, Any, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import logging
from pathlib import Path

import httpx
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)


class SocialPlatform(Enum):
    """Supported social media platforms."""
    INSTAGRAM = "instagram"
    LINKEDIN = "linkedin"
    TWITTER = "twitter"
    FACEBOOK = "facebook"


class ContentType(Enum):
    """Content types for social media."""
    POST = "post"
    STORY = "story"
    CAROUSEL = "carousel"
    INFOGRAPHIC = "infographic"
    VIDEO = "video"
    ARTICLE = "article"


class ToneOfVoice(Enum):
    """Tone of voice options for BYMB Consultancy."""
    PROFESSIONAL = "professional"
    THOUGHT_LEADER = "thought_leader"
    EDUCATIONAL = "educational"
    INSPIRATIONAL = "inspirational"
    CONVERSATIONAL = "conversational"


@dataclass
class PlatformSpecs:
    """Platform-specific content specifications."""
    platform: SocialPlatform
    image_dimensions: Dict[str, Tuple[int, int]]  # content_type -> (width, height)
    video_dimensions: Dict[str, Tuple[int, int]]
    max_caption_length: int
    max_hashtags: int
    optimal_hashtags: int
    character_limits: Dict[str, int]  # content_type -> char limit
    posting_frequency: Dict[str, int]  # content_type -> posts per day
    optimal_times: List[str]  # UTC hours
    engagement_features: List[str]
    content_preferences: List[str]


@dataclass
class ContentOptimization:
    """Optimized content for a specific platform."""
    platform: SocialPlatform
    content_type: ContentType
    title: str
    caption: str
    hashtags: List[str]
    tone: ToneOfVoice
    call_to_action: str
    image_specs: Dict[str, Any]
    engagement_elements: List[str]
    optimal_posting_time: str
    performance_predictions: Dict[str, float]
    brand_compliance: Dict[str, bool]


@dataclass
class EngagementStrategy:
    """Platform-specific engagement optimization strategy."""
    platform: SocialPlatform
    content_hooks: List[str]
    interaction_prompts: List[str]
    hashtag_strategy: Dict[str, List[str]]
    posting_schedule: Dict[str, List[str]]
    engagement_tactics: List[str]
    performance_metrics: List[str]


class SocialMediaOptimizer:
    """Comprehensive social media optimization service."""
    
    def __init__(self):
        """Initialize the social media optimizer."""
        self.platform_specs = self._initialize_platform_specs()
        self.bymb_brand_guidelines = self._initialize_brand_guidelines()
        self.industry_keywords = self._initialize_industry_keywords()
        self.engagement_patterns = self._initialize_engagement_patterns()
        
        logger.info("Social media optimizer initialized with platform specifications")
    
    def _initialize_platform_specs(self) -> Dict[SocialPlatform, PlatformSpecs]:
        """Initialize platform-specific specifications."""
        return {
            SocialPlatform.INSTAGRAM: PlatformSpecs(
                platform=SocialPlatform.INSTAGRAM,
                image_dimensions={
                    "post": (1080, 1080),
                    "story": (1080, 1920),
                    "carousel": (1080, 1080),
                    "infographic": (1080, 1350)
                },
                video_dimensions={
                    "post": (1080, 1080),
                    "story": (1080, 1920),
                    "reel": (1080, 1920)
                },
                max_caption_length=2200,
                max_hashtags=30,
                optimal_hashtags=11,
                character_limits={
                    "post": 2200,
                    "story": 0,  # Text overlay
                    "bio": 150
                },
                posting_frequency={
                    "post": 1,
                    "story": 3,
                    "reel": 1
                },
                optimal_times=[
                    "06:00", "11:00", "14:00", "17:00", "19:00"
                ],
                engagement_features=[
                    "polls", "questions", "quizzes", "countdowns",
                    "slider_stickers", "location_tags", "user_tags"
                ],
                content_preferences=[
                    "visual_storytelling", "behind_the_scenes",
                    "educational_content", "user_generated_content",
                    "carousel_posts", "video_content"
                ]
            ),
            
            SocialPlatform.LINKEDIN: PlatformSpecs(
                platform=SocialPlatform.LINKEDIN,
                image_dimensions={
                    "post": (1200, 627),
                    "article": (1200, 627),
                    "infographic": (1080, 1350),
                    "carousel": (1080, 1080)
                },
                video_dimensions={
                    "post": (1280, 720),
                    "native": (1280, 720)
                },
                max_caption_length=3000,
                max_hashtags=3,
                optimal_hashtags=3,
                character_limits={
                    "post": 3000,
                    "article": 125000,
                    "headline": 120
                },
                posting_frequency={
                    "post": 1,
                    "article": 1  # per week
                },
                optimal_times=[
                    "07:45", "10:45", "12:45", "17:45"  # Business hours focus
                ],
                engagement_features=[
                    "polls", "documents", "events",
                    "professional_insights", "industry_updates"
                ],
                content_preferences=[
                    "thought_leadership", "industry_insights",
                    "professional_development", "case_studies",
                    "business_strategy", "networking_content"
                ]
            ),
            
            SocialPlatform.TWITTER: PlatformSpecs(
                platform=SocialPlatform.TWITTER,
                image_dimensions={
                    "post": (1200, 675),
                    "header": (1500, 500)
                },
                video_dimensions={
                    "post": (1280, 720),
                    "story": (1080, 1920)
                },
                max_caption_length=280,
                max_hashtags=2,
                optimal_hashtags=2,
                character_limits={
                    "tweet": 280,
                    "bio": 160
                },
                posting_frequency={
                    "tweet": 3,
                    "thread": 1
                },
                optimal_times=[
                    "09:00", "12:00", "15:00", "18:00"
                ],
                engagement_features=[
                    "polls", "threads", "spaces",
                    "retweets", "quotes", "replies"
                ],
                content_preferences=[
                    "real_time_insights", "industry_news",
                    "quick_tips", "thought_leadership",
                    "engaging_questions", "thread_content"
                ]
            ),
            
            SocialPlatform.FACEBOOK: PlatformSpecs(
                platform=SocialPlatform.FACEBOOK,
                image_dimensions={
                    "post": (1200, 630),
                    "story": (1080, 1920),
                    "cover": (820, 312)
                },
                video_dimensions={
                    "post": (1280, 720),
                    "story": (1080, 1920)
                },
                max_caption_length=63206,
                max_hashtags=2,
                optimal_hashtags=2,
                character_limits={
                    "post": 63206,
                    "story": 0
                },
                posting_frequency={
                    "post": 1,
                    "story": 2
                },
                optimal_times=[
                    "09:00", "13:00", "15:00"
                ],
                engagement_features=[
                    "polls", "events", "groups",
                    "live_videos", "stories", "reactions"
                ],
                content_preferences=[
                    "community_building", "educational_content",
                    "behind_the_scenes", "customer_stories",
                    "industry_insights", "interactive_content"
                ]
            )
        }
    
    def _initialize_brand_guidelines(self) -> Dict[str, Any]:
        """Initialize BYMB Consultancy brand guidelines."""
        return {
            "brand_voice": {
                "primary": "professional_authority",
                "secondary": "approachable_expertise",
                "tone_attributes": [
                    "confident", "knowledgeable", "trustworthy",
                    "results_oriented", "innovative", "strategic"
                ]
            },
            "messaging_pillars": [
                "business_transformation",
                "strategic_growth", 
                "operational_excellence",
                "leadership_development",
                "market_expansion",
                "digital_transformation"
            ],
            "value_propositions": [
                "23+ years of proven expertise",
                "$35M+ in client results",
                "Bahrain business leadership",
                "Strategic transformation specialist",
                "Results-driven approach"
            ],
            "prohibited_content": [
                "overly_casual_language",
                "unsubstantiated_claims",
                "competitor_criticism",
                "controversial_topics"
            ],
            "required_elements": [
                "clear_value_proposition",
                "professional_credibility",
                "action_oriented_messaging",
                "results_focus"
            ]
        }
    
    def _initialize_industry_keywords(self) -> Dict[str, List[str]]:
        """Initialize business consultancy industry keywords."""
        return {
            "primary_keywords": [
                "business_strategy", "management_consulting",
                "digital_transformation", "operational_efficiency",
                "leadership_development", "growth_strategy",
                "change_management", "process_optimization"
            ],
            "secondary_keywords": [
                "strategic_planning", "business_development",
                "performance_improvement", "organizational_development",
                "market_analysis", "competitive_advantage",
                "innovation_management", "business_intelligence"
            ],
            "location_keywords": [
                "bahrain_business", "middle_east_consulting",
                "gcc_strategy", "manama_consultancy"
            ],
            "expertise_keywords": [
                "proven_results", "experienced_consultant",
                "business_transformation", "strategic_advisor",
                "growth_specialist", "change_leader"
            ]
        }
    
    def _initialize_engagement_patterns(self) -> Dict[str, Any]:
        """Initialize platform-specific engagement patterns."""
        return {
            "question_starters": [
                "What's your biggest challenge with",
                "How do you currently approach",
                "What would success look like for",
                "Which strategy has worked best for",
                "What obstacles are preventing you from"
            ],
            "call_to_actions": {
                SocialPlatform.INSTAGRAM: [
                    "Save this post for later",
                    "Share with your team",
                    "DM us to learn more",
                    "Tag someone who needs this",
                    "Follow for daily insights"
                ],
                SocialPlatform.LINKEDIN: [
                    "Share your thoughts below",
                    "Connect for strategic discussions",
                    "What's been your experience?",
                    "Let's discuss in the comments",
                    "Share this with your network"
                ],
                SocialPlatform.TWITTER: [
                    "Retweet if you agree",
                    "What's your take?",
                    "Thread below 👇",
                    "Thoughts?",
                    "Your experience?"
                ],
                SocialPlatform.FACEBOOK: [
                    "What do you think?",
                    "Share your experience",
                    "Join the discussion",
                    "Learn more at our page",
                    "Connect with us"
                ]
            }
        }
    
    async def optimize_content_for_platform(
        self,
        content: str,
        platform: SocialPlatform,
        content_type: ContentType,
        target_audience: str = "business_leaders",
        tone: ToneOfVoice = ToneOfVoice.PROFESSIONAL
    ) -> ContentOptimization:
        """Optimize content for a specific platform.
        
        Args:
            content: Raw content to optimize
            platform: Target social media platform
            content_type: Type of content (post, story, etc.)
            target_audience: Target audience segment
            tone: Desired tone of voice
            
        Returns:
            Optimized content for the platform
        """
        specs = self.platform_specs[platform]
        
        # Adapt content length and structure
        optimized_caption = await self._adapt_caption_for_platform(
            content, platform, content_type, tone
        )
        
        # Generate platform-appropriate title
        title = await self._generate_platform_title(
            content, platform, content_type
        )
        
        # Optimize hashtags
        hashtags = await self._generate_optimized_hashtags(
            content, platform, target_audience
        )
        
        # Create call-to-action
        cta = await self._generate_platform_cta(platform, content_type)
        
        # Define image specifications
        image_specs = self._get_image_specifications(platform, content_type)
        
        # Generate engagement elements
        engagement_elements = await self._generate_engagement_elements(
            platform, content_type, content
        )
        
        # Determine optimal posting time
        optimal_time = await self._calculate_optimal_posting_time(
            platform, target_audience
        )
        
        # Predict performance
        performance_predictions = await self._predict_content_performance(
            content, platform, content_type, hashtags
        )
        
        # Check brand compliance
        brand_compliance = await self._check_brand_compliance(
            optimized_caption, hashtags, tone
        )
        
        return ContentOptimization(
            platform=platform,
            content_type=content_type,
            title=title,
            caption=optimized_caption,
            hashtags=hashtags,
            tone=tone,
            call_to_action=cta,
            image_specs=image_specs,
            engagement_elements=engagement_elements,
            optimal_posting_time=optimal_time,
            performance_predictions=performance_predictions,
            brand_compliance=brand_compliance
        )
    
    async def _adapt_caption_for_platform(
        self,
        content: str,
        platform: SocialPlatform,
        content_type: ContentType,
        tone: ToneOfVoice
    ) -> str:
        """Adapt caption length and style for platform."""
        specs = self.platform_specs[platform]
        max_length = specs.character_limits.get(content_type.value, specs.max_caption_length)
        
        # Platform-specific adaptations
        if platform == SocialPlatform.TWITTER:
            # Concise, punchy format
            adapted = await self._create_twitter_format(content, max_length)
        elif platform == SocialPlatform.LINKEDIN:
            # Professional, detailed format
            adapted = await self._create_linkedin_format(content, tone)
        elif platform == SocialPlatform.INSTAGRAM:
            # Visual storytelling format
            adapted = await self._create_instagram_format(content, content_type)
        elif platform == SocialPlatform.FACEBOOK:
            # Community-focused format
            adapted = await self._create_facebook_format(content, content_type)
        else:
            adapted = content
        
        # Ensure length compliance
        if len(adapted) > max_length:
            adapted = await self._trim_content_intelligently(adapted, max_length)
        
        return adapted
    
    async def _create_twitter_format(self, content: str, max_length: int) -> str:
        """Create Twitter-optimized format."""
        # Extract key insight
        key_insight = await self._extract_key_insight(content)
        
        # Create hook
        hooks = [
            "🎯 Key insight:",
            "💡 Strategy tip:",
            "📊 Business fact:",
            "⚡ Quick wins:",
            "🔥 Pro tip:"
        ]
        
        hook = hooks[hash(content) % len(hooks)]
        
        # Format for Twitter
        formatted = f"{hook}\n\n{key_insight}"
        
        # Add thread indicator if needed
        if len(content) > max_length * 0.8:
            formatted += "\n\n🧵 Thread below"
        
        return formatted
    
    async def _create_linkedin_format(self, content: str, tone: ToneOfVoice) -> str:
        """Create LinkedIn-optimized format."""
        # Professional opening
        professional_openers = [
            "In my 23+ years of consulting experience,",
            "Having helped businesses achieve $35M+ in results,",
            "Strategic transformation often begins with",
            "Successful business leaders understand that",
            "The key to sustainable growth lies in"
        ]
        
        opener = professional_openers[hash(content) % len(professional_openers)]
        
        # Structure content with line breaks for readability
        paragraphs = content.split('\n')
        formatted_paragraphs = []
        
        for para in paragraphs[:3]:  # Keep main points
            if para.strip():
                formatted_paragraphs.append(para.strip())
        
        # Add strategic insights
        formatted = f"{opener}\n\n"
        formatted += "\n\n".join(formatted_paragraphs)
        formatted += "\n\n💼 What's been your experience with this approach?"
        
        return formatted
    
    async def _create_instagram_format(self, content: str, content_type: ContentType) -> str:
        """Create Instagram-optimized format."""
        if content_type == ContentType.STORY:
            # Story format - very concise
            return await self._extract_key_insight(content)
        
        # Post format with visual storytelling
        story_starters = [
            "🎯 Here's what 23+ years in consulting taught me:",
            "💡 The strategy that helped clients achieve $35M+ results:",
            "📊 Behind every successful transformation:",
            "⚡ The one thing that separates thriving businesses:",
            "🔥 What most business leaders get wrong about growth:"
        ]
        
        starter = story_starters[hash(content) % len(story_starters)]
        
        # Format with emojis and line breaks
        formatted = f"{starter}\n\n"
        
        # Break into digestible chunks
        chunks = content.split('.')[:3]  # First 3 key points
        for i, chunk in enumerate(chunks, 1):
            if chunk.strip():
                formatted += f"{i}. {chunk.strip()}\n"
        
        formatted += "\n💬 What resonates most with your experience?"
        
        return formatted
    
    async def _create_facebook_format(self, content: str, content_type: ContentType) -> str:
        """Create Facebook-optimized format."""
        # Community-focused opening
        community_openers = [
            "Fellow business leaders, let's talk about",
            "I've been reflecting on what makes businesses truly successful:",
            "After helping companies achieve remarkable results,",
            "Something I see consistently across successful organizations:",
            "Here's an insight that could transform your business approach:"
        ]
        
        opener = community_openers[hash(content) % len(community_openers)]
        
        # Create conversational format
        formatted = f"{opener}\n\n{content}\n\n"
        formatted += "👥 What has your experience been? I'd love to hear your thoughts and insights in the comments below."
        
        return formatted
    
    async def _generate_optimized_hashtags(
        self,
        content: str,
        platform: SocialPlatform,
        target_audience: str
    ) -> List[str]:
        """Generate optimized hashtags for platform and content."""
        specs = self.platform_specs[platform]
        
        # Base hashtags for BYMB Consultancy
        base_hashtags = [
            "#BusinessStrategy",
            "#ManagementConsulting", 
            "#BahrainBusiness",
            "#StrategicGrowth",
            "#BusinessTransformation"
        ]
        
        # Content-specific hashtags
        content_lower = content.lower()
        content_hashtags = []
        
        for category, keywords in self.industry_keywords.items():
            for keyword in keywords:
                if keyword.replace('_', ' ') in content_lower:
                    hashtag = '#' + ''.join(word.capitalize() for word in keyword.split('_'))
                    content_hashtags.append(hashtag)
        
        # Platform-specific hashtag strategies
        if platform == SocialPlatform.LINKEDIN:
            # Professional, industry-focused hashtags
            linkedin_hashtags = [
                "#ThoughtLeadership", "#BusinessGrowth", "#Leadership",
                "#Innovation", "#Strategy", "#Consulting"
            ]
            all_hashtags = base_hashtags + content_hashtags + linkedin_hashtags
        
        elif platform == SocialPlatform.INSTAGRAM:
            # Broader, discoverable hashtags
            instagram_hashtags = [
                "#Entrepreneur", "#BusinessTips", "#Success",
                "#Growth", "#Mindset", "#Leadership",
                "#BusinessOwner", "#Strategy", "#Consulting",
                "#Results", "#Transformation"
            ]
            all_hashtags = base_hashtags + content_hashtags + instagram_hashtags
        
        elif platform == SocialPlatform.TWITTER:
            # Trending and conversation hashtags
            twitter_hashtags = [
                "#BusinessStrategy", "#Leadership", "#Growth"
            ]
            all_hashtags = base_hashtags[:2] + twitter_hashtags  # Twitter limit
        
        elif platform == SocialPlatform.FACEBOOK:
            # Community and local hashtags
            facebook_hashtags = [
                "#BusinessGrowth", "#Consulting"
            ]
            all_hashtags = base_hashtags[:1] + facebook_hashtags
        
        # Remove duplicates and limit to platform specs
        unique_hashtags = list(dict.fromkeys(all_hashtags))
        return unique_hashtags[:specs.optimal_hashtags]
    
    async def _generate_platform_cta(
        self,
        platform: SocialPlatform,
        content_type: ContentType
    ) -> str:
        """Generate platform-appropriate call-to-action."""
        platform_ctas = self.engagement_patterns["call_to_actions"][platform]
        return platform_ctas[hash(f"{platform}{content_type}") % len(platform_ctas)]
    
    def _get_image_specifications(
        self,
        platform: SocialPlatform,
        content_type: ContentType
    ) -> Dict[str, Any]:
        """Get image specifications for platform and content type."""
        specs = self.platform_specs[platform]
        dimensions = specs.image_dimensions.get(
            content_type.value,
            specs.image_dimensions.get("post", (1080, 1080))
        )
        
        return {
            "dimensions": dimensions,
            "aspect_ratio": dimensions[0] / dimensions[1],
            "format": "PNG" if content_type == ContentType.INFOGRAPHIC else "JPEG",
            "quality": 95,
            "color_profile": "sRGB",
            "brand_elements_required": True,
            "text_overlay_guidelines": {
                "max_text_percentage": 20,
                "font_family": "professional_sans_serif",
                "brand_colors": True,
                "readability_check": True
            }
        }
    
    async def _generate_engagement_elements(
        self,
        platform: SocialPlatform,
        content_type: ContentType,
        content: str
    ) -> List[str]:
        """Generate platform-specific engagement elements."""
        specs = self.platform_specs[platform]
        available_features = specs.engagement_features
        
        # Select relevant engagement elements based on content
        selected_elements = []
        
        if "poll" in available_features and "?" in content:
            selected_elements.append("poll_question")
        
        if "questions" in available_features:
            selected_elements.append("engagement_question")
        
        if platform == SocialPlatform.LINKEDIN and "insights" in available_features:
            selected_elements.append("professional_insight_request")
        
        if platform == SocialPlatform.INSTAGRAM and content_type == ContentType.STORY:
            selected_elements.extend(["question_sticker", "poll_sticker"])
        
        return selected_elements
    
    async def _calculate_optimal_posting_time(
        self,
        platform: SocialPlatform,
        target_audience: str
    ) -> str:
        """Calculate optimal posting time for platform and audience."""
        specs = self.platform_specs[platform]
        base_times = specs.optimal_times
        
        # Adjust for Bahrain timezone and business audience
        if target_audience == "business_leaders":
            # Focus on business hours for professional content
            business_hours = ["07:00", "09:00", "11:00", "14:00", "16:00"]
            optimal_times = [t for t in base_times if t in business_hours]
            return optimal_times[0] if optimal_times else base_times[0]
        
        return base_times[0]  # Default to first optimal time
    
    async def _predict_content_performance(
        self,
        content: str,
        platform: SocialPlatform,
        content_type: ContentType,
        hashtags: List[str]
    ) -> Dict[str, float]:
        """Predict content performance based on optimization factors."""
        # Simplified performance prediction algorithm
        base_score = 0.6
        
        # Content quality factors
        if len(content) > 100:
            base_score += 0.1
        if "?" in content:  # Engagement question
            base_score += 0.1
        if any(keyword in content.lower() for keyword in self.industry_keywords["primary_keywords"]):
            base_score += 0.1
        
        # Platform optimization factors
        specs = self.platform_specs[platform]
        if len(hashtags) == specs.optimal_hashtags:
            base_score += 0.1
        
        # BYMB brand elements
        brand_elements = ["strategy", "growth", "results", "transformation", "consulting"]
        if any(element in content.lower() for element in brand_elements):
            base_score += 0.1
        
        return {
            "engagement_rate": min(base_score, 1.0),
            "reach_potential": min(base_score * 0.8, 1.0),
            "conversion_likelihood": min(base_score * 0.6, 1.0),
            "brand_alignment": min(base_score * 1.1, 1.0)
        }
    
    async def _check_brand_compliance(
        self,
        caption: str,
        hashtags: List[str],
        tone: ToneOfVoice
    ) -> Dict[str, bool]:
        """Check content compliance with BYMB brand guidelines."""
        guidelines = self.bymb_brand_guidelines
        
        # Check tone compliance
        tone_compliant = tone in [ToneOfVoice.PROFESSIONAL, ToneOfVoice.THOUGHT_LEADER]
        
        # Check messaging pillars
        pillars = guidelines["messaging_pillars"]
        pillar_present = any(
            pillar.replace('_', ' ') in caption.lower() 
            for pillar in pillars
        )
        
        # Check prohibited content
        prohibited = guidelines["prohibited_content"]
        no_prohibited_content = not any(
            prohibited_item.replace('_', ' ') in caption.lower()
            for prohibited_item in prohibited
        )
        
        # Check value propositions
        value_props = guidelines["value_propositions"] 
        value_prop_present = any(
            prop.lower() in caption.lower() for prop in value_props
        )
        
        return {
            "tone_appropriate": tone_compliant,
            "messaging_aligned": pillar_present,
            "content_compliant": no_prohibited_content,
            "value_proposition_included": value_prop_present,
            "overall_compliant": all([
                tone_compliant, pillar_present, 
                no_prohibited_content, value_prop_present
            ])
        }
    
    async def _extract_key_insight(self, content: str) -> str:
        """Extract the key insight from content."""
        sentences = content.split('.')
        # Return first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 50:
                return sentence.strip() + '.'
        return content[:200] + '...' if len(content) > 200 else content
    
    async def _trim_content_intelligently(self, content: str, max_length: int) -> str:
        """Intelligently trim content to fit length requirements."""
        if len(content) <= max_length:
            return content
        
        # Try to end at sentence boundary
        sentences = content.split('.')
        trimmed = ""
        
        for sentence in sentences:
            if len(trimmed + sentence + '.') <= max_length - 3:  # Reserve space for "..."
                trimmed += sentence + '.'
            else:
                break
        
        if not trimmed:  # If no complete sentences fit, truncate with word boundary
            words = content[:max_length - 3].split()
            trimmed = ' '.join(words[:-1])
        
        return trimmed.rstrip() + '...'
    
    async def generate_multi_platform_campaign(
        self,
        base_content: str,
        platforms: List[SocialPlatform],
        content_types: Optional[List[ContentType]] = None,
        target_audience: str = "business_leaders"
    ) -> Dict[SocialPlatform, List[ContentOptimization]]:
        """Generate optimized content for multiple platforms."""
        if content_types is None:
            content_types = [ContentType.POST]
        
        campaign_content = {}
        
        for platform in platforms:
            platform_content = []
            for content_type in content_types:
                # Skip unsupported combinations
                if self._is_valid_platform_content_type(platform, content_type):
                    optimized = await self.optimize_content_for_platform(
                        base_content, platform, content_type, target_audience
                    )
                    platform_content.append(optimized)
            
            campaign_content[platform] = platform_content
        
        return campaign_content
    
    def _is_valid_platform_content_type(
        self,
        platform: SocialPlatform,
        content_type: ContentType
    ) -> bool:
        """Check if platform supports the content type."""
        specs = self.platform_specs[platform]
        
        # Check if platform has specifications for this content type
        return (
            content_type.value in specs.image_dimensions or
            content_type.value in specs.character_limits or
            content_type == ContentType.POST  # All platforms support posts
        )
    
    async def get_platform_analytics_metrics(
        self, 
        platform: SocialPlatform
    ) -> Dict[str, List[str]]:
        """Get recommended analytics metrics for platform."""
        base_metrics = [
            "impressions", "reach", "engagement_rate", 
            "clicks", "saves", "shares"
        ]
        
        platform_specific = {
            SocialPlatform.INSTAGRAM: [
                "story_completion_rate", "profile_visits", 
                "website_clicks", "reel_plays"
            ],
            SocialPlatform.LINKEDIN: [
                "connection_requests", "company_page_views",
                "thought_leadership_score", "professional_clicks"
            ],
            SocialPlatform.TWITTER: [
                "retweets", "quote_tweets", "thread_views",
                "profile_clicks", "hashtag_performance"
            ],
            SocialPlatform.FACEBOOK: [
                "page_likes", "post_reactions", "event_responses",
                "video_completion_rate", "community_engagement"
            ]
        }
        
        return {
            "core_metrics": base_metrics,
            "platform_specific": platform_specific.get(platform, []),
            "business_metrics": [
                "lead_generation", "consultation_inquiries",
                "website_traffic", "brand_awareness_lift"
            ]
        }
    
    async def generate_posting_schedule(
        self,
        platforms: List[SocialPlatform],
        content_frequency: Dict[SocialPlatform, int],
        timezone: str = "Asia/Bahrain"
    ) -> Dict[str, Dict[SocialPlatform, List[str]]]:
        """Generate optimized posting schedule."""
        schedule = {}
        days_of_week = [
            "monday", "tuesday", "wednesday", 
            "thursday", "friday", "saturday", "sunday"
        ]
        
        for day in days_of_week:
            schedule[day] = {}
            for platform in platforms:
                specs = self.platform_specs[platform]
                frequency = content_frequency.get(platform, 1)
                
                # Distribute posting times throughout the day
                day_schedule = []
                optimal_times = specs.optimal_times
                
                # Adjust for business days (reduced weekend posting)
                if day in ["saturday", "sunday"]:
                    frequency = max(1, frequency // 2)
                    optimal_times = optimal_times[:2]  # Fewer times on weekends
                
                # Select times based on frequency
                selected_times = optimal_times[:frequency] if frequency <= len(optimal_times) else optimal_times
                
                schedule[day][platform] = selected_times
        
        return schedule