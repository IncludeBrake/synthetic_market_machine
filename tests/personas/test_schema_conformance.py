#!/usr/bin/env python3
"""
SMVM Persona Schema Conformance Tests

This module contains tests to verify that generated personas conform to the
defined JSON schema and meet quality/validation criteria.
"""

import json
import pytest
import jsonschema
from datetime import datetime
from typing import Dict, List, Any
import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from contracts.schemas.personas_output import PERSONA_OUTPUT_SCHEMA

class TestPersonaSchemaConformance:
    """Test suite for persona schema conformance"""

    @pytest.fixture
    def persona_schema(self):
        """Load the persona output schema"""
        return PERSONA_OUTPUT_SCHEMA

    @pytest.fixture
    def golden_fixtures(self):
        """Load golden test fixtures"""
        fixture_path = os.path.join(os.path.dirname(__file__), 'golden_test_data.json')
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_schema_structure(self, persona_schema):
        """Test that the schema has the expected structure"""
        required_properties = ['type', 'properties', 'required', 'additionalProperties']

        for prop in required_properties:
            assert prop in persona_schema, f"Schema missing required property: {prop}"

        assert persona_schema['type'] == 'object'
        assert persona_schema['additionalProperties'] == False

    def test_required_fields(self, persona_schema):
        """Test that required fields are properly defined"""
        required_fields = [
            'run_id', 'span_id', 'timestamp', 'python_version',
            'python_env_hash', 'content_hash', 'composite_hash',
            'data_zone', 'retention_days', 'personas', 'metadata', 'provenance'
        ]

        assert set(persona_schema['required']) == set(required_fields)

    def test_persona_object_structure(self, persona_schema):
        """Test that persona objects have correct structure"""
        persona_props = persona_schema['properties']['personas']['items']['properties']

        # Check demographics structure
        assert 'demographics' in persona_props
        demo_props = persona_props['demographics']['properties']
        required_demo = ['age', 'gender', 'location', 'education_level', 'occupation', 'income_range']
        assert all(field in demo_props for field in required_demo)

        # Check behavioral attributes
        assert 'behavioral_attributes' in persona_props
        behavior_props = persona_props['behavioral_attributes']['properties']
        required_behavior = ['technology_adoption', 'risk_tolerance', 'brand_loyalty']
        assert all(field in behavior_props for field in required_behavior)

    def test_golden_fixture_conformance(self, persona_schema, golden_fixtures):
        """Test that golden fixtures conform to schema"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # This should not raise an exception if the fixture conforms
            try:
                jsonschema.validate(instance=expected_output, schema=persona_schema)
            except jsonschema.ValidationError as e:
                pytest.fail(f"Golden fixture {scenario['scenario_id']} failed schema validation: {e}")

    def test_fixture_metadata_completeness(self, golden_fixtures):
        """Test that fixture metadata is complete"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check metadata completeness
            assert 'metadata' in expected_output
            metadata = expected_output['metadata']

            required_meta_fields = [
                'generation_timestamp', 'synthesis_method',
                'data_sources_used', 'quality_score'
            ]

            for field in required_meta_fields:
                assert field in metadata, f"Missing metadata field: {field}"

            # Check provenance
            assert 'provenance' in expected_output
            provenance = expected_output['provenance']

            required_prov_fields = [
                'adapter_version', 'pipeline_stages', 'validation_checks'
            ]

            for field in required_prov_fields:
                assert field in provenance, f"Missing provenance field: {field}"

    def test_persona_data_quality(self, golden_fixtures):
        """Test persona data quality metrics"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            for persona in expected_output['personas']:
                # Check age is reasonable
                assert 18 <= persona['demographics']['age'] <= 100, \
                    f"Invalid age for persona {persona['persona_id']}"

                # Check risk tolerance and brand loyalty are in valid range
                risk_tolerance = persona['behavioral_attributes']['risk_tolerance']
                brand_loyalty = persona['behavioral_attributes']['brand_loyalty']

                assert 0.0 <= risk_tolerance <= 10.0, \
                    f"Invalid risk tolerance for persona {persona['persona_id']}"
                assert 0.0 <= brand_loyalty <= 10.0, \
                    f"Invalid brand loyalty for persona {persona['persona_id']}"

                # Check income range is reasonable
                income_min = persona['demographics']['income_range']['min']
                income_max = persona['demographics']['income_range']['max']

                assert income_min > 0 and income_max > income_min, \
                    f"Invalid income range for persona {persona['persona_id']}"

    def test_diversity_validation(self, golden_fixtures):
        """Test diversity requirements are met"""

        # Focus on the diverse persona set scenario
        diverse_scenario = None
        for scenario in golden_fixtures['test_scenarios']:
            if scenario['scenario_id'] == 'scenario_003':
                diverse_scenario = scenario
                break

        assert diverse_scenario is not None, "Missing diverse persona scenario"

        personas = diverse_scenario['expected_output']['personas']

        # Check age diversity
        ages = [p['demographics']['age'] for p in personas]
        age_range = max(ages) - min(ages)
        assert age_range >= 20, "Insufficient age diversity in persona set"

        # Check gender diversity
        genders = [p['demographics']['gender'] for p in personas]
        unique_genders = set(genders)
        assert len(unique_genders) >= 3, "Insufficient gender diversity in persona set"

        # Check location diversity
        locations = [p['demographics']['location']['region'] for p in personas]
        unique_regions = set(locations)
        assert len(unique_regions) >= 2, "Insufficient geographic diversity in persona set"

    def test_behavioral_consistency(self, golden_fixtures):
        """Test behavioral attribute consistency"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            for persona in expected_output['personas']:
                behavior = persona['behavioral_attributes']

                # Technology adoption should correlate with age
                age = persona['demographics']['age']
                tech_adoption = behavior['technology_adoption']

                if age < 30:
                    # Younger personas should be more tech-savvy
                    assert tech_adoption in ['early_adopter', 'innovator'], \
                        f"Inconsistent tech adoption for young persona {persona['persona_id']}"
                elif age > 60:
                    # Older personas should be more conservative
                    assert tech_adoption in ['late_adopter', 'pragmatic_adopter'], \
                        f"Inconsistent tech adoption for senior persona {persona['persona_id']}"

    def test_schema_additional_properties_rejection(self, persona_schema):
        """Test that schema rejects additional properties"""

        # Create a valid persona output
        valid_output = {
            "run_id": "TEST-RUN-001",
            "span_id": "test-span-001",
            "timestamp": "2024-12-01T12:00:00Z",
            "python_version": "3.12.10",
            "python_env_hash": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "content_hash": "b2c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "composite_hash": "c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "data_zone": "GREEN",
            "retention_days": 90,
            "personas": [],
            "metadata": {
                "generation_timestamp": "2024-12-01T12:00:00Z",
                "synthesis_method": "test",
                "data_sources_used": ["test"],
                "quality_score": 0.8
            },
            "provenance": {
                "adapter_version": "1.0.0",
                "pipeline_stages": ["test"],
                "validation_checks": ["test"]
            }
        }

        # This should validate successfully
        jsonschema.validate(instance=valid_output, schema=persona_schema)

        # Add an extra property that should be rejected
        invalid_output = valid_output.copy()
        invalid_output["extra_field"] = "should_be_rejected"

        # This should raise a ValidationError
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_output, schema=persona_schema)

    def test_timestamp_format_validation(self, persona_schema, golden_fixtures):
        """Test that timestamps are in correct ISO format"""

        import re
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check main timestamp
            assert re.match(iso_pattern, expected_output.get('timestamp', '')), \
                f"Invalid timestamp format in scenario {scenario['scenario_id']}"

            # Check metadata timestamp
            meta_timestamp = expected_output.get('metadata', {}).get('generation_timestamp', '')
            assert re.match(iso_pattern, meta_timestamp), \
                f"Invalid metadata timestamp in scenario {scenario['scenario_id']}"

    def test_hash_format_validation(self, persona_schema, golden_fixtures):
        """Test that hashes are in correct format (64-character hex)"""

        import re
        hash_pattern = r'^[a-f0-9]{64}$'

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check all required hashes
            hashes_to_check = [
                expected_output.get('python_env_hash', ''),
                expected_output.get('content_hash', ''),
                expected_output.get('composite_hash', '')
            ]

            for hash_value in hashes_to_check:
                assert re.match(hash_pattern, hash_value), \
                    f"Invalid hash format: {hash_value} in scenario {scenario['scenario_id']}"

