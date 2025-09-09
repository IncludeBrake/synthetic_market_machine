# SMVM Metrics Specification

## Overview

This document defines the comprehensive metrics specification for the Synthetic Market Validation Module (SMVM). Metrics enable quantitative monitoring of system performance, reliability, and business value.

## Metric Categories

### 1. Performance Metrics

#### Request Latency (`smvm_request_duration_seconds`)
- **Type**: Histogram
- **Description**: End-to-end request processing time
- **Labels**:
  - `service`: SMVM service name
  - `operation`: Specific operation
  - `status`: success/error/timeout
- **Buckets**: [0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
- **Example**:
  ```prometheus
  smvm_request_duration_seconds_bucket{service="simulation", operation="execute", status="success", le="5.0"} 95
  smvm_request_duration_seconds_count{service="simulation", operation="execute", status="success"} 100
  smvm_request_duration_seconds_sum{service="simulation", operation="execute", status="success"} 234.56
  ```

#### Service Latency (`smvm_service_duration_seconds`)
- **Type**: Histogram
- **Description**: Individual service processing time
- **Labels**:
  - `service`: SMVM service name
  - `operation`: Service operation
  - `cache_hit`: true/false
- **Buckets**: [0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0]
- **SLO Target**: P95 < 2.0 seconds for cache misses

#### Token Processing Rate (`smvm_token_processing_rate`)
- **Type**: Gauge
- **Description**: Tokens processed per second
- **Labels**:
  - `service`: SMVM service name
  - `direction`: input/output
- **Units**: tokens/second
- **Example**: `smvm_token_processing_rate{service="analysis", direction="input"} 1250.5`

### 2. Token Management Metrics

#### Token Consumption (`smvm_token_consumption_total`)
- **Type**: Counter
- **Description**: Total tokens consumed by service
- **Labels**:
  - `service`: SMVM service name
  - `user_type`: authenticated_user/service_account
  - `priority`: low/normal/high/critical
- **Example**:
  ```prometheus
  smvm_token_consumption_total{service="simulation", user_type="authenticated_user", priority="normal"} 15420
  ```

#### Token Ceiling Breaches (`smvm_token_ceiling_breaches_total`)
- **Type**: Counter
- **Description**: Number of token ceiling breach attempts
- **Labels**:
  - `service`: SMVM service name
  - `ceiling_type`: base/dynamic/emergency
  - `breach_type`: soft/hard
- **Alert Threshold**: > 0 in 5-minute window

#### Token Efficiency (`smvm_token_efficiency_ratio`)
- **Type**: Gauge
- **Description**: Output tokens per input token
- **Labels**:
  - `service`: SMVM service name
  - `operation`: Specific operation
- **Formula**: `token_out / token_in`
- **Target**: > 1.0 (generative operations)

### 3. Cost Estimation Metrics

#### Service Cost (`smvm_service_cost_usd`)
- **Type**: Counter
- **Description**: Estimated cost in USD for service usage
- **Labels**:
  - `service`: SMVM service name
  - `cost_type`: compute/storage/network
- **Example**:
  ```prometheus
  smvm_service_cost_usd{service="simulation", cost_type="compute"} 12.45
  ```

#### Request Cost Estimate (`smvm_request_cost_estimate_usd`)
- **Type**: Histogram
- **Description**: Estimated cost per request
- **Labels**:
  - `service`: SMVM service name
  - `cost_category`: token_usage/compute_time
- **Buckets**: [0.001, 0.01, 0.1, 1.0, 10.0, 100.0]

#### Cost Efficiency (`smvm_cost_efficiency_ratio`)
- **Type**: Gauge
- **Description**: Business value per dollar spent
- **Labels**:
  - `service`: SMVM service name
  - `value_metric`: validation_success/market_insights
- **Formula**: `business_value / cost_usd`

### 4. Governance & Security Metrics

#### Veto Events (`smvm_veto_events_total`)
- **Type**: Counter
- **Description**: Number of requests vetoed by overwatch
- **Labels**:
  - `veto_reason`: risk_assessment/token_limit/policy_violation
  - `severity`: low/medium/high/critical
- **Example**:
  ```prometheus
  smvm_veto_events_total{veto_reason="risk_assessment", severity="high"} 5
  ```

#### Abstain Events (`smvm_abstain_events_total`)
- **Type**: Counter
- **Description**: Number of requests abstained from processing
- **Labels**:
  - `abstain_reason`: high_risk/resource_constraint/maintenance
  - `fallback_action`: retry/defer/reject
- **Alert Threshold**: > 10% of total requests in 1-hour window

#### Security Events (`smvm_security_events_total`)
- **Type**: Counter
- **Description**: Security-related events and violations
- **Labels**:
  - `event_type`: authentication_failure/access_denied/data_exposure
  - `severity`: info/warning/error/critical
- **Alert Threshold**: > 0 for error/critical severity

### 5. Quality & Reliability Metrics

#### Success Rate (`smvm_success_rate_ratio`)
- **Type**: Gauge
- **Description**: Percentage of successful operations
- **Labels**:
  - `service`: SMVM service name
  - `operation`: Specific operation
- **Formula**: `successful_operations / total_operations`
- **SLO Target**: > 99.5% for production

#### Error Rate (`smvm_error_rate_ratio`)
- **Type**: Gauge
- **Description**: Percentage of failed operations
- **Labels**:
  - `service`: SMVM service name
  - `error_type`: validation/network/timeout/internal
- **Alert Threshold**: > 1% in 5-minute window

#### Failure Recovery Time (`smvm_failure_recovery_seconds`)
- **Type**: Histogram
- **Description**: Time to recover from service failures
- **Labels**:
  - `service`: SMVM service name
  - `failure_type`: crash/network_timeout/dependency_failure
- **Buckets**: [1, 5, 10, 30, 60, 300, 600]

### 6. Business Value Metrics

#### Validation Runs Completed (`smvm_validation_runs_completed_total`)
- **Type**: Counter
- **Description**: Total number of completed validation runs
- **Labels**:
  - `outcome`: success/partial_failure/complete_failure
  - `run_type`: full/express/minimal
- **Example**:
  ```prometheus
  smvm_validation_runs_completed_total{outcome="success", run_type="full"} 1250
  ```

#### Market Insights Generated (`smvm_market_insights_generated_total`)
- **Type**: Counter
- **Description**: Number of market insights produced
- **Labels**:
  - `insight_type`: opportunity/threat/trend/anomaly
  - `confidence_level`: low/medium/high
- **Example**:
  ```prometheus
  smvm_market_insights_generated_total{insight_type="opportunity", confidence_level="high"} 450
  ```

#### Decision Accuracy (`smvm_decision_accuracy_ratio`)
- **Type**: Gauge
- **Description**: Accuracy of SMVM recommendations vs. actual outcomes
- **Labels**:
  - `decision_type`: go/no_go/market_entry/pricing
  - `time_horizon`: immediate/short_term/long_term
- **Calculation**: Requires manual validation of outcomes

## Metric Collection & Storage

### Collection Strategy
- **Pull-based**: Prometheus scrapes metrics endpoints
- **Push-based**: Services push metrics to central collector
- **Agent-based**: Sidecar agents collect and forward metrics

### Storage Configuration
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'smvm-services'
    static_configs:
      - targets: ['localhost:9090']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'smvm-overwatch'
    static_configs:
      - targets: ['localhost:9091']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### Retention Policy
- **Raw Metrics**: 15 days
- **5-minute Aggregates**: 90 days
- **1-hour Aggregates**: 1 year
- **1-day Aggregates**: 5 years

## Alerting Rules

### Critical Alerts
```prometheus
# Service Down
ALERT ServiceDown
  IF up{job="smvm-services"} == 0
  FOR 5m
  LABELS { severity = "critical" }
  ANNOTATIONS {
    summary = "SMVM service {{ $labels.service }} is down",
    description = "SMVM service {{ $labels.service }} has been down for 5 minutes"
  }

# High Error Rate
ALERT HighErrorRate
  IF smvm_error_rate_ratio > 0.05
  FOR 5m
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary = "High error rate for {{ $labels.service }}",
    description = "Error rate for {{ $labels.service }} is {{ $value | printf "%.2f" }}%"
  }
```

### Performance Alerts
```prometheus
# High Latency
ALERT HighLatency
  IF histogram_quantile(0.95, rate(smvm_request_duration_seconds_bucket[5m])) > 30
  FOR 5m
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary = "High latency for {{ $labels.service }}",
    description = "P95 latency for {{ $labels.service }} is {{ $value | printf "%.2f" }}s"
  }

# Token Ceiling Breach
ALERT TokenCeilingBreach
  IF increase(smvm_token_ceiling_breaches_total[5m]) > 0
  FOR 1m
  LABELS { severity = "error" }
  ANNOTATIONS {
    summary = "Token ceiling breach detected",
    description = "Token ceiling breached for {{ $labels.service }}"
  }
```

### Business Alerts
```prometheus
# Low Success Rate
ALERT LowSuccessRate
  IF smvm_success_rate_ratio < 0.95
  FOR 15m
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary = "Low success rate for {{ $labels.service }}",
    description = "Success rate for {{ $labels.service }} dropped to {{ $value | printf "%.2f" }}%"
  }

# Validation Backlog
ALERT ValidationBacklog
  IF smvm_validation_queue_length > 50
  FOR 10m
  LABELS { severity = "info" }
  ANNOTATIONS {
    summary = "Validation queue building up",
    description = "Validation queue length is {{ $value }}"
  }
```

## Dashboards & Visualization

### Service Health Dashboard
```
Row 1: Service Status & Uptime
- Service availability (up/down status)
- Uptime percentage (last 24h, 7d, 30d)
- Restart count and reasons

Row 2: Performance Metrics
- Request rate (requests/second)
- Latency percentiles (P50, P95, P99)
- Error rate percentage

Row 3: Resource Utilization
- CPU usage percentage
- Memory usage (absolute + percentage)
- Token consumption rate
```

### Business Value Dashboard
```
Row 1: Validation Outcomes
- Successful validation runs (count + trend)
- Average validation time
- Success rate by run type

Row 2: Market Insights
- Insights generated by type
- Insight quality distribution
- Business impact estimation

Row 3: Cost Analysis
- Cost per validation run
- Token efficiency ratio
- Cost vs. business value
```

### Operational Dashboard
```
Row 1: System Health
- Service health status
- Dependency status
- Alert summary

Row 2: Security & Governance
- Authentication failures
- Authorization denials
- Veto/abstain events

Row 3: Data Quality
- Input data quality scores
- Processing success rates
- Output validation rates
```

## Metric Validation

### Data Quality Checks
- **Completeness**: All required metrics present
- **Accuracy**: Metrics match expected ranges and distributions
- **Timeliness**: Metrics updated within expected intervals
- **Consistency**: Related metrics show logical relationships

### Anomaly Detection
```python
def detect_metric_anomaly(current_value, historical_values, threshold=3.0):
    """Detect metric anomalies using statistical methods"""
    mean = statistics.mean(historical_values)
    std_dev = statistics.stdev(historical_values)

    if std_dev == 0:
        return False

    z_score = abs(current_value - mean) / std_dev
    return z_score > threshold
```

### Metric Health Monitoring
- **Staleness**: Alert if metrics haven't been updated
- **Cardinality**: Monitor label combinations for explosion
- **Distribution**: Ensure metrics follow expected distributions
- **Correlation**: Verify related metrics move together

## Integration with Other Observability

### Log Correlation
```json
{
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "level": "INFO",
  "message": "Simulation completed",
  "metrics_context": {
    "request_duration": 45.23,
    "token_consumed": 2300,
    "success_rate": 0.98
  },
  "trace_context": {
    "span_id": "RUN-20241201-143052-a1b2c3d4-0004-SIM",
    "parent_span_id": "RUN-20241201-143052-a1b2c3d4-0000-ROOT"
  }
}
```

### Trace Enrichment
```json
{
  "span_id": "RUN-20241201-143052-a1b2c3d4-0004-SIM",
  "operation": "execute_simulation",
  "start_time": "2024-12-01T14:30:52.123456Z",
  "end_time": "2024-12-01T14:31:37.345678Z",
  "metrics": {
    "duration_seconds": 45.22,
    "token_input": 1500,
    "token_output": 2300,
    "success": true
  },
  "business_context": {
    "validation_run": true,
    "market_scenario": "growth_projection",
    "confidence_level": 0.91
  }
}
```

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX

*This metrics specification enables comprehensive quantitative monitoring and alerting for SMVM operations.*
