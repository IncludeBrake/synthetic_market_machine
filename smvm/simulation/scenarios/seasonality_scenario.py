#!/usr/bin/env python3
"""
SMVM Seasonality Scenario

This module defines a comprehensive seasonality scenario for agent-based simulation,
including seasonal demand patterns, holiday effects, and temporal market dynamics.
"""

import json
import hashlib
import math
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Scenario metadata
SCENARIO_NAME = "seasonality"
SCENARIO_VERSION = "1.0.0"
SCENARIO_DESCRIPTION = "Seasonal demand patterns and holiday effects scenario"

class SeasonalityScenario:
    """
    Seasonality scenario configuration and parameters
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.scenario_id = self._generate_scenario_id()

        # Scenario parameters
        self.seasonal_amplitude = config.get("amplitude", 0.6)      # 0-1 scale of seasonal variation
        self.holiday_intensity = config.get("holiday_intensity", 0.8)  # Holiday impact strength
        self.business_cycle = config.get("business_cycle", 0.7)    # Business cycle influence
        self.weather_sensitivity = config.get("weather_sensitivity", 0.5)  # Weather impact

        # Seasonal patterns
        self.seasonal_patterns = {
            "q1_winter": {
                "demand_multiplier": 0.7,
                "duration_months": 3,
                "peak_events": ["New Year", "Valentine's Day"],
                "weather_impact": self.weather_sensitivity * 0.8,
                "business_focus": "planning"
            },
            "q2_spring": {
                "demand_multiplier": 0.9,
                "duration_months": 3,
                "peak_events": ["Easter", "Mother's Day"],
                "weather_impact": self.weather_sensitivity * 0.4,
                "business_focus": "growth"
            },
            "q3_summer": {
                "demand_multiplier": 1.1,
                "duration_months": 3,
                "peak_events": ["Summer Sales", "Back to School"],
                "weather_impact": self.weather_sensitivity * 0.6,
                "business_focus": "peak_season"
            },
            "q4_holiday": {
                "demand_multiplier": 1.4,
                "duration_months": 3,
                "peak_events": ["Black Friday", "Christmas", "New Year"],
                "weather_impact": self.weather_sensitivity * 0.7,
                "business_focus": "holiday_season"
            }
        }

        # Holiday effects
        self.holiday_effects = {
            "black_friday": {
                "duration_days": 7,
                "demand_spike": self.holiday_intensity * 2.0,
                "price_elasticity": -2.5,
                "channel_shift": "retail_focus",
                "inventory_impact": "high_demand"
            },
            "christmas_season": {
                "duration_days": 45,
                "demand_spike": self.holiday_intensity * 1.8,
                "price_elasticity": -1.8,
                "channel_shift": "gift_focus",
                "inventory_impact": "seasonal_stock"
            },
            "valentines_day": {
                "duration_days": 14,
                "demand_spike": self.holiday_intensity * 1.3,
                "price_elasticity": -1.5,
                "channel_shift": "emotional_purchases",
                "inventory_impact": "targeted_stock"
            },
            "back_to_school": {
                "duration_days": 30,
                "demand_spike": self.holiday_intensity * 1.2,
                "price_elasticity": -1.2,
                "channel_shift": "family_focus",
                "inventory_impact": "bulk_purchases"
            }
        }

        # Business cycle integration
        self.business_cycles = {
            "expansion": {
                "seasonal_amplification": 1.2,
                "investment_capacity": 0.9,
                "risk_tolerance": 0.8,
                "growth_orientation": 0.9
            },
            "contraction": {
                "seasonal_amplification": 0.8,
                "investment_capacity": 0.4,
                "risk_tolerance": 0.3,
                "growth_orientation": 0.3
            },
            "recovery": {
                "seasonal_amplification": 1.1,
                "investment_capacity": 0.7,
                "risk_tolerance": 0.6,
                "growth_orientation": 0.7
            },
            "recession": {
                "seasonal_amplification": 0.6,
                "investment_capacity": 0.2,
                "risk_tolerance": 0.2,
                "growth_orientation": 0.2
            }
        }

        # Channel seasonal performance
        self.channel_seasonality = {
            "ecommerce": {
                "q1_winter": 0.8,
                "q2_spring": 0.9,
                "q3_summer": 1.2,
                "q4_holiday": 1.8,
                "peak_capacity": 0.95
            },
            "retail_stores": {
                "q1_winter": 0.6,
                "q2_spring": 0.8,
                "q3_summer": 1.4,
                "q4_holiday": 2.2,
                "peak_capacity": 0.85
            },
            "direct_sales": {
                "q1_winter": 0.7,
                "q2_spring": 0.85,
                "q3_summer": 1.0,
                "q4_holiday": 1.3,
                "peak_capacity": 0.9
            },
            "wholesale": {
                "q1_winter": 0.9,
                "q2_spring": 1.0,
                "q3_summer": 0.8,
                "q4_holiday": 1.1,
                "peak_capacity": 0.8
            }
        }

        # Inventory and supply chain effects
        self.inventory_dynamics = {
            "seasonal_stockpiling": {
                "lead_time_increase": 1.5,
                "cost_premium": 0.3,
                "risk_premium": 0.4
            },
            "just_in_time_pressure": {
                "efficiency_gain": 0.2,
                "risk_increase": 0.6,
                "cost_volatility": 0.5
            },
            "demand_forecasting": {
                "accuracy_variation": 0.3,
                "safety_stock_multiplier": 1.8,
                "cost_of_carry": 0.25
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
                "seasonal_amplitude": self.seasonal_amplitude,
                "holiday_intensity": self.holiday_intensity,
                "business_cycle": self.business_cycle,
                "weather_sensitivity": self.weather_sensitivity
            },
            "seasonal_patterns": self.seasonal_patterns,
            "holiday_effects": self.holiday_effects,
            "business_cycles": self.business_cycles,
            "channel_seasonality": self.channel_seasonality,
            "inventory_dynamics": self.inventory_dynamics,
            "simulation_requirements": {
                "min_time_periods": 12,
                "recommended_models": ["channel_dynamics", "consumer_bounded_rationality"],
                "key_metrics": ["seasonal_demand", "holiday_performance", "inventory_turnover", "channel_efficiency"]
            },
            "success_criteria": {
                "seasonal_adaptation": f">{80 - self.seasonal_amplitude * 20:.0f}% demand capture",
                "holiday_performance": f">{self.holiday_intensity * 90:.0f}% peak utilization",
                "inventory_efficiency": "<15% stockout rate during peaks",
                "cash_flow_stability": "Positive cash flow maintained year-round"
            },
            "risk_factors": {
                "demand_volatility": f"{self.seasonal_amplitude * 100:.0f}% seasonal variation",
                "inventory_mismanagement": "Stockouts and overstock risks",
                "capacity_constraints": "Peak period resource limitations",
                "competitive_seasonal_shifts": "Competitor holiday strategies"
            },
            "created_at": datetime.utcnow().isoformat() + "Z"
        }

    def get_initial_conditions(self) -> Dict[str, Any]:
        """Get initial market conditions for the scenario"""

        return {
            "market_state": {
                "current_season": "q1_winter",
                "business_cycle_phase": "expansion",
                "demand_baseline": 1.0,
                "inventory_levels": 0.8,
                "capacity_utilization": 0.7,
                "cash_position": 0.9
            },
            "trigger_event": {
                "event_type": "seasonal_transition",
                "magnitude": self.seasonal_amplitude,
                "timing": 0,
                "seasonal_indicators": ["calendar_events", "weather_patterns", "consumer_behavior"]
            },
            "expected_responses": {
                "consumer_segments": {
                    "seasonal_shoppers": {
                        "response_time": 30,
                        "demand_elasticity": self.seasonal_amplitude * 1.5,
                        "price_sensitivity": 1.3,
                        "loyalty_factor": 0.7
                    },
                    "holiday_buyers": {
                        "response_time": 60,
                        "demand_elasticity": self.holiday_intensity * 2.0,
                        "price_sensitivity": 1.8,
                        "loyalty_factor": 0.5
                    },
                    "steady_customers": {
                        "response_time": 7,
                        "demand_elasticity": self.seasonal_amplitude * 0.5,
                        "price_sensitivity": 1.0,
                        "loyalty_factor": 0.9
                    }
                },
                "channel_responses": {
                    "ecommerce": {
                        "capacity_planning": self.channel_seasonality["ecommerce"]["peak_capacity"],
                        "inventory_strategy": "dynamic_replenishment",
                        "marketing_intensity": self.seasonal_amplitude * 1.2
                    },
                    "retail_stores": {
                        "capacity_planning": self.channel_seasonality["retail_stores"]["peak_capacity"],
                        "inventory_strategy": "seasonal_stockpiling",
                        "marketing_intensity": self.seasonal_amplitude * 1.5
                    }
                }
            }
        }

    def get_timeline_events(self) -> List[Dict[str, Any]]:
        """Get timeline of expected events in the scenario"""

        events = []
        month = 0

        # Generate seasonal transition events
        for quarter, pattern in self.seasonal_patterns.items():
            events.append({
                "month": month,
                "event": f"{quarter.replace('_', ' ').title()} Begins",
                "description": f"Market transitions to {quarter.split('_')[1]} season",
                "market_impact": {
                    "demand_shift": pattern["demand_multiplier"] - 1.0,
                    "channel_pressure": self._calculate_channel_pressure(quarter),
                    "inventory_turnover": self._calculate_inventory_turnover(quarter),
                    "cash_flow_impact": self._calculate_cash_flow_impact(quarter)
                },
                "seasonal_characteristics": {
                    "duration_months": pattern["duration_months"],
                    "key_events": pattern["peak_events"],
                    "weather_influence": pattern["weather_impact"],
                    "business_focus": pattern["business_focus"]
                }
            })

            # Add holiday events within quarters
            if quarter == "q4_holiday":
                holiday_month = month
                for holiday_name, holiday_config in self.holiday_effects.items():
                    if holiday_name in ["black_friday", "christmas_season"]:
                        events.append({
                            "month": holiday_month,
                            "event": f"{holiday_name.replace('_', ' ').title()} Peak",
                            "description": f"Major holiday shopping period begins",
                            "market_impact": {
                                "demand_spike": holiday_config["demand_spike"] - 1.0,
                                "price_pressure": holiday_config["price_elasticity"],
                                "channel_saturation": 0.9,
                                "inventory_drain": 0.8
                            },
                            "holiday_characteristics": {
                                "duration_days": holiday_config["duration_days"],
                                "peak_intensity": holiday_config["demand_spike"],
                                "channel_focus": holiday_config["channel_shift"],
                                "operational_stress": "high"
                            }
                        })
                        holiday_month += 1

            month += pattern["duration_months"]

        # Add business cycle integration events
        events.extend([
            {
                "month": 6,
                "event": "Mid-Year Business Cycle Assessment",
                "description": "Evaluate business cycle impact on seasonal patterns",
                "market_impact": {
                    "cycle_amplification": self.business_cycle * 0.3,
                    "investment_capacity": 0.8,
                    "strategic_adjustments": "moderate"
                },
                "strategic_implications": [
                    "Business cycle alignment",
                    "Investment timing optimization",
                    "Risk assessment update"
                ]
            },
            {
                "month": 12,
                "event": "Annual Seasonal Performance Review",
                "description": "Complete seasonal cycle and plan for next year",
                "market_impact": {
                    "year_over_year_growth": self.business_cycle * 0.4,
                    "seasonal_efficiency": 0.85,
                    "strategic_learning": "comprehensive"
                },
                "strategic_implications": [
                    "Seasonal strategy refinement",
                    "Inventory planning improvement",
                    "Capacity planning optimization"
                ]
            }
        ])

        return events

    def _calculate_channel_pressure(self, quarter: str) -> float:
        """Calculate channel pressure for a quarter"""

        channel_pressure = 0
        for channel, seasonality in self.channel_seasonality.items():
            quarter_key = quarter.lower()
            if quarter_key in seasonality:
                pressure = seasonality[quarter_key] - 1.0
                channel_pressure = max(channel_pressure, pressure)

        return channel_pressure

    def _calculate_inventory_turnover(self, quarter: str) -> float:
        """Calculate inventory turnover rate for a quarter"""

        base_turnover = 4.0  # Annual turnover

        quarter_multipliers = {
            "q1_winter": 0.8,
            "q2_spring": 1.0,
            "q3_summer": 1.4,
            "q4_holiday": 2.2
        }

        return base_turnover * quarter_multipliers.get(quarter, 1.0)

    def _calculate_cash_flow_impact(self, quarter: str) -> float:
        """Calculate cash flow impact for a quarter"""

        base_impact = 0.0

        cash_flow_multipliers = {
            "q1_winter": -0.2,   # Investment period
            "q2_spring": 0.1,    # Early returns
            "q3_summer": 0.3,    # Peak earnings
            "q4_holiday": 0.4    # Holiday profits
        }

        return cash_flow_multipliers.get(quarter, 0.0)

    def get_simulation_parameters(self) -> Dict[str, Any]:
        """Get parameters for running the simulation"""

        return {
            "scenario_type": "temporal_dynamics",
            "disruption_type": "seasonal_patterns",
            "disruption_magnitude": self.seasonal_amplitude,
            "time_horizon": 24,
            "key_variables": [
                "seasonal_demand",
                "holiday_performance",
                "inventory_levels",
                "channel_capacity",
                "cash_flow_patterns",
                "weather_impact"
            ],
            "monte_carlo_iterations": 1000,
            "confidence_intervals": [0.80, 0.90, 0.95],
            "sensitivity_analysis": {
                "amplitude_range": [0.3, 0.8],
                "holiday_intensity_range": [0.6, 0.9],
                "business_cycle_range": [0.5, 0.8]
            },
            "output_metrics": [
                "seasonal_demand_curve",
                "holiday_performance_index",
                "inventory_turnover_ratio",
                "channel_utilization_rate",
                "cash_flow_volatility",
                "year_over_year_growth",
                "seasonal_efficiency_score"
            ]
        }

    def get_risk_assessment(self) -> Dict[str, Any]:
        """Get comprehensive risk assessment for the scenario"""

        return {
            "execution_risks": {
                "forecasting_accuracy": {
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "Advanced analytics and AI forecasting"
                },
                "capacity_planning": {
                    "probability": 0.7,
                    "impact": "high",
                    "mitigation": "Scalable infrastructure and staffing plans"
                },
                "inventory_management": {
                    "probability": 0.8,
                    "impact": "high",
                    "mitigation": "Just-in-time and safety stock strategies"
                }
            },
            "market_risks": {
                "demand_volatility": {
                    "probability": self.seasonal_amplitude * 0.8,
                    "impact": "high",
                    "mitigation": "Demand forecasting and flexible pricing"
                },
                "competitive_seasonal_moves": {
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "Competitive intelligence and response planning"
                },
                "weather_disruption": {
                    "probability": self.weather_sensitivity * 0.7,
                    "impact": "medium",
                    "mitigation": "Weather contingency planning"
                }
            },
            "operational_risks": {
                "supply_chain_disruption": {
                    "probability": 0.5,
                    "impact": "high",
                    "mitigation": "Multiple supplier relationships"
                },
                "labor_shortages": {
                    "probability": 0.6,
                    "impact": "medium",
                    "mitigation": "Staffing and training programs"
                },
                "cash_flow_pressure": {
                    "probability": 0.7,
                    "impact": "high",
                    "mitigation": "Working capital management"
                }
            },
            "overall_risk_score": self._calculate_overall_risk(),
            "recommended_mitigations": [
                "Implement advanced demand forecasting systems",
                "Develop comprehensive capacity planning models",
                "Create flexible inventory management strategies",
                "Establish seasonal marketing calendar",
                "Build cash flow management and working capital plans",
                "Monitor weather patterns and competitive actions",
                "Develop contingency plans for peak season disruptions"
            ]
        }

    def _calculate_overall_risk(self) -> float:
        """Calculate overall risk score for the scenario"""

        risk_factors = [
            self.seasonal_amplitude * 0.6,    # Seasonal variation risk
            self.holiday_intensity * 0.7,     # Holiday intensity risk
            (1 - self.business_cycle) * 0.5,  # Business cycle risk
            self.weather_sensitivity * 0.4    # Weather sensitivity risk
        ]

        return min(1.0, sum(risk_factors) / len(risk_factors))

    def get_success_metrics(self) -> Dict[str, Any]:
        """Get success metrics and KPIs for the scenario"""

        return {
            "primary_metrics": {
                "seasonal_demand_capture": {
                    "target": f">{80 - self.seasonal_amplitude * 15:.0f}%",
                    "measurement": "seasonal_demand_capture_percentage",
                    "timeframe": "annual"
                },
                "holiday_peak_performance": {
                    "target": f">{self.holiday_intensity * 85:.0f}%",
                    "measurement": "peak_capacity_utilization",
                    "timeframe": "holiday_season"
                },
                "inventory_efficiency": {
                    "target": "<12%",
                    "measurement": "stockout_rate_percentage",
                    "timeframe": "annual"
                }
            },
            "secondary_metrics": {
                "cash_flow_stability": {
                    "target": "Positive quarterly cash flow",
                    "measurement": "quarterly_cash_flow",
                    "timeframe": "annual"
                },
                "channel_capacity_utilization": {
                    "target": f">{75 + self.seasonal_amplitude * 10:.0f}%",
                    "measurement": "average_channel_utilization",
                    "timeframe": "annual"
                },
                "seasonal_margin_maintenance": {
                    "target": f">{85 - self.seasonal_amplitude * 15:.0f}% of annual average",
                    "measurement": "seasonal_margin_percentage",
                    "timeframe": "annual"
                }
            },
            "leading_indicators": {
                "demand_forecasting_accuracy": {
                    "measurement": "forecast_accuracy_percentage",
                    "target": ">85% for seasonal peaks"
                },
                "capacity_planning_effectiveness": {
                    "measurement": "capacity_utilization_variance",
                    "target": "<15% variance from plan"
                },
                "inventory_turnover_consistency": {
                    "measurement": "inventory_turnover_stability",
                    "target": "Consistent with seasonal expectations"
                }
            },
            "lagging_indicators": {
                "year_over_year_seasonal_growth": {
                    "measurement": "seasonal_growth_percentage",
                    "target": f">{self.business_cycle * 80:.0f}%"
                },
                "customer_seasonal_retention": {
                    "measurement": "seasonal_customer_retention_rate",
                    "target": ">75% year-over-year"
                },
                "seasonal_roi_efficiency": {
                    "measurement": "seasonal_roi_percentage",
                    "target": f">{100 + self.seasonal_amplitude * 20:.0f}% of annual ROI"
                }
            }
        }


# Scenario interface definition
SCENARIO_INTERFACE = {
    "scenario": SCENARIO_NAME,
    "version": SCENARIO_VERSION,
    "description": SCENARIO_DESCRIPTION,
    "category": "temporal_dynamics",
    "complexity": "medium",
    "duration": "annual_cycle",
    "stakeholders": ["operations", "finance", "supply_chain", "marketing"],
    "required_models": ["channel_dynamics", "consumer_bounded_rationality"],
    "key_variables": [
        "seasonal_amplitude",
        "holiday_intensity",
        "demand_volatility",
        "inventory_efficiency",
        "cash_flow_stability"
    ],
    "expected_outcomes": [
        "seasonal_adaptation",
        "peak_performance",
        "inventory_optimization",
        "cash_flow_management"
    ],
    "risk_level": "medium",
    "success_probability": 0.75
}


def create_seasonality_scenario(seasonal_amplitude: float = 0.6,
                              holiday_intensity: float = 0.8) -> SeasonalityScenario:
    """
    Factory function to create a seasonality scenario

    Args:
        seasonal_amplitude: Amplitude of seasonal variation (0.0 to 1.0)
        holiday_intensity: Intensity of holiday effects (0.0 to 1.0)

    Returns:
        Configured SeasonalityScenario instance
    """

    config = {
        "amplitude": seasonal_amplitude,
        "holiday_intensity": holiday_intensity,
        "business_cycle": 0.7,
        "weather_sensitivity": 0.5
    }

    return SeasonalityScenario(config)


if __name__ == "__main__":
    # Example usage
    scenario = create_seasonality_scenario(seasonal_amplitude=0.65, holiday_intensity=0.85)

    print(f"Seasonality Scenario: {scenario.seasonal_amplitude * 100:.0f}% amplitude")
    print(f"Holiday intensity: {scenario.holiday_intensity * 100:.0f}%")
    print(f"Overall risk score: {scenario._calculate_overall_risk():.2f}")

    config = scenario.get_scenario_config()
    print(f"Scenario ID: {config['scenario_id']}")

    timeline = scenario.get_timeline_events()
    print(f"Timeline events: {len(timeline)}")

    success_metrics = scenario.get_success_metrics()
    print(f"Primary metrics: {len(success_metrics['primary_metrics'])}")
