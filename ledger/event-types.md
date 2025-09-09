# SMVM Event Types

## Overview

This document defines the comprehensive event types for the Synthetic Market Validation Module (SMVM) ledger. Events provide an immutable audit trail of all operations and state changes throughout the validation process.

## Event Structure

### Base Event Schema
All SMVM events follow this JSON schema:

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "type": "object",
  "properties": {
    "event_id": {"type": "string", "pattern": "^EVT-\\d{8}-\\d{6}-[a-f0-9]{12}$"},
    "event_type": {"type": "string", "enum": ["INGESTED", "NORMALIZED", "SANITIZED", "SYNTHESIZED", "SIMULATED", "FLAGGED", "ANALYZED", "DECIDED", "PERSISTED"]},
    "timestamp": {"type": "string", "format": "date-time"},
    "run_id": {"type": "string", "pattern": "^RUN-\\d{8}-\\d{6}-[a-f0-9]{8}$"},
    "span_id": {"type": "string", "pattern": "^RUN-\\d{8}-\\d{6}-[a-f0-9]{8}-\\d{4}-[A-Z]{3}$"},
    "service": {"type": "string", "enum": ["ingestion", "personas", "competitors", "simulation", "analysis", "overwatch", "memory", "cli"]},
    "agent_id": {"type": "string"},
    "data_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    "metadata": {"type": "object", "additionalProperties": false},
    "provenance": {"type": "object", "additionalProperties": false}
  },
  "required": ["event_id", "event_type", "timestamp", "run_id", "span_id", "service", "agent_id", "data_hash", "metadata", "provenance"],
  "additionalProperties": false
}
```

## Event Type Definitions

### INGESTED
**Description**: Records the ingestion of external data sources into SMVM

**Trigger**: When data is successfully received from external sources (APIs, files, databases)

**Metadata Schema**:
```json
{
  "source_type": "string (api/file/database)",
  "source_url": "string",
  "record_count": "integer",
  "data_format": "string (json/csv/xml)",
  "ingestion_method": "string (batch/stream)",
  "quality_score": "number (0.0-1.0)",
  "estimated_size_bytes": "integer"
}
```

**Provenance Schema**:
```json
{
  "source_checksum": "string (SHA-256 of source data)",
  "ingestion_timestamp": "string (ISO 8601)",
  "ingestion_duration_ms": "integer",
  "bytes_processed": "integer",
  "records_filtered": "integer",
  "error_count": "integer"
}
```

**Example**:
```json
{
  "event_id": "EVT-20241201-143052-a1b2c3d4e5f6",
  "event_type": "INGESTED",
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "run_id": "RUN-20241201-143052-a1b2c3d4",
  "span_id": "RUN-20241201-143052-a1b2c3d4-0001-ING",
  "service": "ingestion",
  "agent_id": "smvm-ingestion-01",
  "data_hash": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6",
  "metadata": {
    "source_type": "api",
    "source_url": "https://api.marketdata.com/v2/prices",
    "record_count": 1500,
    "data_format": "json",
    "ingestion_method": "batch",
    "quality_score": 0.87,
    "estimated_size_bytes": 2048576
  },
  "provenance": {
    "source_checksum": "b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7",
    "ingestion_timestamp": "2024-12-01T14:30:52.123456Z",
    "ingestion_duration_ms": 2340,
    "bytes_processed": 2048576,
    "records_filtered": 5,
    "error_count": 2
  }
}
```

### NORMALIZED
**Description**: Records the normalization of ingested data to SMVM standard schemas

**Trigger**: When data is successfully transformed to match SMVM contracts

**Metadata Schema**:
```json
{
  "original_schema": "string",
  "target_schema": "string (idea.input/personas.output/etc.)",
  "field_mapping_count": "integer",
  "transformation_rules_applied": "array",
  "data_quality_improved": "boolean",
  "validation_errors_resolved": "integer"
}
```

**Provenance Schema**:
```json
{
  "normalization_engine_version": "string",
  "transformation_duration_ms": "integer",
  "fields_normalized": "integer",
  "default_values_applied": "integer",
  "data_loss_percentage": "number (0.0-1.0)",
  "schema_compliance_score": "number (0.0-1.0)"
}
```

### SANITIZED
**Description**: Records the sanitization and redaction of sensitive data

**Trigger**: When PII or sensitive information is detected and redacted

**Metadata Schema**:
```json
{
  "sensitivity_level": "string (public/internal/confidential)",
  "pii_fields_detected": "array",
  "redaction_rules_applied": "array",
  "data_utility_preserved": "number (0.0-1.0)",
  "compliance_requirements": "array"
}
```

**Provenance Schema**:
```json
{
  "sanitization_engine_version": "string",
  "redaction_duration_ms": "integer",
  "fields_redacted": "integer",
  "hashing_algorithm": "string (SHA-256/SHA-3)",
  "audit_trail_preserved": "boolean",
  "reversibility_status": "string (reversible/irreversible)"
}
```

### SYNTHESIZED
**Description**: Records the generation of synthetic personas or market data

**Trigger**: When synthetic data is successfully generated and validated

**Metadata Schema**:
```json
{
  "synthesis_type": "string (personas/market_data/scenarios)",
  "target_count": "integer",
  "generation_parameters": "object",
  "bias_controls_applied": "array",
  "diversity_targets": "object",
  "statistical_properties": "object"
}
```

**Provenance Schema**:
```json
{
  "synthesis_engine_version": "string",
  "generation_duration_ms": "integer",
  "random_seed": "integer",
  "bias_assessment_score": "number (0.0-1.0)",
  "diversity_score": "number (0.0-1.0)",
  "validation_passed": "boolean"
}
```

### SIMULATED
**Description**: Records the execution of market simulation scenarios

**Trigger**: When simulation completes successfully with results

**Metadata Schema**:
```json
{
  "scenario_type": "string (market_growth/competition/pricing)",
  "simulation_parameters": "object",
  "time_horizon": "string (months/years)",
  "assumptions_made": "array",
  "convergence_achieved": "boolean",
  "statistical_significance": "number (0.0-1.0)"
}
```

**Provenance Schema**:
```json
{
  "simulation_engine_version": "string",
  "execution_duration_ms": "integer",
  "iterations_completed": "integer",
  "random_seed": "integer",
  "numerical_stability": "number (0.0-1.0)",
  "result_confidence": "number (0.0-1.0)"
}
```

### FLAGGED
**Description**: Records the detection of anomalies, risks, or quality issues

**Trigger**: When automated monitoring detects issues requiring attention

**Metadata Schema**:
```json
{
  "flag_type": "string (anomaly/risk/quality/bias)",
  "severity_level": "string (low/medium/high/critical)",
  "detection_method": "string (statistical/rule-based/ml)",
  "affected_entities": "array",
  "recommended_actions": "array",
  "escalation_required": "boolean"
}
```

**Provenance Schema**:
```json
{
  "detection_engine_version": "string",
  "detection_timestamp": "string (ISO 8601)",
  "confidence_score": "number (0.0-1.0)",
  "false_positive_probability": "number (0.0-1.0)",
  "historical_precedence": "boolean",
  "automated_response_taken": "boolean"
}
```

### ANALYZED
**Description**: Records the completion of market analysis and insights generation

**Trigger**: When analysis algorithms complete and produce insights

**Metadata Schema**:
```json
{
  "analysis_type": "string (elasticity/wtp/roi/decision_matrix)",
  "analysis_scope": "string (market/segment/product)",
  "methodology_used": "array",
  "key_findings": "array",
  "confidence_levels": "object",
  "recommendations_generated": "integer"
}
```

**Provenance Schema**:
```json
{
  "analysis_engine_version": "string",
  "analysis_duration_ms": "integer",
  "data_points_processed": "integer",
  "statistical_tests_passed": "integer",
  "model_accuracy_score": "number (0.0-1.0)",
  "insight_quality_score": "number (0.0-1.0)"
}
```

### DECIDED
**Description**: Records business decisions and recommendations made by SMVM

**Trigger**: When decision algorithms produce final recommendations

**Metadata Schema**:
```json
{
  "decision_type": "string (go_no_go/market_entry/pricing)",
  "decision_options": "array",
  "evaluation_criteria": "array",
  "decision_logic": "string",
  "recommended_action": "string",
  "confidence_level": "number (0.0-1.0)",
  "alternative_considerations": "array"
}
```

**Provenance Schema**:
```json
{
  "decision_engine_version": "string",
  "decision_duration_ms": "integer",
  "criteria_weighted": "boolean",
  "sensitivity_analysis_performed": "boolean",
  "stakeholder_alignment": "number (0.0-1.0)",
  "decision_traceability": "boolean"
}
```

### PERSISTED
**Description**: Records the successful storage of SMVM results and artifacts

**Trigger**: When validation results are successfully saved to persistent storage

**Metadata Schema**:
```json
{
  "storage_type": "string (database/file/memory)",
  "data_classification": "string (green/amber)",
  "retention_policy": "string (days/months/years)",
  "artifact_types": "array",
  "storage_location": "string",
  "backup_strategy": "string"
}
```

**Provenance Schema**:
```json
{
  "storage_engine_version": "string",
  "persistence_duration_ms": "integer",
  "data_volume_bytes": "integer",
  "compression_ratio": "number",
  "integrity_check_passed": "boolean",
  "replication_status": "string (completed/pending/failed)"
}
```

## Event Lifecycle

### Event Generation
1. **Trigger Detection**: System identifies event-triggering condition
2. **Data Collection**: Gather all required metadata and provenance
3. **Hash Calculation**: Generate cryptographic hashes for data integrity
4. **Schema Validation**: Ensure event conforms to type-specific schema
5. **ID Generation**: Create unique event ID with timestamp
6. **Persistence**: Write event to ledger with atomic operation

### Event Validation
- **Schema Compliance**: Must match event type schema
- **Data Integrity**: Hashes must be valid and consistent
- **Temporal Ordering**: Events must be in chronological order
- **Referential Integrity**: References to other entities must be valid
- **Business Rules**: Must comply with SMVM business logic

### Event Retrieval
```python
def get_events_by_run(run_id: str, event_types: List[str] = None) -> List[dict]:
    """Retrieve events for a specific validation run"""
    # Implementation for efficient event retrieval

