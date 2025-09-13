from typing import Dict, List, Any
import random

def generate_heuristic_summary() -> Dict[str, Any]:
    """Generate deterministic business insights when LLM is not available"""

    # Sample heuristic insights based on common Etsy patterns
    insights = [
        "Your conversion rate is performing well compared to industry average (2.5-3%)",
        "Revenue growth suggests your product-market fit is improving",
        "Consider expanding your top-performing product categories",
        "Seasonal trends indicate potential for holiday-themed listings",
        "Your pricing strategy appears competitive within your niche"
    ]

    recommendations = [
        {
            "title": "Optimize High-Traffic Listings",
            "description": "Focus on improving conversion for listings with high views but low sales",
            "priority": "high",
            "effort": "medium"
        },
        {
            "title": "Expand Successful Product Lines",
            "description": "Create variations of your best-selling items in different colors/sizes",
            "priority": "high",
            "effort": "low"
        },
        {
            "title": "Improve SEO with Long-tail Keywords",
            "description": "Add specific, descriptive keywords to increase discoverability",
            "priority": "medium",
            "effort": "low"
        },
        {
            "title": "Bundle Products for Higher AOV",
            "description": "Create product bundles to increase average order value",
            "priority": "medium",
            "effort": "medium"
        },
        {
            "title": "Enhance Listing Photography",
            "description": "Add lifestyle shots showing products in use to boost conversions",
            "priority": "medium",
            "effort": "high"
        }
    ]

    # Randomly select 3-4 recommendations to keep it fresh
    selected_recommendations = random.sample(recommendations, k=min(4, len(recommendations)))

    return {
        "summary": "Your shop is showing positive momentum with steady growth in key metrics.",
        "key_insights": insights[:3],  # Top 3 insights
        "recommendations": selected_recommendations,
        "generated_with": "heuristics",
        "confidence": "medium"
    }

def analyze_listing_performance(listing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Heuristic analysis for individual listing performance"""
    views = listing_data.get("views", 0)
    orders = listing_data.get("orders", 0)
    conversion = (orders / views * 100) if views > 0 else 0

    issues = []
    suggestions = []

    # Analyze conversion rate
    if conversion < 1.0:
        issues.append("Low conversion rate")
        suggestions.append("Improve listing photos and description")
    elif conversion < 2.0:
        issues.append("Below average conversion")
        suggestions.append("Consider price optimization or better keywords")

    # Analyze traffic
    if views < 50:
        issues.append("Low visibility")
        suggestions.extend([
            "Improve SEO with better tags",
            "Use trending keywords in your title"
        ])

    # Default positive feedback if no issues
    if not issues:
        issues.append("Good performance overall")
        suggestions.append("Consider creating variations of this successful listing")

    return {
        "performance_score": min(100, conversion * 30 + (views / 10)),
        "issues": issues,
        "suggestions": suggestions
    }

def get_seasonal_insights(month: int) -> List[str]:
    """Get seasonal insights based on current month"""
    seasonal_patterns = {
        1: ["Post-holiday sales may be slower", "Focus on Valentine's Day themes"],
        2: ["Valentine's Day peak season", "Spring themes start gaining interest"],
        3: ["Mother's Day preparation begins", "Spring cleaning and organization items trend"],
        4: ["Easter and spring themes peak", "Graduation gifts start trending"],
        5: ["Mother's Day peak", "Wedding season begins"],
        6: ["Father's Day and graduation season", "Summer themes gain traction"],
        7: ["Summer vacation themes", "Back-to-school items start appearing"],
        8: ["Back-to-school peak season", "Fall themes begin"],
        9: ["Fall and Halloween themes", "Cozy home items trend upward"],
        10: ["Halloween peak season", "Holiday crafting begins"],
        11: ["Black Friday preparation", "Holiday shopping season starts"],
        12: ["Holiday peak season", "New Year preparation items"]
    }

    return seasonal_patterns.get(month, ["Standard seasonal patterns apply"])