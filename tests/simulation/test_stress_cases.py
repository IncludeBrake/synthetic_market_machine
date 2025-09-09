#!/usr/bin/env python3
"""
SMVM Simulation Stress Tests

This module tests simulation robustness under extreme conditions and edge cases,
including boundary values, error conditions, and performance limits.
"""

import json
import pytest
import random
import time
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

class SimulationStressTester:
    """
    Test class for simulation stress testing and edge cases
    """

    def __init__(self):
        self.stress_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "stress_tests_run": 0,
            "stress_tests_passed": 0,
            "stress_tests_failed": 0,
            "performance_metrics": {},
            "edge_case_coverage": {},
            "failure_details": []
        }

    def run_comprehensive_stress_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive stress tests across all simulation models
        """

        print("Running SMVM Simulation Stress Tests...")
        print("=" * 60)

        # Test boundary conditions
        self._test_boundary_conditions()

        # Test extreme values
        self._test_extreme_values()

        # Test error conditions
        self._test_error_conditions()

        # Test performance limits
        self._test_performance_limits()

        # Test concurrent operations
        self._test_concurrent_operations()

        # Calculate stress test metrics
        self._calculate_stress_metrics()

        print("\n" + "=" * 60)
        print(f"STRESS TEST RESULTS: {self.stress_results['stress_tests_passed']}/{self.stress_results['stress_tests_run']} passed")

        if self.stress_results['stress_tests_failed'] > 0:
            print(f"FAILED TESTS: {self.stress_results['stress_tests_failed']}")
            for failure in self.stress_results['failure_details']:
                print(f"  - {failure['test_name']}: {failure['reason']}")

        return self.stress_results

    def _test_boundary_conditions(self):
        """Test simulation behavior at boundary conditions"""

        print("\nTesting Boundary Conditions...")

        # Test consumer model with extreme attention spans
        self._test_consumer_boundaries()

        # Test channel model with zero/very high investments
        self._test_channel_boundaries()

        # Test social proof with minimal/maximal network sizes
        self._test_social_proof_boundaries()

        # Test competitor model with extreme resource levels
        self._test_competitor_boundaries()

    def _test_consumer_boundaries(self):
        """Test consumer model boundary conditions"""

        test_cases = [
            {
                "name": "zero_attention_span",
                "config": {"attention_span": 0, "processing_capacity": 10},
                "expected_behavior": "minimal_options_considered"
            },
            {
                "name": "maximum_attention_span",
                "config": {"attention_span": 20, "processing_capacity": 10},
                "expected_behavior": "many_options_considered"
            },
            {
                "name": "extreme_risk_tolerance",
                "config": {"attention_span": 5, "processing_capacity": 10},
                "consumer_profile": {
                    "persona_id": "EXTREME_RISK_001",
                    "behavioral_attributes": {"risk_tolerance": 10.0, "brand_loyalty": 10.0}
                },
                "expected_behavior": "high_risk_decisions"
            }
        ]

        for test_case in test_cases:
            try:
                self._run_consumer_boundary_test(test_case)
                self.stress_results["stress_tests_passed"] += 1
                print(f"  ✓ {test_case['name']}: PASSED")
            except Exception as e:
                self._record_stress_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: FAILED - {str(e)}")

            self.stress_results["stress_tests_run"] += 1

    def _run_consumer_boundary_test(self, test_case: Dict[str, Any]):
        """Run a specific consumer boundary test"""

        config = test_case["config"]
        model = ConsumerBoundedRationalityModel(config)

        # Use default or custom consumer profile
        consumer_profile = test_case.get("consumer_profile", {
            "persona_id": "BOUNDARY_TEST_001",
            "demographics": {"age": 35, "gender": "other"},
            "behavioral_attributes": {
                "risk_tolerance": 5.0,
                "brand_loyalty": 5.0,
                "price_sensitivity": "medium"
            },
            "market_receptivity": {
                "decision_style": "balanced",
                "preferred_channels": ["online"]
            }
        })

        product_options = [
            {"product_id": f"PROD_{i:03d}", "product_name": f"Option {i}", "price": 50 + i * 10, "quality_score": 0.5 + i * 0.1}
            for i in range(min(config["attention_span"] + 5, 15))  # Create options based on attention span
        ]

        market_context = {
            "dissatisfaction_level": 0.5,
            "information_exposure": 0.5,
            "social_influence": 0.5
        }

        # Run simulation
        result = model.simulate_consumer_decision(
            consumer_profile, product_options, market_context, seed=42
        )

        # Validate expected behavior
        if test_case["expected_behavior"] == "minimal_options_considered":
            assert len(result["decision_stages"]["information_search"]["considered_options"]) <= 1
        elif test_case["expected_behavior"] == "many_options_considered":
            assert len(result["decision_stages"]["information_search"]["considered_options"]) >= config["attention_span"]
        elif test_case["expected_behavior"] == "high_risk_decisions":
            assert result["decision_stages"]["evaluation_of_alternatives"]["options_evaluated"][0]["overall_score"] > 0.7

    def _test_channel_boundaries(self):
        """Test channel model boundary conditions"""

        test_cases = [
            {
                "name": "zero_investment",
                "strategies": {
                    "seo": {"investment": 0.0, "effectiveness": 0.5, "content_quality": 0.5},
                    "social": {"investment": 1.0, "effectiveness": 0.8, "content_quality": 0.7}
                },
                "expected_behavior": "minimal_channel_performance"
            },
            {
                "name": "extreme_investment",
                "strategies": {
                    "seo": {"investment": 5.0, "effectiveness": 0.9, "content_quality": 0.9},
                    "social": {"investment": 5.0, "effectiveness": 0.9, "content_quality": 0.9}
                },
                "expected_behavior": "saturation_effects"
            }
        ]

        for test_case in test_cases:
            try:
                model = ChannelDynamicsModel({"realism_level": "high"})

                conditions = {
                    "economic_conditions": 0.7,
                    "competition_intensity": 0.5,
                    "seasonal_effects": 0.4
                }

                result = model.simulate_channel_performance(
                    test_case["strategies"], conditions, time_periods=5, seed=42
                )

                # Validate expected behavior
                if test_case["expected_behavior"] == "minimal_channel_performance":
                    total_conversions = result["overall_performance"]["total_conversions"]
                    assert total_conversions < 100  # Very low performance expected
                elif test_case["expected_behavior"] == "saturation_effects":
                    # Check for saturation in results
                    has_saturation = any(
                        period_result.get("saturation_level", 0) > 0.8
                        for channel_results in result["channel_results"].values()
                        for period_result in channel_results
                    )
                    assert has_saturation

                self.stress_results["stress_tests_passed"] += 1
                print(f"  ✓ {test_case['name']}: PASSED")

            except Exception as e:
                self._record_stress_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: FAILED - {str(e)}")

            self.stress_results["stress_tests_run"] += 1

    def _test_social_proof_boundaries(self):
        """Test social proof model boundary conditions"""

        test_cases = [
            {
                "name": "minimal_network",
                "network_structure": "small_world",
                "initial_adopters": ["0"],
                "total_population": 5,
                "expected_behavior": "limited_spread"
            },
            {
                "name": "maximal_network",
                "network_structure": "scale_free",
                "initial_adopters": [str(i) for i in range(10)],
                "total_population": 1000,
                "expected_behavior": "rapid_spread"
            }
        ]

        for test_case in test_cases:
            try:
                model = SocialProofModel({"realism_level": "high"})

                result = model.simulate_social_influence(
                    test_case["network_structure"],
                    test_case["initial_adopters"],
                    test_case["total_population"],
                    time_periods=10,
                    seed=42
                )

                # Validate expected behavior
                if test_case["expected_behavior"] == "limited_spread":
                    final_adoption_rate = result["adoption_history"][-1]["adoption_rate"]
                    assert final_adoption_rate < 0.5  # Limited spread expected
                elif test_case["expected_behavior"] == "rapid_spread":
                    final_adoption_rate = result["adoption_history"][-1]["adoption_rate"]
                    assert final_adoption_rate > 0.3  # Some spread expected

                self.stress_results["stress_tests_passed"] += 1
                print(f"  ✓ {test_case['name']}: PASSED")

            except Exception as e:
                self._record_stress_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: FAILED - {str(e)}")

            self.stress_results["stress_tests_run"] += 1

    def _test_competitor_boundaries(self):
        """Test competitor model boundary conditions"""

        test_cases = [
            {
                "name": "zero_resources",
                "competitors": [{
                    "name": "BrokeCorp",
                    "market_position": "challenger",
                    "resources": 0
                }],
                "expected_behavior": "minimal_reactions"
            },
            {
                "name": "extreme_resources",
                "competitors": [{
                    "name": "MegaCorp",
                    "market_position": "leader",
                    "resources": 10000
                }],
                "expected_behavior": "aggressive_reactions"
            }
        ]

        for test_case in test_cases:
            try:
                model = CompetitorReactionsModel({"realism_level": "high"})

                market_state = {
                    "average_price": 100,
                    "average_features": 0.7,
                    "trends": [{"name": "market_disruption", "impact_score": 0.8}]
                }

                result = model.simulate_competitor_reactions(
                    market_state, test_case["competitors"], time_periods=5, seed=42
                )

                # Validate expected behavior
                total_reactions = result["reaction_effectiveness"]["total_reactions"]

                if test_case["expected_behavior"] == "minimal_reactions":
                    assert total_reactions == 0  # No resources, no reactions
                elif test_case["expected_behavior"] == "aggressive_reactions":
                    assert total_reactions > 0  # Should have reactions with resources

                self.stress_results["stress_tests_passed"] += 1
                print(f"  ✓ {test_case['name']}: PASSED")

            except Exception as e:
                self._record_stress_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: FAILED - {str(e)}")

            self.stress_results["stress_tests_run"] += 1

    def _test_extreme_values(self):
        """Test simulation behavior with extreme input values"""

        print("\nTesting Extreme Values...")

        # Test with extreme market conditions
        extreme_conditions = {
            "economic_conditions": 0.0,  # Complete depression
            "competition_intensity": 1.0,  # Perfect competition
            "seasonal_effects": 1.0,  # Maximum seasonality
            "technological_change": 1.0  # Revolutionary change
        }

        try:
            channel_model = ChannelDynamicsModel({"realism_level": "high"})
            strategies = {
                "seo": {"investment": 1.0, "effectiveness": 0.5, "content_quality": 0.5},
                "social": {"investment": 1.0, "effectiveness": 0.5, "content_quality": 0.5}
            }

            result = channel_model.simulate_channel_performance(
                strategies, extreme_conditions, time_periods=3, seed=42
            )

            # Should handle extreme conditions without crashing
            assert "overall_performance" in result
            assert result["overall_performance"]["total_conversions"] >= 0

            self.stress_results["stress_tests_passed"] += 1
            print("  ✓ extreme_market_conditions: PASSED")

        except Exception as e:
            self._record_stress_failure("extreme_market_conditions", str(e))
            print(f"  ✗ extreme_market_conditions: FAILED - {str(e)}")

        self.stress_results["stress_tests_run"] += 1

    def _test_error_conditions(self):
        """Test simulation behavior under error conditions"""

        print("\nTesting Error Conditions...")

        # Test with invalid inputs
        try:
            consumer_model = ConsumerBoundedRationalityModel({"attention_span": 5})

            # Invalid consumer profile
            invalid_profile = {"invalid": "data"}
            product_options = [{"product_id": "TEST", "price": 100}]

            # Should handle gracefully
            result = consumer_model.simulate_consumer_decision(
                invalid_profile, product_options, {}, seed=42
            )

            # Should return some result even with invalid input
            assert "final_decision" in result

            self.stress_results["stress_tests_passed"] += 1
            print("  ✓ invalid_input_handling: PASSED")

        except Exception as e:
            self._record_stress_failure("invalid_input_handling", str(e))
            print(f"  ✗ invalid_input_handling: FAILED - {str(e)}")

        self.stress_results["stress_tests_run"] += 1

    def _test_performance_limits(self):
        """Test simulation performance under load"""

        print("\nTesting Performance Limits...")

        # Test with large population
        try:
            social_model = SocialProofModel({"realism_level": "high"})

            start_time = time.time()
            result = social_model.simulate_social_influence(
                "scale_free",
                [str(i) for i in range(50)],  # Many initial adopters
                500,  # Large population
                time_periods=20,
                seed=42
            )
            end_time = time.time()

            execution_time = end_time - start_time

            # Should complete within reasonable time (30 seconds)
            assert execution_time < 30.0
            assert result["adoption_history"][-1]["adoption_rate"] > 0

            self.stress_results["performance_metrics"]["large_population_test_time"] = execution_time
            self.stress_results["stress_tests_passed"] += 1
            print(f"  ✓ large_population_performance: PASSED ({execution_time:.2f}s)")

        except Exception as e:
            self._record_stress_failure("large_population_performance", str(e))
            print(f"  ✗ large_population_performance: FAILED - {str(e)}")

        self.stress_results["stress_tests_run"] += 1

    def _test_concurrent_operations(self):
        """Test simulation behavior with concurrent operations"""

        print("\nTesting Concurrent Operations...")

        # Test multiple simulations running simultaneously
        try:
            import threading

            results = []
            errors = []

            def run_simulation(seed):
                try:
                    model = ConsumerBoundedRationalityModel({"attention_span": 5})
                    consumer = {
                        "persona_id": f"CONCURRENT_{seed}",
                        "behavioral_attributes": {"risk_tolerance": 5.0, "brand_loyalty": 5.0}
                    }
                    products = [{"product_id": f"P{seed}", "price": 100}]
                    result = model.simulate_consumer_decision(consumer, products, {}, seed=seed)
                    results.append(result)
                except Exception as e:
                    errors.append(str(e))

            # Run multiple simulations concurrently
            threads = []
            for i in range(5):
                thread = threading.Thread(target=run_simulation, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join(timeout=10)

            # Should have results from all threads
            assert len(results) == 5
            assert len(errors) == 0

            self.stress_results["stress_tests_passed"] += 1
            print("  ✓ concurrent_simulations: PASSED")

        except Exception as e:
            self._record_stress_failure("concurrent_simulations", str(e))
            print(f"  ✗ concurrent_simulations: FAILED - {str(e)}")

        self.stress_results["stress_tests_run"] += 1

    def _record_stress_failure(self, test_name: str, reason: str):
        """Record a stress test failure"""

        failure = {
            "test_name": test_name,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.stress_results["failure_details"].append(failure)
        self.stress_results["stress_tests_failed"] += 1

    def _calculate_stress_metrics(self):
        """Calculate overall stress test metrics"""

        total_tests = self.stress_results["stress_tests_run"]

        if total_tests == 0:
            self.stress_results["performance_metrics"]["overall_stress_score"] = 0.0
        else:
            pass_rate = self.stress_results["stress_tests_passed"] / total_tests
            self.stress_results["performance_metrics"]["overall_stress_score"] = pass_rate

            # Calculate edge case coverage
            self.stress_results["edge_case_coverage"] = {
                "boundary_conditions_tested": 4,  # consumer, channel, social, competitor
                "extreme_values_tested": 1,
                "error_conditions_tested": 1,
                "performance_limits_tested": 1,
                "concurrent_operations_tested": 1
            }


def run_stress_tests():
    """Run all stress tests"""

    tester = SimulationStressTester()
    results = tester.run_comprehensive_stress_tests()

    # Save results to file
    output_file = "tests/simulation/stress_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on stress test score
    return results["performance_metrics"]["overall_stress_score"] >= 0.80  # Require 80% pass rate


if __name__ == "__main__":
    success = run_stress_tests()
    exit(0 if success else 1)
