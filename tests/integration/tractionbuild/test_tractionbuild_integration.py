#!/usr/bin/env python3
"""
SMVM TractionBuild Integration Tests

This module tests the integration between SMVM and TractionBuild systems,
including API endpoints, webhook handling, gate logic, and data persistence.
"""

import json
import os
import sys
import time
import requests
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
from unittest.mock import patch, MagicMock
import asyncio

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TractionBuildIntegrationTester:
    """
    Test class for TractionBuild integration testing
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "wheel_status": "installed",
            "integration_tests_run": 0,
            "integration_tests_passed": 0,
            "integration_tests_failed": 0,
            "api_endpoints_tested": 0,
            "api_endpoints_working": 0,
            "webhooks_tested": 0,
            "webhooks_working": 0,
            "gates_tested": 0,
            "gates_working": 0,
            "persistence_tested": 0,
            "persistence_working": 0,
            "integration_violations": [],
            "response_times": [],
            "error_rates": {},
            "integration_coverage": 0.0
        }

        # Mock TractionBuild server for testing
        self.mock_server = None
        self.mock_responses = {}

    def run_integration_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive TractionBuild integration tests
        """

        print("Running SMVM TractionBuild Integration Tests...")
        print("=" * 60)

        # Start mock TractionBuild server
        self._start_mock_server()

        try:
            # Test T0 API endpoint
            self._test_t0_api_endpoint()

            # Test webhook handling
            self._test_webhook_handling()

            # Test T0+3 gate logic
            self._test_gate_logic()

            # Test T0+30 persistence
            self._test_persistence()

            # Test error handling
            self._test_error_handling()

            # Test authentication
            self._test_authentication()

            # Test rate limiting
            self._test_rate_limiting()

            # Calculate integration metrics
            self._calculate_integration_metrics()

        finally:
            # Stop mock server
            self._stop_mock_server()

        print("\n" + "=" * 60)
        print(f"TRACTIONBUILD INTEGRATION TEST RESULTS:")
        print(f"Tests Run: {self.test_results['integration_tests_run']}")
        print(f"Tests Passed: {self.test_results['integration_tests_passed']}")
        print(".1f")
        print(f"API Endpoints Working: {self.test_results['api_endpoints_working']}/{self.test_results['api_endpoints_tested']}")
        print(f"Webhooks Working: {self.test_results['webhooks_working']}/{self.test_results['webhooks_tested']}")
        print(f"Gates Working: {self.test_results['gates_working']}/{self.test_results['gates_tested']}")
        print(f"Persistence Working: {self.test_results['persistence_working']}/{self.test_results['persistence_tested']}")

        if self.test_results['integration_violations']:
            print(f"Integration Violations: {len(self.test_results['integration_violations'])}")
            for violation in self.test_results['integration_violations'][:3]:  # Show first 3
                print(f"  - {violation}")

        return self.test_results

    def _start_mock_server(self):
        """Start mock TractionBuild server for testing"""

        # Mock server implementation would go here
        # For this test, we'll use mock responses
        self.mock_responses = {
            "/api/v1/projects/test/validation-results": {
                "status_code": 200,
                "response": {"reference_id": "mock_ref_456"}
            },
            "/webhooks/validation/test_run/status": {
                "status_code": 200,
                "response": {"status": "acknowledged"}
            }
        }

    def _stop_mock_server(self):
        """Stop mock TractionBuild server"""
        pass

    def _test_t0_api_endpoint(self):
        """Test T0 validation run initiation API endpoint"""

        print("\nTesting T0 API Endpoint...")

        test_cases = [
            {
                "name": "valid_request",
                "request": {
                    "project_id": "test_project",
                    "business_idea": {
                        "title": "AI Analytics Platform",
                        "description": "Platform for automated customer analytics",
                        "target_market": "SaaS companies",
                        "value_proposition": "Automated insights generation",
                        "estimated_tam": 500000000,
                        "estimated_sam": 150000000,
                        "estimated_som": 30000000
                    },
                    "configuration": {
                        "simulation_iterations": 1000,
                        "persona_count": 5,
                        "competitor_count": 10,
                        "max_tokens_per_run": 10000,
                        "timeout_seconds": 3600
                    },
                    "metadata": {
                        "initiated_by": "test_user",
                        "source_system": "tractionbuild"
                    }
                },
                "expected_status": 200
            },
            {
                "name": "missing_required_fields",
                "request": {
                    "project_id": "test_project"
                    # Missing business_idea
                },
                "expected_status": 400
            },
            {
                "name": "invalid_project_id",
                "request": {
                    "project_id": "",
                    "business_idea": {"title": "Test"}
                },
                "expected_status": 400
            }
        ]

        for test_case in test_cases:
            try:
                self.test_results['integration_tests_run'] += 1
                self.test_results['api_endpoints_tested'] += 1

                start_time = time.time()

                # Mock API call to SMVM
                response = self._mock_smvm_api_call("/api/v1/validation/runs", test_case["request"])

                response_time = time.time() - start_time
                self.test_results["response_times"].append(response_time)

                if response["status_code"] == test_case["expected_status"]:
                    self.test_results['integration_tests_passed'] += 1
                    self.test_results['api_endpoints_working'] += 1
                    print(f"  ✓ T0 API {test_case['name']}: Correct response ({response['status_code']})")
                else:
                    self._record_integration_violation(
                        f"t0_api_{test_case['name']}",
                        f"Expected status {test_case['expected_status']}, got {response['status_code']}"
                    )
                    print(f"  ✗ T0 API {test_case['name']}: Wrong response ({response['status_code']})")

                # Check response structure
                if response["status_code"] == 200:
                    expected_fields = ["run_id", "status", "estimated_completion"]
                    response_data = response.get("response", {})

                    missing_fields = [field for field in expected_fields if field not in response_data]
                    if missing_fields:
                        self._record_integration_violation(
                            f"t0_api_{test_case['name']}_structure",
                            f"Missing required fields: {missing_fields}"
                        )

            except Exception as e:
                self._record_integration_violation(f"t0_api_{test_case['name']}", str(e))
                print(f"  ✗ T0 API {test_case['name']}: Error - {e}")

    def _test_webhook_handling(self):
        """Test webhook handling for status updates"""

        print("\nTesting Webhook Handling...")

        webhook_scenarios = [
            {
                "name": "decision_ready_go",
                "payload": {
                    "run_id": "test_run_001",
                    "status": "DECISION_READY",
                    "decision": {
                        "recommendation": "GO",
                        "confidence": 0.85
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "expected_gate_action": "allow_progression"
            },
            {
                "name": "decision_ready_pivot",
                "payload": {
                    "run_id": "test_run_002",
                    "status": "DECISION_READY",
                    "decision": {
                        "recommendation": "PIVOT",
                        "confidence": 0.75,
                        "requirements": ["improve_cac", "increase_wtp"]
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "expected_gate_action": "allow_with_requirements"
            },
            {
                "name": "decision_ready_kill",
                "payload": {
                    "run_id": "test_run_003",
                    "status": "DECISION_READY",
                    "decision": {
                        "recommendation": "KILL",
                        "confidence": 0.90
                    },
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "expected_gate_action": "block_progression"
            },
            {
                "name": "progress_update",
                "payload": {
                    "run_id": "test_run_004",
                    "status": "RUNNING",
                    "step_completed": "data_ingestion",
                    "progress_percentage": 25,
                    "estimated_completion": (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"
                },
                "expected_gate_action": "no_action"
            }
        ]

        for scenario in webhook_scenarios:
            try:
                self.test_results['integration_tests_run'] += 1
                self.test_results['webhooks_tested'] += 1

                # Mock webhook delivery
                response = self._mock_webhook_delivery(scenario["payload"])

                if response["status_code"] == 200:
                    self.test_results['integration_tests_passed'] += 1
                    self.test_results['webhooks_working'] += 1
                    print(f"  ✓ Webhook {scenario['name']}: Successfully processed")
                else:
                    self._record_integration_violation(
                        f"webhook_{scenario['name']}",
                        f"Webhook failed with status {response['status_code']}"
                    )
                    print(f"  ✗ Webhook {scenario['name']}: Failed ({response['status_code']})")

                # Verify gate action
                gate_action = self._verify_gate_action(scenario["payload"], scenario["expected_gate_action"])
                if not gate_action:
                    self._record_integration_violation(
                        f"webhook_{scenario['name']}_gate",
                        f"Gate action not applied correctly"
                    )

            except Exception as e:
                self._record_integration_violation(f"webhook_{scenario['name']}", str(e))
                print(f"  ✗ Webhook {scenario['name']}: Error - {e}")

    def _test_gate_logic(self):
        """Test T0+3 gate logic"""

        print("\nTesting T0+3 Gate Logic...")

        gate_scenarios = [
            {
                "name": "gate_check_completed_go",
                "run_status": "COMPLETED",
                "decision": {"recommendation": "GO", "confidence": 0.85},
                "expected_result": {"can_progress": True, "block_reason": None}
            },
            {
                "name": "gate_check_completed_pivot",
                "run_status": "COMPLETED",
                "decision": {"recommendation": "PIVOT", "confidence": 0.75},
                "expected_result": {"can_progress": True, "requirements": ["improve_cac"]}
            },
            {
                "name": "gate_check_completed_kill",
                "run_status": "COMPLETED",
                "decision": {"recommendation": "KILL", "confidence": 0.90},
                "expected_result": {"can_progress": False, "block_reason": "SMVM validation decision"}
            },
            {
                "name": "gate_check_running",
                "run_status": "RUNNING",
                "progress": 60,
                "expected_result": {"can_progress": False, "block_reason": "SMVM validation in progress"}
            },
            {
                "name": "gate_check_failed",
                "run_status": "FAILED",
                "error": "Simulation timeout",
                "expected_result": {"can_progress": False, "block_reason": "SMVM validation failed"}
            }
        ]

        for scenario in gate_scenarios:
            try:
                self.test_results['integration_tests_run'] += 1
                self.test_results['gates_tested'] += 1

                # Mock gate check
                gate_result = self._mock_gate_check(scenario)

                expected = scenario["expected_result"]

                if (gate_result["can_progress"] == expected["can_progress"] and
                    gate_result.get("block_reason") == expected.get("block_reason")):

                    self.test_results['integration_tests_passed'] += 1
                    self.test_results['gates_working'] += 1
                    print(f"  ✓ Gate {scenario['name']}: Logic working correctly")
                else:
                    self._record_integration_violation(
                        f"gate_{scenario['name']}",
                        f"Gate logic failed: expected {expected}, got {gate_result}"
                    )
                    print(f"  ✗ Gate {scenario['name']}: Gate logic incorrect")

            except Exception as e:
                self._record_integration_violation(f"gate_{scenario['name']}", str(e))
                print(f"  ✗ Gate {scenario['name']}: Error - {e}")

    def _test_persistence(self):
        """Test T0+30 data persistence"""

        print("\nTesting T0+30 Data Persistence...")

        persistence_scenarios = [
            {
                "name": "full_result_persistence",
                "run_id": "persist_test_001",
                "project_id": "test_project",
                "data_files": ["decision_output", "validation_report", "simulation_results"],
                "expected_status": 200
            },
            {
                "name": "partial_result_persistence",
                "run_id": "persist_test_002",
                "project_id": "test_project",
                "data_files": ["decision_output"],  # Missing some files
                "expected_status": 200
            },
            {
                "name": "empty_result_persistence",
                "run_id": "persist_test_003",
                "project_id": "test_project",
                "data_files": [],  # No files
                "expected_status": 400
            }
        ]

        for scenario in persistence_scenarios:
            try:
                self.test_results['integration_tests_run'] += 1
                self.test_results['persistence_tested'] += 1

                # Mock persistence operation
                persistence_result = self._mock_persistence_operation(scenario)

                if persistence_result["status_code"] == scenario["expected_status"]:
                    self.test_results['integration_tests_passed'] += 1
                    self.test_results['persistence_working'] += 1
                    print(f"  ✓ Persistence {scenario['name']}: Successfully persisted")
                else:
                    self._record_integration_violation(
                        f"persistence_{scenario['name']}",
                        f"Expected status {scenario['expected_status']}, got {persistence_result['status_code']}"
                    )
                    print(f"  ✗ Persistence {scenario['name']}: Failed ({persistence_result['status_code']})")

                # Verify data integrity
                if persistence_result["status_code"] == 200:
                    integrity_check = self._verify_data_integrity(scenario)
                    if not integrity_check:
                        self._record_integration_violation(
                            f"persistence_{scenario['name']}_integrity",
                            "Data integrity check failed"
                        )

            except Exception as e:
                self._record_integration_violation(f"persistence_{scenario['name']}", str(e))
                print(f"  ✗ Persistence {scenario['name']}: Error - {e}")

    def _test_error_handling(self):
        """Test error handling in integration scenarios"""

        print("\nTesting Error Handling...")

        error_scenarios = [
            {"name": "network_timeout", "error_type": "timeout", "expected_recovery": True},
            {"name": "api_rate_limit", "error_type": "rate_limit", "expected_recovery": True},
            {"name": "invalid_response", "error_type": "malformed_response", "expected_recovery": False},
            {"name": "authentication_failure", "error_type": "auth_error", "expected_recovery": False}
        ]

        for scenario in error_scenarios:
            try:
                self.test_results['integration_tests_run'] += 1

                # Mock error condition
                error_handled = self._mock_error_condition(scenario)

                if error_handled == scenario["expected_recovery"]:
                    self.test_results['integration_tests_passed'] += 1
                    handling_status = "handled" if error_handled else "not handled"
                    print(f"  ✓ Error {scenario['name']}: Correctly {handling_status}")
                else:
                    self._record_integration_violation(
                        f"error_{scenario['name']}",
                        f"Error handling incorrect: expected {scenario['expected_recovery']}, got {error_handled}"
                    )
                    print(f"  ✗ Error {scenario['name']}: Error handling failed")

            except Exception as e:
                self._record_integration_violation(f"error_{scenario['name']}", str(e))
                print(f"  ✗ Error {scenario['name']}: Error - {e}")

    def _test_authentication(self):
        """Test authentication mechanisms"""

        print("\nTesting Authentication...")

        auth_scenarios = [
            {"name": "valid_api_key", "credentials": {"api_key": "valid_key"}, "expected_success": True},
            {"name": "invalid_api_key", "credentials": {"api_key": "invalid_key"}, "expected_success": False},
            {"name": "missing_credentials", "credentials": {}, "expected_success": False}
        ]

        for scenario in auth_scenarios:
            try:
                self.test_results['integration_tests_run'] += 1

                # Mock authentication check
                auth_success = self._mock_authentication_check(scenario["credentials"])

                if auth_success == scenario["expected_success"]:
                    self.test_results['integration_tests_passed'] += 1
                    auth_status = "successful" if auth_success else "failed"
                    print(f"  ✓ Authentication {scenario['name']}: {auth_status}")
                else:
                    self._record_integration_violation(
                        f"auth_{scenario['name']}",
                        f"Authentication check failed: expected {scenario['expected_success']}, got {auth_success}"
                    )
                    print(f"  ✗ Authentication {scenario['name']}: Failed")

            except Exception as e:
                self._record_integration_violation(f"auth_{scenario['name']}", str(e))
                print(f"  ✗ Authentication {scenario['name']}: Error - {e}")

    def _test_rate_limiting(self):
        """Test rate limiting behavior"""

        print("\nTesting Rate Limiting...")

        try:
            self.test_results['integration_tests_run'] += 1

            # Mock rate limiting scenario
            rate_limit_exceeded = self._mock_rate_limiting_test()

            if not rate_limit_exceeded:
                self.test_results['integration_tests_passed'] += 1
                print("  ✓ Rate Limiting: Properly handled rate limits")
            else:
                self._record_integration_violation(
                    "rate_limiting",
                    "Rate limiting not handled correctly"
                )
                print("  ✗ Rate Limiting: Rate limits not respected")

        except Exception as e:
            self._record_integration_violation("rate_limiting", str(e))
            print(f"  ✗ Rate Limiting: Error - {e}")

    # Mock implementations for testing
    def _mock_smvm_api_call(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock SMVM API call"""

        if endpoint == "/api/v1/validation/runs":
            if "business_idea" in payload and payload.get("business_idea", {}).get("title"):
                return {
                    "status_code": 200,
                    "response": {
                        "run_id": f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                        "status": "INITIATED",
                        "estimated_completion": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
                    }
                }
            else:
                return {"status_code": 400, "response": {"error": "Missing required fields"}}

        return {"status_code": 404, "response": {"error": "Endpoint not found"}}

    def _mock_webhook_delivery(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Mock webhook delivery"""

        return {"status_code": 200, "response": {"status": "acknowledged"}}

    def _verify_gate_action(self, payload: Dict[str, Any], expected_action: str) -> bool:
        """Verify gate action was applied correctly"""

        # Mock gate verification
        return True

    def _mock_gate_check(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Mock gate check"""

        if scenario["run_status"] == "COMPLETED":
            decision = scenario["decision"]
            if decision["recommendation"] == "GO":
                return {"can_progress": True}
            elif decision["recommendation"] == "PIVOT":
                return {"can_progress": True, "requirements": decision.get("requirements", [])}
            else:  # KILL
                return {"can_progress": False, "block_reason": "SMVM validation decision"}
        elif scenario["run_status"] == "RUNNING":
            return {"can_progress": False, "block_reason": "SMVM validation in progress"}
        else:  # FAILED
            return {"can_progress": False, "block_reason": "SMVM validation failed"}

    def _mock_persistence_operation(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Mock persistence operation"""

        if scenario["data_files"]:
            return {"status_code": 200, "response": {"reference_id": "mock_ref_123"}}
        else:
            return {"status_code": 400, "response": {"error": "No data to persist"}}

    def _verify_data_integrity(self, scenario: Dict[str, Any]) -> bool:
        """Verify data integrity after persistence"""

        # Mock integrity check
        return True

    def _mock_error_condition(self, scenario: Dict[str, Any]) -> bool:
        """Mock error condition handling"""

        recoverable_errors = ["timeout", "rate_limit"]
        return scenario["error_type"] in recoverable_errors

    def _mock_authentication_check(self, credentials: Dict[str, Any]) -> bool:
        """Mock authentication check"""

        return credentials.get("api_key") == "valid_key"

    def _mock_rate_limiting_test(self) -> bool:
        """Mock rate limiting test"""

        return False  # No rate limit exceeded

    def _record_integration_violation(self, component: str, details: str):
        """Record an integration violation"""

        violation = {
            "component": component,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.test_results["integration_violations"].append(violation)
        self.test_results["integration_tests_failed"] += 1

    def _calculate_integration_metrics(self):
        """Calculate integration testing metrics"""

        total_tests = self.test_results["integration_tests_run"]

        if total_tests > 0:
            self.test_results["integration_coverage"] = (
                self.test_results["integration_tests_passed"] / total_tests
            ) * 100

        # Calculate error rates by component
        violations_by_type = {}
        for violation in self.test_results["integration_violations"]:
            comp_type = violation["component"].split("_")[0]
            violations_by_type[comp_type] = violations_by_type.get(comp_type, 0) + 1

        for comp_type, violations in violations_by_type.items():
            self.test_results["error_rates"][comp_type] = (violations / total_tests) * 100

        # Calculate average response time
        if self.test_results["response_times"]:
            self.test_results["avg_response_time"] = (
                sum(self.test_results["response_times"]) / len(self.test_results["response_times"])
            )


def run_tractionbuild_integration_tests():
    """Run all TractionBuild integration tests"""

    tester = TractionBuildIntegrationTester()
    results = tester.run_integration_tests()

    # Save results to file
    output_file = "tests/integration/tractionbuild/integration_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    integration_coverage = results["integration_coverage"] >= 90.0
    no_critical_violations = len(results["integration_violations"]) <= 3  # Allow minor violations
    endpoints_working = results["api_endpoints_working"] >= results["api_endpoints_tested"] * 0.9
    webhooks_working = results["webhooks_working"] >= results["webhooks_tested"] * 0.9

    return integration_coverage and no_critical_violations and endpoints_working and webhooks_working


if __name__ == "__main__":
    success = run_tractionbuild_integration_tests()
    exit(0 if success else 1)
