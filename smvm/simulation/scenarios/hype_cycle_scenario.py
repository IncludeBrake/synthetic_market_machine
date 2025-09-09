#!/usr/bin/env python3
"""
SMVM Hype Cycle Scenario

This module defines a comprehensive hype cycle scenario for agent-based simulation,
including Gartner hype cycle dynamics, adoption waves, and market expectation management.
"""

import json
import hashlib
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Scenario metadata
SCENARIO_NAME = "hype_cycle"
SCENARIO_VERSION = "1.0.0"
SCENARIO_DESCRIPTION = "Technology hype cycle scenario with expectation management challenges"

class HypeCycleScenario:
    """
    Hype cycle scenario configuration and parameters
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scenario_id = self._generate_scenario_id()

        # Scenario parameters
        self.hype_intensity = config.get("hype_intensity", 0.8)    # 0-1 scale of hype level
        self.technology_maturity = config.get("maturity", 0.6)     # Technology readiness level
        self.market_expectations = config.get("expectations", 0.9) # Market expectation level
        self.adoption_friction = config.get("friction", 0.4)       # Barriers to adoption

        # Hype cycle phases
        self.hype_phases = {
            "innovation_trigger": {
                "duration": 2,
                "hype_multiplier": self.hype_intensity * 0.3,
                "adoption_rate": 0.02,
                "media_attention": self.hype_intensity * 0.8
            },
            "peak_hype": {
                "duration": 4,
                "hype_multiplier": self.hype_intensity,
                "adoption_rate": 0.08,
                "media_attention": self.hype_intensity * 1.2
            },
            "trough_disillusionment": {
                "duration": 6,
                "hype_multiplier": self.hype_intensity * 0.2,
                "adoption_rate": 0.03,
                "media_attention": self.hype_intensity * 0.3
            },
            "slope_enlightenment": {
                "duration": 8,
                "hype_multiplier": self.hype_intensity * 0.4,
                "adoption_rate": 0.12,
                "media_attention": self.hype_intensity * 0.6
            },
            "plateau_productivity": {
                "duration": 12,
                "hype_multiplier": self.hype_intensity * 0.2,
                "adoption_rate": 0.15,
                "media_attention": self.hype_intensity * 0.4
            }
        }

        # Consumer expectation patterns
        self.consumer_expectations = {
            "over_expecters": {
                "segment_size": 0.25,
                "expectation_inflation": self.hype_intensity * 1.5,
                "disappointment_threshold": 0.7,
                "switching_probability": 0.8
            },
            "realistic_adopters": {
                "segment_size": 0.45,
                "expectation_inflation": self.hype_intensity * 0.8,
                "disappointment_threshold": 0.5,
                "switching_probability": 0.4
            },
            "skeptical_waiters": {
                "segment_size": 0.20,
                "expectation_inflation": self.hype_intensity * 0.3,
                "disappointment_threshold": 0.3,
                "switching_probability": 0.2
            },
            "late_comers": {
                "segment_size": 0.10,
                "expectation_inflation": self.hype_intensity * 0.1,
                "disappointment_threshold": 0.2,
                "switching_probability": 0.1
            }
        }

        # Media and analyst influence
        self.media_influence = {
            "mainstream_media": {
                "reach": 0.6,
                "credibility": 0.7,
                "hype_amplification": self.hype_intensity * 0.8,
                "cycle_acceleration": 0.2
            },
            "tech_media": {
                "reach": 0.8,
                "credibility": 0.8,
                "hype_amplification": self.hype_intensity * 1.2,
                "cycle_acceleration": 0.4
            },
            "analyst_reports": {
                "reach": 0.4,
                "credibility": 0.9,
                "hype_amplification": self.hype_intensity * 0.6,
                "cycle_acceleration": 0.1
            },
            "social_influencers": {
                "reach": 0.7,
                "credibility": 0.5,
                "hype_amplification": self.hype_intensity * 1.5,
                "cycle_acceleration": 0.6
            }
        }

        # Technology maturity factors
        self.maturity_factors = {
            "technical_readiness": self.technology_maturity,
            "infrastructure_maturity": self.technology_maturity * 0.9,
            "market_readiness": self.technology_maturity * 0.8,
            "regulatory_readiness": self.technology_maturity * 0.7,
            "adoption_barriers": 1.0 - self.technology_maturity
        }

        # Market expectation management
        self.expectation_management = {
            "under_promise_over_deliver": {
                "effectiveness": 0.8,
                "risk_reduction": 0.6,
                "adoption_delay": 2
            },
            "education_focused": {
                "effectiveness": 0.9,
                "risk_reduction": 0.7,
                "adoption_delay": 1
            },
            "segmented_messaging": {
                "effectiveness": 0.7,
                "risk_reduction": 0.8,
                "adoption_delay": 0
            },
            "transparent_communication": {
                "effectiveness": 0.85,
                "risk_reduction": 0.75,
                "adoption_delay": 1
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
                "hype_intensity": self.hype_intensity,
                "technology_maturity": self.technology_maturity,
                "market_expectations": self.market_expectations,
                "adoption_friction": self.adoption_friction
            },
            "hype_phases": self.hype_phases,
            "consumer_expectations": self.consumer_expectations,
            "media_influence": self.media_influence,
            "maturity_factors": self.maturity_factors,
            "expectation_management": self.expectation_management,
            "simulation_requirements": {
                "min_time_periods": 24,
                "recommended_models": ["social_proof", "consumer_bounded_rationality"],
                "key_metrics": ["hype_trajectory", "expectation_gap", "adoption_curve", "disappointment_rate"]
            },
            "success_criteria": {
                "hype_management": f"<{self.hype_intensity * 30:.0f}% expectation gap",
                "adoption_stability": ">70% sustained adoption post-peak",
                "brand_credibility": ">80% maintained credibility",
                "market_timing": "Optimal entry and positioning"
            },
            "risk_factors": {
                "expectation_gap": f"{self.hype_intensity * 100:.0f}% disappointment risk",
                "adoption_plunge": f"{(1 - self.technology_maturity) * 100:.0f}% trough depth",
                "credibility_damage": "Long-term brand impact",
                "opportunity_cost": "Missed market timing"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    def get_initial_conditions(self) -> Dict[str, Any]:
        """Get initial market conditions for the scenario"""

        return {
            "market_state": {
                "expectation_level": self.market_expectations,
                "hype_momentum": self.hype_intensity * 0.5,
                "technology_perception": self.technology_maturity * 0.8,
                "market_readiness": self.technology_maturity * 0.9,
                "competitive_attention": self.hype_intensity * 0.7
            },
            "trigger_event": {
                "event_type": "technology_announcement",
                "magnitude": self.hype_intensity,
                "timing": 0,
                "amplification_channels": ["tech_media", "social_influencers", "analyst_reports"]
            },
            "expected_responses": {
                "consumer_segments": {
                    "over_expecters": {
                        "response_time": 1,
                        "expectation_amplification": self.consumer_expectations["over_expecters"]["expectation_inflation"],
                        "disappointment_risk": self.consumer_expectations["over_expecters"]["disappointment_threshold"]
                    },
                    "realistic_adopters": {
                        "response_time": 3,
                        "expectation_amplification": self.consumer_expectations["realistic_adopters"]["expectation_inflation"],
                        "disappointment_risk": self.consumer_expectations["realistic_adopters"]["disappointment_threshold"]
                    },
                    "skeptical_waiters": {
                        "response_time": 7,
                        "expectation_amplification": self.consumer_expectations["skeptical_waiters"]["expectation_inflation"],
                        "disappointment_risk": self.consumer_expectations["skeptical_waiters"]["disappointment_threshold"]
                    }
                },
                "media_ecosystem": {
                    "tech_media": {
                        "coverage_intensity": self.media_influence["tech_media"]["hype_amplification"],
                        "credibility_weight": self.media_influence["tech_media"]["credibility"],
                        "cycle_acceleration": self.media_influence["tech_media"]["cycle_acceleration"]
                    },
                    "mainstream_media": {
                        "coverage_intensity": self.media_influence["mainstream_media"]["hype_amplification"],
                        "credibility_weight": self.media_influence["mainstream_media"]["credibility"],
                        "cycle_acceleration": self.media_influence["mainstream_media"]["cycle_acceleration"]
                    }
                }
            }
        }

    def get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get timeline of expected events in the scenario"""

        phase_start = 0
        events = []

        for phase_name, phase_config in self.hype_phases.items():
            events.append({
                "month": phase_start,
                "event": f"{phase_name.replace('_', ' ').title()} Phase Begins",
                "description": f"Market enters {phase_name.replace('_', ' ')} phase of hype cycle",
                "market_impact": {
                    "hype_level": phase_config["hype_multiplier"],
                    "adoption_acceleration": phase_config["adoption_rate"],
                    "media_attention": phase_config["media_attention"],
                    "expectation_pressure": self._calculate_expectation_pressure(phase_name)
                },
                "phase_characteristics": {
                    "duration_months": phase_config["duration"],
                    "peak_expectations": self._get_phase_expectations(phase_name),
                    "adoption_challenge": self._get_phase_adoption_challenge(phase_name)
                }
            })
            phase_start += phase_config["duration"]

        # Add critical transition events
        events.extend([
            {
                "month": 6,
                "event": "Peak Hype to Trough Transition",
                "description": "Critical transition from hype peak to disillusionment trough",
                "market_impact": {
                    "expectation_gap": self.hype_intensity * 0.8,
                    "adoption_decline": 0.6,
                    "credibility_impact": 0.4
                },
                "strategic_implications": [
                    "Expectation management critical",
                    "Product maturity demonstration",
                    "Customer education focus"
                ]
            },
            {
                "month": 14,
                "event": "Trough to Enlightenment Transition",
                "description": "Market begins to understand realistic technology capabilities",
                "market_impact": {
                    "understanding_improvement": self.technology_maturity * 0.7,
                    "adoption_stabilization": 0.5,
                    "confidence_restoration": 0.6
                },
                "strategic_implications": [
                    "Value proposition clarification",
                    "Use case demonstration",
                    "Realistic messaging adoption"
                ]
            }
        ])

        return events

    def _calculate_expectation_pressure(self, phase_name: str) -> float:
        """Calculate expectation pressure for a phase"""

        phase_multipliers = {
            "innovation_trigger": 0.3,
            "peak_hype": 1.0,
            "trough_disillusionment": 0.8,
            "slope_enlightenment": 0.5,
            "plateau_productivity": 0.2
        }

        return self.hype_intensity * phase_multipliers.get(phase_name, 0.5)

    def _get_phase_expectations(self, phase_name: str) -> str:
        """Get expectation level description for phase"""

        expectations = {
            "innovation_trigger": "High curiosity, low commitment",
            "peak_hype": "Extreme optimism, rapid adoption pressure",
            "trough_disillusionment": "Deep disappointment, credibility damage",
            "slope_enlightenment": "Realistic understanding, practical adoption",
            "plateau_productivity": "Stable expectations, productive use"
        }

        return expectations.get(phase_name, "Moderate expectations")

    def _get_phase_adoption_challenge(self, phase_name: str) -> str:
        """Get adoption challenge description for phase"""

        challenges = {
            "innovation_trigger": "Awareness building",
            "peak_hype": "Managing expectations vs reality",
            "trough_disillusionment": "Overcoming disappointment and skepticism",
            "slope_enlightenment": "Demonstrating practical value",
            "plateau_productivity": "Sustaining adoption momentum"
        }

        return challenges.get(phase_name, "General adoption challenges")

    def get_simulation_parameters(self) -> Dict[str, Any]:
        """Get parameters for running the simulation"""

        return {
            "scenario_type": "market_psychology",
            "disruption_type": "expectation_management",
            "disruption_magnitude": self.hype_intensity,
            "time_horizon": 32,
            "key_variables": [
                "hype_trajectory",
                "expectation_gap",
                "adoption_curve",
                "disappointment_rate",
                "credibility_trend",
                "market_timing"
            ],
            "monte_carlo_iterations": 1000,
            "confidence_intervals": [0.80, 0.90, 0.95],
            "sensitivity_analysis": {
                "hype_intensity_range": [0.5, 0.9],
                "maturity_range": [0.4, 0.8],
                "expectation_range": [0.7, 0.95]
            },
            "output_metrics": [
                "hype_cycle_trajectory",
                "expectation_vs_reality_gap",
                "adoption_velocity_curve",
                "disappointment_impact",
                "credibility_trend",
                "market_timing_efficiency",
                "long_term_adoption_rate"
            ]
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment for the scenario"""

        return {
            "execution_risks": {
                "timing_misjudgment": {
                    "probability": self.hype_intensity * 0.7,
                    "impact": "high",
                    "mitigation": "Market intelligence and timing analysis"
                },
                "messaging_inconsistency": {
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "Coordinated communication planning"
                },
                "product_maturity_gap": {
                    "probability": (1 - self.technology_maturity) * 0.8,
                    "impact": "high",
                    "mitigation": "Technology readiness assessment"
                }
            },
            "market_risks": {
                "expectation_inflation": {
                    "probability": self.hype_intensity * 0.9,
                    "impact": "critical",
                    "mitigation": "Expectation management framework"
                },
                "adoption_plunge": {
                    "probability": self.hype_intensity * 0.8,
                    "impact": "high",
                    "mitigation": "Adoption acceleration strategies"
                },
                "competitor_opportunism": {
                    "probability": self.hype_intensity * 0.6,
                    "impact": "medium",
                    "mitigation": "Competitive monitoring and response"
                }
            },
            "operational_risks": {
                "resource_overcommitment": {
                    "probability": self.hype_intensity * 0.7,
                    "impact": "medium",
                    "mitigation": "Capacity planning and resource allocation"
                },
                "channel_conflicts": {
                    "probability": 0.5,
                    "impact": "low",
                    "mitigation": "Channel strategy coordination"
                },
                "credibility_damage": {
                    "probability": self.hype_intensity * 0.8,
                    "impact": "high",
                    "mitigation": "Brand protection and reputation management"
                }
            },
            "overall_risk_score": self._calculate_overall_risk(),
            "recommended_mitigations": [
                "Develop comprehensive hype cycle management plan",
                "Establish realistic expectation setting framework",
                "Create multi-phase communication strategy",
                "Build product maturity demonstration capabilities",
                "Develop disappointment recovery and renaissance strategies",
                "Monitor hype cycle indicators and adjust positioning"
            ]
        }

    def _calculate_overall_risk(self) -> float:
        """Calculate overall risk score for the scenario"""

        risk_factors = [
            self.hype_intensity * 0.7,        # Hype risk
            (1 - self.technology_maturity) * 0.8,  # Maturity gap risk
            self.market_expectations * 0.6,   # Expectation risk
            self.adoption_friction * 0.4      # Adoption barrier risk
        ]

        return min(1.0, sum(risk_factors) / len(risk_factors))

    def get_success_metrics(self) -> Dict[str, Any]:
        """Get success metrics and KPIs for the scenario"""

        return {
            "primary_metrics": {
                "expectation_gap_management": {
                    "target": f"<{self.hype_intensity * 25:.0f}%",
                    "measurement": "expectation_vs_reality_gap_percentage",
                    "timeframe": "12_months"
                },
                "sustained_adoption_rate": {
                    "target": ">70%",
                    "measurement": "adoption_rate_post_trough",
                    "timeframe": "24_months"
                },
                "credibility_maintenance": {
                    "target": ">80%",
                    "measurement": "brand_credibility_index",
                    "timeframe": "18_months"
                }
            },
            "secondary_metrics": {
                "hype_peak_timing": {
                    "target": f"Month {6 + int(self.hype_intensity * 3)}",
                    "measurement": "peak_hype_month",
                    "timeframe": "peak_identification"
                },
                "trough_recovery_speed": {
                    "target": f"<{8 - int(self.technology_maturity * 4)} months",
                    "measurement": "trough_to_enlightenment_duration",
                    "timeframe": "transition_measurement"
                },
                "productivity_plateau_achievement": {
                    "target": f">{self.technology_maturity * 80:.0f}% of potential",
                    "measurement": "plateau_productivity_percentage",
                    "timeframe": "24_months"
                }
            },
            "leading_indicators": {
                "hype_momentum_tracking": {
                    "measurement": "hype_intensity_index",
                    "target": f"Peak at {self.hype_intensity * 100:.0f}% intensity"
                },
                "expectation_tracking": {
                    "measurement": "market_expectation_index",
                    "target": f"Gap < {self.hype_intensity * 20:.0f}%"
                },
                "adoption_velocity": {
                    "measurement": "monthly_adoption_rate",
                    "target": "S-curve pattern maintained"
                }
            },
            "lagging_indicators": {
                "long_term_adoption": {
                    "measurement": "36_month_adoption_rate",
                    "target": f">{self.technology_maturity * 60:.0f}%"
                },
                "market_position_stability": {
                    "measurement": "market_share_stability_index",
                    "target": ">85% retention"
                },
                "brand_value_impact": {
                    "measurement": "brand_value_change_percentage",
                    "target": f"> -{self.hype_intensity * 15:.0f}%"
                }
            }
        }


# Scenario interface definition
SCENARIO_INTERFACE = {
    "scenario": SCENARIO_NAME,
    "version": SCENARIO_VERSION,
    "description": SCENARIO_DESCRIPTION,
    "category": "market_psychology",
    "complexity": "high",
    "duration": "medium_term",
    "stakeholders": ["marketing", "product", "communications", "strategy"],
    "required_models": ["social_proof", "consumer_bounded_rationality"],
    "key_variables": [
        "hype_intensity",
        "expectation_gap",
        "technology_maturity",
        "market_timing",
        "credibility_trend"
    ],
    "expected_outcomes": [
        "expectation_management",
        "adoption_acceleration",
        "credibility_protection",
        "market_positioning"
    ],
    "risk_level": "high",
    "success_probability": 0.6
}


def create_hype_cycle_scenario(hype_intensity: float = 0.8,
                             technology_maturity: float = 0.6) -> HypeCycleScenario:
    """
    Factory function to create a hype cycle scenario

    Args:
        hype_intensity: Intensity of market hype (0.0 to 1.0)
        technology_maturity: Technology readiness level (0.0 to 1.0)

    Returns:
        Configured HypeCycleScenario instance
    """

    config = {
        "hype_intensity": hype_intensity,
        "maturity": technology_maturity,
        "expectations": 0.9,
        "friction": 0.4
    }

    return HypeCycleScenario(config)


if __name__ == "__main__":
    # Example usage
    scenario = create_hype_cycle_scenario(hype_intensity=0.85, technology_maturity=0.65)

    print(f"Hype Cycle Scenario: {scenario.hype_intensity * 100:.0f}% hype intensity")
    print(f"Technology maturity: {scenario.technology_maturity * 100:.0f}%")
    print(f"Overall risk score: {scenario._calculate_overall_risk():.2f}")

    config = scenario.get_scenario_config()
    print(f"Scenario ID: {config['scenario_id']}")

    timeline = scenario.get_timeline_events()
    print(f"Timeline events: {len(timeline)}")

    success_metrics = scenario.get_success_metrics()
    print(f"Primary metrics: {len(success_metrics['primary_metrics'])}")
