"""
API Integration Examples for BYMB Social Media Optimization System

This file contains practical examples of how to integrate with the social media
optimization API endpoints for common use cases.
"""

import asyncio
import json
import httpx
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class SocialMediaAPIClient:
    """Client for interacting with the BYMB Social Media Optimization API."""
    
    def __init__(self, base_url: str = "http://localhost:8000/api"):
        """Initialize the API client.
        
        Args:
            base_url: Base URL for the API endpoints
        """
        self.base_url = base_url.rstrip('/')
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
    
    async def optimize_single_platform(
        self,
        content: str,
        platform: str,
        content_type: str = "post",
        target_audience: str = "business_leaders",
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Optimize content for a single platform.
        
        Args:
            content: Business insight or content to optimize
            platform: Target platform (linkedin, instagram, twitter, facebook)
            content_type: Type of content (post, carousel, story, etc.)
            target_audience: Target audience segment
            tone: Desired tone of voice
            
        Returns:
            Optimized content dictionary
        """
        payload = {
            "content": content,
            "platform": platform,
            "content_type": content_type,
            "target_audience": target_audience,
            "tone": tone
        }
        
        response = await self.client.post(
            f"{self.base_url}/social-media/optimize",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def create_multi_platform_campaign(
        self,
        content: str,
        platforms: List[str],
        content_types: Optional[List[str]] = None,
        target_audience: str = "business_leaders"
    ) -> Dict[str, Any]:
        """Create optimized content for multiple platforms.
        
        Args:
            content: Base content for the campaign
            platforms: List of target platforms
            content_types: List of content types for each platform
            target_audience: Target audience segment
            
        Returns:
            Multi-platform campaign dictionary
        """
        payload = {
            "content": content,
            "platforms": platforms,
            "content_types": content_types,
            "target_audience": target_audience
        }
        
        response = await self.client.post(
            f"{self.base_url}/social-media/multi-platform",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def predict_engagement(
        self,
        content: str,
        platform: str,
        content_type: str = "post",
        hashtags: List[str] = None,
        posting_time: str = "09:00",
        tone: str = "professional"
    ) -> Dict[str, Any]:
        """Predict engagement for content.
        
        Args:
            content: Content to analyze
            platform: Target platform
            content_type: Type of content
            hashtags: List of hashtags to use
            posting_time: Posting time in HH:MM format
            tone: Content tone
            
        Returns:
            Engagement prediction dictionary
        """
        payload = {
            "content": content,
            "platform": platform,
            "content_type": content_type,
            "hashtags": hashtags or [],
            "posting_time": posting_time,
            "tone": tone
        }
        
        response = await self.client.post(
            f"{self.base_url}/engagement/predict",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_optimization_recommendations(
        self,
        content: str,
        platform: str,
        current_performance: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """Get optimization recommendations for content.
        
        Args:
            content: Content to analyze
            platform: Target platform
            current_performance: Current performance metrics (optional)
            
        Returns:
            Optimization recommendations dictionary
        """
        payload = {
            "content": content,
            "platform": platform,
            "current_performance": current_performance
        }
        
        response = await self.client.post(
            f"{self.base_url}/engagement/recommendations",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def recommend_posting_time(
        self,
        content: Dict[str, Any],
        target_date: Optional[str] = None,
        avoid_conflicts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get posting time recommendation.
        
        Args:
            content: Optimized content dictionary
            target_date: Target date for posting (ISO format)
            avoid_conflicts: List of datetime strings to avoid
            
        Returns:
            Time recommendation dictionary
        """
        payload = {
            "content": content,
            "target_date": target_date,
            "avoid_conflicts": avoid_conflicts or []
        }
        
        response = await self.client.post(
            f"{self.base_url}/scheduling/recommend-time",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def track_performance(
        self,
        content_id: str,
        platform: str,
        metrics_data: Dict[str, float],
        timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """Track content performance metrics.
        
        Args:
            content_id: Unique content identifier
            platform: Platform where content was posted
            metrics_data: Performance metrics dictionary
            timestamp: Metrics timestamp (ISO format)
            
        Returns:
            Tracking confirmation dictionary
        """
        payload = {
            "content_id": content_id,
            "platform": platform,
            "metrics_data": metrics_data,
            "timestamp": timestamp or datetime.now().isoformat()
        }
        
        response = await self.client.post(
            f"{self.base_url}/performance/track",
            json=payload
        )
        response.raise_for_status()
        return response.json()
    
    async def get_platform_analytics(self, platform: str) -> Dict[str, Any]:
        """Get analytics metrics recommendations for a platform.
        
        Args:
            platform: Target platform
            
        Returns:
            Platform analytics dictionary
        """
        response = await self.client.get(
            f"{self.base_url}/analytics/platform-metrics/{platform}"
        )
        response.raise_for_status()
        return response.json()
    
    async def health_check(self) -> Dict[str, Any]:
        """Check system health status.
        
        Returns:
            Health status dictionary
        """
        response = await self.client.get(
            f"{self.base_url}/health/social-media"
        )
        response.raise_for_status()
        return response.json()


# Example Usage Functions

async def example_single_optimization():
    """Example: Optimize content for LinkedIn."""
    
    business_insight = """
    In my 23+ years of consulting experience, I've seen businesses repeatedly 
    make the same strategic planning mistake. They focus on short-term gains 
    while neglecting long-term sustainability. Here's how we helped one client 
    achieve 40% revenue growth by shifting their planning horizon.
    """
    
    async with SocialMediaAPIClient() as client:
        # Optimize for LinkedIn
        optimization = await client.optimize_single_platform(
            content=business_insight,
            platform="linkedin",
            content_type="post",
            tone="thought_leader"
        )
        
        print("LinkedIn Optimization:")
        print(f"Title: {optimization.get('title', 'N/A')}")
        print(f"Caption: {optimization['caption'][:200]}...")
        print(f"Hashtags: {', '.join(optimization['hashtags'])}")
        print(f"Optimal Time: {optimization['optimal_posting_time']}")
        print(f"Expected Engagement: {optimization['performance_predictions']['engagement_rate']*100:.1f}%")
        
        return optimization


async def example_multi_platform_campaign():
    """Example: Create a multi-platform campaign."""
    
    campaign_content = """
    Digital transformation isn't just about technology - it's about people. 
    We've guided 150+ organizations through successful digital transformations. 
    The secret? Start with culture, not code. Here are the 5 critical steps 
    that separate successful transformations from failed ones.
    """
    
    async with SocialMediaAPIClient() as client:
        # Create multi-platform campaign
        campaign = await client.create_multi_platform_campaign(
            content=campaign_content,
            platforms=["linkedin", "instagram", "twitter", "facebook"],
            target_audience="business_leaders"
        )
        
        print("Multi-Platform Campaign Results:")
        print(f"Platforms: {campaign['platforms_count']}")
        print(f"Total Content Pieces: {campaign['total_content_pieces']}")
        
        # Show optimization for each platform
        for platform, optimizations in campaign['campaign'].items():
            print(f"\n{platform.upper()}:")
            for opt in optimizations:
                print(f"  - {opt['content_type']}: {opt['caption'][:100]}...")
                print(f"    Hashtags: {len(opt['hashtags'])} tags")
                print(f"    Engagement: {opt['performance_predictions']['engagement_rate']*100:.1f}%")
        
        return campaign


async def example_engagement_prediction():
    """Example: Get engagement predictions for content."""
    
    test_content = """
    Leadership lesson from 23 years of consulting: The best leaders don't 
    have all the answers. They ask better questions. What's the most 
    powerful question you've been asked as a leader?
    """
    
    async with SocialMediaAPIClient() as client:
        # Get prediction for LinkedIn
        prediction = await client.predict_engagement(
            content=test_content,
            platform="linkedin",
            hashtags=["#Leadership", "#BusinessStrategy", "#ThoughtLeadership"],
            posting_time="09:00"
        )
        
        print("Engagement Prediction:")
        print(f"Confidence Score: {prediction['confidence_score']*100:.0f}%")
        print("\nPredicted Metrics:")
        for metric, value in prediction['predicted_metrics'].items():
            print(f"  {metric}: {value*100:.2f}%")
        
        print(f"\nKey Factors: {', '.join(prediction['key_factors'])}")
        
        print("\nOptimization Suggestions:")
        for suggestion in prediction['optimization_suggestions']:
            print(f"  • {suggestion}")
        
        if prediction['risk_factors']:
            print("\nRisk Factors:")
            for risk in prediction['risk_factors']:
                print(f"  ⚠ {risk}")
        
        return prediction


async def example_content_scheduling():
    """Example: Get posting time recommendations."""
    
    # First, create optimized content
    async with SocialMediaAPIClient() as client:
        optimization = await client.optimize_single_platform(
            content="Strategic planning insights from BYMB Consultancy",
            platform="linkedin"
        )
        
        # Get posting time recommendation
        recommendation = await client.recommend_posting_time(
            content=optimization,
            target_date=(datetime.now() + timedelta(days=1)).isoformat()
        )
        
        print("Posting Time Recommendation:")
        print(f"Recommended Time: {recommendation['recommended_time']}")
        print(f"Confidence: {recommendation['confidence_score']*100:.0f}%")
        print(f"Expected Engagement: {recommendation['expected_engagement']*100:.2f}%")
        
        print("\nReasoning:")
        for reason in recommendation['reasoning']:
            print(f"  • {reason}")
        
        print("\nAlternative Times:")
        for alt in recommendation['alternative_times'][:3]:
            time_str = datetime.fromisoformat(alt['time']).strftime('%H:%M')
            print(f"  {time_str} (score: {alt['score']:.2f})")
        
        return recommendation


async def example_performance_tracking():
    """Example: Track content performance."""
    
    # Simulate tracking performance for posted content
    content_id = "example-content-123"
    
    # Sample performance data (would come from social media APIs)
    performance_data = {
        "engagement_rate": 0.052,  # 5.2%
        "clicks": 0.018,           # 1.8%
        "comments": 0.012,         # 1.2%
        "shares": 0.008,           # 0.8%
        "impressions": 2500,
        "reach": 1800
    }
    
    async with SocialMediaAPIClient() as client:
        tracking_result = await client.track_performance(
            content_id=content_id,
            platform="linkedin",
            metrics_data=performance_data,
            timestamp=datetime.now().isoformat()
        )
        
        print("Performance Tracking Result:")
        print(f"Content ID: {tracking_result['content_id']}")
        print(f"Platform: {tracking_result['platform']}")
        print(f"Tracking Success: {tracking_result['tracking_success']}")
        
        print("\nMetrics Recorded:")
        for metric, value in tracking_result['metrics'].items():
            if isinstance(value, float) and value < 1:
                print(f"  {metric}: {value*100:.2f}%")
            else:
                print(f"  {metric}: {value:,}")
        
        print("\nComparative Performance:")
        for metric, ratio in tracking_result['comparative_performance'].items():
            status = "above" if ratio > 1 else "below"
            print(f"  {metric}: {ratio:.2f}x ({status} average)")
        
        return tracking_result


async def example_optimization_recommendations():
    """Example: Get optimization recommendations for underperforming content."""
    
    underperforming_content = """
    We offer business consulting services to help companies grow. 
    Contact us for more information about our services.
    """
    
    # Simulate current poor performance
    current_performance = {
        "engagement_rate": 0.008,  # 0.8% - below average
        "clicks": 0.002,           # 0.2% - very low
        "comments": 0.001          # 0.1% - minimal
    }
    
    async with SocialMediaAPIClient() as client:
        recommendations = await client.get_optimization_recommendations(
            content=underperforming_content,
            platform="linkedin",
            current_performance=current_performance
        )
        
        print("Optimization Recommendations:")
        print(f"Total Recommendations: {recommendations['total_recommendations']}")
        print(f"High Priority Items: {recommendations['high_priority_count']}")
        
        print("\nRecommendations (by priority):")
        for rec in recommendations['recommendations']:
            priority_stars = "★" * rec['priority']
            impact = f"+{rec['expected_impact']*100:.0f}%"
            print(f"\n{priority_stars} {rec['category'].upper()}: {rec['recommendation']}")
            print(f"   Expected Impact: {impact} | Effort: {rec['implementation_effort']}")
            print(f"   Reasoning: {rec['reasoning']}")
        
        return recommendations


async def example_platform_analytics():
    """Example: Get platform-specific analytics recommendations."""
    
    async with SocialMediaAPIClient() as client:
        # Get analytics for LinkedIn
        analytics = await client.get_platform_analytics("linkedin")
        
        print("LinkedIn Analytics Recommendations:")
        print(f"Platform: {analytics['platform']}")
        
        print("\nCore Metrics to Track:")
        for metric in analytics['metrics']['core_metrics']:
            print(f"  • {metric}")
        
        print("\nPlatform-Specific Metrics:")
        for metric in analytics['metrics']['platform_specific']:
            print(f"  • {metric}")
        
        print("\nBusiness Impact Metrics:")
        for metric in analytics['metrics']['business_metrics']:
            print(f"  • {metric}")
        
        print(f"\nRecommended Tracking Frequency: {analytics['tracking_recommendations']['frequency']}")
        
        return analytics


async def example_complete_workflow():
    """Example: Complete workflow from content creation to performance tracking."""
    
    print("=== BYMB Social Media Optimization Workflow ===\n")
    
    business_insight = """
    After helping 500+ businesses achieve transformation, I've identified the 
    #1 reason why 70% of change initiatives fail. It's not lack of strategy 
    or resources - it's resistance to letting go of what worked yesterday. 
    
    Here's how we guide leaders through the psychology of transformation:
    
    1. Acknowledge the success of past methods
    2. Create urgency around future threats
    3. Paint a vivid picture of future success
    4. Start with small, visible wins
    5. Celebrate progress and persistence
    
    The companies that master this process don't just survive change - 
    they use it as a competitive advantage.
    
    What's your experience with organizational change? What worked for you?
    """
    
    async with SocialMediaAPIClient() as client:
        print("Step 1: Health Check")
        health = await client.health_check()
        print(f"System Status: {health.get('functionality_test', 'unknown')}")
        print()
        
        print("Step 2: Multi-Platform Content Optimization")
        campaign = await client.create_multi_platform_campaign(
            content=business_insight,
            platforms=["linkedin", "instagram", "twitter"],
            target_audience="business_leaders"
        )
        print(f"✓ Generated {campaign['total_content_pieces']} pieces for {campaign['platforms_count']} platforms")
        print()
        
        print("Step 3: Engagement Prediction")
        # Get the LinkedIn optimization from the campaign
        linkedin_content = campaign['campaign']['linkedin'][0]['caption']
        prediction = await client.predict_engagement(
            content=linkedin_content,
            platform="linkedin",
            hashtags=campaign['campaign']['linkedin'][0]['hashtags']
        )
        print(f"✓ Predicted engagement rate: {prediction['predicted_metrics']['engagement_rate']*100:.1f}%")
        print(f"✓ Confidence score: {prediction['confidence_score']*100:.0f}%")
        print()
        
        print("Step 4: Posting Time Recommendation")
        recommendation = await client.recommend_posting_time(
            content=campaign['campaign']['linkedin'][0],
            target_date=(datetime.now() + timedelta(days=1)).isoformat()
        )
        recommended_time = datetime.fromisoformat(recommendation['recommended_time'])
        print(f"✓ Recommended posting time: {recommended_time.strftime('%A, %B %d at %H:%M')}")
        print()
        
        print("Step 5: Simulate Performance Tracking (after posting)")
        # Simulate good performance based on predictions
        simulated_performance = {
            "engagement_rate": prediction['predicted_metrics']['engagement_rate'] * 1.1,  # 10% better
            "clicks": prediction['predicted_metrics'].get('clicks', 0.015),
            "comments": prediction['predicted_metrics'].get('comments', 0.008),
            "shares": prediction['predicted_metrics'].get('shares', 0.003),
            "impressions": 3200,
            "reach": 2400
        }
        
        tracking = await client.track_performance(
            content_id="workflow-example-001",
            platform="linkedin",
            metrics_data=simulated_performance
        )
        print(f"✓ Performance tracked: {tracking['tracking_success']}")
        
        # Calculate performance vs prediction
        actual_engagement = simulated_performance['engagement_rate']
        predicted_engagement = prediction['predicted_metrics']['engagement_rate']
        performance_ratio = actual_engagement / predicted_engagement
        
        print(f"✓ Actual vs Predicted: {performance_ratio:.1f}x ({'+' if performance_ratio > 1 else ''}{(performance_ratio-1)*100:.0f}%)")
        print()
        
        print("Step 6: Get Analytics Recommendations")
        analytics = await client.get_platform_analytics("linkedin")
        print(f"✓ Analytics framework: {len(analytics['metrics']['core_metrics'])} core metrics")
        print()
        
        print("🎉 Complete workflow executed successfully!")
        print("\nWorkflow Summary:")
        print(f"  • Content optimized for {campaign['platforms_count']} platforms")
        print(f"  • Engagement predicted with {prediction['confidence_score']*100:.0f}% confidence")
        print(f"  • Optimal posting time identified")
        print(f"  • Performance tracking system ready")
        print(f"  • Analytics framework established")
        
        return {
            "campaign": campaign,
            "prediction": prediction,
            "recommendation": recommendation,
            "tracking": tracking,
            "analytics": analytics
        }


# Main execution function
async def main():
    """Run all examples."""
    
    print("BYMB Social Media Optimization API - Integration Examples")
    print("=" * 60)
    
    try:
        # Run individual examples
        print("\n1. Single Platform Optimization Example:")
        await example_single_optimization()
        
        print("\n" + "="*60)
        print("\n2. Multi-Platform Campaign Example:")
        await example_multi_platform_campaign()
        
        print("\n" + "="*60)
        print("\n3. Engagement Prediction Example:")
        await example_engagement_prediction()
        
        print("\n" + "="*60)
        print("\n4. Content Scheduling Example:")
        await example_content_scheduling()
        
        print("\n" + "="*60)
        print("\n5. Performance Tracking Example:")
        await example_performance_tracking()
        
        print("\n" + "="*60)
        print("\n6. Optimization Recommendations Example:")
        await example_optimization_recommendations()
        
        print("\n" + "="*60)
        print("\n7. Platform Analytics Example:")
        await example_platform_analytics()
        
        print("\n" + "="*60)
        print("\n8. Complete Workflow Example:")
        await example_complete_workflow()
        
    except Exception as e:
        print(f"Error running examples: {e}")
        print("Make sure the API server is running at http://localhost:8000")


if __name__ == "__main__":
    asyncio.run(main())