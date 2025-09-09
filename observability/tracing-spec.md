# SMVM Tracing Specification

## Overview

This document defines the distributed tracing specification for the Synthetic Market Validation Module (SMVM). Tracing enables end-to-end observability of validation runs across all services and operations.

## Trace Context

### Run ID Format
```
RUN-YYYYMMDD-HHMMSS-xxxxxxxx
```
- **YYYYMMDD**: Date (e.g., 20241201)
- **HHMMSS**: Time (e.g., 143052)
- **xxxxxxxx**: 8-character hex random identifier

### Span ID Format
```
RUN-YYYYMMDD-HHMMSS-xxxxxxxx-NNNN-XXX
```
- **RUN-YYYYMMDD-HHMMSS-xxxxxxxx**: Parent run ID
- **NNNN**: 4-digit sequence number (0001, 0002, etc.)
- **XXX**: 3-letter service code (ING, PER, COM, SIM, ANA, DEC)

### Service Codes
| Service | Code | Description |
|---------|------|-------------|
| Ingestion | ING | Data ingestion and normalization |
| Personas | PER | Persona synthesis and bias control |
| Competitors | COM | Competitor analysis and taxonomy |
| Simulation | SIM | Market simulation execution |
| Analysis | ANA | Market analysis and decision support |
| Decision | DEC | Final decision and recommendation |

## Trace Hierarchy

### Root Span (Level 0)
```
RUN-20241201-143052-a1b2c3d4-0000-ROOT
```
- **Parent**: None
- **Service**: CLI or API Gateway
- **Operation**: `validate_idea`
- **Duration**: Entire validation run

### Service Spans (Level 1)
```
RUN-20241201-143052-a1b2c3d4-0001-ING  (Ingestion)
RUN-20241201-143052-a1b2c3d4-0002-PER  (Personas)
RUN-20241201-143052-a1b2c3d4-0003-COM  (Competitors)
RUN-20241201-143052-a1b2c3d4-0004-SIM  (Simulation)
RUN-20241201-143052-a1b2c3d4-0005-ANA  (Analysis)
RUN-20241201-143052-a1b2c3d4-0006-DEC  (Decision)
```
- **Parent**: Root span
- **Service**: Individual SMVM services
- **Operation**: Service-specific operations
- **Execution**: Sequential (ingest → personas → competitors → simulation → analysis → decision)

### Operation Spans (Level 2)
```
RUN-20241201-143052-a1b2c3d4-0001-ING-0001  (Data validation)
RUN-20241201-143052-a1b2c3d4-0001-ING-0002  (Schema normalization)
RUN-20241201-143052-a1b2c3d4-0001-ING-0003  (Quality assessment)
```
- **Parent**: Service span
- **Service**: Same as parent
- **Operation**: Granular operations within service
- **Execution**: Parallel or sequential within service

## Span Lifecycle

### Span Creation
```json
{
  "span_id": "RUN-20241201-143052-a1b2c3d4-0001-ING",
  "parent_span_id": "RUN-20241201-143052-a1b2c3d4-0000-ROOT",
  "service": "ingestion",
  "operation": "process_data",
  "start_time": "2024-12-01T14:30:52.123456Z",
  "status": "started",
  "metadata": {
    "input_records": 100,
    "expected_output": "normalized_data"
  }
}
```

### Span Completion
```json
{
  "span_id": "RUN-20241201-143052-a1b2c3d4-0001-ING",
  "parent_span_id": "RUN-20241201-143052-a1b2c3d4-0000-ROOT",
  "service": "ingestion",
  "operation": "process_data",
  "start_time": "2024-12-01T14:30:52.123456Z",
  "end_time": "2024-12-01T14:30:55.789012Z",
  "duration_ms": 3456,
  "status": "completed",
  "metadata": {
    "output_records": 95,
    "quality_score": 0.87,
    "error_count": 2
  }
}
```

### Span Error
```json
{
  "span_id": "RUN-20241201-143052-a1b2c3d4-0001-ING",
  "parent_span_id": "RUN-20241201-143052-a1b2c3d4-0000-ROOT",
  "service": "ingestion",
  "operation": "process_data",
  "start_time": "2024-12-01T14:30:52.123456Z",
  "end_time": "2024-12-01T14:30:53.456789Z",
  "duration_ms": 1233,
  "status": "error",
  "error": {
    "type": "ValidationError",
    "message": "Schema validation failed",
    "details": "Missing required field: description"
  }
}
```

## Service-Specific Spans

### Ingestion Service Spans

