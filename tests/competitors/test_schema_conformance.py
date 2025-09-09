#!/usr/bin/env python3
"""
SMVM Competitor Schema Conformance Tests

This module contains tests to verify that generated competitor analyses conform to the
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

from contracts.schemas.competitors_output import COMPETITOR_OUTPUT_SCHEMA

class TestCompetitorSchemaConformance:
    """Test suite for competitor schema conformance"""

    @pytest.fixture
    def competitor_schema(self):
        """Load the competitor output schema"""
        return COMPETITOR_OUTPUT_SCHEMA

    @pytest.fixture
    def golden_fixtures(self):
        """Load golden test fixtures"""
        fixture_path = os.path.join(os.path.dirname(__file__), 'golden_test_data.json')
        with open(fixture_path, 'r') as f:
            return json.load(f)

    def test_schema_structure(self, competitor_schema):
        """Test that the schema has the expected structure"""
        required_properties = ['type', 'properties', 'required', 'additionalProperties']

        for prop in required_properties:
            assert prop in competitor_schema, f"Schema missing required property: {prop}"

        assert competitor_schema['type'] == 'object'
        assert competitor_schema['additionalProperties'] == False

    def test_required_fields(self, competitor_schema):
        """Test that required fields are properly defined"""
        required_fields = [
            'run_id', 'span_id', 'timestamp', 'python_version',
            'python_env_hash', 'content_hash', 'composite_hash',
            'data_zone', 'retention_days', 'competitors', 'market_analysis',
            'competitive_landscape', 'metadata', 'provenance'
        ]

        assert set(competitor_schema['required']) == set(required_fields)

    def test_competitor_object_structure(self, competitor_schema):
        """Test that competitor objects have correct structure"""
        competitor_props = competitor_schema['properties']['competitors']['items']['properties']

        # Check required competitor fields
        required_competitor_fields = [
            'company_name', 'market_position', 'feature_scores',
            'positioning_scores', 'competitive_advantages',
            'competitive_disadvantages', 'market_share_estimate',
            'growth_trajectory'
        ]

        for field in required_competitor_fields:
            assert field in competitor_props, f"Missing required competitor field: {field}"

        # Check feature scores structure
        feature_scores_props = competitor_props['feature_scores']['properties']
        expected_features = [
            'technology_platform', 'user_experience', 'data_analytics',
            'business_features', 'support_ecosystem'
        ]

        for feature in expected_features:
            assert feature in feature_scores_props, f"Missing feature score: {feature}"

    def test_golden_fixture_conformance(self, competitor_schema, golden_fixtures):
        """Test that golden fixtures conform to schema"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # This should not raise an exception if the fixture conforms
            try:
                jsonschema.validate(instance=expected_output, schema=competitor_schema)
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
                'analysis_timestamp', 'analysis_method',
                'data_sources_used', 'quality_score', 'confidence_level'
            ]

            for field in required_meta_fields:
                assert field in metadata, f"Missing metadata field: {field}"

            # Check provenance
            assert 'provenance' in expected_output
            provenance = expected_output['provenance']

            required_prov_fields = [
                'adapter_version', 'feature_taxonomy_version',
                'data_freshness_score', 'validation_checks'
            ]

            for field in required_prov_fields:
                assert field in provenance, f"Missing provenance field: {field}"

    def test_competitor_data_quality(self, golden_fixtures):
        """Test competitor data quality metrics"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            for competitor in expected_output['competitors']:
                # Check feature scores are in valid range
                feature_scores = competitor['feature_scores']
                for feature, score in feature_scores.items():
                    assert 0.0 <= score <= 1.0, \
                        f"Invalid feature score {score} for {feature} in {competitor['company_name']}"

                # Check positioning scores
                positioning_scores = competitor['positioning_scores']
                for axis, score in positioning_scores.items():
                    assert 0.0 <= score <= 1.0, \
                        f"Invalid positioning score {score} for {axis} in {competitor['company_name']}"

                # Check market share estimate
                market_share = competitor['market_share_estimate']
                assert 0.0 <= market_share <= 1.0, \
                    f"Invalid market share {market_share} for {competitor['company_name']}"

    def test_market_analysis_completeness(self, golden_fixtures):
        """Test market analysis data completeness"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check market analysis
            assert 'market_analysis' in expected_output
            market_analysis = expected_output['market_analysis']

            required_market_fields = [
                'total_market_size', 'growth_rate',
                'concentration_ratio', 'barriers_to_entry'
            ]

            for field in required_market_fields:
                assert field in market_analysis, f"Missing market analysis field: {field}"

                # Check reasonable value ranges
                if field == 'total_market_size':
                    assert market_analysis[field] > 0, "Market size must be positive"
                elif field == 'growth_rate':
                    assert -0.5 <= market_analysis[field] <= 1.0, "Growth rate out of reasonable range"
                elif field == 'concentration_ratio':
                    assert 0.0 <= market_analysis[field] <= 1.0, "Concentration ratio out of valid range"

    def test_competitive_positioning_consistency(self, golden_fixtures):
        """Test competitive positioning consistency"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            competitors = expected_output['competitors']

            # Group competitors by market position
            positions = {}
            for competitor in competitors:
                position = competitor['market_position']
                if position not in positions:
                    positions[position] = []
                positions[position].append(competitor)

            # Validate positioning consistency within groups
            for position, comp_list in positions.items():
                if len(comp_list) > 1:
                    # Check that competitors in same position have similar scores
                    avg_feature_completeness = sum(
                        c['positioning_scores']['feature_completeness'] for c in comp_list
                    ) / len(comp_list)

                    for competitor in comp_list:
                        score = competitor['positioning_scores']['feature_completeness']
                        deviation = abs(score - avg_feature_completeness)
                        assert deviation <= 0.3, \
                            f"Inconsistent feature completeness for {position} position: {competitor['company_name']}"

    def test_competitive_landscape_completeness(self, golden_fixtures):
        """Test competitive landscape completeness"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check competitive landscape
            assert 'competitive_landscape' in expected_output
            landscape = expected_output['competitive_landscape']

            required_landscape_fields = [
                'market_segments', 'key_success_factors',
                'emerging_trends', 'disruptive_threats'
            ]

            for field in required_landscape_fields:
                assert field in landscape, f"Missing competitive landscape field: {field}"
                assert len(landscape[field]) > 0, f"Empty {field} list"

    def test_advantage_disadvantage_balance(self, golden_fixtures):
        """Test that advantages and disadvantages are reasonably balanced"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            for competitor in expected_output['competitors']:
                advantages = competitor['competitive_advantages']
                disadvantages = competitor['competitive_disadvantages']

                # Should have at least one advantage and disadvantage
                assert len(advantages) > 0, f"No advantages listed for {competitor['company_name']}"
                assert len(disadvantages) > 0, f"No disadvantages listed for {competitor['company_name']}"

                # Advantages and disadvantages should be reasonably balanced
                balance_ratio = len(advantages) / max(len(disadvantages), 1)
                assert 0.25 <= balance_ratio <= 4.0, \
                    f"Unbalanced advantage/disadvantage ratio for {competitor['company_name']}: {balance_ratio}"

    def test_schema_additional_properties_rejection(self, competitor_schema):
        """Test that schema rejects additional properties"""

        # Create a valid competitor output
        valid_output = {
            "run_id": "TEST-RUN-001",
            "span_id": "test-span-001",
            "timestamp": "2024-12-01T13:00:00Z",
            "python_version": "3.12.10",
            "python_env_hash": "a1b2c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "content_hash": "b2c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "composite_hash": "c3d4e5f6789012345678901234567890123456789012345678901234567890",
            "data_zone": "GREEN",
            "retention_days": 90,
            "competitors": [{
                "company_name": "TestCorp",
                "market_position": "challenger",
                "feature_scores": {
                    "technology_platform": 0.8,
                    "user_experience": 0.85,
                    "data_analytics": 0.75,
                    "business_features": 0.8,
                    "support_ecosystem": 0.7
                },
                "positioning_scores": {
                    "feature_completeness": 0.8,
                    "ease_of_use": 0.82,
                    "scalability": 0.75,
                    "innovation": 0.8
                },
                "competitive_advantages": ["Good UX"],
                "competitive_disadvantages": ["Limited features"],
                "market_share_estimate": 0.1,
                "growth_trajectory": "rapid_growth"
            }],
            "market_analysis": {
                "total_market_size": 1000000000,
                "growth_rate": 0.2,
                "concentration_ratio": 0.6,
                "barriers_to_entry": "medium",
                "innovation_pace": "rapid"
            },
            "competitive_landscape": {
                "market_segments": ["enterprise", "mid_market"],
                "key_success_factors": ["scalability", "usability"],
                "emerging_trends": ["AI integration"],
                "disruptive_threats": ["open source"]
            },
            "metadata": {
                "analysis_timestamp": "2024-12-01T13:00:00Z",
                "analysis_method": "test",
                "data_sources_used": ["test"],
                "quality_score": 0.8,
                "confidence_level": 0.9,
                "analysis_depth": "test"
            },
            "provenance": {
                "adapter_version": "1.0.0",
                "feature_taxonomy_version": "1.0.0",
                "data_freshness_score": 0.8,
                "validation_checks": ["test"]
            }
        }

        # This should validate successfully
        jsonschema.validate(instance=valid_output, schema=competitor_schema)

        # Add an extra property that should be rejected
        invalid_output = valid_output.copy()
        invalid_output["extra_field"] = "should_be_rejected"

        # This should raise a ValidationError
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_output, schema=competitor_schema)

    def test_timestamp_format_validation(self, competitor_schema, golden_fixtures):
        """Test that timestamps are in correct ISO format"""

        import re
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            # Check main timestamp
            assert re.match(iso_pattern, expected_output.get('timestamp', '')), \
                f"Invalid timestamp format in scenario {scenario['scenario_id']}"

            # Check metadata timestamp
            meta_timestamp = expected_output.get('metadata', {}).get('analysis_timestamp', '')
            assert re.match(iso_pattern, meta_timestamp), \
                f"Invalid metadata timestamp in scenario {scenario['scenario_id']}"

    def test_hash_format_validation(self, competitor_schema, golden_fixtures):
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

    def test_market_share_distribution(self, golden_fixtures):
        """Test that market share estimates are reasonable"""

        for scenario in golden_fixtures['test_scenarios']:
            expected_output = scenario['expected_output']

            competitors = expected_output['competitors']
            total_market_share = sum(c['market_share_estimate'] for c in competitors)

            # Total market share should be reasonable (allowing for uncovered market)
            assert total_market_share <= 1.2, \
                f"Total market share too high: {total_market_share} in scenario {scenario['scenario_id']}"

            # Largest competitor shouldn't dominate unrealistically
            max_share = max(c['market_share_estimate'] for c in competitors)
            assert max_share <= 0.8, \
                f"Largest competitor market share too high: {max_share} in scenario {scenario['scenario_id']}"

def run_schema_validation_tests():
    """Run all schema validation tests"""

    print("Running Competitor Schema Conformance Tests...")
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
        required_output_keys = ['competitors', 'market_analysis', 'competitive_landscape', 'metadata', 'provenance']
        if not all(key in expected_output for key in required_output_keys):
            print(f"ERROR: Missing required keys in expected output for scenario {scenario['scenario_id']}")
            return False

    print("✓ Testing competitor data quality...")
    for scenario in golden_fixtures['test_scenarios']:
        for competitor in scenario['expected_output']['competitors']:
            # Feature score validation
            feature_scores = competitor.get('feature_scores', {})
            for feature, score in feature_scores.items():
                if not isinstance(score, (int, float)) or not (0.0 <= score <= 1.0):
                    print(f"ERROR: Invalid feature score {score} for {feature} in {competitor.get('company_name', 'unknown')}")
                    return False

            # Market share validation
            market_share = competitor.get('market_share_estimate')
            if not isinstance(market_share, (int, float)) or not (0.0 <= market_share <= 1.0):
                print(f"ERROR: Invalid market share {market_share} in {competitor.get('company_name', 'unknown')}")
                return False

    print("✓ Testing market analysis completeness...")
    for scenario in golden_fixtures['test_scenarios']:
        market_analysis = scenario['expected_output']['market_analysis']
        required_fields = ['total_market_size', 'growth_rate', 'concentration_ratio']

        for field in required_fields:
            if field not in market_analysis:
                print(f"ERROR: Missing market analysis field: {field}")
                return False

    print("✓ Testing competitive landscape...")
    for scenario in golden_fixtures['test_scenarios']:
        landscape = scenario['expected_output']['competitive_landscape']
        required_fields = ['market_segments', 'key_success_factors', 'emerging_trends']

        for field in required_fields:
            if field not in landscape or not landscape[field]:
                print(f"ERROR: Missing or empty landscape field: {field}")
                return False

    print("✓ All schema conformance tests passed!")
    return True

if __name__ == "__main__":
    success = run_schema_validation_tests()
    sys.exit(0 if success else 1)
