#!/usr/bin/env python3
"""
SMVM Economic Downturn Scenario

This module defines a comprehensive economic downturn scenario for agent-based simulation,
including consumer behavior changes, competitor reactions, and market contraction dynamics.
"""

import json
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Scenario metadata
SCENARIO_NAME = "downturn"
SCENARIO_VERSION = "1.0.0"
SCENARIO_DESCRIPTION = "Economic downturn scenario with market contraction and behavioral shifts"

class DownturnScenario:
    """
    Economic downturn scenario configuration and parameters
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scenario_id = self._generate_scenario_id()

        # Scenario parameters
        self.downturn_severity = config.get("severity", 0.7)      # 0-1 scale of economic impact
        self.downturn_duration = config.get("duration", 24)       # Months of downturn
        self.recovery_rate = config.get("recovery_rate", 0.3)     # Speed of economic recovery
        self.consumer_confidence_impact = config.get("confidence_impact", 0.8)

        # Market impact parameters
        self.market_impact = {
            "demand_contraction": self.downturn_severity * 0.8,
            "price_sensitivity_increase": self.downturn_severity * 0.9,
            "brand_loyalty_decay": self.consumer_confidence_impact * 0.6,
            "competition_intensity": self.downturn_severity * 0.7,
            "innovation_budget_cuts": self.downturn_severity * 0.8
        }

        # Consumer behavior shifts
        self.consumer_behavior = {
            "price_focused": {
                "adoption_probability": self.downturn_severity * 0.9,
                "switching_likelihood": self.consumer_confidence_impact * 0.8,
                "feature_importance": 0.3,
                "brand_importance": 0.4
            },
            "value_conscious": {
                "adoption_probability": self.downturn_severity * 0.7,
                "switching_likelihood": self.consumer_confidence_impact * 0.6,
                "feature_importance": 0.5,
                "brand_importance": 0.6
            },
            "loyalty_driven": {
                "adoption_probability": (1 - self.downturn_severity) * 0.8,
                "switching_likelihood": self.consumer_confidence_impact * 0.3,
                "feature_importance": 0.7,
                "brand_importance": 0.9
            },
            "discretionary_cutters": {
                "adoption_probability": self.downturn_severity * 0.6,
                "switching_likelihood": self.consumer_confidence_impact * 0.9,
                "feature_importance": 0.4,
                "brand_importance": 0.3
            }
        }

        # Competitor survival strategies
        self.competitor_strategies = {
            "cost_optimization": {
                "probability": self.downturn_severity * 0.8,
                "effectiveness": 0.7,
                "implementation_time": 3,
                "resource_impact": 0.6
            },
            "price_defense": {
                "probability": self.downturn_severity * 0.9,
                "effectiveness": 0.8,
                "implementation_time": 2,
                "resource_impact": 0.8
            },
            "market_consolidation": {
                "probability": self.downturn_severity * 0.5,
                "effectiveness": 0.9,
                "implementation_time": 6,
                "resource_impact": 0.9
            },
            "innovation_pivot": {
                "probability": (1 - self.downturn_severity) * 0.6,
                "effectiveness": 0.5,
                "implementation_time": 9,
                "resource_impact": 0.4
            },
            "exit_strategy": {
                "probability": self.downturn_severity * 0.3,
                "effectiveness": 1.0,
                "implementation_time": 12,
                "resource_impact": 0.0
            }
        }

        # Channel effectiveness changes
        self.channel_changes = {
            "organic_search": {
                "demand_shift": -self.downturn_severity * 0.6,
                "cost_efficiency": self.downturn_severity * 0.4,
                "conversion_trends": "stable"
            },
            "paid_advertising": {
                "demand_shift": -self.downturn_severity * 0.8,
                "cost_efficiency": -self.downturn_severity * 0.6,
                "conversion_trends": "declining"
            },
            "social_media": {
                "demand_shift": -self.downturn_severity * 0.4,
                "cost_efficiency": self.downturn_severity * 0.3,
                "conversion_trends": "stable"
            },
            "direct_sales": {
                "demand_shift": -self.downturn_severity * 0.9,
                "cost_efficiency": -self.downturn_severity * 0.7,
                "conversion_trends": "declining"
            },
            "email_marketing": {
                "demand_shift": -self.downturn_severity * 0.3,
                "cost_efficiency": self.downturn_severity * 0.5,
                "conversion_trends": "improving"
            }
        }

        # Recovery phases
        self.recovery_phases = {
            "contraction_phase": {
                "duration": self.downturn_duration * 0.4,
                "demand_multiplier": 0.7,
                "confidence_level": 0.4
            },
            "stabilization_phase": {
                "duration": self.downturn_duration * 0.3,
                "demand_multiplier": 0.85,
                "confidence_level": 0.6
            },
            "recovery_phase": {
                "duration": self.downturn_duration * 0.3,
                "demand_multiplier": 1.0,
                "confidence_level": 0.8
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
                "downturn_severity": self.downturn_severity,
                "downturn_duration": self.downturn_duration,
                "recovery_rate": self.recovery_rate,
                "consumer_confidence_impact": self.consumer_confidence_impact
            },
            "market_impact": self.market_impact,
            "consumer_behavior": self.consumer_behavior,
            "competitor_strategies": self.competitor_strategies,
            "channel_changes": self.channel_changes,
            "recovery_phases": self.recovery_phases,
            "simulation_requirements": {
                "min_time_periods": self.downturn_duration * 30,
                "recommended_models": ["consumer_bounded_rationality", "competitor_reactions", "channel_dynamics"],
                "key_metrics": ["demand_contraction", "price_sensitivity", "competitor_survival", "channel_shift"]
            },
            "success_criteria": {
                "demand_preservation": f"<{self.market_impact['demand_contraction'] * 100:.0f}% contraction",
                "price_defense": f"<{self.market_impact['price_sensitivity_increase'] * 50:.0f}% margin erosion",
                "market_share_maintenance": ">90% market share retention",
                "cash_position": "Positive cash flow maintained"
            },
            "risk_factors": {
                "insolvency_risk": f"{self.downturn_severity * 100:.0f}% probability",
                "market_exit": f"{self.competitor_strategies['exit_strategy']['probability'] * 100:.0f}% competitor exit rate",
                "brand_damage": f"{self.market_impact['brand_loyalty_decay'] * 100:.0f}% loyalty erosion",
                "recovery_delay": "Extended time to market recovery"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    def get_initial_conditions(self) -> Dict[str, Any]:
        """Get initial market conditions for the scenario"""

        return {
            "market_state": {
                "economic_indicators": {
                    "gdp_growth": -self.downturn_severity * 0.05,
                    "unemployment_rate": self.downturn_severity * 0.03,
                    "consumer_confidence": 1.0 - self.consumer_confidence_impact
                },
                "demand_level": 1.0 - self.market_impact["demand_contraction"],
                "price_sensitivity": 1.0 + self.market_impact["price_sensitivity_increase"],
                "competition_intensity": 1.0 + self.market_impact["competition_intensity"],
                "market_stability": 0.6
            },
            "trigger_event": {
                "event_type": "economic_downturn_signal",
                "magnitude": self.downturn_severity,
                "timing": 0,
                "indicators": ["economic_data_release", "market_volatility", "consumer_sentiment_drop"]
            },
            "expected_responses": {
                "consumer_segments": {
                    "price_focused": {
                        "response_time": 7,
                        "behavior_shift": self.consumer_behavior["price_focused"]["switching_likelihood"],
                        "spending_reduction": self.downturn_severity * 0.8
                    },
                    "value_conscious": {
                        "response_time": 14,
                        "behavior_shift": self.consumer_behavior["value_conscious"]["switching_likelihood"],
                        "spending_reduction": self.downturn_severity * 0.6
                    },
                    "loyalty_driven": {
                        "response_time": 21,
                        "behavior_shift": self.consumer_behavior["loyalty_driven"]["switching_likelihood"],
                        "spending_reduction": self.downturn_severity * 0.3
                    }
                },
                "competitors": {
                    "aggressive_competitors": {
                        "reaction_probability": self.competitor_strategies["price_defense"]["probability"],
                        "strategy_preference": "price_defense",
                        "survival_probability": 0.8
                    },
                    "defensive_competitors": {
                        "reaction_probability": self.competitor_strategies["cost_optimization"]["probability"],
                        "strategy_preference": "cost_optimization",
                        "survival_probability": 0.9
                    },
                    "weak_competitors": {
                        "reaction_probability": self.competitor_strategies["exit_strategy"]["probability"],
                        "strategy_preference": "exit_strategy",
                        "survival_probability": 0.4
                    }
                }
            }
        }

    def get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get timeline of expected events in the scenario"""

        return [
            {
                "month": 0,
                "event": "Economic downturn signal",
                "description": f"Economic indicators signal downturn with {self.downturn_severity * 100:.0f}% severity impact",
                "market_impact": {
                    "demand_shock": -self.market_impact["demand_contraction"],
                    "confidence_drop": -self.consumer_confidence_impact,
                    "competition_increase": self.market_impact["competition_intensity"]
                },
                "consumer_responses": {
                    "immediate_reaction": "spending_caution",
                    "primary_concern": "job_security"
                }
            },
            {
                "month": 3,
                "event": "Consumer behavior shift",
                "description": "Clear patterns emerge in consumer spending and purchasing behavior",
                "market_impact": {
                    "price_sensitivity": self.market_impact["price_sensitivity_increase"] * 0.6,
                    "brand_loyalty": -self.market_impact["brand_loyalty_decay"] * 0.4,
                    "channel_shift": "cost_conscious_channels"
                },
                "behavioral_changes": {
                    "switching_behavior": self.consumer_behavior["price_focused"]["switching_likelihood"],
                    "feature_vs_price": "price_domination"
                }
            },
            {
                "month": 6,
                "event": "Competitor consolidation begins",
                "description": "Market consolidation and competitor rationalization accelerates",
                "market_impact": {
                    "competition_reduction": -self.competitor_strategies["exit_strategy"]["probability"] * 0.5,
                    "price_pressure": self.competitor_strategies["price_defense"]["effectiveness"] * 0.7,
                    "market_stability": 0.5
                },
                "competitor_actions": [
                    "Cost cutting initiatives",
                    "Strategic acquisitions",
                    "Market exit considerations"
                ]
            },
            {
                "month": 12,
                "event": "Market bottom formation",
                "description": "Economic indicators suggest market has reached cyclical bottom",
                "market_impact": {
                    "stabilization_signals": 0.7,
                    "recovery_expectations": self.recovery_rate * 0.5,
                    "investor_sentiment": 0.4
                },
                "strategic_implications": [
                    "Positioning for recovery",
                    "Cost structure optimization",
                    "Market share protection"
                ]
            },
            {
                "month": self.downturn_duration,
                "event": "Recovery phase begins",
                "description": "Economic recovery signals emerge, market begins gradual improvement",
                "market_impact": {
                    "demand_recovery": self.recovery_phases["recovery_phase"]["demand_multiplier"],
                    "confidence_restoration": self.recovery_phases["recovery_phase"]["confidence_level"],
                    "competitive_restructuring": "post_downturn_landscape"
                },
                "recovery_indicators": [
                    "Economic data improvement",
                    "Consumer confidence rebound",
                    "Competitive landscape stabilization"
                ]
            }
        ]

    def get_simulation_parameters(self) -> Dict[str, Any]:
        """Get parameters for running the simulation"""

        return {
            "scenario_type": "economic_disruption",
            "disruption_type": "downturn",
            "disruption_magnitude": self.downturn_severity,
            "time_horizon": self.downturn_duration * 30,
            "key_variables": [
                "economic_severity",
                "consumer_confidence",
                "price_elasticity",
                "competitor_survival_rate",
                "channel_effectiveness_shift"
            ],
            "monte_carlo_iterations": 1000,
            "confidence_intervals": [0.80, 0.90, 0.95],
            "sensitivity_analysis": {
                "severity_range": [0.5, 0.9],
                "duration_range": [18, 36],
                "recovery_range": [0.2, 0.5]
            },
            "output_metrics": [
                "demand_contraction_rate",
                "price_sensitivity_index",
                "market_share_stability",
                "competitor_survival_rate",
                "channel_performance_shift",
                "cash_flow_impact",
                "recovery_trajectory"
            ]
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment for the scenario"""

        return {
            "execution_risks": {
                "strategic_misjudgment": {
                    "probability": self.downturn_severity * 0.6,
                    "impact": "high",
                    "mitigation": "Economic forecasting and scenario planning"
                },
                "timing_errors": {
                    "probability": 0.5,
                    "impact": "medium",
                    "mitigation": "Leading indicator monitoring"
                },
                "resource_allocation": {
                    "probability": self.downturn_severity * 0.7,
                    "impact": "high",
                    "mitigation": "Contingency budget planning"
                }
            },
            "market_risks": {
                "demand_destruction": {
                    "probability": self.downturn_severity * 0.9,
                    "impact": "critical",
                    "mitigation": "Market segmentation and targeting"
                },
                "competitive_failure": {
                    "probability": self.competitor_strategies["exit_strategy"]["probability"],
                    "impact": "high",
                    "mitigation": "Competitive intelligence and monitoring"
                },
                "recovery_delay": {
                    "probability": (1 - self.recovery_rate) * 0.8,
                    "impact": "high",
                    "mitigation": "Flexible strategic positioning"
                }
            },
            "operational_risks": {
                "cost_overrun": {
                    "probability": self.downturn_severity * 0.8,
                    "impact": "high",
                    "mitigation": "Cost control and efficiency programs"
                },
                "talent_retention": {
                    "probability": self.downturn_severity * 0.6,
                    "impact": "medium",
                    "mitigation": "Employee engagement and retention programs"
                },
                "supply_chain_disruption": {
                    "probability": self.downturn_severity * 0.4,
                    "impact": "medium",
                    "mitigation": "Supplier diversification and risk management"
                }
            },
            "overall_risk_score": self._calculate_overall_risk(),
            "recommended_mitigations": [
                "Develop comprehensive economic monitoring system",
                "Create multiple scenario response plans",
                "Establish early warning indicator dashboard",
                "Build strategic financial reserves",
                "Develop flexible pricing and product strategies",
                "Strengthen customer relationships and loyalty programs"
            ]
        }

    def _calculate_overall_risk(self) -> float:
        """Calculate overall risk score for the scenario"""

        risk_factors = [
            self.downturn_severity * 0.8,         # Economic severity
            self.consumer_confidence_impact * 0.6, # Confidence impact
            self.market_impact["demand_contraction"] * 0.9,  # Demand risk
            (1 - self.recovery_rate) * 0.7        # Recovery uncertainty
        ]

        return min(1.0, sum(risk_factors) / len(risk_factors))

    def get_success_metrics(self) -> Dict[str, Any]:
        """Get success metrics and KPIs for the scenario"""

        return {
            "primary_metrics": {
                "demand_preservation": {
                    "target": f"<{self.market_impact['demand_contraction'] * 100:.0f}%",
                    "measurement": "demand_contraction_percentage",
                    "timeframe": f"{self.downturn_duration}_months"
                },
                "market_share_maintenance": {
                    "target": ">90%",
                    "measurement": "market_share_retention",
                    "timeframe": f"{self.downturn_duration}_months"
                },
                "cash_flow_stability": {
                    "target": "Positive cash flow maintained",
                    "measurement": "monthly_cash_flow",
                    "timeframe": "ongoing"
                }
            },
            "secondary_metrics": {
                "price_defense": {
                    "target": f"<{self.market_impact['price_sensitivity_increase'] * 30:.0f}%",
                    "measurement": "average_price_erosion",
                    "timeframe": f"{int(self.downturn_duration * 0.6)}_months"
                },
                "brand_loyalty_retention": {
                    "target": f">{100 - self.market_impact['brand_loyalty_decay'] * 50:.0f}%",
                    "measurement": "brand_loyalty_index",
                    "timeframe": f"{self.downturn_duration}_months"
                },
                "competitor_survival_impact": {
                    "target": f"<{self.competitor_strategies['exit_strategy']['probability'] * 50:.0f}%",
                    "measurement": "competitor_exit_rate",
                    "timeframe": f"{self.downturn_duration}_months"
                }
            },
            "leading_indicators": {
                "economic_leading_indicators": {
                    "measurement": "economic_indicator_trend",
                    "target": "Early warning signals detected"
                },
                "consumer_sentiment_tracking": {
                    "measurement": "consumer_confidence_index",
                    "target": f"<{100 - self.consumer_confidence_impact * 20:.0f}"
                },
                "competitor_health_signals": {
                    "measurement": "competitor_stress_indicators",
                    "target": "Early warning of competitor distress"
                }
            },
            "lagging_indicators": {
                "recovery_velocity": {
                    "measurement": "demand_recovery_rate",
                    "target": f">{self.recovery_rate * 100:.0f}% quarterly growth"
                },
                "market_position_recovery": {
                    "measurement": "market_share_recovery",
                    "target": "Pre-downturn market share regained"
                },
                "profitability_restoration": {
                    "measurement": "profit_margin_recovery",
                    "target": f">{80 - self.downturn_severity * 20:.0f}% of pre-downturn margins"
                }
            }
        }


# Scenario interface definition
SCENARIO_INTERFACE = {
    "scenario": SCENARIO_NAME,
    "version": SCENARIO_VERSION,
    "description": SCENARIO_DESCRIPTION,
    "category": "economic_disruption",
    "complexity": "high",
    "duration": "long_term",
    "stakeholders": ["finance", "strategy", "operations", "sales"],
    "required_models": ["consumer_bounded_rationality", "competitor_reactions", "channel_dynamics"],
    "key_variables": [
        "economic_severity",
        "consumer_confidence",
        "demand_elasticity",
        "competitor_survival",
        "recovery_trajectory"
    ],
    "expected_outcomes": [
        "demand_contraction",
        "price_pressure",
        "market_consolidation",
        "strategic_adaptation"
    ],
    "risk_level": "critical",
    "success_probability": 0.55
}


def create_downturn_scenario(downturn_severity: float = 0.7,
                           downturn_duration: int = 24) -> DownturnScenario:
    """
    Factory function to create a downturn scenario

    Args:
        downturn_severity: Severity of economic downturn (0.0 to 1.0)
        downturn_duration: Duration in months

    Returns:
        Configured DownturnScenario instance
    """

    config = {
        "severity": downturn_severity,
        "duration": downturn_duration,
        "recovery_rate": 0.3,
        "confidence_impact": 0.8
    }

    return DownturnScenario(config)


if __name__ == "__main__":
    # Example usage
    scenario = create_downturn_scenario(downturn_severity=0.8, downturn_duration=18)

    print(f"Downturn Scenario: {scenario.downturn_severity * 100:.0f}% severity")
    print(f"Duration: {scenario.downturn_duration} months")
    print(f"Overall risk score: {scenario._calculate_overall_risk():.2f}")

    config = scenario.get_scenario_config()
    print(f"Scenario ID: {config['scenario_id']}")

    timeline = scenario.get_timeline_events()
    print(f"Timeline events: {len(timeline)}")

    success_metrics = scenario.get_success_metrics()
    print(f"Primary metrics: {len(success_metrics['primary_metrics'])}")