#### ING-0001: Data Validation
- **Operation**: `validate_input`
- **Inputs**: Raw data records
- **Outputs**: Validation results
- **Success Criteria**: All records pass schema validation
- **Error Handling**: Log validation failures, continue with valid records

#### ING-0002: Schema Normalization
- **Operation**: `normalize_schema`
- **Inputs**: Validated data records
- **Outputs**: Normalized data in SMVM format
- **Success Criteria**: All fields mapped to standard schema
- **Error Handling**: Skip unmappable records, log normalization issues

#### ING-0003: Quality Assessment
- **Operation**: `assess_quality`
- **Inputs**: Normalized data records
- **Outputs**: Quality metrics and scores
- **Success Criteria**: Quality score meets threshold
- **Error Handling**: Flag low-quality data, continue processing

### Personas Service Spans

#### PER-0001: Bias Detection
- **Operation**: `detect_bias`
- **Inputs**: Demographic data, behavioral patterns
- **Outputs**: Bias metrics and flags
- **Success Criteria**: Bias scores within acceptable ranges
- **Error Handling**: Apply bias correction, log mitigation actions

#### PER-0002: Persona Synthesis
- **Operation**: `synthesize_personas`
- **Inputs**: Constraints, demographic targets, seed
- **Outputs**: Synthetic persona profiles
- **Success Criteria**: Target count achieved, diversity met
- **Error Handling**: Adjust synthesis parameters, retry with different seed

#### PER-0003: Validation & Calibration
- **Operation**: `validate_personas`
- **Inputs**: Synthetic personas
- **Outputs**: Validation results and confidence scores
- **Success Criteria**: Confidence score above threshold
- **Error Handling**: Discard invalid personas, generate replacements

### Competitors Service Spans

#### COM-0001: Feature Classification
- **Operation**: `classify_features`
- **Inputs**: Raw feature descriptions
- **Outputs**: Classified features by taxonomy
- **Success Criteria**: All features successfully classified
- **Error Handling**: Apply default classification, log ambiguities

#### COM-0002: Price Normalization
- **Operation**: `normalize_pricing`
- **Inputs**: Raw pricing data, target currencies
- **Outputs**: Normalized pricing in standard format
- **Success Criteria**: All prices successfully converted
- **Error Handling**: Use fallback rates, log conversion issues

#### COM-0003: Competitive Analysis
- **Operation**: `analyze_competition`
- **Inputs**: Normalized competitor data, market context
- **Outputs**: Competitive positioning and insights
- **Success Criteria**: Complete analysis for all competitors
- **Error Handling**: Use partial data, note analysis limitations

### Simulation Service Spans

#### SIM-0001: Scenario Validation
- **Operation**: `validate_scenario`
- **Inputs**: Scenario configuration, constraints
- **Outputs**: Validation results and recommendations
- **Success Criteria**: Scenario passes all realism checks
- **Error Handling**: Suggest parameter adjustments, block invalid scenarios

#### SIM-0002: Seed Generation
- **Operation**: `generate_seed`
- **Inputs**: Run context, reproducibility requirements
- **Outputs**: Cryptographically secure random seed
- **Success Criteria**: Seed quality meets requirements
- **Error Handling**: Retry seed generation, log quality issues

#### SIM-0003: Simulation Execution
- **Operation**: `execute_simulation`
- **Inputs**: Validated scenario, seed, iteration count
- **Outputs**: Simulation results and performance metrics
- **Success Criteria**: Simulation converges within time limits
- **Error Handling**: Reduce iterations, log convergence issues

### Analysis Service Spans

#### ANA-0001: Elasticity Analysis
- **Operation**: `calculate_elasticity`
- **Inputs**: Price and demand data points
- **Outputs**: Elasticity coefficients and confidence intervals
- **Success Criteria**: Statistical significance achieved
- **Error Handling**: Use alternative methods, note reduced confidence

#### ANA-0002: WTP Estimation
- **Operation**: `estimate_wtp`
- **Inputs**: Survey data, market segmentation
- **Outputs**: Willingness to pay distributions
- **Success Criteria**: Sufficient sample size and statistical power
- **Error Handling**: Pool data across segments, note estimation uncertainty

#### ANA-0003: Decision Matrix
- **Operation**: `build_decision_matrix`
- **Inputs**: Options, criteria, weights
- **Outputs**: Weighted decision matrix and recommendations
- **Success Criteria**: All options evaluated against all criteria
- **Error Handling**: Use default weights, note evaluation gaps

### Overwatch Service Spans

