# SMVM Competitors Service
# Handles competitor analysis with feature taxonomy and price normalization

"""
SMVM Competitors Service

Purpose: Analyze competitor offerings with structured feature comparison and normalized pricing
- Feature taxonomy classification and mapping
- Price normalization across currencies and models
- Competitive positioning analysis
- Market intelligence aggregation

Data Zone: AMBER (competitive intelligence) → GREEN (aggregated market insights)
Retention: 365 days for detailed analysis, indefinite for taxonomy models
"""

from typing import Dict, List, Optional, Protocol
import logging
from datetime import datetime
from pathlib import Path
import re

# Service metadata
SERVICE_NAME = "competitors"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"  # Must match SMVM requirements
DATA_ZONE = "AMBER"  # Competitive intelligence data
RETENTION_DAYS = 365

logger = logging.getLogger(__name__)


class FeatureTaxonomy:
    """
    Feature taxonomy for competitor analysis

    Standardizes feature classification across:
    - Product categories
    - Feature types
    - Capability levels
    - Technology implementations
    """

    # Product category taxonomy
    PRODUCT_CATEGORIES = {
        "checking_account": {
            "description": "Checking/debit account products",
            "subcategories": ["basic", "premium", "business", "student"]
        },
        "savings_account": {
            "description": "Savings and deposit products",
            "subcategories": ["high_yield", "cd", "money_market", "retirement"]
        },
        "credit_card": {
            "description": "Credit and charge card products",
            "subcategories": ["cashback", "travel", "business", "secured"]
        },
        "loan": {
            "description": "Lending and credit products",
            "subcategories": ["personal", "business", "mortgage", "student"]
        },
        "investment": {
            "description": "Investment and wealth management products",
            "subcategories": ["brokerage", "advisory", "retirement", "education"]
        },
        "insurance": {
            "description": "Insurance products",
            "subcategories": ["life", "health", "property", "liability"]
        },
        "payment_service": {
            "description": "Payment processing and transfer services",
            "subcategories": ["p2p", "bill_pay", "merchant", "international"]
        },
        "fintech_app": {
            "description": "Digital financial applications",
            "subcategories": ["budgeting", "investing", "banking", "lending"]
        }
    }

    # Feature taxonomy by capability type
    FEATURE_TAXONOMY = {
        "security": {
            "description": "Security and fraud protection features",
            "features": [
                "biometric_authentication",
                "two_factor_authentication",
                "encryption_at_rest",
                "fraud_detection",
                "dispute_resolution",
                "secure_messaging"
            ]
        },
        "usability": {
            "description": "User experience and accessibility features",
            "features": [
                "mobile_app",
                "web_interface",
                "voice_commands",
                "accessibility_support",
                "multilingual_support",
                "24_7_support"
            ]
        },
        "financial": {
            "description": "Core financial product features",
            "features": [
                "interest_bearing",
                "fee_free_transactions",
                "cashback_rewards",
                "investment_options",
                "insurance_coverage",
                "credit_limits"
            ]
        },
        "integration": {
            "description": "Third-party integration capabilities",
            "features": [
                "api_access",
                "webhooks",
                "open_banking",
                "partner_integrations",
                "data_export",
                "bulk_operations"
            ]
        },
        "analytics": {
            "description": "Reporting and analytics features",
            "features": [
                "spending_analytics",
                "budget_tracking",
                "investment_performance",
                "tax_reporting",
                "custom_reports",
                "real_time_alerts"
            ]
        }
    }

    @staticmethod
    def classify_features(raw_features: List[str]) -> Dict[str, List[str]]:
        """Classify raw features into taxonomy categories"""
        classified = {}

        for category, category_data in FeatureTaxonomy.FEATURE_TAXONOMY.items():
            classified[category] = []

            for feature in category_data["features"]:
                # Simple keyword matching (could be enhanced with ML)
                for raw_feature in raw_features:
                    if feature.replace("_", " ") in raw_feature.lower():
                        classified[category].append(feature)
                        break

        return classified

    @staticmethod
    def validate_category(product_category: str) -> bool:
        """Validate product category against taxonomy"""
        return product_category in FeatureTaxonomy.PRODUCT_CATEGORIES

    @staticmethod
    def get_category_features(category: str) -> List[str]:
        """Get expected features for a product category"""
        if category not in FeatureTaxonomy.PRODUCT_CATEGORIES:
            return []

        # Return features most relevant to category
        category_features = {
            "checking_account": ["mobile_app", "fee_free_transactions", "24_7_support", "fraud_detection"],
            "savings_account": ["interest_bearing", "mobile_app", "web_interface", "secure_messaging"],
            "credit_card": ["cashback_rewards", "fraud_detection", "24_7_support", "spending_analytics"],
            "loan": ["secure_messaging", "24_7_support", "web_interface", "fraud_detection"],
            "investment": ["investment_performance", "spending_analytics", "secure_messaging", "web_interface"],
            "insurance": ["24_7_support", "secure_messaging", "web_interface", "custom_reports"],
            "payment_service": ["mobile_app", "api_access", "fraud_detection", "24_7_support"],
            "fintech_app": ["mobile_app", "analytics", "api_access", "multilingual_support"]
        }

        return category_features.get(category, [])


