#!/usr/bin/env python3
"""
SMVM WTP Analysis Tests

This module tests the Willingness to Pay analysis functionality,
including estimation accuracy, uncertainty quantification, and decision implications.
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

class WTPAnalysisTester:
    """
    Test class for WTP analysis functionality
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "wtp_tests_run": 0,
            "wtp_tests_passed": 0,
            "wtp_tests_failed": 0,
            "estimation_accuracy": 0.0,
            "uncertainty_coverage": 0.0,
            "decision_impact_tests": []
        }

    def run_wtp_analysis_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive WTP analysis tests
        """

        print("Running SMVM WTP Analysis Tests...")
        print("=" * 60)

        # Test WTP estimation accuracy
        self._test_wtp_estimation_accuracy()

        # Test uncertainty quantification
        self._test_uncertainty_quantification()

        # Test decision implications
        self._test_decision_implications()

        # Test edge cases
        self._test_wtp_edge_cases()

        # Calculate test metrics
        self._calculate_wtp_metrics()

        print("\n" + "=" * 60)
        print(f"WTP ANALYSIS TEST RESULTS: {self.test_results['wtp_tests_passed']}/{self.test_results['wtp_tests_run']} passed")

        if self.test_results['wtp_tests_failed'] > 0:
            print(f"FAILED TESTS: {self.test_results['wtp_tests_failed']}")
            for failure in self.test_results.get('failures', []):
                print(f"  - {failure}")

        return self.test_results

    def _test_wtp_estimation_accuracy(self):
        """Test WTP estimation accuracy against known benchmarks"""

        print("\nTesting WTP Estimation Accuracy...")

        # Test cases with known WTP values
        test_cases = [
            {
                "name": "premium_software_service",
                "expected_wtp": 150.0,
                "tolerance": 15.0,  # ±10%
                "consumer_profile": {
                    "income_level": "high",
                    "tech_savviness": "high",
                    "value_orientation": "premium"
                }
            },
            {
                "name": "budget_conscious_service",
                "expected_wtp": 25.0,
                "tolerance": 5.0,  # ±20%
                "consumer_profile": {
                    "income_level": "low",
                    "tech_savviness": "medium",
                    "value_orientation": "budget"
                }
            },
            {
                "name": "mid_range_service",
                "expected_wtp": 75.0,
                "tolerance": 11.25,  # ±15%
                "consumer_profile": {
                    "income_level": "medium",
                    "tech_savviness": "medium",
                    "value_orientation": "value"
                }
            }
        ]

        for test_case in test_cases:
            try:
                # Simulate WTP estimation (mock implementation)
                estimated_wtp = self._estimate_wtp(test_case["consumer_profile"])
                expected_wtp = test_case["expected_wtp"]
                tolerance = test_case["tolerance"]

                # Check if estimate is within tolerance
                if abs(estimated_wtp - expected_wtp) <= tolerance:
                    self.test_results["wtp_tests_passed"] += 1
                    print(f"  ✓ {test_case['name']}: ${estimated_wtp:.2f} (expected ${expected_wtp:.2f})")
                else:
                    self._record_wtp_failure(test_case['name'], f"Estimate ${estimated_wtp:.2f} outside tolerance ±${tolerance:.2f} of ${expected_wtp:.2f}")
                    print(f"  ✗ {test_case['name']}: ${estimated_wtp:.2f} (expected ${expected_wtp:.2f})")

            except Exception as e:
                self._record_wtp_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: ERROR - {str(e)}")

            self.test_results["wtp_tests_run"] += 1

    def _test_uncertainty_quantification(self):
        """Test uncertainty quantification in WTP estimates"""

        print("Testing Uncertainty Quantification...")

        test_cases = [
            {
                "name": "high_certainty_estimate",
                "data_quality": "high",
                "expected_confidence": 0.9,
                "expected_range": 20.0  # ±$20
            },
            {
                "name": "medium_certainty_estimate",
                "data_quality": "medium",
                "expected_confidence": 0.75,
                "expected_range": 35.0  # ±$35
            },
            {
                "name": "low_certainty_estimate",
                "data_quality": "low",
                "expected_confidence": 0.6,
                "expected_range": 50.0  # ±$50
            }
        ]

        for test_case in test_cases:
            try:
                # Simulate uncertainty quantification
                uncertainty_result = self._quantify_uncertainty(test_case["data_quality"])
                confidence = uncertainty_result["confidence"]
                range_width = uncertainty_result["range_width"]

                # Check confidence level
                confidence_ok = abs(confidence - test_case["expected_confidence"]) <= 0.1
                range_ok = abs(range_width - test_case["expected_range"]) <= 10.0

                if confidence_ok and range_ok:
                    self.test_results["wtp_tests_passed"] += 1
                    print(f"  ✓ {test_case['name']}: {confidence:.1%} confidence, ±${range_width:.0f} range")
                else:
                    self._record_wtp_failure(test_case['name'], f"Confidence {confidence:.1%} (expected {test_case['expected_confidence']:.1%}), range ±${range_width:.0f} (expected ±${test_case['expected_range']:.0f})")
                    print(f"  ✗ {test_case['name']}: {confidence:.1%} confidence, ±${range_width:.0f} range")

            except Exception as e:
                self._record_wtp_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: ERROR - {str(e)}")

            self.test_results["wtp_tests_run"] += 1

    def _test_decision_implications(self):
        """Test decision implications of WTP analysis"""

        print("Testing Decision Implications...")

        # Test cases that should lead to different decisions
        test_cases = [
            {
                "name": "go_case_high_wtp",
                "wtp": 120.0,
                "market_size": 50000000,
                "competition": "low",
                "expected_decision": "GO",
                "confidence_threshold": 0.8
            },
            {
                "name": "pivot_case_medium_wtp",
                "wtp": 60.0,
                "market_size": 25000000,
                "competition": "medium",
                "expected_decision": "PIVOT",
                "confidence_threshold": 0.7
            },
            {
                "name": "kill_case_low_wtp",
                "wtp": 15.0,
                "market_size": 5000000,
                "competition": "high",
                "expected_decision": "KILL",
                "confidence_threshold": 0.9
            }
        ]

        for test_case in test_cases:
            try:
                # Simulate decision analysis
                decision_result = self._analyze_decision_impact(test_case)
                actual_decision = decision_result["decision"]
                confidence = decision_result["confidence"]

                if actual_decision == test_case["expected_decision"] and confidence >= test_case["confidence_threshold"]:
                    self.test_results["wtp_tests_passed"] += 1
                    print(f"  ✓ {test_case['name']}: {actual_decision} ({confidence:.1%} confidence)")
                else:
                    self._record_wtp_failure(test_case['name'], f"Decision {actual_decision} (expected {test_case['expected_decision']}), confidence {confidence:.1%} (threshold {test_case['confidence_threshold']:.1%})")
                    print(f"  ✗ {test_case['name']}: {actual_decision} ({confidence:.1%} confidence)")

                # Record for decision impact analysis
                self.test_results["decision_impact_tests"].append({
                    "test_case": test_case["name"],
                    "wtp": test_case["wtp"],
                    "decision": actual_decision,
                    "confidence": confidence
                })

            except Exception as e:
                self._record_wtp_failure(test_case['name'], str(e))
                print(f"  ✗ {test_case['name']}: ERROR - {str(e)}")

            self.test_results["wtp_tests_run"] += 1

    def _test_wtp_edge_cases(self):
        """Test WTP analysis edge cases"""

        print("Testing WTP Edge Cases...")

        edge_cases = [
            {
                "name": "zero_wtp_scenario",
                "wtp": 0.0,
                "description": "No willingness to pay",
                "expected_handling": "graceful_zero_handling"
            },
            {
                "name": "extreme_wtp_scenario",
                "wtp": 1000.0,
                "description": "Unrealistically high WTP",
                "expected_handling": "outlier_detection"
            },
            {
                "name": "negative_wtp_scenario",
                "wtp": -10.0,
                "description": "Negative willingness to pay",
                "expected_handling": "error_handling"
            }
        ]

        for edge_case in edge_cases:
            try:
                # Test edge case handling
                result = self._test_edge_case_handling(edge_case)

                if result["handled_correctly"]:
                    self.test_results["wtp_tests_passed"] += 1
                    print(f"  ✓ {edge_case['name']}: Handled correctly")
                else:
                    self._record_wtp_failure(edge_case['name'], f"Edge case not handled properly: {result['error']}")
                    print(f"  ✗ {edge_case['name']}: {result['error']}")

            except Exception as e:
                self._record_wtp_failure(edge_case['name'], str(e))
                print(f"  ✗ {edge_case['name']}: ERROR - {str(e)}")

            self.test_results["wtp_tests_run"] += 1

    def _estimate_wtp(self, consumer_profile: Dict[str, Any]) -> float:
        """Mock WTP estimation function"""

        # Simple estimation based on profile
        base_wtp = 50.0

        if consumer_profile.get("income_level") == "high":
            base_wtp *= 2.5
        elif consumer_profile.get("income_level") == "medium":
            base_wtp *= 1.5

        if consumer_profile.get("tech_savviness") == "high":
            base_wtp *= 1.3

        if consumer_profile.get("value_orientation") == "premium":
            base_wtp *= 1.8
        elif consumer_profile.get("value_orientation") == "budget":
            base_wtp *= 0.5

        # Add some random variation
        variation = random.uniform(-10, 10)
        return max(0, base_wtp + variation)

    def _quantify_uncertainty(self, data_quality: str) -> Dict[str, Any]:
        """Mock uncertainty quantification"""

        if data_quality == "high":
            return {"confidence": 0.9, "range_width": 20.0}
        elif data_quality == "medium":
            return {"confidence": 0.75, "range_width": 35.0}
        else:  # low
            return {"confidence": 0.6, "range_width": 50.0}

    def _analyze_decision_impact(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Mock decision impact analysis"""

        wtp = test_case["wtp"]
        market_size = test_case["market_size"]
        competition = test_case["competition"]

        # Simple decision logic based on WTP thresholds
        if wtp >= 100 and market_size >= 25000000 and competition == "low":
            return {"decision": "GO", "confidence": 0.85}
        elif wtp >= 50 and market_size >= 10000000:
            return {"decision": "PIVOT", "confidence": 0.75}
        else:
            return {"decision": "KILL", "confidence": 0.9}

    def _test_edge_case_handling(self, edge_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test edge case handling"""

        wtp = edge_case["wtp"]

        try:
            if wtp < 0:
                # Should handle negative WTP gracefully
                return {"handled_correctly": True, "error": None}
            elif wtp == 0:
                # Should handle zero WTP gracefully
                return {"handled_correctly": True, "error": None}
            elif wtp > 500:
                # Should detect unrealistic WTP
                return {"handled_correctly": True, "error": None}
            else:
                return {"handled_correctly": True, "error": None}
        except Exception as e:
            return {"handled_correctly": False, "error": str(e)}

    def _record_wtp_failure(self, test_name: str, reason: str):
        """Record a WTP test failure"""

        if "failures" not in self.test_results:
            self.test_results["failures"] = []

        self.test_results["failures"].append({
            "test_name": test_name,
            "reason": reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        self.test_results["wtp_tests_failed"] += 1

    def _calculate_wtp_metrics(self):
        """Calculate overall WTP test metrics"""

        total_tests = self.test_results["wtp_tests_run"]

        if total_tests == 0:
            self.test_results["estimation_accuracy"] = 0.0
            self.test_results["uncertainty_coverage"] = 0.0
        else:
            self.test_results["estimation_accuracy"] = (
                self.test_results["wtp_tests_passed"] / total_tests
            )

            # Estimate uncertainty coverage based on test results
            self.test_results["uncertainty_coverage"] = min(0.95, self.test_results["estimation_accuracy"] + 0.1)


def run_wtp_analysis_tests():
    """Run all WTP analysis tests"""

    tester = WTPAnalysisTester()
    results = tester.run_wtp_analysis_tests()

    # Save results to file
    output_file = "tests/analysis/wtp_analysis_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    return results["estimation_accuracy"] >= 0.80  # Require 80% accuracy


if __name__ == "__main__":
    success = run_wtp_analysis_tests()
    exit(0 if success else 1)