#### OVW-0001: Request Evaluation
- **Operation**: `evaluate_request`
- **Inputs**: Service request, context, system state
- **Outputs**: Risk assessment and approval decision
- **Success Criteria**: Clear approval/rejection decision
- **Error Handling**: Escalate to manual review, apply conservative defaults

#### OVW-0002: Token Enforcement
- **Operation**: `enforce_tokens`
- **Inputs**: Token request, user context, ceilings
- **Outputs**: Token allocation decision
- **Success Criteria**: Token limits respected
- **Error Handling**: Reject request, suggest alternatives

#### OVW-0003: Quality Monitoring
- **Operation**: `monitor_quality`
- **Inputs**: Service outputs, quality metrics
- **Outputs**: Quality assessment and alerts
- **Success Criteria**: Quality thresholds maintained
- **Error Handling**: Flag quality issues, trigger remediation

## Trace Propagation

### Context Passing
```python
@dataclass
class TraceContext:
    run_id: str
    parent_span_id: str
    service: str
    operation: str
    metadata: Dict[str, Any]

    def create_child_span(self, operation: str) -> 'TraceContext':
        """Create a child span context"""
        span_sequence = self._get_next_sequence()
        span_id = f"{self.run_id}-{span_sequence:04d}-{self.service[:3].upper()}"

        return TraceContext(
            run_id=self.run_id,
            parent_span_id=self.span_id,
            service=self.service,
            operation=operation,
            metadata={}
        )
```

### Service Integration
```python
class TracedService:
    def __init__(self, service_name: str, tracer: Tracer):
        self.service_name = service_name
        self.tracer = tracer

    def execute_operation(self, operation: str, context: TraceContext):
        """Execute an operation with tracing"""
        with self.tracer.start_span(
            operation=operation,
            context=context
        ) as span:
            try:
                # Operation logic here
                result = self._do_operation()

                span.set_attribute("result.success", True)
                span.set_attribute("result.size", len(result))

                return result

            except Exception as e:
                span.set_attribute("error", True)
                span.set_attribute("error.message", str(e))
                raise
```

## Trace Storage & Retrieval

### Storage Format
- **Format**: JSON Lines (.jsonl)
- **Compression**: Gzip for spans older than 1 hour
- **Retention**: 30 days for active traces, 365 days for archived

### Retrieval Patterns
```python
# Get all spans for a run
def get_run_trace(run_id: str) -> List[Span]:
    return query_spans({"run_id": run_id})

# Get spans for a specific service
def get_service_spans(run_id: str, service: str) -> List[Span]:
    return query_spans({
        "run_id": run_id,
        "service": service
    })

# Get span hierarchy
def get_span_tree(run_id: str) -> SpanTree:
    spans = get_run_trace(run_id)
    return build_hierarchy(spans)
```

## Performance Considerations

### Sampling Strategy
- **Development**: 100% sampling (all spans)
- **Testing**: 50% sampling (every other span)
- **Production**: 10% sampling (performance-critical only)

### Overhead Management
- **Span Creation**: < 1ms overhead
- **Attribute Setting**: < 0.1ms per attribute
- **Storage**: Asynchronous batch writing
- **Memory**: Bounded span buffers (max 10,000 spans)

### Alerting Thresholds
- **Span Duration**: > 30 seconds (warning), > 5 minutes (critical)
- **Error Rate**: > 5% spans with errors
- **Missing Spans**: > 1% of expected spans missing
- **Storage Backlog**: > 1000 unsaved spans

## Integration with Logging

### Correlated Events
```json
{
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "run_id": "RUN-20241201-143052-a1b2c3d4",
  "span_id": "RUN-20241201-143052-a1b2c3d4-0001-ING",
  "level": "INFO",
  "message": "Data normalization completed",
  "correlation_data": {
    "input_records": 100,
    "output_records": 95,
    "processing_time_ms": 3456
  }
}
```

### Trace-to-Log Linking
- **Span ID**: Links logs to specific operations
- **Run ID**: Groups all logs for a validation run
- **Service**: Identifies the service generating logs
- **Operation**: Specifies the operation being logged

## Monitoring & Alerting

### Trace Quality Metrics
- **Completeness**: Percentage of operations with spans
- **Duration**: P95 span duration by service/operation
- **Error Rate**: Percentage of spans with errors
- **Hierarchy**: Percentage of spans with correct parent-child relationships

### Alert Conditions
- Completeness < 95%: "Span coverage degraded"
- Duration > 2x baseline: "Performance degradation detected"
- Error rate > 10%: "Service reliability issues"
- Hierarchy violations: "Trace integrity compromised"

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX

*This tracing specification ensures complete observability and debugging capabilities for SMVM validation runs.*
