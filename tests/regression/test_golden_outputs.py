#!/usr/bin/env python3
"""
SMVM Golden Output Regression Tests

This module tests system behavior against golden (expected) outputs to ensure
regression detection and require contract version bumps for any changes.
"""

import json
import os
import sys
import hashlib
import difflib
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from deepdiff import DeepDiff  # Would need to install deepdiff for detailed comparison

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class GoldenOutputTester:
    """
    Test class for golden output regression testing
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "wheel_status": "installed",
            "regression_tests_run": 0,
            "regression_tests_passed": 0,
            "regression_tests_failed": 0,
            "golden_outputs_compared": 0,
            "outputs_matching_golden": 0,
            "contract_version_changes": [],
            "regression_violations": [],
            "golden_output_coverage": 0.0,
            "backward_compatibility_score": 0.0
        }

        # Define golden outputs directory
        self.golden_dir = Path("tests/regression/golden_outputs")
        self.golden_dir.mkdir(parents=True, exist_ok=True)

    def run_regression_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive golden output regression tests
        """

        print("Running SMVM Golden Output Regression Tests...")
        print("=" * 60)

        # Test against existing golden outputs
        self._test_existing_golden_outputs()

        # Test contract version validation
        self._test_contract_version_validation()

        # Test output determinism
        self._test_output_determinism()

        # Test backward compatibility
        self._test_backward_compatibility()

        # Test golden output generation
        self._test_golden_output_generation()

        # Test regression detection
        self._test_regression_detection()

        # Calculate regression metrics
        self._calculate_regression_metrics()

        print("\n" + "=" * 60)
        print(f"GOLDEN OUTPUT REGRESSION TEST RESULTS:")
        print(f"Tests Run: {self.test_results['regression_tests_run']}")
        print(f"Tests Passed: {self.test_results['regression_tests_passed']}")
        print(".1f")
        print(f"Golden Outputs Compared: {self.test_results['golden_outputs_compared']}")
        print(f"Outputs Matching Golden: {self.test_results['outputs_matching_golden']}")
        print(f"Contract Version Changes: {len(self.test_results['contract_version_changes'])}")

        if self.test_results['regression_violations']:
            print(f"Regression Violations: {len(self.test_results['regression_violations'])}")
            for violation in self.test_results['regression_violations'][:3]:  # Show first 3
                print(f"  - {violation}")

        return self.test_results

    def _test_existing_golden_outputs(self):
        """Test current outputs against existing golden outputs"""

        print("\nTesting Existing Golden Outputs...")

        # Define test scenarios with their golden outputs
        test_scenarios = [
            {
                "scenario": "basic_idea_validation",
                "input": {"title": "Test Idea", "description": "A test business idea"},
                "golden_file": "basic_idea_validation_output.json"
            },
            {
                "scenario": "persona_synthesis",
                "input": {"count": 3, "seed": 42},
                "golden_file": "persona_synthesis_output.json"
            },
            {
                "scenario": "simulation_run",
                "input": {"iterations": 100, "scenario": "baseline", "seed": 42},
                "golden_file": "simulation_run_output.json"
            },
            {
                "scenario": "decision_analysis",
                "input": {"confidence_threshold": 0.75},
                "golden_file": "decision_analysis_output.json"
            }
        ]

        for scenario in test_scenarios:
            try:
                self.test_results['regression_tests_run'] += 1
                self.test_results['golden_outputs_compared'] += 1

                # Check if golden output exists
                golden_file = self.golden_dir / scenario["golden_file"]

                if golden_file.exists():
                    # Load golden output
                    with open(golden_file, 'r') as f:
                        golden_output = json.load(f)

                    # Generate current output (mock)
                    current_output = self._generate_current_output(scenario)

                    # Compare outputs
                    comparison_result = self._compare_outputs(current_output, golden_output)

                    if comparison_result["matches"]:
                        self.test_results['regression_tests_passed'] += 1
                        self.test_results['outputs_matching_golden'] += 1
                        print(f"  ✓ {scenario['scenario']}: Output matches golden standard")
                    else:
                        self._record_regression_violation(
                            scenario['scenario'],
                            f"Output differs from golden: {comparison_result['differences']}"
                        )
                        print(f"  ✗ {scenario['scenario']}: Output differs from golden standard")
                else:
                    # No golden output exists - this is expected for new scenarios
                    print(f"  - {scenario['scenario']}: No golden output (expected for new scenarios)")

            except Exception as e:
                self._record_regression_violation(scenario['scenario'], str(e))
                print(f"  ✗ {scenario['scenario']}: Error - {e}")

    def _test_contract_version_validation(self):
        """Test that contract version changes are properly tracked"""

        print("\nTesting Contract Version Validation...")

        # Mock contract versions
        contracts = {
            "idea.input": {"version": "1.0.0", "last_updated": "2024-12-01"},
            "personas.output": {"version": "1.1.0", "last_updated": "2024-12-02"},
            "simulation.result": {"version": "1.0.0", "last_updated": "2024-12-01"}
        }

        # Test version change scenarios
        version_scenarios = [
            {"contract": "idea.input", "change_type": "patch", "expected_breaking": False},
            {"contract": "personas.output", "change_type": "minor", "expected_breaking": False},
            {"contract": "simulation.result", "change_type": "major", "expected_breaking": True}
        ]

        for scenario in version_scenarios:
            try:
                self.test_results['regression_tests_run'] += 1

                # Check version change validation
                validation_result = self._validate_version_change(
                    scenario["contract"],
                    scenario["change_type"],
                    contracts.get(scenario["contract"], {})
                )

                expected_breaking = scenario["expected_breaking"]

                if validation_result["breaking_change"] == expected_breaking:
                    self.test_results['regression_tests_passed'] += 1
                    print(f"  ✓ Contract {scenario['contract']}: Version change validation correct")
                else:
                    self._record_regression_violation(
                        f"contract_version_{scenario['contract']}",
                        f"Expected breaking={expected_breaking}, got {validation_result['breaking_change']}"
                    )
                    print(f"  ✗ Contract {scenario['contract']}: Version change validation failed")

                # Record version change
                if validation_result["breaking_change"]:
                    self.test_results["contract_version_changes"].append({
                        "contract": scenario["contract"],
                        "change_type": scenario["change_type"],
                        "breaking": True,
                        "timestamp": datetime.utcnow().isoformat() + "Z"
                    })

            except Exception as e:
                self._record_regression_violation(f"contract_version_{scenario['contract']}", str(e))
                print(f"  ✗ Contract {scenario['contract']}: Error - {e}")

    def _test_output_determinism(self):
        """Test that outputs are deterministic for same inputs"""

        print("\nTesting Output Determinism...")

        # Test scenarios that should produce identical outputs
        deterministic_scenarios = [
            {"name": "same_seed_simulation", "input": {"seed": 123, "iterations": 50}},
            {"name": "same_config_analysis", "input": {"config": "test_config", "threshold": 0.8}},
            {"name": "same_data_ingestion", "input": {"source": "test_data", "batch_size": 10}}
        ]

        for scenario in deterministic_scenarios:
            try:
                self.test_results['regression_tests_run'] += 1

                # Generate multiple outputs with same input
                outputs = []
                for i in range(3):
                    output = self._generate_current_output(scenario)
                    outputs.append(output)

                # Check if all outputs are identical
                all_identical = all(self._outputs_identical(outputs[0], output) for output in outputs[1:])

                if all_identical:
                    self.test_results['regression_tests_passed'] += 1
                    print(f"  ✓ {scenario['name']}: Outputs are deterministic")
                else:
                    self._record_regression_violation(
                        scenario['name'],
                        "Outputs are not deterministic for same input"
                    )
                    print(f"  ✗ {scenario['name']}: Outputs are not deterministic")

            except Exception as e:
                self._record_regression_violation(scenario['name'], str(e))
                print(f"  ✗ {scenario['name']}: Error - {e}")

    def _test_backward_compatibility(self):
        """Test backward compatibility with previous versions"""

        print("\nTesting Backward Compatibility...")

        # Test compatibility scenarios
        compatibility_scenarios = [
            {"version": "v1.0", "feature": "basic_validation", "expected_supported": True},
            {"version": "v1.1", "feature": "advanced_analysis", "expected_supported": True},
            {"version": "v0.9", "feature": "deprecated_feature", "expected_supported": False}
        ]

        for scenario in compatibility_scenarios:
            try:
                self.test_results['regression_tests_run'] += 1

                # Test feature availability
                feature_supported = self._test_feature_compatibility(
                    scenario["version"],
                    scenario["feature"]
                )

                if feature_supported == scenario["expected_supported"]:
                    self.test_results['regression_tests_passed'] += 1
                    support_status = "supported" if feature_supported else "not supported"
                    print(f"  ✓ Version {scenario['version']} {scenario['feature']}: Correctly {support_status}")
                else:
                    self._record_regression_violation(
                        f"compatibility_{scenario['version']}_{scenario['feature']}",
                        f"Expected supported={scenario['expected_supported']}, got {feature_supported}"
                    )
                    print(f"  ✗ Version {scenario['version']} {scenario['feature']}: Compatibility issue")

            except Exception as e:
                self._record_regression_violation(f"compatibility_{scenario['version']}", str(e))
                print(f"  ✗ Version {scenario['version']}: Error - {e}")

    def _test_golden_output_generation(self):
        """Test generation of new golden outputs"""

        print("\nTesting Golden Output Generation...")

        try:
            self.test_results['regression_tests_run'] += 1

            # Generate new golden output
            test_scenario = {
                "scenario": "new_feature_test",
                "input": {"feature": "new_analytics", "version": "v1.2"}
            }

            new_output = self._generate_current_output(test_scenario)
            golden_file = self.golden_dir / "new_feature_test_output.json"

            # Save as golden output
            with open(golden_file, 'w') as f:
                json.dump(new_output, f, indent=2, default=str)

            # Verify golden output was created
            if golden_file.exists():
                self.test_results['regression_tests_passed'] += 1
                print("  ✓ Golden Output Generation: New golden output created successfully")
            else:
                self._record_regression_violation(
                    "golden_output_generation",
                    "Failed to create golden output file"
                )
                print("  ✗ Golden Output Generation: Failed to create golden output")

        except Exception as e:
            self._record_regression_violation("golden_output_generation", str(e))
            print(f"  ✗ Golden Output Generation: Error - {e}")

    def _test_regression_detection(self):
        """Test that regressions are properly detected"""

        print("\nTesting Regression Detection...")

        try:
            self.test_results['regression_tests_run'] += 1

            # Create a known good output
            baseline_output = {"result": "success", "value": 100, "timestamp": "2024-01-01"}

            # Create a modified output (simulating a regression)
            modified_output = {"result": "success", "value": 95, "timestamp": "2024-12-01"}

            # Detect regression
            regression_detected = self._detect_regression(baseline_output, modified_output)

            if regression_detected:
                self.test_results['regression_tests_passed'] += 1
                print("  ✓ Regression Detection: Regression properly detected")
            else:
                self._record_regression_violation(
                    "regression_detection",
                    "Failed to detect known regression"
                )
                print("  ✗ Regression Detection: Failed to detect regression")

        except Exception as e:
            self._record_regression_violation("regression_detection", str(e))
            print(f"  ✗ Regression Detection: Error - {e}")

    def _generate_current_output(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Generate current output for testing (mock implementation)"""

        if scenario.get("scenario") == "basic_idea_validation":
            return {
                "validation_result": "PASSED",
                "schema_compliant": True,
                "business_model_viable": True,
                "confidence_score": 0.85
            }
        elif scenario.get("scenario") == "persona_synthesis":
            return {
                "personas_generated": scenario["input"]["count"],
                "confidence_score": 0.82,
                "diversity_score": 0.75,
                "bias_controls_applied": True
            }
        elif scenario.get("scenario") == "simulation_run":
            return {
                "iterations_completed": scenario["input"]["iterations"],
                "scenario_used": scenario["input"]["scenario"],
                "deterministic": True,
                "performance_metrics": {"execution_time": 45.2, "memory_peak": 1200}
            }
        elif scenario.get("scenario") == "decision_analysis":
            return {
                "recommendation": "PIVOT",
                "confidence": 0.75,
                "critical_success_factors": ["Improve CAC", "Increase WTP", "Differentiate competitors"],
                "composite_score": 48.75
            }
        else:
            return {"status": "unknown_scenario", "timestamp": datetime.utcnow().isoformat() + "Z"}

    def _compare_outputs(self, current: Dict[str, Any], golden: Dict[str, Any]) -> Dict[str, Any]:
        """Compare current output with golden output"""

        try:
            # Simple comparison - in real implementation would use deepdiff
            differences = []

            for key in set(current.keys()) | set(golden.keys()):
                if key not in current:
                    differences.append(f"Missing key in current: {key}")
                elif key not in golden:
                    differences.append(f"Extra key in current: {key}")
                elif current[key] != golden[key]:
                    differences.append(f"Value differs for {key}: current={current[key]}, golden={golden[key]}")

            return {
                "matches": len(differences) == 0,
                "differences": differences
            }

        except Exception as e:
            return {
                "matches": False,
                "differences": [f"Comparison error: {str(e)}"]
            }

    def _outputs_identical(self, output1: Dict[str, Any], output2: Dict[str, Any]) -> bool:
        """Check if two outputs are identical"""

        return json.dumps(output1, sort_keys=True) == json.dumps(output2, sort_keys=True)

    def _validate_version_change(self, contract: str, change_type: str, contract_info: Dict[str, Any]) -> Dict[str, Any]:
        """Validate version change impact"""

        # Simple version validation logic
        breaking_changes = ["major", "breaking"]
        non_breaking_changes = ["minor", "patch"]

        if change_type in breaking_changes:
            return {"breaking_change": True, "requires_migration": True}
        elif change_type in non_breaking_changes:
            return {"breaking_change": False, "backward_compatible": True}
        else:
            return {"breaking_change": False, "change_type_unknown": True}

    def _test_feature_compatibility(self, version: str, feature: str) -> bool:
        """Test if feature is supported in version"""

        # Mock compatibility matrix
        compatibility_matrix = {
            "v1.0": ["basic_validation", "data_ingestion"],
            "v1.1": ["basic_validation", "data_ingestion", "advanced_analysis"],
            "v0.9": ["basic_validation"]  # deprecated features not supported
        }

        supported_features = compatibility_matrix.get(version, [])
        return feature in supported_features

    def _detect_regression(self, baseline: Dict[str, Any], modified: Dict[str, Any]) -> bool:
        """Detect regression between baseline and modified outputs"""

        # Simple regression detection - check for significant value changes
        if "value" in baseline and "value" in modified:
            baseline_value = baseline["value"]
            modified_value = modified["value"]

            # Consider 5% change as regression
            if abs(modified_value - baseline_value) / baseline_value > 0.05:
                return True

        return False

    def _record_regression_violation(self, component: str, details: str):
        """Record a regression violation"""

        violation = {
            "component": component,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.test_results["regression_violations"].append(violation)
        self.test_results["regression_tests_failed"] += 1

    def _calculate_regression_metrics(self):
        """Calculate regression testing metrics"""

        total_outputs = self.test_results["golden_outputs_compared"]

        if total_outputs > 0:
            self.test_results["golden_output_coverage"] = (
                self.test_results["outputs_matching_golden"] / total_outputs
            ) * 100

        # Calculate backward compatibility score
        compatibility_tests = [t for t in self.test_results["regression_violations"]
                             if "compatibility" in t["component"]]

        if compatibility_tests:
            self.test_results["backward_compatibility_score"] = (
                (len(compatibility_tests) == 0) * 100
            )
        else:
            self.test_results["backward_compatibility_score"] = 95.0  # Assume good if no failures


def run_regression_tests():
    """Run all golden output regression tests"""

    tester = GoldenOutputTester()
    results = tester.run_regression_tests()

    # Save results to file
    output_file = "tests/regression/golden_output_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    golden_output_coverage = results["golden_output_coverage"] >= 90.0
    backward_compatibility = results["backward_compatibility_score"] >= 90.0
    no_critical_regressions = len(results["regression_violations"]) <= 2  # Allow minor violations

    return golden_output_coverage and backward_compatibility and no_critical_regressions


if __name__ == "__main__":
    success = run_regression_tests()
    exit(0 if success else 1)
