#!/usr/bin/env python3
"""
Mock E2E SMVM Validation Run

This script simulates a complete SMVM validation run, generating events.jsonl
with all required event types and demonstrating the observability system.
"""

import json
import hashlib
import random
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import time

# Import SMVM components
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from smvm.overwatch.token_monitor import get_token_monitor, TokenCeilingBreach
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Token monitor not available - running without token enforcement")
    get_token_monitor = None
    TokenCeilingBreach = Exception


def generate_run_id() -> str:
    """Generate a unique run ID"""
    timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S")
    random_part = hashlib.md5(str(random.random()).encode()).hexdigest()[:8]
    return f"RUN-{timestamp}-{random_part}"


def calculate_hash(data: any) -> str:
    """Calculate SHA-256 hash of data"""
    if isinstance(data, (dict, list)):
        data = json.dumps(data, sort_keys=True)
    elif not isinstance(data, str):
        data = str(data)

    return hashlib.sha256(data.encode()).hexdigest()


def create_event(event_type: str, run_id: str, span_id: str, service: str,
                data_hash: str, metadata: Dict = None, provenance: Dict = None) -> Dict:
    """Create a standardized SMVM event"""

    return {
        "event_id": f"EVT-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{hashlib.md5(str(random.random()).encode()).hexdigest()[:12]}",
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "run_id": run_id,
        "span_id": span_id,
        "service": service,
        "agent_id": f"smvm-{service}-01",
        "data_hash": data_hash,
        "metadata": metadata or {},
        "provenance": provenance or {}
    }


