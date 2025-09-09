#!/usr/bin/env python3
"""
SMVM Price Cut Scenario

This module defines a comprehensive price cut scenario for agent-based simulation,
including competitor reactions, consumer responses, and market dynamics.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Scenario metadata
SCENARIO_NAME = "price_cut"
SCENARIO_VERSION = "1.0.0"
SCENARIO_DESCRIPTION = "Competitive price reduction scenario with market-wide implications"

class PriceCutScenario:
    """
    Price cut scenario configuration and parameters
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scenario_id = self._generate_scenario_id()

        # Scenario parameters
        self.price_cut_percentage = config.get("price_cut_percentage", 0.15)  # 15% price cut
        self.implementation_delay = config.get("implementation_delay", 7)     # 7 days
        self.market_reaction_window = config.get("market_reaction_window", 30) # 30 days
        self.competitor_reaction_probability = config.get("competitor_reaction_probability", 0.7)

        # Market impact parameters
        self.market_impact = {
            "demand_elasticity": -1.5,      # Price elasticity of demand
            "competitor_pressure": 0.8,     # Competitive response intensity
            "consumer_perception": 0.6,     # How consumers perceive the price cut
            "brand_dilution_risk": 0.3      # Risk of brand value dilution
        }

        # Consumer response models
        self.consumer_responses = {
            "price_sensitive": {
                "adoption_probability": 0.8,
                "loyalty_impact": -0.2,
                "word_of_mouth": 0.6
            },
            "value_driven": {
                "adoption_probability": 0.6,
                "loyalty_impact": 0.1,
                "word_of_mouth": 0.4
            },
            "premium_loyalists": {
                "adoption_probability": 0.2,
                "loyalty_impact": -0.5,
                "word_of_mouth": -0.3
            }
        }

        # Competitor reaction strategies
        self.competitor_strategies = {
            "aggressive_match": {
                "probability": 0.4,
                "price_response": 1.0,      # Match the price cut
                "delay_days": 3,
                "market_impact": 0.8
            },
            "selective_match": {
                "probability": 0.3,
                "price_response": 0.7,      # Partial match
                "delay_days": 7,
                "market_impact": 0.5
            },
            "no_response": {
                "probability": 0.3,
                "price_response": 0.0,      # No change
                "delay_days": 0,
                "market_impact": 0.0
            }
        }

        # Channel-specific impacts
        self.channel_impacts = {
            "seo": {
                "immediate_impact": 0.1,
                "sustained_impact": 0.3,
                "recovery_time": 60
            },
            "social": {
                "immediate_impact": 0.4,
                "sustained_impact": 0.6,
                "recovery_time": 30
            },
            "email": {
                "immediate_impact": 0.2,
                "sustained_impact": 0.4,
                "recovery_time": 45
            },
            "direct": {
                "immediate_impact": 0.3,
                "sustained_impact": 0.5,
                "recovery_time": 40
            }
        }

    def _generate_scenario_id(self) -> str:
        """Generate unique scenario identifier"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = hashlib.md5(str(hash(self)).encode()).hexdigest()[:8]
        return f"scenario_{SCENARIO_NAME}_{timestamp}_{random_part}"

    def get_scenario_config(self) -> Dict[str, Any]:
        """Get complete scenario configuration"""

        return {
            "scenario_id": self.scenario_id,
            "scenario_name": SCENARIO_NAME,
            "version": SCENARIO_VERSION,
            "description": SCENARIO_DESCRIPTION,
            "parameters": {
                "price_cut_percentage": self.price_cut_percentage,
                "implementation_delay": self.implementation_delay,
                "market_reaction_window": self.market_reaction_window,
                "competitor_reaction_probability": self.competitor_reaction_probability
            },
            "market_impact": self.market_impact,
            "consumer_responses": self.consumer_responses,
            "competitor_strategies": self.competitor_strategies,
            "channel_impacts": self.channel_impacts,
            "simulation_requirements": {
                "min_time_periods": 30,
                "recommended_models": ["consumer_bounded_rationality", "competitor_reactions", "channel_dynamics"],
                "key_metrics": ["conversion_rate", "market_share", "competitor_response", "channel_performance"]
            },
            "success_criteria": {
                "demand_increase": f">{self.price_cut_percentage * self.market_impact['demand_elasticity'] * 100:.1f}%",
                "competitor_reaction": f"{self.competitor_reaction_probability * 100:.0f}% probability",
                "channel_shift": "Expected redistribution across channels",
                "long_term_impact": "Sustainable vs. short-term effects"
            },
            "risk_factors": {
                "brand_dilution": f"{self.market_impact['brand_dilution_risk'] * 100:.0f}% risk",
                "margin_compression": f"{self.price_cut_percentage * 100:.0f}% immediate impact",
                "competitor_retaliation": "Price war potential",
                "customer_segmentation": "Different responses by customer type"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    def get_initial_conditions(self) -> Dict[str, Any]:
        """Get initial market conditions for the scenario"""

        return {
            "market_state": {
                "price_level": 1.0,  # Normalized baseline
                "demand_level": 1.0,
                "competition_intensity": 0.6,
                "consumer_sentiment": 0.7,
                "economic_conditions": 0.8
            },
            "trigger_event": {
                "event_type": "price_cut_announcement",
                "magnitude": self.price_cut_percentage,
                "timing": self.implementation_delay,
                "communication_channels": ["press_release", "website", "social_media"]
            },
            "expected_responses": {
                "consumer_segments": {
                    "price_sensitive": {"probability": 0.4, "response_time": 2},
                    "value_driven": {"probability": 0.3, "response_time": 5},
                    "premium_loyalists": {"probability": 0.1, "response_time": 10}
                },
                "competitors": {
                    "market_leader": {"reaction_probability": 0.8, "strategy": "selective_match"},
                    "close_competitor": {"reaction_probability": 0.6, "strategy": "aggressive_match"},
                    "niche_player": {"reaction_probability": 0.2, "strategy": "no_response"}
                }
            }
        }

    def get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get timeline of expected events in the scenario"""

        return [
            {
                "day": 0,
                "event": "Price cut announcement",
                "description": f"Company announces {self.price_cut_percentage * 100:.0f}% price reduction",
                "market_impact": {
                    "demand_shock": self.price_cut_percentage * 0.5,
                    "competitor_attention": 0.9,
                    "consumer_awareness": 0.3
                },
                "channel_impacts": {
                    "social": self.channel_impacts["social"]["immediate_impact"],
                    "direct": self.channel_impacts["direct"]["immediate_impact"]
                }
            },
            {
                "day": self.implementation_delay,
                "event": "Price cut implementation",
                "description": "New pricing goes into effect across all channels",
                "market_impact": {
                    "demand_response": self.price_cut_percentage * self.market_impact["demand_elasticity"],
                    "competitor_reaction_window": self.market_reaction_window,
                    "consumer_conversion": self.consumer_responses["price_sensitive"]["adoption_probability"]
                },
                "channel_impacts": {
                    "all_channels": "full_price_impact"
                }
            },
            {
                "day": self.implementation_delay + 3,
                "event": "Initial competitor responses",
                "description": "First wave of competitor reactions to price cut",
                "market_impact": {
                    "competition_intensity": self.competitor_reaction_probability * 0.3,
                    "price_pressure": self.price_cut_percentage * 0.2,
                    "market_stability": 0.7
                },
                "competitor_actions": [
                    "Price monitoring increase",
                    "Customer retention campaigns",
                    "Value proposition emphasis"
                ]
            },
            {
                "day": self.market_reaction_window,
                "event": "Market stabilization",
                "description": "Market adjusts to new competitive landscape",
                "market_impact": {
                    "new_equilibrium": "price_competition",
                    "segment_shift": "value_vs_premium",
                    "long_term_trends": "increased_price_sensitivity"
                },
                "strategic_implications": [
                    "Customer segmentation importance",
                    "Value proposition differentiation",
                    "Cost optimization focus"
                ]
            }
        ]

    def get_simulation_parameters(self) -> Dict[str, Any]:
        """Get parameters for running the simulation"""

        return {
            "scenario_type": "market_disruption",
            "disruption_type": "pricing",
            "disruption_magnitude": self.price_cut_percentage,
            "time_horizon": max(60, self.market_reaction_window + 30),
            "key_variables": [
                "demand_elasticity",
                "competitor_reaction_time",
                "consumer_response_delay",
                "channel_effectiveness",
                "brand_perception_change"
            ],
            "monte_carlo_iterations": 1000,
            "confidence_intervals": [0.80, 0.90, 0.95],
            "sensitivity_analysis": {
                "price_elasticity_range": [-2.0, -1.0],
                "reaction_probability_range": [0.5, 0.9],
                "consumer_response_range": [0.6, 0.9]
            },
            "output_metrics": [
                "conversion_rate_change",
                "market_share_change",
                "revenue_impact",
                "customer_acquisition_cost",
                "customer_lifetime_value",
                "brand_perception",
                "competitor_market_share",
                "channel_performance_distribution"
            ]
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment for the scenario"""

        return {
            "execution_risks": {
                "implementation_delays": {
                    "probability": 0.3,
                    "impact": "medium",
                    "mitigation": "Phased rollout strategy"
                },
                "competitor_retaliation": {
                    "probability": self.competitor_reaction_probability,
                    "impact": "high",
                    "mitigation": "Competitive intelligence monitoring"
                },
                "brand_dilution": {
                    "probability": self.market_impact["brand_dilution_risk"],
                    "impact": "medium",
                    "mitigation": "Premium positioning reinforcement"
                }
            },
            "market_risks": {
                "demand_overestimation": {
                    "probability": 0.4,
                    "impact": "high",
                    "mitigation": "Pilot testing and gradual rollout"
                },
                "segment_cannibalization": {
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "Customer segmentation analysis"
                },
                "economic_downturn": {
                    "probability": 0.2,
                    "impact": "high",
                    "mitigation": "Economic indicator monitoring"
                }
            },
            "operational_risks": {
                "margin_compression": {
                    "probability": 0.9,
                    "impact": "high",
                    "mitigation": "Cost optimization initiatives"
                },
                "capacity_constraints": {
                    "probability": 0.5,
                    "impact": "medium",
                    "mitigation": "Scalability planning"
                },
                "channel_conflicts": {
                    "probability": 0.3,
                    "impact": "low",
                    "mitigation": "Channel strategy alignment"
                }
            },
            "overall_risk_score": self._calculate_overall_risk(),
            "recommended_mitigations": [
                "Implement phased rollout with monitoring",
                "Establish competitor reaction monitoring",
                "Prepare contingency pricing strategies",
                "Monitor brand perception metrics",
                "Develop customer retention programs"
            ]
        }

    def _calculate_overall_risk(self) -> float:
        """Calculate overall risk score for the scenario"""

        risk_factors = [
            self.competitor_reaction_probability * 0.8,  # Competitor retaliation
            self.market_impact["brand_dilution_risk"] * 0.6,  # Brand dilution
            abs(self.market_impact["demand_elasticity"]) * 0.3,  # Demand uncertainty
            self.price_cut_percentage * 0.7  # Margin impact
        ]

        return min(1.0, sum(risk_factors) / len(risk_factors))

    def get_success_metrics(self) -> Dict[str, Any]:
        """Get success metrics and KPIs for the scenario"""

        return {
            "primary_metrics": {
                "conversion_rate_increase": {
                    "target": f">{self.price_cut_percentage * abs(self.market_impact['demand_elasticity']) * 100:.1f}%",
                    "measurement": "percentage_increase",
                    "timeframe": "30_days_post_implementation"
                },
                "market_share_gain": {
                    "target": f">{self.price_cut_percentage * 50:.1f}%",
                    "measurement": "percentage_point_increase",
                    "timeframe": "60_days_post_implementation"
                },
                "customer_acquisition_cost": {
                    "target": f"<${100 * (1 - self.price_cut_percentage):.0f}",
                    "measurement": "cost_per_acquisition",
                    "timeframe": "ongoing"
                }
            },
            "secondary_metrics": {
                "brand_perception_impact": {
                    "target": f"Δ < {self.market_impact['brand_dilution_risk'] * 20:.1f} points",
                    "measurement": "brand_perception_index",
                    "timeframe": "90_days_post_implementation"
                },
                "competitor_response_rate": {
                    "target": f"{self.competitor_reaction_probability * 100:.0f}%",
                    "measurement": "competitor_reaction_percentage",
                    "timeframe": "30_days_post_announcement"
                },
                "channel_migration": {
                    "target": "Balanced distribution",
                    "measurement": "channel_contribution_percentage",
                    "timeframe": "60_days_post_implementation"
                }
            },
            "leading_indicators": {
                "announcement_engagement": {
                    "measurement": "social_media_engagement_rate",
                    "target": ">200% of baseline"
                },
                "competitor_monitoring": {
                    "measurement": "price_change_detection_rate",
                    "target": ">95%"
                },
                "customer_inquiries": {
                    "measurement": "pricing_question_increase",
                    "target": ">150% of baseline"
                }
            },
            "lagging_indicators": {
                "revenue_impact": {
                    "measurement": "revenue_per_customer",
                    "target": f"Δ > {self.price_cut_percentage * 30:.1f}%"
                },
                "customer_lifetime_value": {
                    "measurement": "clv_change_percentage",
                    "target": f"Δ > {self.price_cut_percentage * 20:.1f}%"
                },
                "market_position": {
                    "measurement": "competitive_position_index",
                    "target": "Improvement of 15+ points"
                }
            }
        }


# Scenario interface definition
SCENARIO_INTERFACE = {
    "scenario": SCENARIO_NAME,
    "version": SCENARIO_VERSION,
    "description": SCENARIO_DESCRIPTION,
    "category": "pricing_strategy",
    "complexity": "high",
    "duration": "medium_term",
    "stakeholders": ["product", "marketing", "finance", "sales"],
    "required_models": ["consumer_bounded_rationality", "competitor_reactions", "channel_dynamics"],
    "key_variables": [
        "price_elasticity",
        "competitor_reaction_probability",
        "consumer_response_time",
        "channel_effectiveness",
        "brand_dilution_risk"
    ],
    "expected_outcomes": [
        "demand_increase",
        "market_share_gain",
        "channel_redistribution",
        "competitor_response",
        "brand_impact"
    ],
    "risk_level": "high",
    "success_probability": 0.7
}


def create_price_cut_scenario(price_cut_percentage: float = 0.15,
                            implementation_delay: int = 7) -> PriceCutScenario:
    """
    Factory function to create a price cut scenario

    Args:
        price_cut_percentage: Percentage price reduction (0.0 to 1.0)
        implementation_delay: Days until price cut takes effect

    Returns:
        Configured PriceCutScenario instance
    """

    config = {
        "price_cut_percentage": price_cut_percentage,
        "implementation_delay": implementation_delay,
        "market_reaction_window": 30,
        "competitor_reaction_probability": 0.7
    }

    return PriceCutScenario(config)


if __name__ == "__main__":
    # Example usage
    scenario = create_price_cut_scenario(price_cut_percentage=0.20, implementation_delay=5)

    print(f"Price Cut Scenario: {scenario.price_cut_percentage * 100:.0f}% reduction")
    print(f"Implementation delay: {scenario.implementation_delay} days")
    print(f"Overall risk score: {scenario._calculate_overall_risk():.2f}")

    config = scenario.get_scenario_config()
    print(f"Scenario ID: {config['scenario_id']}")

    timeline = scenario.get_timeline_events()
    print(f"Timeline events: {len(timeline)}")

    success_metrics = scenario.get_success_metrics()
    print(f"Primary metrics: {len(success_metrics['primary_metrics'])}")
