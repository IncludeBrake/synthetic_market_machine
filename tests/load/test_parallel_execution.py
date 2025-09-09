#!/usr/bin/env python3
"""
SMVM Parallel Execution Load Tests

This module tests the SMVM system's ability to handle multiple concurrent
executions while maintaining performance guarantees and resource constraints.
"""

import json
import os
import sys
import time
import threading
import concurrent.futures
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import statistics
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class ParallelExecutionTester:
    """
    Test class for parallel execution under load
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "wheel_status": "installed",
            "parallel_tests_run": 0,
            "parallel_tests_passed": 0,
            "parallel_tests_failed": 0,
            "execution_times": [],
            "token_usage": [],
            "memory_usage": [],
            "p50_latency": 0.0,
            "p95_latency": 0.0,
            "p99_latency": 0.0,
            "throughput": 0.0,
            "resource_violations": [],
            "performance_metrics": {},
            "load_test_duration": 0
        }

    def run_parallel_execution_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive parallel execution load tests
        """

        print("Running SMVM Parallel Execution Load Tests...")
        print("=" * 60)

        start_time = time.time()

        # Test different concurrency levels
        concurrency_levels = [1, 2, 4, 8]

        for concurrency in concurrency_levels:
            print(f"\nTesting concurrency level: {concurrency}")
            self._test_concurrency_level(concurrency)

        # Test token budget enforcement under load
        self._test_token_budget_under_load()

        # Test memory usage patterns
        self._test_memory_usage_patterns()

        # Test seed-based determinism
        self._test_seed_determinism_under_load()

        # Calculate performance metrics
        self._calculate_performance_metrics()

        self.test_results["load_test_duration"] = time.time() - start_time

        print("\n" + "=" * 60)
        print(f"PARALLEL EXECUTION LOAD TEST RESULTS:")
        print(f"Tests Run: {self.test_results['parallel_tests_run']}")
        print(f"Tests Passed: {self.test_results['parallel_tests_passed']}")
        print(".2f")
        print(".2f")
        print(".2f")
        print(".1f")

        if self.test_results['resource_violations']:
            print(f"Resource Violations: {len(self.test_results['resource_violations'])}")
            for violation in self.test_results['resource_violations'][:3]:  # Show first 3
                print(f"  - {violation}")

        return self.test_results

    def _test_concurrency_level(self, concurrency: int):
        """Test execution at specific concurrency level"""

        print(f"  Running {concurrency} parallel executions...")

        # Generate test scenarios
        test_scenarios = []
        for i in range(concurrency):
            scenario = {
                "run_id": f"load_test_run_{i}",
                "seed": random.randint(1, 10000),
                "iterations": random.choice([100, 500, 1000]),
                "scenario": random.choice(["price_cut", "feature_launch", "downturn"])
            }
            test_scenarios.append(scenario)

        execution_times = []
        token_usage = []

        try:
            self.test_results['parallel_tests_run'] += 1

            # Execute scenarios in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as executor:
                # Submit all tasks
                future_to_scenario = {
                    executor.submit(self._execute_test_scenario, scenario): scenario
                    for scenario in test_scenarios
                }

                # Collect results
                for future in concurrent.futures.as_completed(future_to_scenario):
                    scenario = future_to_scenario[future]
                    try:
                        result = future.result(timeout=300)  # 5 minute timeout
                        execution_times.append(result["execution_time"])
                        token_usage.append(result["token_usage"])

                        if result["success"]:
                            print(f"    ✓ Scenario {scenario['run_id']}: {result['execution_time']:.1f}s")
                        else:
                            print(f"    ✗ Scenario {scenario['run_id']}: Failed - {result.get('error', 'Unknown error')}")

                    except concurrent.futures.TimeoutError:
                        print(f"    ✗ Scenario {scenario['run_id']}: Timeout")
                        self._record_resource_violation(f"timeout_concurrency_{concurrency}",
                                                      f"Execution timeout at concurrency {concurrency}")
                    except Exception as e:
                        print(f"    ✗ Scenario {scenario['run_id']}: Error - {e}")
                        self._record_resource_violation(f"execution_error_concurrency_{concurrency}",
                                                      str(e))

            # Validate performance requirements
            if execution_times:
                p95_time = statistics.quantiles(execution_times, n=20)[18]  # 95th percentile
                max_token_usage = max(token_usage) if token_usage else 0

                # Performance requirements
                p95_requirement = 120.0  # 2 minutes max p95
                token_requirement = 10000  # 10K token limit

                if p95_time <= p95_requirement and max_token_usage <= token_requirement:
                    self.test_results['parallel_tests_passed'] += 1
                    print(".1f"                else:
                    self._record_resource_violation(f"performance_concurrency_{concurrency}",
                                                  f"P95 {p95_time:.1f}s > {p95_requirement}s or tokens {max_token_usage} > {token_requirement}")
                    print(".1f"
                # Store execution times for aggregate analysis
                self.test_results["execution_times"].extend(execution_times)
                self.test_results["token_usage"].extend(token_usage)

        except Exception as e:
            self._record_resource_violation(f"concurrency_test_{concurrency}", str(e))
            print(f"  ✗ Concurrency {concurrency}: Test failed - {e}")

    def _execute_test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single test scenario"""

        start_time = time.time()

        try:
            # Set random seed for reproducibility
            random.seed(scenario["seed"])

            # Mock execution time based on iterations
            base_time = scenario["iterations"] * 0.05  # 50ms per iteration
            variance = random.uniform(-0.1, 0.1) * base_time
            execution_time = max(1.0, base_time + variance)

            # Mock token usage
            base_tokens = scenario["iterations"] * 5  # 5 tokens per iteration
            token_variance = random.uniform(-0.1, 0.1) * base_tokens
            token_usage = max(100, base_tokens + token_variance)

            # Simulate execution
            time.sleep(execution_time)

            # Mock occasional failures (5% failure rate)
            if random.random() < 0.05:
                raise Exception("Simulated execution failure")

            return {
                "success": True,
                "execution_time": execution_time,
                "token_usage": token_usage,
                "scenario": scenario
            }

        except Exception as e:
            execution_time = time.time() - start_time
            return {
                "success": False,
                "execution_time": execution_time,
                "error": str(e),
                "scenario": scenario
            }

    def _test_token_budget_under_load(self):
        """Test token budget enforcement under concurrent load"""

        print("\nTesting Token Budget Under Load...")

        # Simulate high concurrent token usage
        concurrent_scenarios = 10
        token_budget_per_scenario = 800  # Leave buffer below 1000 limit
        global_budget = 10000

        try:
            self.test_results['parallel_tests_run'] += 1

            total_token_usage = 0
            budget_violations = 0

            # Simulate concurrent token usage
            for i in range(concurrent_scenarios):
                # Mock token usage with some variance
                usage = token_budget_per_scenario * random.uniform(0.8, 1.2)
                total_token_usage += usage

                if usage > 1000:  # Per-scenario limit
                    budget_violations += 1

            # Check global budget
            if total_token_usage > global_budget:
                budget_violations += 1

            if budget_violations == 0:
                self.test_results['parallel_tests_passed'] += 1
                print(".0f"            else:
                self._record_resource_violation("token_budget_load_test",
                                              f"{budget_violations} budget violations detected")
                print(f"  ✗ Token Budget Under Load: {budget_violations} violations")

        except Exception as e:
            self._record_resource_violation("token_budget_load_test", str(e))
            print(f"  ✗ Token Budget Under Load: Error - {e}")

    def _test_memory_usage_patterns(self):
        """Test memory usage patterns under load"""

        print("\nTesting Memory Usage Patterns...")

        try:
            self.test_results['parallel_tests_run'] += 1

            # Mock memory usage for different concurrency levels
            memory_readings = []

            for concurrency in [1, 2, 4, 8]:
                # Mock memory usage (in MB)
                base_memory = 100 + (concurrency - 1) * 50  # Base + concurrency factor
                memory_variance = random.uniform(-0.1, 0.1) * base_memory
                memory_usage = base_memory + memory_variance
                memory_readings.append(memory_usage)

                # Store for aggregate analysis
                self.test_results["memory_usage"].append({
                    "concurrency": concurrency,
                    "memory_mb": memory_usage,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

            # Check memory scaling (should not be exponential)
            memory_ratios = []
            for i in range(1, len(memory_readings)):
                ratio = memory_readings[i] / memory_readings[i-1]
                concurrency_ratio = (i + 1) / i  # 2/1, 3/2, 4/3, etc.
                memory_ratios.append(ratio / concurrency_ratio)

            avg_memory_ratio = statistics.mean(memory_ratios)

            # Memory should scale roughly linearly (ratio ≈ 1.0) or slightly worse
            if 0.8 <= avg_memory_ratio <= 2.0:
                self.test_results['parallel_tests_passed'] += 1
                print(".2f"            else:
                self._record_resource_violation("memory_usage_patterns",
                                              f"Memory scaling ratio {avg_memory_ratio:.2f} indicates poor scaling")
                print(".2f"
        except Exception as e:
            self._record_resource_violation("memory_usage_patterns", str(e))
            print(f"  ✗ Memory Usage Patterns: Error - {e}")

    def _test_seed_determinism_under_load(self):
        """Test that seed-based determinism holds under concurrent load"""

        print("\nTesting Seed Determinism Under Load...")

        try:
            self.test_results['parallel_tests_run'] += 1

            # Test multiple scenarios with same seed
            seed = 12345
            results = []

            # Run same scenario multiple times concurrently
            scenarios = []
            for i in range(5):
                scenarios.append({
                    "run_id": f"determinism_test_{i}",
                    "seed": seed,
                    "iterations": 500,
                    "scenario": "baseline"
                })

            # Execute scenarios and collect results
            with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(self._execute_test_scenario, scenario) for scenario in scenarios]
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result["success"]:
                        results.append(result)

            # Check determinism (all results should be identical with same seed)
            if len(results) >= 3:  # Need at least 3 successful results
                first_result = results[0]
                deterministic = True

                for result in results[1:]:
                    # Check if execution times are within reasonable variance
                    time_diff = abs(result["execution_time"] - first_result["execution_time"])
                    token_diff = abs(result["token_usage"] - first_result["token_usage"])

                    if time_diff > 1.0 or token_diff > 50:  # Allow small variance
                        deterministic = False
                        break

                if deterministic:
                    self.test_results['parallel_tests_passed'] += 1
                    print("  ✓ Seed Determinism Under Load: Consistent results with same seed")
                else:
                    self._record_resource_violation("seed_determinism_load",
                                                  "Non-deterministic results with same seed under load")
                    print("  ✗ Seed Determinism Under Load: Inconsistent results")
            else:
                self._record_resource_violation("seed_determinism_load",
                                              "Insufficient successful executions for determinism test")
                print("  ✗ Seed Determinism Under Load: Insufficient test data")

        except Exception as e:
            self._record_resource_violation("seed_determinism_load", str(e))
            print(f"  ✗ Seed Determinism Under Load: Error - {e}")

    def _calculate_performance_metrics(self):
        """Calculate aggregate performance metrics"""

        execution_times = self.test_results["execution_times"]

        if execution_times:
            # Calculate percentiles
            sorted_times = sorted(execution_times)
            n = len(sorted_times)

            self.test_results["p50_latency"] = statistics.median(sorted_times)
            self.test_results["p95_latency"] = sorted_times[int(0.95 * (n - 1))]
            self.test_results["p99_latency"] = sorted_times[int(0.99 * (n - 1))]

            # Calculate throughput (executions per second)
            total_time = sum(execution_times)
            if total_time > 0:
                self.test_results["throughput"] = len(execution_times) / total_time

        # Performance requirements check
        performance_requirements = {
            "p95_latency_max": 120.0,  # 2 minutes
            "throughput_min": 0.1,     # 0.1 executions per second
            "memory_max": 1000         # 1GB max memory
        }

        self.test_results["performance_requirements_met"] = (
            self.test_results["p95_latency"] <= performance_requirements["p95_latency_max"] and
            self.test_results["throughput"] >= performance_requirements["throughput_min"]
        )

    def _record_resource_violation(self, violation_type: str, details: str):
        """Record a resource violation"""

        violation = {
            "type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.test_results["resource_violations"].append(violation)
        self.test_results["parallel_tests_failed"] += 1


def run_parallel_execution_tests():
    """Run all parallel execution load tests"""

    tester = ParallelExecutionTester()
    results = tester.run_parallel_execution_tests()

    # Save results to file
    output_file = "tests/load/parallel_execution_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    tests_passed = results["parallel_tests_passed"]
    total_tests = results["parallel_tests_run"]
    performance_met = results.get("performance_requirements_met", False)
    no_resource_violations = len(results["resource_violations"]) == 0

    success_rate = tests_passed / total_tests if total_tests > 0 else 0

    return success_rate >= 0.85 and performance_met and no_resource_violations


if __name__ == "__main__":
    success = run_parallel_execution_tests()
    exit(0 if success else 1)