class PriceNormalizer(Protocol):
    """Protocol for price normalization algorithms"""

    def normalize_price(self, price: Dict, target_currency: str) -> Dict:
        """Normalize price to target currency"""
        ...

    def convert_model(self, pricing_model: str, price_data: Dict) -> Dict:
        """Convert between pricing models"""
        ...

    def calculate_effective_cost(self, pricing_data: Dict, usage_scenario: Dict) -> float:
        """Calculate effective cost for usage scenario"""
        ...


class PriceNormalizationEngine:
    """
    Price normalization engine

    Handles:
    - Currency conversion
    - Pricing model standardization
    - Effective cost calculations
    - Regional price adjustments
    """

    # Currency exchange rates (sample - in production, use live rates)
    EXCHANGE_RATES = {
        "USD": 1.0,
        "EUR": 0.85,
        "GBP": 0.73,
        "JPY": 110.0,
        "CAD": 1.25,
        "AUD": 1.35
    }

    # Pricing model conversion factors
    MODEL_FACTORS = {
        "free": {"base_multiplier": 0.0, "transaction_multiplier": 0.0},
        "freemium": {"base_multiplier": 0.5, "transaction_multiplier": 0.8},
        "subscription": {"base_multiplier": 1.0, "transaction_multiplier": 0.3},
        "transaction_based": {"base_multiplier": 0.2, "transaction_multiplier": 1.0},
        "tiered": {"base_multiplier": 0.8, "transaction_multiplier": 0.6},
        "usage_based": {"base_multiplier": 0.3, "transaction_multiplier": 0.9}
    }

    @staticmethod
    def normalize_currency(amount: float, from_currency: str, to_currency: str = "USD") -> float:
        """Convert amount between currencies"""
        if from_currency not in PriceNormalizationEngine.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {from_currency}")
        if to_currency not in PriceNormalizationEngine.EXCHANGE_RATES:
            raise ValueError(f"Unsupported currency: {to_currency}")

        # Convert to USD first, then to target currency
        usd_amount = amount / PriceNormalizationEngine.EXCHANGE_RATES[from_currency]
        return usd_amount * PriceNormalizationEngine.EXCHANGE_RATES[to_currency]

    @staticmethod
    def standardize_pricing_model(pricing_data: Dict) -> Dict:
        """Standardize pricing data to common format"""
        model = pricing_data.get("model", "subscription")
        currency = pricing_data.get("currency", "USD")

        standardized = {
            "model": model,
            "currency": currency,
            "standardized_costs": {}
        }

        # Monthly equivalent cost calculation
        if model == "free":
            standardized["standardized_costs"]["monthly"] = 0.0
        elif model == "subscription":
            base_price = pricing_data.get("base_price", 0.0)
            standardized["standardized_costs"]["monthly"] = base_price
        elif model == "transaction_based":
            # Estimate based on typical usage
            transaction_fee = pricing_data.get("transaction_fee", {}).get("fixed_amount", 0.0)
            estimated_monthly = transaction_fee * 50  # Assume 50 transactions/month
            standardized["standardized_costs"]["monthly"] = estimated_monthly
        elif model == "tiered":
            # Use middle tier as reference
            tiers = pricing_data.get("tiers", [])
            if tiers:
                mid_tier = tiers[len(tiers) // 2]
                standardized["standardized_costs"]["monthly"] = mid_tier.get("price", 0.0)

        return standardized

    @staticmethod
    def calculate_price_position(offer_price: float, competitor_prices: List[float]) -> Dict:
        """Calculate price positioning relative to competitors"""
        if not competitor_prices:
            return {"position": "market_leader", "percentile": 100.0}

        sorted_prices = sorted(competitor_prices + [offer_price])
        position = sorted_prices.index(offer_price) / len(sorted_prices)

        if position <= 0.33:
            price_position = "budget"
        elif position <= 0.66:
            price_position = "mid_range"
        else:
            price_position = "premium"

        return {
            "position": price_position,
            "percentile": position * 100.0,
            "market_percentile": (len([p for p in competitor_prices if p <= offer_price]) / len(competitor_prices)) * 100.0
        }


class CompetitorAnalysisService:
    """
    Main competitor analysis service

    Provides:
    - Feature comparison and taxonomy
    - Price normalization and positioning
    - Competitive intelligence aggregation
    - Market analysis and insights
    """

    def __init__(self, config: Dict):
        self.config = config
        self.price_normalizer: Optional[PriceNormalizer] = None
        self.logger = logging.getLogger(f"{__name__}.CompetitorAnalysisService")

    def register_price_normalizer(self, normalizer: PriceNormalizer) -> None:
        """Register price normalization component"""
        self.price_normalizer = normalizer
        self.logger.info("Registered price normalizer")

    def analyze_competitor(self, competitor_data: Dict, market_context: Dict) -> Dict:
        """
        Analyze a single competitor offering

        Args:
            competitor_data: Raw competitor data
            market_context: Market analysis context

        Returns:
            Dict containing structured competitor analysis
        """
        # Classify features using taxonomy
        raw_features = competitor_data.get("features", [])
        feature_classification = FeatureTaxonomy.classify_features(raw_features)

        # Normalize pricing
        pricing_data = competitor_data.get("pricing", {})
        normalized_pricing = PriceNormalizationEngine.standardize_pricing_model(pricing_data)

        # Calculate price positioning
        offer_price = normalized_pricing["standardized_costs"].get("monthly", 0.0)
        competitor_prices = market_context.get("competitor_prices", [])
        price_positioning = PriceNormalizationEngine.calculate_price_position(offer_price, competitor_prices)

        # Generate analysis
        analysis = {
            "competitor_id": competitor_data.get("competitor_id"),
            "feature_analysis": {
                "raw_features": raw_features,
                "classified_features": feature_classification,
                "feature_completeness": len(raw_features) / max(1, len(FeatureTaxonomy.get_category_features(
                    competitor_data.get("category", ""))))
            },
            "pricing_analysis": {
                "original_pricing": pricing_data,
                "normalized_pricing": normalized_pricing,
                "price_positioning": price_positioning,
                "value_assessment": self._assess_value(feature_classification, normalized_pricing)
            },
            "competitive_positioning": {
                "strengths": self._identify_strengths(feature_classification, price_positioning),
                "weaknesses": self._identify_weaknesses(feature_classification, price_positioning),
                "market_fit": self._assess_market_fit(competitor_data, market_context)
            }
        }

        return analysis

    def compare_offerings(self, offerings: List[Dict], market_context: Dict) -> Dict:
        """
        Compare multiple competitor offerings

        Args:
            offerings: List of competitor data
            market_context: Market analysis context

        Returns:
            Dict containing comparative analysis
        """
        analyses = [self.analyze_competitor(offering, market_context) for offering in offerings]

        # Aggregate comparisons
        comparison = {
            "individual_analyses": analyses,
            "market_summary": self._generate_market_summary(analyses),
            "competitive_landscape": self._map_competitive_landscape(analyses),
            "recommendations": self._generate_competitive_recommendations(analyses),
            "metadata": {
                "analysis_timestamp": datetime.utcnow().isoformat() + "Z",
                "competitor_count": len(analyses),
                "service_version": SERVICE_VERSION,
                "python_version": PYTHON_VERSION
            }
        }

        self.logger.info(f"Completed competitive analysis of {len(offerings)} offerings")
        return comparison

    def _assess_value(self, features: Dict[str, List[str]], pricing: Dict) -> str:
        """Assess value proposition based on features and pricing"""
        feature_count = sum(len(feature_list) for feature_list in features.values())
        monthly_cost = pricing.get("standardized_costs", {}).get("monthly", 0.0)

        if feature_count >= 10 and monthly_cost <= 10:
            return "high_value"
        elif feature_count >= 5 and monthly_cost <= 25:
            return "good_value"
        elif feature_count >= 3 or monthly_cost <= 50:
            return "fair_value"
        else:
            return "low_value"

    def _identify_strengths(self, features: Dict[str, List[str]], pricing: Dict) -> List[str]:
        """Identify competitive strengths"""
        strengths = []

        # Feature strengths
        if len(features.get("security", [])) >= 3:
            strengths.append("strong_security")
        if len(features.get("usability", [])) >= 3:
            strengths.append("excellent_usability")
        if len(features.get("analytics", [])) >= 2:
            strengths.append("advanced_analytics")

        # Pricing strengths
        position = pricing.get("position", "")
        if position == "budget":
            strengths.append("competitive_pricing")
        elif position == "premium":
            strengths.append("premium_positioning")

        return strengths

    def _identify_weaknesses(self, features: Dict[str, List[str]], pricing: Dict) -> List[str]:
        """Identify competitive weaknesses"""
        weaknesses = []

        # Feature gaps
        if len(features.get("security", [])) < 2:
            weaknesses.append("limited_security")
        if len(features.get("integration", [])) < 1:
            weaknesses.append("poor_integration")
        if len(features.get("analytics", [])) < 1:
            weaknesses.append("basic_reporting")

        # Pricing issues
        position = pricing.get("position", "")
        percentile = pricing.get("percentile", 50.0)
        if position == "premium" and percentile > 80:
            weaknesses.append("overpriced")

        return weaknesses

    def _assess_market_fit(self, competitor: Dict, market_context: Dict) -> str:
        """Assess how well competitor fits market needs"""
        category = competitor.get("category", "")
        market_demand = market_context.get("category_demand", {}).get(category, 0.5)

        if market_demand >= 0.8:
            return "excellent_fit"
        elif market_demand >= 0.6:
            return "good_fit"
        elif market_demand >= 0.4:
            return "moderate_fit"
        else:
            return "poor_fit"

    def _generate_market_summary(self, analyses: List[Dict]) -> Dict:
        """Generate market-level summary from individual analyses"""
        total_competitors = len(analyses)

        # Aggregate pricing distribution
        prices = [a["pricing_analysis"]["normalized_pricing"]["standardized_costs"].get("monthly", 0.0)
                 for a in analyses if "pricing_analysis" in a]
        avg_price = sum(prices) / max(1, len(prices))

        # Feature coverage summary
        feature_counts = {}
        for analysis in analyses:
            for category, features in analysis.get("feature_analysis", {}).get("classified_features", {}).items():
                feature_counts[category] = feature_counts.get(category, 0) + len(features)

        return {
            "total_competitors": total_competitors,
            "average_price": avg_price,
            "feature_coverage": feature_counts,
            "market_saturation": "high" if total_competitors > 10 else "medium" if total_competitors > 5 else "low"
        }

    def _map_competitive_landscape(self, analyses: List[Dict]) -> Dict:
        """Map competitive positioning landscape"""
        positions = {}
        for analysis in analyses:
            price_pos = analysis.get("pricing_analysis", {}).get("price_positioning", {}).get("position", "unknown")
            positions[price_pos] = positions.get(price_pos, 0) + 1

        return {
            "price_distribution": positions,
            "dominant_strategy": max(positions.keys(), key=lambda k: positions[k]) if positions else "unknown"
        }

    def _generate_competitive_recommendations(self, analyses: List[Dict]) -> List[str]:
        """Generate strategic recommendations based on competitive analysis"""
        recommendations = []

        # Analyze market gaps
        all_features = set()
        for analysis in analyses:
            for category_features in analysis.get("feature_analysis", {}).get("classified_features", {}).values():
                all_features.update(category_features)

        if len(all_features) < 10:
            recommendations.append("opportunity_for_feature_differentiation")

        # Analyze pricing gaps
        prices = [a.get("pricing_analysis", {}).get("normalized_pricing", {}).get("standardized_costs", {}).get("monthly", 0.0)
                 for a in analyses]
        if prices and max(prices) - min(prices) > 50:
            recommendations.append("significant_pricing_opportunities")

        return recommendations


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Competitor analysis with feature taxonomy and price normalization",
    "endpoints": {
        "analyze_competitor": {
            "method": "POST",
            "path": "/api/v1/competitors/analyze",
            "input": {
                "competitor_data": "object (competitor offering data)",
                "market_context": "object (market analysis context)"
            },
            "output": {
                "analysis": "object (structured competitor analysis)",
                "recommendations": "array (strategic recommendations)"
            },
            "token_budget": 1500,
            "timeout_seconds": 300
        },
        "compare_offerings": {
            "method": "POST",
            "path": "/api/v1/competitors/compare",
            "input": {
                "offerings": "array (competitor data objects)",
                "market_context": "object (market analysis context)"
            },
            "output": {
                "comparison": "object (comparative analysis)",
                "market_summary": "object (market-level insights)",
                "competitive_landscape": "object (positioning map)"
            },
            "token_budget": 2500,
            "timeout_seconds": 600
        },
        "normalize_pricing": {
            "method": "POST",
            "path": "/api/v1/competitors/normalize-pricing",
            "input": {
                "pricing_data": "object (raw pricing information)",
                "target_currency": "string (optional target currency)"
            },
            "output": {
                "normalized_pricing": "object (standardized pricing)",
                "comparative_analysis": "object (market positioning)"
            },
            "token_budget": 800,
            "timeout_seconds": 120
        }
    },
    "failure_modes": {
        "insufficient_data": "Competitor data missing required fields",
        "taxonomy_mismatch": "Features don't match known taxonomy",
        "pricing_parse_error": "Unable to parse pricing model",
        "currency_conversion_failed": "Currency conversion not available",
        "market_context_missing": "Required market context data unavailable"
    },
    "grounding_sources": [
        "Industry analyst reports (Gartner, Forrester)",
        "Public financial disclosures and pricing pages",
        "Customer review aggregations",
        "Competitive intelligence databases",
        "Regulatory filings and public records"
    ],
    "redaction_points": [
        "Proprietary pricing strategies in logs",
        "Competitor confidential information",
        "Sensitive market intelligence data",
        "Internal competitive analysis methods"
    ],
    "observability": {
        "spans": ["feature_classification", "price_normalization", "competitive_positioning", "market_analysis"],
        "metrics": ["competitors_analyzed", "features_classified", "pricing_normalized", "analysis_completed"],
        "logs": ["taxonomy_application", "pricing_conversion", "positioning_calculation", "recommendation_generation"]
    }
}
