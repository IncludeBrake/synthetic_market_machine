#!/usr/bin/env python3
"""
SMVM Simulation Determinism Tests

This module tests that simulation runs produce identical results when given the same
random seed, ensuring reproducibility and reliability of simulation outcomes.
"""

import json
import hashlib
import pytest
import random
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

class SimulationDeterminismTester:
    """
    Test class for verifying simulation determinism
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "determinism_score": 0.0,
            "performance_metrics": {},
            "failure_details": []
        }

    def run_comprehensive_determinism_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive determinism tests across all simulation models
        """

        print("Running SMVM Simulation Determinism Tests...")
        print("=" * 60)

        # Test Consumer Bounded Rationality Model
        self._test_consumer_model_determinism()

        # Test Channel Dynamics Model
        self._test_channel_model_determinism()

        # Test Competitor Reactions Model
        self._test_competitor_model_determinism()

        # Test Social Proof Model
        self._test_social_proof_determinism()

        # Test Integrated Simulation
        self._test_integrated_simulation_determinism()

        # Calculate final determinism score
        self._calculate_determinism_score()

        print("\n" + "=" * 60)
        print(f"DETERMINISM TEST RESULTS: {self.test_results['determinism_score']:.1%}")
        print(f"Tests Passed: {self.test_results['tests_passed']}/{self.test_results['tests_run']}")

        if self.test_results['tests_failed'] > 0:
            print(f"FAILED TESTS: {self.test_results['tests_failed']}")
            for failure in self.test_results['failure_details']:
                print(f"  - {failure}")

        return self.test_results

    def _test_consumer_model_determinism(self):
        """Test determinism of consumer bounded rationality model"""

        print("\nTesting Consumer Bounded Rationality Model...")

        config = {"attention_span": 5, "processing_capacity": 10}
        model = ConsumerBoundedRationalityModel(config)

        # Test data
        consumer_profile = {
            "persona_id": "TEST_CONSUMER_001",
            "demographics": {"age": 35, "gender": "female"},
            "behavioral_attributes": {
                "risk_tolerance": 6.5,
                "brand_loyalty": 7.2,
                "price_sensitivity": "medium"
            },
            "market_receptivity": {
                "decision_style": "balanced",
                "preferred_channels": ["online", "reviews"]
            }
        }

        product_options = [
            {"product_id": "PROD_001", "product_name": "Budget Option", "price": 50, "quality_score": 0.7},
            {"product_id": "PROD_002", "product_name": "Premium Option", "price": 150, "quality_score": 0.9}
        ]

        market_context = {
            "dissatisfaction_level": 0.7,
            "information_exposure": 0.8,
            "social_influence": 0.5
        }

        # Run multiple times with same seed
        results = []
        test_seed = 42

        for i in range(5):
            result = model.simulate_consumer_decision(
                consumer_profile, product_options, market_context, seed=test_seed
            )
            results.append(result)

        # Verify determinism
        self._verify_determinism("consumer_model", results, ["final_decision", "decision_confidence", "cognitive_load"])

    def _test_channel_model_determinism(self):
        """Test determinism of channel dynamics model"""

        print("Testing Channel Dynamics Model...")

        config = {"realism_level": "high"}
        model = ChannelDynamicsModel(config)

        # Test data
        strategies = {
            "seo": {"investment": 1.5, "effectiveness": 0.9, "content_quality": 0.8},
            "social": {"investment": 2.0, "effectiveness": 0.8, "content_quality": 0.9},
            "email": {"investment": 1.0, "effectiveness": 0.95, "content_quality": 0.7},
            "direct": {"investment": 1.2, "effectiveness": 0.85, "content_quality": 0.6}
        }

        conditions = {
            "economic_conditions": 0.8,
            "competition_intensity": 0.6,
            "seasonal_effects": 0.3
        }

        # Run multiple times with same seed
        results = []
        test_seed = 123

        for i in range(3):
            result = model.simulate_channel_performance(
                strategies, conditions, time_periods=10, seed=test_seed
            )
            results.append(result)

        # Verify determinism
        self._verify_determinism("channel_model", results, ["overall_performance", "channel_results"])

    def _test_competitor_model_determinism(self):
        """Test determinism of competitor reactions model"""

        print("Testing Competitor Reactions Model...")

        config = {"realism_level": "high"}
        model = CompetitorReactionsModel(config)

        # Test data
        competitors = [
            {
                "name": "TechCorp",
                "market_position": "leader",
                "strategy": {"pricing_strategy": "premium"},
                "intelligence_level": "high",
                "resources": 200
            },
            {
                "name": "BudgetSoft",
                "market_position": "challenger",
                "strategy": {"pricing_strategy": "aggressive"},
                "intelligence_level": "medium",
                "resources": 100
            }
        ]

        market_state = {
            "average_price": 100,
            "average_features": 0.7,
            "trends": [{"name": "digital_transformation", "impact_score": 0.8}]
        }

        # Run multiple times with same seed
        results = []
        test_seed = 456

        for i in range(3):
            result = model.simulate_competitor_reactions(
                market_state, competitors, time_periods=10, seed=test_seed
            )
            results.append(result)

        # Verify determinism
        self._verify_determinism("competitor_model", results, ["reaction_effectiveness", "competitor_reactions"])

    def _test_social_proof_determinism(self):
        """Test determinism of social proof model"""

        print("Testing Social Proof Model...")

        config = {"realism_level": "high"}
        model = SocialProofModel(config)

        # Run multiple times with same seed
        results = []
        test_seed = 789

        for i in range(3):
            result = model.simulate_social_influence(
                network_structure="small_world",
                initial_adopters=["0", "1", "2"],
                total_population=50,
                time_periods=8,
                seed=test_seed
            )
            results.append(result)

        # Verify determinism
        self._verify_determinism("social_proof_model", results, ["virality_metrics", "adoption_history"])

    def _test_integrated_simulation_determinism(self):
        """Test determinism of integrated simulation"""

        print("Testing Integrated Simulation...")

        # This would test a full simulation pipeline
        # For now, we'll test a simplified integrated scenario

        results = []
        test_seed = 999

        for i in range(3):
            # Simulate integrated behavior with same seed
            integrated_result = self._run_integrated_simulation(test_seed)
            results.append(integrated_result)

        # Verify determinism
        self._verify_determinism("integrated_simulation", results, ["final_state", "performance_metrics"])

    def _run_integrated_simulation(self, seed: int) -> Dict[str, Any]:
        """Run a simplified integrated simulation"""

        random.seed(seed)

        # Simulate consumer decision
        consumer_decision = random.choice(["purchase", "delay", "no_purchase"])

        # Simulate channel performance
        channel_performance = {
            "traffic": random.randint(800, 1200),
            "conversions": random.randint(25, 45),
            "cost": random.randint(800, 1500)
        }

        # Simulate competitor reaction
        competitor_reaction = random.choice(["price_match", "feature_response", "no_action"])

        # Calculate integrated metrics
        integrated_result = {
            "consumer_decision": consumer_decision,
            "channel_performance": channel_performance,
            "competitor_reaction": competitor_reaction,
            "overall_score": random.uniform(0.6, 0.9),
            "simulation_hash": self._calculate_result_hash({
                "consumer_decision": consumer_decision,
                "channel_performance": channel_performance,
                "competitor_reaction": competitor_reaction
            })
        }

        return integrated_result

    def _verify_determinism(self, test_name: str, results: List[Dict[str, Any]], key_paths: List[str]):
        """Verify determinism across multiple runs"""

        self.test_results["tests_run"] += 1

        if len(results) < 2:
            self._record_failure(test_name, "Insufficient results for determinism test")
            return

        # Check that key results are identical
        reference_result = results[0]
        all_identical = True

        for i, result in enumerate(results[1:], 1):
            for key_path in key_paths:
                if not self._compare_nested_values(reference_result, result, key_path):
                    all_identical = False
                    self._record_failure(
                        test_name,
                        f"Non-deterministic result in run {i} for key path '{key_path}'"
                    )
                    break

            if not all_identical:
                break

        if all_identical:
            self.test_results["tests_passed"] += 1
            print(f"  ✓ {test_name}: DETERMINISTIC")
        else:
            self.test_results["tests_failed"] += 1
            print(f"  ✗ {test_name}: NON-DETERMINISTIC")

    def _compare_nested_values(self, obj1: Any, obj2: Any, key_path: str) -> bool:
        """Compare nested values in objects"""

        keys = key_path.split(".")
        current_obj1 = obj1
        current_obj2 = obj2

        try:
            for key in keys:
                if isinstance(current_obj1, dict) and isinstance(current_obj2, dict):
                    current_obj1 = current_obj1[key]
                    current_obj2 = current_obj2[key]
                else:
                    return False

            # Compare values (with some tolerance for floats)
            if isinstance(current_obj1, float) and isinstance(current_obj2, float):
                return abs(current_obj1 - current_obj2) < 1e-10
            else:
                return current_obj1 == current_obj2

        except (KeyError, TypeError):
            return False

    def _record_failure(self, test_name: str, reason: str):
        """Record a test failure"""

        failure = {
            "test_name": test_name,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.test_results["failure_details"].append(failure)

    def _calculate_result_hash(self, data: Dict[str, Any]) -> str:
        """Calculate hash of result data for comparison"""

        # Convert to JSON string for consistent hashing
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _calculate_determinism_score(self):
        """Calculate overall determinism score"""

        if self.test_results["tests_run"] == 0:
            self.test_results["determinism_score"] = 0.0
        else:
            self.test_results["determinism_score"] = (
                self.test_results["tests_passed"] / self.test_results["tests_run"]
            )

        # Calculate performance metrics
        self.test_results["performance_metrics"] = {
            "pass_rate": self.test_results["determinism_score"],
            "failure_rate": self.test_results["tests_failed"] / max(self.test_results["tests_run"], 1),
            "total_tests": self.test_results["tests_run"],
            "test_duration_seconds": 0.0  # Would be calculated in real implementation
        }


def run_determinism_tests():
    """Run all determinism tests"""

    tester = SimulationDeterminismTester()
    results = tester.run_comprehensive_determinism_tests()

    # Save results to file
    output_file = "tests/simulation/determinism_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on determinism score
    return results["determinism_score"] >= 0.95  # Require 95% determinism


if __name__ == "__main__":
    success = run_determinism_tests()
    exit(0 if success else 1)
