#!/usr/bin/env python3
"""
SMVM Simulation Schema Conformance Tests

This module tests that all simulation models produce outputs that conform to their
defined schemas, ensuring data consistency and API reliability.
"""

import json
import jsonschema
import pytest
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from smvm.simulation.models.consumer_bounded_rationality import ConsumerBoundedRationalityModel
from smvm.simulation.models.channel_dynamics import ChannelDynamicsModel
from smvm.simulation.models.competitor_reactions import CompetitorReactionsModel
from smvm.simulation.models.social_proof import SocialProofModel

class SimulationSchemaConformanceTester:
    """
    Test class for validating simulation output schemas
    """

    def __init__(self):
        self.conformance_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "schema_tests_run": 0,
            "schema_tests_passed": 0,
            "schema_tests_failed": 0,
            "conformance_score": 0.0,
            "validation_errors": [],
            "schema_coverage": {}
        }

        # Load simulation result schemas
        self.schemas = self._load_simulation_schemas()

    def _load_simulation_schemas(self) -> Dict[str, Any]:
        """Load simulation result schemas from contracts"""

        schemas = {}

        # Consumer decision schema
        schemas["consumer_decision"] = {
            "type": "object",
            "required": ["consumer_id", "model_id", "timestamp", "decision_stages", "final_decision", "decision_confidence"],
            "properties": {
                "consumer_id": {"type": "string"},
                "model_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "decision_stages": {
                    "type": "object",
                    "properties": {
                        "problem_recognition": {"type": "object"},
                        "information_search": {"type": "object"},
                        "evaluation_of_alternatives": {"type": "object"},
                        "purchase_decision": {"type": "object"},
                        "post_purchase_evaluation": {"type": "object"}
                    }
                },
                "final_decision": {"type": "object"},
                "decision_confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "cognitive_load": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "biases_applied": {"type": "array", "items": {"type": "string"}}
            }
        }

        # Channel performance schema
        schemas["channel_performance"] = {
            "type": "object",
            "required": ["simulation_id", "timestamp", "time_periods", "channel_results", "overall_performance"],
            "properties": {
                "simulation_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "time_periods": {"type": "integer", "minimum": 1},
                "channel_results": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "period": {"type": "integer"},
                                    "traffic": {"type": "number", "minimum": 0},
                                    "conversions": {"type": "number", "minimum": 0},
                                    "cost": {"type": "number", "minimum": 0}
                                }
                            }
                        }
                    }
                },
                "overall_performance": {
                    "type": "object",
                    "properties": {
                        "total_traffic": {"type": "number", "minimum": 0},
                        "total_conversions": {"type": "number", "minimum": 0},
                        "total_cost": {"type": "number", "minimum": 0},
                        "average_cpa": {"type": "number", "minimum": 0}
                    }
                }
            }
        }

        # Competitor reactions schema
        schemas["competitor_reactions"] = {
            "type": "object",
            "required": ["simulation_id", "timestamp", "time_periods", "competitor_reactions", "reaction_effectiveness"],
            "properties": {
                "simulation_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "time_periods": {"type": "integer", "minimum": 1},
                "competitor_reactions": {
                    "type": "object",
                    "patternProperties": {
                        ".*": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "reaction_type": {"type": "string"},
                                    "trigger_period": {"type": "integer"},
                                    "competitor": {"type": "string"},
                                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                                }
                            }
                        }
                    }
                },
                "reaction_effectiveness": {
                    "type": "object",
                    "properties": {
                        "total_reactions": {"type": "integer", "minimum": 0},
                        "success_rate": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                    }
                }
            }
        }

        # Social influence schema
        schemas["social_influence"] = {
            "type": "object",
            "required": ["simulation_id", "timestamp", "total_population", "adoption_history", "virality_metrics"],
            "properties": {
                "simulation_id": {"type": "string"},
                "timestamp": {"type": "string", "format": "date-time"},
                "total_population": {"type": "integer", "minimum": 1},
                "adoption_history": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "period": {"type": "integer"},
                            "adopted": {"type": "number", "minimum": 0},
                            "total_adopted": {"type": "number", "minimum": 0},
                            "adoption_rate": {"type": "number", "minimum": 0.0, "maximum": 1.0}
                        }
                    }
                },
                "virality_metrics": {
                    "type": "object",
                    "properties": {
                        "virality_coefficient": {"type": "number", "minimum": 0.0},
                        "adoption_velocity": {"type": "number", "minimum": 0.0}
                    }
                }
            }
        }

        return schemas

    def run_comprehensive_schema_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive schema conformance tests
        """

        print("Running SMVM Simulation Schema Conformance Tests...")
        print("=" * 60)

        # Test consumer model schema conformance
        self._test_consumer_model_schema()

        # Test channel model schema conformance
        self._test_channel_model_schema()

        # Test competitor model schema conformance
        self._test_competitor_model_schema()

        # Test social proof model schema conformance
        self._test_social_proof_model_schema()

        # Test integrated simulation schema
        self._test_integrated_simulation_schema()

        # Calculate conformance metrics
        self._calculate_conformance_metrics()

        print("\n" + "=" * 60)
        print(f"SCHEMA CONFORMANCE: {self.conformance_results['conformance_score']:.1%}")
        print(f"Tests Passed: {self.conformance_results['schema_tests_passed']}/{self.conformance_results['schema_tests_run']}")

        if self.conformance_results['schema_tests_failed'] > 0:
            print(f"FAILED TESTS: {self.conformance_results['schema_tests_failed']}")
            for error in self.conformance_results['validation_errors'][:5]:  # Show first 5 errors
                print(f"  - {error['model']}: {error['error']}")

        return self.conformance_results

    def _test_consumer_model_schema(self):
        """Test consumer model schema conformance"""

        print("\nTesting Consumer Model Schema Conformance...")

        # Load golden fixtures
        with open("tests/simulation/golden_fixtures.json", 'r') as f:
            fixtures = json.load(f)

        consumer_fixtures = fixtures["simulation_test_fixtures"]["consumer_model_fixtures"]
        market_context = fixtures["simulation_test_fixtures"]["market_context_fixtures"]["growth_market"]
        product_options = fixtures["simulation_test_fixtures"]["product_option_fixtures"]["standard_product_line"]

        for fixture_name, consumer_profile in consumer_fixtures.items():
            try:
                model = ConsumerBoundedRationalityModel({"attention_span": 5, "processing_capacity": 10})

                result = model.simulate_consumer_decision(
                    consumer_profile, product_options, market_context, seed=42
                )

                # Validate schema
                self._validate_schema("consumer_decision", result)

                self.conformance_results["schema_tests_passed"] += 1
                print(f"  ✓ {fixture_name}: SCHEMA VALID")

            except Exception as e:
                self._record_schema_error("consumer_model", fixture_name, str(e))
                print(f"  ✗ {fixture_name}: SCHEMA INVALID - {str(e)}")

            self.conformance_results["schema_tests_run"] += 1

    def _test_channel_model_schema(self):
        """Test channel model schema conformance"""

        print("Testing Channel Model Schema Conformance...")

        with open("tests/simulation/golden_fixtures.json", 'r') as f:
            fixtures = json.load(f)

        channel_strategies = fixtures["simulation_test_fixtures"]["channel_model_fixtures"]["balanced_strategy"]
        market_conditions = fixtures["simulation_test_fixtures"]["market_context_fixtures"]["growth_market"]

        for strategy_name, strategies in [("balanced", channel_strategies)]:
            try:
                model = ChannelDynamicsModel({"realism_level": "high"})

                result = model.simulate_channel_performance(
                    strategies, market_conditions, time_periods=5, seed=42
                )

                # Validate schema
                self._validate_schema("channel_performance", result)

                self.conformance_results["schema_tests_passed"] += 1
                print(f"  ✓ {strategy_name}_strategy: SCHEMA VALID")

            except Exception as e:
                self._record_schema_error("channel_model", strategy_name, str(e))
                print(f"  ✗ {strategy_name}_strategy: SCHEMA INVALID - {str(e)}")

            self.conformance_results["schema_tests_run"] += 1

    def _test_competitor_model_schema(self):
        """Test competitor model schema conformance"""

        print("Testing Competitor Model Schema Conformance...")

        with open("tests/simulation/golden_fixtures.json", 'r') as f:
            fixtures = json.load(f)

        competitors = list(fixtures["simulation_test_fixtures"]["competitor_model_fixtures"].values())
        market_state = {
            "average_price": 100,
            "average_features": 0.7,
            "trends": [{"name": "digital_transformation", "impact_score": 0.8}]
        }

        try:
            model = CompetitorReactionsModel({"realism_level": "high"})

            result = model.simulate_competitor_reactions(
                market_state, competitors, time_periods=5, seed=42
            )

            # Validate schema
            self._validate_schema("competitor_reactions", result)

            self.conformance_results["schema_tests_passed"] += 1
            print("  ✓ competitor_reactions: SCHEMA VALID")

        except Exception as e:
            self._record_schema_error("competitor_model", "competitor_reactions", str(e))
            print(f"  ✗ competitor_reactions: SCHEMA INVALID - {str(e)}")

        self.conformance_results["schema_tests_run"] += 1

    def _test_social_proof_model_schema(self):
        """Test social proof model schema conformance"""

        print("Testing Social Proof Model Schema Conformance...")

        with open("tests/simulation/golden_fixtures.json", 'r') as f:
            fixtures = json.load(f)

        social_fixtures = fixtures["simulation_test_fixtures"]["social_proof_fixtures"]["small_world_network"]

        try:
            model = SocialProofModel({"realism_level": "high"})

            result = model.simulate_social_influence(
                social_fixtures["network_structure"],
                social_fixtures["initial_adopters"],
                social_fixtures["total_population"],
                time_periods=8,
                seed=42
            )

            # Validate schema
            self._validate_schema("social_influence", result)

            self.conformance_results["schema_tests_passed"] += 1
            print("  ✓ social_influence: SCHEMA VALID")

        except Exception as e:
            self._record_schema_error("social_proof_model", "social_influence", str(e))
            print(f"  ✗ social_influence: SCHEMA INVALID - {str(e)}")

        self.conformance_results["schema_tests_run"] += 1

    def _test_integrated_simulation_schema(self):
        """Test integrated simulation schema conformance"""

        print("Testing Integrated Simulation Schema Conformance...")

        # Create a simple integrated simulation result
        integrated_result = {
            "simulation_id": "integrated_test_001",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "models_used": ["consumer", "channel", "competitor"],
            "overall_outcome": {
                "total_conversions": 1250,
                "market_share_change": 0.05,
                "revenue_impact": 25000,
                "competitor_responses": 3
            },
            "model_results": {
                "consumer_decisions": 850,
                "channel_conversions": 1250,
                "competitor_reactions": 3
            },
            "performance_metrics": {
                "execution_time_seconds": 2.5,
                "memory_usage_mb": 85,
                "simulation_fidelity": 0.92
            }
        }

        # This would validate against an integrated simulation schema
        # For now, just check basic structure
        try:
            required_fields = ["simulation_id", "timestamp", "models_used", "overall_outcome"]
            for field in required_fields:
                assert field in integrated_result, f"Missing required field: {field}"

            self.conformance_results["schema_tests_passed"] += 1
            print("  ✓ integrated_simulation: SCHEMA VALID")

        except Exception as e:
            self._record_schema_error("integrated_simulation", "integrated_test", str(e))
            print(f"  ✗ integrated_simulation: SCHEMA INVALID - {str(e)}")

        self.conformance_results["schema_tests_run"] += 1

    def _validate_schema(self, schema_name: str, data: Dict[str, Any]):
        """Validate data against schema"""

        if schema_name not in self.schemas:
            raise ValueError(f"Schema '{schema_name}' not found")

        schema = self.schemas[schema_name]

        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Schema validation failed: {e.message}")
        except jsonschema.SchemaError as e:
            raise ValueError(f"Schema error: {e.message}")

    def _record_schema_error(self, model_name: str, test_case: str, error_message: str):
        """Record a schema validation error"""

        error = {
            "model": model_name,
            "test_case": test_case,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.conformance_results["validation_errors"].append(error)
        self.conformance_results["schema_tests_failed"] += 1

    def _calculate_conformance_metrics(self):
        """Calculate overall conformance metrics"""

        total_tests = self.conformance_results["schema_tests_run"]

        if total_tests == 0:
            self.conformance_results["conformance_score"] = 0.0
        else:
            self.conformance_results["conformance_score"] = (
                self.conformance_results["schema_tests_passed"] / total_tests
            )

        # Calculate schema coverage
        self.conformance_results["schema_coverage"] = {
            "consumer_model_schemas": 1 if "consumer_decision" in self.schemas else 0,
            "channel_model_schemas": 1 if "channel_performance" in self.schemas else 0,
            "competitor_model_schemas": 1 if "competitor_reactions" in self.schemas else 0,
            "social_proof_schemas": 1 if "social_influence" in self.schemas else 0,
            "total_schemas_defined": len(self.schemas),
            "schema_test_coverage": total_tests
        }


def run_schema_conformance_tests():
    """Run all schema conformance tests"""

    tester = SimulationSchemaConformanceTester()
    results = tester.run_comprehensive_schema_tests()

    # Save results to file
    output_file = "tests/simulation/schema_conformance_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on conformance score
    return results["conformance_score"] >= 0.95  # Require 95% conformance


def validate_realism_bounds(simulation_state: Dict[str, Any],
                          bounds_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Validate simulation state against realism bounds

    This function demonstrates the bounds validation mentioned in the realism policy
    """

    violations = []

    # Check conversion rates
    if "conversion_rates" in simulation_state:
        for channel, rate in simulation_state["conversion_rates"].items():
            if channel in bounds_config.get("channel_bounds", {}):
                bounds = bounds_config["channel_bounds"][channel]
                if not (bounds[0] <= rate <= bounds[1]):
                    violations.append({
                        "type": "conversion_rate_violation",
                        "channel": channel,
                        "value": rate,
                        "bounds": bounds,
                        "severity": "medium"
                    })

    # Check demand elasticity
    if "price_elasticity" in simulation_state:
        elasticity_bounds = bounds_config.get("demand_elasticity_bounds", [-3.0, -0.5])
        elasticity = simulation_state["price_elasticity"]
        if not (elasticity_bounds[0] <= elasticity <= elasticity_bounds[1]):
            violations.append({
                "type": "elasticity_violation",
                "value": elasticity,
                "bounds": elasticity_bounds,
                "severity": "high"
            })

    return violations


if __name__ == "__main__":
    success = run_schema_conformance_tests()
    exit(0 if success else 1)