def run_schema_validation_tests():
    """Run all schema validation tests"""

    print("Running Persona Schema Conformance Tests...")
    print("=" * 50)

    # Load test data
    test_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(test_dir, 'golden_test_data.json')

    try:
        with open(fixture_path, 'r') as f:
            golden_fixtures = json.load(f)
    except FileNotFoundError:
        print("ERROR: Golden fixtures file not found")
        return False
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in golden fixtures: {e}")
        return False

    # Basic structure validation
    print("✓ Testing fixture structure...")
    required_keys = ['fixture_id', 'fixture_version', 'test_scenarios']
    if not all(key in golden_fixtures for key in required_keys):
        print("ERROR: Missing required keys in golden fixtures")
        return False

    # Scenario validation
    print("✓ Testing scenario structure...")
    for scenario in golden_fixtures['test_scenarios']:
        required_scenario_keys = ['scenario_id', 'scenario_name', 'input_parameters', 'expected_output', 'validation_criteria']
        if not all(key in scenario for key in required_scenario_keys):
            print(f"ERROR: Missing required keys in scenario {scenario.get('scenario_id', 'unknown')}")
            return False

        # Validate expected output structure
        expected_output = scenario['expected_output']
        if 'personas' not in expected_output or 'metadata' not in expected_output or 'provenance' not in expected_output:
            print(f"ERROR: Invalid expected output structure in scenario {scenario['scenario_id']}")
            return False

    print("✓ Testing persona data quality...")
    for scenario in golden_fixtures['test_scenarios']:
        for persona in scenario['expected_output']['personas']:
            # Age validation
            age = persona.get('demographics', {}).get('age')
            if not isinstance(age, (int, float)) or not (18 <= age <= 100):
                print(f"ERROR: Invalid age {age} in persona {persona.get('persona_id', 'unknown')}")
                return False

            # Risk tolerance validation
            risk_tolerance = persona.get('behavioral_attributes', {}).get('risk_tolerance')
            if not isinstance(risk_tolerance, (int, float)) or not (0.0 <= risk_tolerance <= 10.0):
                print(f"ERROR: Invalid risk tolerance {risk_tolerance} in persona {persona.get('persona_id', 'unknown')}")
                return False

    print("✓ Testing diversity requirements...")
    # Check the diverse scenario specifically
    diverse_scenario = None
    for scenario in golden_fixtures['test_scenarios']:
        if scenario['scenario_id'] == 'scenario_003':
            diverse_scenario = scenario
            break

    if diverse_scenario:
        personas = diverse_scenario['expected_output']['personas']
        ages = [p['demographics']['age'] for p in personas]
        genders = [p['demographics']['gender'] for p in personas]

        if max(ages) - min(ages) < 20:
            print("ERROR: Insufficient age diversity in diverse scenario")
            return False

        if len(set(genders)) < 3:
            print("ERROR: Insufficient gender diversity in diverse scenario")
            return False

    print("✓ All schema conformance tests passed!")
    return True

if __name__ == "__main__":
    success = run_schema_validation_tests()
    sys.exit(0 if success else 1)
