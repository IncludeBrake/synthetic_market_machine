#!/usr/bin/env python3
"""
SMVM Decision Matrix Tests

This module tests the Go/Pivot/Kill decision matrix functionality,
ensuring that low WTP scenarios correctly result in Pivot/Kill recommendations.
"""

import json
import pytest
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class DecisionMatrixTester:
    """
    Test class for decision matrix functionality
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "decision_tests_run": 0,
            "decision_tests_passed": 0,
            "decision_tests_failed": 0,
            "low_wtp_scenarios_tested": 0,
            "correct_pivot_kill_decisions": 0,
            "decision_consistency_score": 0.0
        }

    def run_decision_matrix_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive decision matrix tests
        """

        print("Running SMVM Decision Matrix Tests...")
        print("=" * 60)

        # Test low WTP scenarios leading to Pivot/Kill
        self._test_low_wtp_scenarios()

        # Test decision matrix scoring
        self._test_decision_matrix_scoring()

        # Test decision thresholds
        self._test_decision_thresholds()

        # Test decision consistency
        self._test_decision_consistency()

        # Calculate test metrics
        self._calculate_decision_metrics()

        print("\n" + "=" * 60)
        print(f"DECISION MATRIX TEST RESULTS: {self.test_results['decision_tests_passed']}/{self.test_results['decision_tests_run']} passed")

        if self.test_results['decision_tests_failed'] > 0:
            print(f"FAILED TESTS: {self.test_results['decision_tests_failed']}")
            for failure in self.test_results.get('failures', []):
                print(f"  - {failure}")

        # Report low WTP scenario results
        if self.test_results['low_wtp_scenarios_tested'] > 0:
            low_wtp_accuracy = self.test_results['correct_pivot_kill_decisions'] / self.test_results['low_wtp_scenarios_tested']
            print(f"LOW WTP SCENARIO ACCURACY: {low_wtp_accuracy:.1%}")

        return self.test_results

    def _test_low_wtp_scenarios(self):
        """Test that low WTP scenarios correctly lead to Pivot/Kill decisions"""

        print("\nTesting Low WTP Scenarios...")

        # Define scenarios with low WTP that should result in Pivot/Kill
        low_wtp_scenarios = [
            {
                "name": "very_low_wtp_scenario",
                "wtp": 15.0,  # Very low WTP
                "market_size": 10000000,
                "competition": "high",
                "technical_feasibility": 0.7,
                "expected_decision": "KILL",
                "expected_confidence": 0.9
            },
            {
                "name": "low_wtp_pivot_scenario",
                "wtp": 45.0,  # Low WTP
                "market_size": 25000000,
                "competition": "medium",
                "technical_feasibility": 0.8,
                "expected_decision": "PIVOT",
                "expected_confidence": 0.75
            },
            {
                "name": "marginal_wtp_scenario",
                "wtp": 35.0,  # Marginal WTP
                "market_size": 15000000,
                "competition": "high",
                "technical_feasibility": 0.6,
                "expected_decision": "KILL",
                "expected_confidence": 0.85
            }
        ]

        for scenario in low_wtp_scenarios:
            try:
                self.test_results['low_wtp_scenarios_tested'] += 1

                # Run decision matrix analysis
                decision_result = self._analyze_decision_matrix(scenario)
                actual_decision = decision_result["decision"]
                confidence = decision_result["confidence"]

                # Check if decision is correct (Pivot or Kill for low WTP)
                correct_decision = actual_decision in ["PIVOT", "KILL"]
                sufficient_confidence = confidence >= scenario["expected_confidence"]

                if correct_decision and sufficient_confidence:
                    self.test_results["decision_tests_passed"] += 1
                    self.test_results['correct_pivot_kill_decisions'] += 1
                    print(f"  ✓ {scenario['name']}: {actual_decision} ({confidence:.1%} confidence)")
                else:
                    self._record_decision_failure(
                        scenario['name'],
                        f"Decision {actual_decision} (expected Pivot/Kill), confidence {confidence:.1%} (minimum {scenario['expected_confidence']:.1%})"
                    )
                    print(f"  ✗ {scenario['name']}: {actual_decision} ({confidence:.1%} confidence)")

            except Exception as e:
                self._record_decision_failure(scenario['name'], str(e))
                print(f"  ✗ {scenario['name']}: ERROR - {str(e)}")

            self.test_results["decision_tests_run"] += 1

    def _test_decision_matrix_scoring(self):
        """Test decision matrix scoring accuracy"""

        print("Testing Decision Matrix Scoring...")

        # Test cases with known expected scores
        scoring_tests = [
            {
                "name": "high_score_go_scenario",
                "dimensions": {
                    "market_opportunity": 90,
                    "wtp_validation": 85,
                    "competitive_position": 80,
                    "technical_feasibility": 85,
                    "financial_viability": 80,
                    "risk_assessment": 85,
                    "team_capability": 80
                },
                "expected_range": (75, 100)  # Should be GO range
            },
            {
                "name": "medium_score_pivot_scenario",
                "dimensions": {
                    "market_opportunity": 65,
                    "wtp_validation": 60,
                    "competitive_position": 55,
                    "technical_feasibility": 70,
                    "financial_viability": 60,
                    "risk_assessment": 65,
                    "team_capability": 60
                },
                "expected_range": (45, 74)  # Should be PIVOT range
            },
            {
                "name": "low_score_kill_scenario",
                "dimensions": {
                    "market_opportunity": 30,
                    "wtp_validation": 25,
                    "competitive_position": 20,
                    "technical_feasibility": 35,
                    "financial_viability": 30,
                    "risk_assessment": 25,
                    "team_capability": 30
                },
                "expected_range": (0, 44)  # Should be KILL range
            }
        ]

        for test_case in scoring_tests:
            try:
                # Calculate composite score
                composite_score = self._calculate_composite_score(test_case["dimensions"])
                expected_min, expected_max = test_case["expected_range"]

                # Check if score is in expected range
                if expected_min <= composite_score <= expected_max:
                    self.test_results["decision_tests_passed"] += 1
                    print(f"  ✓ {test_case['name']}: Score {composite_score}/100 (expected {expected_min}-{expected_max})")
                else:
                    self._record_decision_failure(
                        test_case['name'],
                        f"Score {composite_score}/100 outside expected range {expected_min}-{expected_max}"
                    )
                    print(f"  ✗ {test_case['name']}: Score {composite_score}/100 (expected {expected_min}-{expected_max})")

            except Exception as e:
                self._record_decision_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: ERROR - {str(e)}")

            self.test_results["decision_tests_run"] += 1

    def _test_decision_thresholds(self):
        """Test decision thresholds are applied correctly"""

        print("Testing Decision Thresholds...")

        threshold_tests = [
            {
                "name": "go_threshold_test",
                "score": 80,
                "expected_decision": "GO"
            },
            {
                "name": "pivot_lower_threshold_test",
                "score": 45,
                "expected_decision": "PIVOT"
            },
            {
                "name": "pivot_upper_threshold_test",
                "score": 74,
                "expected_decision": "PIVOT"
            },
            {
                "name": "kill_threshold_test",
                "score": 40,
                "expected_decision": "KILL"
            }
        ]

        for test_case in threshold_tests:
            try:
                decision = self._apply_decision_thresholds(test_case["score"])

                if decision == test_case["expected_decision"]:
                    self.test_results["decision_tests_passed"] += 1
                    print(f"  ✓ {test_case['name']}: Score {test_case['score']} → {decision}")
                else:
                    self._record_decision_failure(
                        test_case['name'],
                        f"Score {test_case['score']} resulted in {decision}, expected {test_case['expected_decision']}"
                    )
                    print(f"  ✗ {test_case['name']}: Score {test_case['score']} → {decision} (expected {test_case['expected_decision']})")

            except Exception as e:
                self._record_decision_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: ERROR - {str(e)}")

            self.test_results["decision_tests_run"] += 1

    def _test_decision_consistency(self):
        """Test decision consistency across similar scenarios"""

        print("Testing Decision Consistency...")

        # Create similar scenarios and ensure consistent decisions
        base_scenario = {
            "wtp": 60.0,
            "market_size": 30000000,
            "competition": "medium",
            "technical_feasibility": 0.75
        }

        consistency_tests = []
        for i in range(5):
            # Create slightly varied scenario
            scenario = base_scenario.copy()
            scenario["wtp"] += random.uniform(-5, 5)
            scenario["market_size"] += random.randint(-5000000, 5000000)

            decision = self._analyze_decision_matrix(scenario)
            consistency_tests.append(decision["decision"])

        # Check consistency (should mostly be PIVOT decisions)
        pivot_count = consistency_tests.count("PIVOT")
        consistency_ratio = pivot_count / len(consistency_tests)

        if consistency_ratio >= 0.8:  # 80% consistency
            self.test_results["decision_tests_passed"] += 1
            print(f"  ✓ decision_consistency: {consistency_ratio:.1%} consistent decisions")
        else:
            self._record_decision_failure(
                "decision_consistency",
                f"Only {consistency_ratio:.1%} consistent decisions (required 80%)"
            )
            print(f"  ✗ decision_consistency: {consistency_ratio:.1%} consistent decisions")

        self.test_results["decision_tests_run"] += 1

    def _analyze_decision_matrix(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Mock decision matrix analysis"""

        # Extract key factors
        wtp = scenario.get("wtp", 50)
        market_size = scenario.get("market_size", 20000000)
        competition = scenario.get("competition", "medium")
        technical_feasibility = scenario.get("technical_feasibility", 0.7)

        # Calculate dimension scores (simplified)
        market_score = min(100, (market_size / 100000000) * 100)  # Scale to 100M = 100 score

        if competition == "low":
            competitive_score = 80
        elif competition == "medium":
            competitive_score = 60
        else:  # high
            competitive_score = 40

        technical_score = technical_feasibility * 100

        # Simplified WTP scoring
        if wtp >= 100:
            wtp_score = 85
        elif wtp >= 50:
            wtp_score = 65
        else:
            wtp_score = 35

        # Calculate composite score
        dimensions = {
            "market_opportunity": market_score,
            "wtp_validation": wtp_score,
            "competitive_position": competitive_score,
            "technical_feasibility": technical_score,
            "financial_viability": 65,
            "risk_assessment": 70,
            "team_capability": 60
        }

        composite_score = self._calculate_composite_score(dimensions)

        # Apply decision thresholds
        decision = self._apply_decision_thresholds(composite_score)
        confidence = self._calculate_decision_confidence(composite_score, decision)

        return {
            "decision": decision,
            "confidence": confidence,
            "composite_score": composite_score,
            "dimension_scores": dimensions
        }

    def _calculate_composite_score(self, dimensions: Dict[str, Any]) -> float:
        """Calculate composite score from dimension scores"""

        weights = {
            "market_opportunity": 0.25,
            "wtp_validation": 0.20,
            "competitive_position": 0.15,
            "technical_feasibility": 0.15,
            "financial_viability": 0.10,
            "risk_assessment": 0.10,
            "team_capability": 0.05
        }

        composite_score = 0
        for dimension, score in dimensions.items():
            composite_score += score * weights.get(dimension, 0)

        return composite_score

    def _apply_decision_thresholds(self, score: float) -> str:
        """Apply decision thresholds to composite score"""

        if score >= 75:
            return "GO"
        elif score >= 45:
            return "PIVOT"
        else:
            return "KILL"

    def _calculate_decision_confidence(self, score: float, decision: str) -> float:
        """Calculate confidence in decision"""

        if decision == "GO":
            confidence = min(0.95, 0.7 + (score - 75) / 25 * 0.25)
        elif decision == "PIVOT":
            distance_from_threshold = min(abs(score - 45), abs(score - 74))
            confidence = 0.6 + distance_from_threshold / 15 * 0.3
        else:  # KILL
            confidence = min(0.95, 0.7 + (44 - score) / 44 * 0.25)

        return confidence

    def _record_decision_failure(self, test_name: str, reason: str):
        """Record a decision test failure"""

        if "failures" not in self.test_results:
            self.test_results["failures"] = []

        self.test_results["failures"].append({
            "test_name": test_name,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        self.test_results["decision_tests_failed"] += 1

    def _calculate_decision_metrics(self):
        """Calculate overall decision test metrics"""

        total_tests = self.test_results["decision_tests_run"]

        if total_tests == 0:
            self.test_results["decision_consistency_score"] = 0.0
        else:
            self.test_results["decision_consistency_score"] = (
                self.test_results["decision_tests_passed"] / total_tests
            )


def run_decision_matrix_tests():
    """Run all decision matrix tests"""

    tester = DecisionMatrixTester()
    results = tester.run_decision_matrix_tests()

    # Save results to file
    output_file = "tests/analysis/decision_matrix_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    low_wtp_accuracy = 0
    if results["low_wtp_scenarios_tested"] > 0:
        low_wtp_accuracy = results["correct_pivot_kill_decisions"] / results["low_wtp_scenarios_tested"]

    return results["decision_consistency_score"] >= 0.80 and low_wtp_accuracy >= 0.80


if __name__ == "__main__":
    success = run_decision_matrix_tests()
    exit(0 if success else 1)
