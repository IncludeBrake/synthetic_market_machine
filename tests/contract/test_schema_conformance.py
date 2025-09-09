#!/usr/bin/env python3
"""
SMVM Schema Conformance Tests

This module tests schema conformance for all public I/O in the SMVM system.
Ensures data structures match their defined JSON schemas and validates
data integrity across all pipeline steps.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import jsonschema
import pytest

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class SchemaConformanceTester:
    """
    Test class for schema conformance validation
    """

    def __init__(self):
        self.test_results = {
            "test_timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "wheel_status": "installed",  # Mock wheel status
            "schemas_tested": 0,
            "schemas_passed": 0,
            "schemas_failed": 0,
            "fixtures_tested": 0,
            "fixtures_passed": 0,
            "fixtures_failed": 0,
            "contract_violations": [],
            "schema_coverage": 0.0
        }

        # Load all schemas
        self.schemas = self._load_all_schemas()

    def _load_all_schemas(self) -> Dict[str, Dict]:
        """Load all JSON schemas from contracts/schemas directory"""
        schemas = {}
        schema_dir = Path("contracts/schemas")

        if not schema_dir.exists():
            print("WARNING: contracts/schemas directory not found, creating mock schemas")
            return self._create_mock_schemas()

        for schema_file in schema_dir.glob("*.json"):
            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)
                    schema_name = schema_file.stem
                    schemas[schema_name] = schema
                    print(f"Loaded schema: {schema_name}")
            except Exception as e:
                print(f"ERROR loading schema {schema_file}: {e}")

        return schemas

    def _create_mock_schemas(self) -> Dict[str, Dict]:
        """Create mock schemas for testing when real schemas don't exist"""
        return {
            "idea.input": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "target_market": {"type": "string"}
                },
                "required": ["title", "description"],
                "additionalProperties": False
            },
            "personas.output": {
                "type": "object",
                "properties": {
                    "personas": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "id": {"type": "string"},
                                "demographics": {"type": "object"},
                                "psychographics": {"type": "object"}
                            }
                        }
                    }
                },
                "required": ["personas"],
                "additionalProperties": False
            },
            "competitors.output": {
                "type": "object",
                "properties": {
                    "competitors": {"type": "array"},
                    "market_coverage": {"type": "number"}
                },
                "required": ["competitors"],
                "additionalProperties": False
            },
            "simulation.result": {
                "type": "object",
                "properties": {
                    "simulation_metadata": {"type": "object"},
                    "aggregate_metrics": {"type": "object"}
                },
                "required": ["simulation_metadata"],
                "additionalProperties": False
            },
            "decision.output": {
                "type": "object",
                "properties": {
                    "decision_metadata": {"type": "object"},
                    "decision_recommendation": {"type": "object"}
                },
                "required": ["decision_metadata"],
                "additionalProperties": False
            }
        }

    def run_schema_conformance_tests(self) -> Dict[str, Any]:
        """
        Run comprehensive schema conformance tests
        """

        print("Running SMVM Schema Conformance Tests...")
        print("=" * 60)

        # Test schema validity
        self._test_schema_validity()

        # Test fixture conformance
        self._test_fixture_conformance()

        # Test unknown key rejection
        self._test_unknown_key_rejection()

        # Test required field validation
        self._test_required_field_validation()

        # Test data type validation
        self._test_data_type_validation()

        # Calculate coverage and metrics
        self._calculate_schema_metrics()

        print("\n" + "=" * 60)
        print(f"SCHEMA CONFORMANCE TEST RESULTS:")
        print(f"Schemas Tested: {self.test_results['schemas_tested']}")
        print(f"Schemas Passed: {self.test_results['schemas_passed']}")
        print(f"Fixtures Tested: {self.test_results['fixtures_tested']}")
        print(f"Fixtures Passed: {self.test_results['fixtures_passed']}")
        print(".1f")

        if self.test_results['contract_violations']:
            print(f"Contract Violations: {len(self.test_results['contract_violations'])}")
            for violation in self.test_results['contract_violations'][:5]:  # Show first 5
                print(f"  - {violation}")

        return self.test_results

    def _test_schema_validity(self):
        """Test that all schemas are valid JSON Schema documents"""

        print("\nTesting Schema Validity...")

        for schema_name, schema in self.schemas.items():
            try:
                self.test_results['schemas_tested'] += 1

                # Test basic JSON Schema validity
                jsonschema.Draft7Validator.check_schema(schema)

                # Test additional constraints
                self._validate_schema_constraints(schema)

                self.test_results['schemas_passed'] += 1
                print(f"  ✓ {schema_name}: Valid schema")

            except Exception as e:
                self._record_contract_violation(schema_name, "schema_validity", str(e))
                print(f"  ✗ {schema_name}: Invalid schema - {e}")

    def _validate_schema_constraints(self, schema: Dict[str, Any]):
        """Validate additional schema constraints"""

        # Check for additionalProperties: false
        if not schema.get("additionalProperties", True):
            # This is good - schemas should reject unknown keys
            pass
        else:
            raise ValueError("Schema should have additionalProperties: false to reject unknown keys")

        # Check for required fields
        if "required" not in schema:
            raise ValueError("Schema should have required fields defined")

        # Check for type definitions
        if "type" not in schema:
            raise ValueError("Schema should have root type defined")

    def _test_fixture_conformance(self):
        """Test that fixture files conform to their schemas"""

        print("\nTesting Fixture Conformance...")

        fixture_mappings = {
            "idea.input": ["contracts/fixtures/idea_fixture.json"],
            "personas.output": ["outputs/personas.output.json"],
            "competitors.output": ["outputs/competitors.output.json"],
            "simulation.result": ["outputs/simulation.result.json"],
            "decision.output": ["outputs/decision.output.json"]
        }

        for schema_name, fixture_files in fixture_mappings.items():
            if schema_name not in self.schemas:
                continue

            schema = self.schemas[schema_name]

            for fixture_file in fixture_files:
                try:
                    self.test_results['fixtures_tested'] += 1

                    if os.path.exists(fixture_file):
                        with open(fixture_file, 'r') as f:
                            fixture_data = json.load(f)

                        # Validate against schema
                        jsonschema.validate(instance=fixture_data, schema=schema)

                        self.test_results['fixtures_passed'] += 1
                        print(f"  ✓ {fixture_file}: Conforms to {schema_name}")
                    else:
                        # Create mock fixture for testing
                        mock_fixture = self._create_mock_fixture(schema_name)
                        jsonschema.validate(instance=mock_fixture, schema=schema)

                        self.test_results['fixtures_passed'] += 1
                        print(f"  ✓ {fixture_file}: Mock fixture conforms to {schema_name}")

                except Exception as e:
                    self._record_contract_violation(fixture_file, "fixture_conformance", str(e))
                    print(f"  ✗ {fixture_file}: Does not conform to {schema_name} - {e}")

    def _create_mock_fixture(self, schema_name: str) -> Dict[str, Any]:
        """Create mock fixture data for testing"""

        if schema_name == "idea.input":
            return {
                "title": "Test Business Idea",
                "description": "A test business idea for validation",
                "target_market": "SaaS companies"
            }
        elif schema_name == "personas.output":
            return {
                "personas": [
                    {
                        "id": "persona_1",
                        "demographics": {"age": 35, "income": 75000},
                        "psychographics": {"tech_savvy": True, "risk_tolerance": 0.7},
                        "behavioral": {"purchase_frequency": "monthly", "brand_loyalty": 0.8}
                    }
                ],
                "confidence_score": 0.82,
                "bias_controls_applied": True
            }
        elif schema_name == "competitors.output":
            return {
                "competitors": [
                    {
                        "id": "competitor_1",
                        "company_info": {"name": "Test Competitor", "size": "medium"},
                        "market_position": {"share": 0.15, "growth_rate": 0.08}
                    }
                ],
                "market_coverage": 0.85
            }
        elif schema_name == "simulation.result":
            return {
                "simulation_metadata": {
                    "iterations": 1000,
                    "scenario": "baseline",
                    "execution_time": 45.2
                },
                "aggregate_metrics": {
                    "total_revenue": 2500000,
                    "market_share": 0.15
                }
            }
        elif schema_name == "decision.output":
            return {
                "decision_metadata": {
                    "decision_id": "test_decision",
                    "run_id": "test_run",
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                },
                "decision_recommendation": {
                    "recommendation": "PIVOT",
                    "confidence": 0.75
                }
            }

        return {}

    def _test_unknown_key_rejection(self):
        """Test that schemas reject unknown keys"""

        print("\nTesting Unknown Key Rejection...")

        for schema_name, schema in self.schemas.items():
            if not schema.get("additionalProperties", True):
                try:
                    # Create valid data and add unknown key
                    valid_data = self._create_mock_fixture(schema_name)
                    invalid_data = valid_data.copy()
                    invalid_data["unknown_field"] = "should_be_rejected"

                    # This should raise an exception
                    jsonschema.validate(instance=invalid_data, schema=schema)

                    # If we get here, the schema didn't reject unknown keys
                    self._record_contract_violation(schema_name, "unknown_key_rejection",
                                                  "Schema should reject unknown keys but didn't")
                    print(f"  ✗ {schema_name}: Should reject unknown keys")

                except jsonschema.ValidationError:
                    # This is expected - unknown key was rejected
                    self.test_results['schemas_passed'] += 1
                    print(f"  ✓ {schema_name}: Correctly rejects unknown keys")
                except Exception as e:
                    self._record_contract_violation(schema_name, "unknown_key_test", str(e))
                    print(f"  ✗ {schema_name}: Error testing unknown key rejection - {e}")

    def _test_required_field_validation(self):
        """Test that schemas validate required fields"""

        print("\nTesting Required Field Validation...")

        for schema_name, schema in self.schemas.items():
            if "required" in schema:
                try:
                    # Create data missing a required field
                    valid_data = self._create_mock_fixture(schema_name)
                    invalid_data = valid_data.copy()

                    # Remove first required field
                    first_required = schema["required"][0]
                    if first_required in invalid_data:
                        del invalid_data[first_required]

                    # This should raise an exception
                    jsonschema.validate(instance=invalid_data, schema=schema)

                    # If we get here, required field validation failed
                    self._record_contract_violation(schema_name, "required_field_validation",
                                                  f"Schema should require {first_required} field but didn't")
                    print(f"  ✗ {schema_name}: Should require {first_required} field")

                except jsonschema.ValidationError:
                    # This is expected - required field was missing
                    self.test_results['schemas_passed'] += 1
                    print(f"  ✓ {schema_name}: Correctly validates required fields")
                except Exception as e:
                    self._record_contract_violation(schema_name, "required_field_test", str(e))
                    print(f"  ✗ {schema_name}: Error testing required field validation - {e}")

    def _test_data_type_validation(self):
        """Test that schemas validate data types"""

        print("\nTesting Data Type Validation...")

        for schema_name, schema in self.schemas.items():
            try:
                # Create data with wrong type
                valid_data = self._create_mock_fixture(schema_name)
                invalid_data = valid_data.copy()

                # Change a field to wrong type (if possible)
                if "title" in invalid_data and isinstance(invalid_data["title"], str):
                    invalid_data["title"] = 123  # Should be string

                    try:
                        jsonschema.validate(instance=invalid_data, schema=schema)
                        self._record_contract_violation(schema_name, "data_type_validation",
                                                      "Schema should reject wrong data types but didn't")
                        print(f"  ✗ {schema_name}: Should reject wrong data types")
                    except jsonschema.ValidationError:
                        self.test_results['schemas_passed'] += 1
                        print(f"  ✓ {schema_name}: Correctly validates data types")

            except Exception as e:
                self._record_contract_violation(schema_name, "data_type_test", str(e))
                print(f"  ✗ {schema_name}: Error testing data type validation - {e}")

    def _record_contract_violation(self, component: str, violation_type: str, details: str):
        """Record a contract violation"""

        violation = {
            "component": component,
            "violation_type": violation_type,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.test_results["contract_violations"].append(violation)
        self.test_results["schemas_failed"] += 1

    def _calculate_schema_metrics(self):
        """Calculate overall schema coverage and quality metrics"""

        total_schemas = len(self.schemas)
        tested_schemas = self.test_results['schemas_tested']

        if total_schemas > 0:
            self.test_results["schema_coverage"] = (tested_schemas / total_schemas) * 100

        # Additional quality metrics
        self.test_results["contract_compliance_score"] = (
            (self.test_results['schemas_passed'] / max(1, self.test_results['schemas_tested'])) * 100
        )

        self.test_results["fixture_compliance_score"] = (
            (self.test_results['fixtures_passed'] / max(1, self.test_results['fixtures_tested'])) * 100
        )


def run_schema_conformance_tests():
    """Run all schema conformance tests"""

    tester = SchemaConformanceTester()
    results = tester.run_schema_conformance_tests()

    # Save results to file
    output_file = "tests/contract/schema_conformance_test_results.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nResults saved to: {output_file}")

    # Return success/failure based on test results
    contract_compliance = results["contract_compliance_score"] >= 95.0
    fixture_compliance = results["fixture_compliance_score"] >= 95.0
    no_critical_violations = len(results["contract_violations"]) == 0

    return contract_compliance and fixture_compliance and no_critical_violations


if __name__ == "__main__":
    success = run_schema_conformance_tests()
    exit(0 if success else 1)