def get_event_chain(run_id: str) -> List[dict]:
    """Get complete event chain for replay purposes"""
    # Implementation for chronological event ordering

def validate_event_integrity(event: dict) -> bool:
    """Validate event data integrity using hashes"""
    # Implementation for cryptographic verification
```

## Event Storage & Management

### Storage Strategy
- **Format**: JSON Lines (.jsonl) for efficient streaming
- **Partitioning**: By run_id for parallel processing
- **Compression**: Gzip compression after 1 hour
- **Encryption**: AES-256 for sensitive event data
- **Backup**: Cross-region replication with 99.999% durability

### Retention Policies
| Event Type | Hot Storage | Warm Storage | Cold Storage | Deletion |
|------------|-------------|--------------|--------------|----------|
| INGESTED | 30 days | 90 days | 1 year | 2 years |
| NORMALIZED | 30 days | 90 days | 1 year | 2 years |
| SANITIZED | 90 days | 1 year | 2 years | 5 years |
| SYNTHESIZED | 30 days | 90 days | 1 year | 2 years |
| SIMULATED | 90 days | 1 year | 2 years | 5 years |
| FLAGGED | 1 year | 2 years | 5 years | Never |
| ANALYZED | 90 days | 1 year | 2 years | 5 years |
| DECIDED | 1 year | 2 years | 5 years | Never |
| PERSISTED | 30 days | 90 days | 1 year | 2 years |

### Audit & Compliance
- **Immutability**: Events cannot be modified after creation
- **Chain of Custody**: Complete audit trail of event access
- **Regulatory Compliance**: GDPR, SOX, industry-specific requirements
- **Access Controls**: Role-based access with audit logging

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX

*This event type specification ensures complete auditability and reproducibility of SMVM operations.*