def simulate_ingestion_stage(run_id: str, events_file: Path) -> Dict:
    """Simulate data ingestion stage"""

    print("🔄 Simulating ingestion stage...")

    # Create ingestion span
    span_id = f"{run_id}-0001-ING"

    # Simulate raw data
    raw_data = {
        "market_data": [
            {"company": "TechCorp", "revenue": 50000000, "employees": 500},
            {"company": "DataInc", "revenue": 30000000, "employees": 200},
            {"company": "FinTech LLC", "revenue": 15000000, "employees": 80}
        ],
        "source": "market_api",
        "record_count": 3
    }

    # INGESTED event
    ingested_event = create_event(
        "INGESTED",
        run_id,
        span_id,
        "ingestion",
        calculate_hash(raw_data),
        {
            "source_type": "api",
            "source_url": "https://api.marketdata.com/v2/companies",
            "record_count": 3,
            "data_format": "json",
            "ingestion_method": "batch",
            "quality_score": 0.89,
            "estimated_size_bytes": 2048
        },
        {
            "source_checksum": calculate_hash("source_data"),
            "ingestion_timestamp": datetime.utcnow().isoformat() + "Z",
            "ingestion_duration_ms": 2340,
            "bytes_processed": 2048,
            "records_filtered": 0,
            "error_count": 0
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(ingested_event) + '\n')

    # Simulate data normalization
    normalized_data = {
        "companies": [
            {"id": "COMP-001", "name": "TechCorp", "revenue_usd": 50000000, "employee_count": 500},
            {"id": "COMP-002", "name": "DataInc", "revenue_usd": 30000000, "employee_count": 200},
            {"id": "COMP-003", "name": "FinTech LLC", "revenue_usd": 15000000, "employee_count": 80}
        ]
    }

    # NORMALIZED event
    normalized_event = create_event(
        "NORMALIZED",
        run_id,
        span_id,
        "ingestion",
        calculate_hash(normalized_data),
        {
            "original_schema": "raw_api_response",
            "target_schema": "smvm_company_v1",
            "field_mapping_count": 8,
            "transformation_rules_applied": ["currency_conversion", "field_renaming", "data_validation"],
            "data_quality_improved": True,
            "validation_errors_resolved": 2
        },
        {
            "normalization_engine_version": "1.0.0",
            "transformation_duration_ms": 450,
            "fields_normalized": 8,
            "default_values_applied": 1,
            "data_loss_percentage": 0.0,
            "schema_compliance_score": 0.95
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(normalized_event) + '\n')

    return normalized_data


def simulate_personas_stage(run_id: str, events_file: Path, input_data: Dict) -> Dict:
    """Simulate personas synthesis stage"""

    print("🔄 Simulating personas stage...")

    span_id = f"{run_id}-0002-PER"

    # SYNTHESIZED event
    personas_data = {
        "personas": [
            {
                "persona_id": "P-US-202412-a1b2",
                "demographics": {"age": 35, "gender": "female", "location": {"country": "US", "region": "CA"}, "education_level": "bachelor", "occupation": "Software Engineer"},
                "behavioral_attributes": {"risk_tolerance": 7.5, "brand_loyalty": 8.2, "tech_adoption": "early_adopter", "shopping_frequency": "weekly"},
                "economic_profile": {"income_range": {"min": 80000, "max": 120000, "currency": "USD"}, "net_worth": 250000, "debt_to_income_ratio": 0.25, "savings_rate": 0.15}
            },
            {
                "persona_id": "P-US-202412-b3c4",
                "demographics": {"age": 28, "gender": "male", "location": {"country": "US", "region": "NY"}, "education_level": "master", "occupation": "Financial Analyst"},
                "behavioral_attributes": {"risk_tolerance": 6.8, "brand_loyalty": 7.9, "tech_adoption": "innovator", "shopping_frequency": "monthly"},
                "economic_profile": {"income_range": {"min": 60000, "max": 90000, "currency": "USD"}, "net_worth": 150000, "debt_to_income_ratio": 0.20, "savings_rate": 0.12}
            }
        ]
    }

    synthesized_event = create_event(
        "SYNTHESIZED",
        run_id,
        span_id,
        "personas",
        calculate_hash(personas_data),
        {
            "synthesis_type": "personas",
            "target_count": 2,
            "generation_parameters": {"bias_controls": True, "diversity_target": 0.8},
            "bias_controls_applied": ["demographic_balancing", "economic_distribution"],
            "diversity_targets": {"gender": 0.5, "age_groups": 0.7},
            "statistical_properties": {"confidence_interval": 0.95, "margin_of_error": 0.05}
        },
        {
            "synthesis_engine_version": "1.0.0",
            "generation_duration_ms": 3200,
            "random_seed": 12345,
            "bias_assessment_score": 0.12,
            "diversity_score": 0.87,
            "validation_passed": True
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(synthesized_event) + '\n')

    return personas_data


def simulate_competitors_stage(run_id: str, events_file: Path, input_data: Dict) -> Dict:
    """Simulate competitors analysis stage"""

    print("🔄 Simulating competitors stage...")

    span_id = f"{run_id}-0003-COM"

    # FLAGGED event (simulating anomaly detection)
    flagged_event = create_event(
        "FLAGGED",
        run_id,
        span_id,
        "competitors",
        calculate_hash("anomaly_data"),
        {
            "flag_type": "anomaly",
            "severity_level": "medium",
            "detection_method": "statistical",
            "affected_entities": ["COMP-001", "COMP-003"],
            "recommended_actions": ["review_data_quality", "validate_source"],
            "escalation_required": False
        },
        {
            "detection_engine_version": "1.0.0",
            "detection_timestamp": datetime.utcnow().isoformat() + "Z",
            "confidence_score": 0.78,
            "false_positive_probability": 0.15,
            "historical_precedence": True,
            "automated_response_taken": False
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(flagged_event) + '\n')

    return {"flagged": True}


def simulate_simulation_stage(run_id: str, events_file: Path, input_data: Dict) -> Dict:
    """Simulate market simulation stage"""

    print("🔄 Simulating simulation stage...")

    span_id = f"{run_id}-0004-SIM"

    # SIMULATED event
    simulation_results = {
        "performance_metrics": {
            "returns": {"mean": 0.085, "std": 0.023, "min": 0.045, "max": 0.145},
            "risk_measures": {"var_95": 0.067, "sharpe_ratio": 1.85, "max_drawdown": 0.089},
            "market_states": {"bull_market_prob": 0.65, "bear_market_prob": 0.15, "sideways_prob": 0.20}
        },
        "market_outcomes": {
            "scenario_results": [
                {"scenario": "growth_projection", "probability": 0.45, "expected_return": 0.095},
                {"scenario": "recession_impact", "probability": 0.30, "expected_return": 0.025},
                {"scenario": "market_volatility", "probability": 0.25, "expected_return": 0.055}
            ]
        }
    }

    simulated_event = create_event(
        "SIMULATED",
        run_id,
        span_id,
        "simulation",
        calculate_hash(simulation_results),
        {
            "scenario_type": "market_growth",
            "simulation_parameters": {"iterations": 10000, "time_horizon": "3_years", "confidence_level": 0.95},
            "time_horizon": "36_months",
            "assumptions_made": ["normal_market_returns", "moderate_volatility", "no_black_swan_events"],
            "convergence_achieved": True,
            "statistical_significance": 0.98
        },
        {
            "simulation_engine_version": "1.0.0",
            "execution_duration_ms": 45000,
            "iterations_completed": 10000,
            "random_seed": 12345,
            "numerical_stability": 0.96,
            "result_confidence": 0.92
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(simulated_event) + '\n')

    return simulation_results


def simulate_analysis_stage(run_id: str, events_file: Path, input_data: Dict) -> Dict:
    """Simulate market analysis stage"""

    print("🔄 Simulating analysis stage...")

    span_id = f"{run_id}-0005-ANA"

    # ANALYZED event
    analysis_results = {
        "elasticity_analysis": {
            "price_elasticity": -1.45,
            "confidence_interval": {"lower": -1.67, "upper": -1.23},
            "demand_curve": "elastic",
            "price_sensitivity": "moderate"
        },
        "wtp_analysis": {
            "segments": [
                {"segment": "early_adopters", "mean_wtp": 45.50, "std_wtp": 12.30},
                {"segment": "mainstream", "mean_wtp": 32.75, "std_wtp": 8.90},
                {"segment": "price_sensitive", "mean_wtp": 18.25, "std_wtp": 5.45}
            ]
        },
        "decision_matrix": {
            "options": ["premium_strategy", "value_strategy", "niche_strategy"],
            "recommended_option": "premium_strategy",
            "confidence_score": 0.78
        }
    }

    analyzed_event = create_event(
        "ANALYZED",
        run_id,
        span_id,
        "analysis",
        calculate_hash(analysis_results),
        {
            "analysis_type": "comprehensive",
            "analysis_scope": "market_segmentation",
            "methodology_used": ["econometric_modeling", "survey_analysis", "decision_theory"],
            "key_findings": ["strong_price_elasticity", "segmented_willingness_to_pay", "premium_positioning_recommended"],
            "confidence_levels": {"elasticity": 0.89, "wtp": 0.76, "decision": 0.82},
            "recommendations_generated": 5
        },
        {
            "analysis_engine_version": "1.0.0",
            "analysis_duration_ms": 15200,
            "data_points_processed": 2500,
            "statistical_tests_passed": 8,
            "model_accuracy_score": 0.84,
            "insight_quality_score": 0.79
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(analyzed_event) + '\n')

    return analysis_results


def simulate_decision_stage(run_id: str, events_file: Path, input_data: Dict) -> Dict:
    """Simulate decision stage"""

    print("🔄 Simulating decision stage...")

    span_id = f"{run_id}-0006-DEC"

    # DECIDED event
    decision_result = {
        "decision_type": "go_no_go",
        "decision_options": ["proceed_with_investment", "pivot_strategy", "cancel_project"],
        "evaluation_criteria": ["market_opportunity", "technical_feasibility", "financial_returns", "risk_profile"],
        "decision_logic": "weighted_criteria_analysis",
        "recommended_action": "proceed_with_investment",
        "confidence_level": 0.82,
        "alternative_considerations": ["monitor_market_conditions", "phase_implementation", "validate_assumptions"]
    }

    decided_event = create_event(
        "DECIDED",
        run_id,
        span_id,
        "analysis",
        calculate_hash(decision_result),
        {
            "decision_type": "go_no_go",
            "decision_options": ["proceed_with_investment", "pivot_strategy", "cancel_project"],
            "evaluation_criteria": ["market_opportunity", "technical_feasibility", "financial_returns", "risk_profile"],
            "decision_logic": "weighted_criteria_analysis",
            "recommended_action": "proceed_with_investment",
            "confidence_level": 0.82,
            "alternative_considerations": ["monitor_market_conditions", "phase_implementation", "validate_assumptions"]
        },
        {
            "decision_engine_version": "1.0.0",
            "decision_duration_ms": 890,
            "criteria_weighted": True,
            "sensitivity_analysis_performed": True,
            "stakeholder_alignment": 0.91,
            "decision_traceability": True
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(decided_event) + '\n')

    # PERSISTED event
    persisted_data = {
        "artifacts": ["validation_report.md", "simulation_results.json", "analysis_summary.json"],
        "storage_locations": ["s3://smvm-artifacts/runs/", "postgres://results_db/"],
        "retention_policy": "365_days"
    }

    persisted_event = create_event(
        "PERSISTED",
        run_id,
        span_id,
        "memory",
        calculate_hash(persisted_data),
        {
            "storage_type": "hybrid",
            "data_classification": "amber",
            "retention_policy": "365_days",
            "artifact_types": ["report", "data", "metadata"],
            "storage_location": "s3://smvm-artifacts/runs/",
            "backup_strategy": "cross_region_replication"
        },
        {
            "storage_engine_version": "1.0.0",
            "persistence_duration_ms": 2340,
            "data_volume_bytes": 5242880,
            "compression_ratio": 0.75,
            "integrity_check_passed": True,
            "replication_status": "completed"
        }
    )

    with open(events_file, 'a') as f:
        f.write(json.dumps(persisted_event) + '\n')

    return decision_result


def run_mock_e2e():
    """Run the complete mock E2E validation"""

    print("🚀 Starting Mock SMVM E2E Validation Run")
    print("=" * 50)

    # Generate run ID
    run_id = generate_run_id()
    print(f"📋 Run ID: {run_id}")

    # Initialize token monitor
    if get_token_monitor:
        monitor = get_token_monitor()
    else:
        monitor = None

    # Create events file
    events_file = Path("events.jsonl")
    if events_file.exists():
        events_file.unlink()  # Start fresh

    try:
        # Stage 1: Ingestion
        ingestion_result = simulate_ingestion_stage(run_id, events_file)
        time.sleep(0.5)  # Simulate processing time

        # Stage 2: Personas
        personas_result = simulate_personas_stage(run_id, events_file, ingestion_result)
        time.sleep(0.5)

        # Stage 3: Competitors
        competitors_result = simulate_competitors_stage(run_id, events_file, personas_result)
        time.sleep(0.5)

        # Stage 4: Simulation
        simulation_result = simulate_simulation_stage(run_id, events_file, competitors_result)
        time.sleep(0.5)

        # Stage 5: Analysis
        analysis_result = simulate_analysis_stage(run_id, events_file, simulation_result)
        time.sleep(0.5)

        # Stage 6: Decision
        decision_result = simulate_decision_stage(run_id, events_file, analysis_result)

        print("✅ Mock E2E validation completed successfully!")
        print(f"📄 Events written to: {events_file}")
        print(f"📊 Total events generated: {sum(1 for _ in open(events_file))}")

        # Show token status
        if monitor:
            status = monitor.get_system_status()
            print(f"🎫 Final token status: {status['total_current']}/{status['total_ceiling']} allocated")
        else:
            print("🎫 Token monitoring not available")

        return True

    except TokenCeilingBreach as e:
        print(f"❌ Token ceiling breach: {e}")
        return False
    except Exception as e:
        print(f"❌ Mock E2E failed: {e}")
        return False
    finally:
        # Cleanup
        if monitor:
            monitor.shutdown()


if __name__ == "__main__":
    success = run_mock_e2e()
    exit(0 if success else 1)
