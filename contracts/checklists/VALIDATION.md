# SMVM Schema Validation Checklist

This document outlines the validation invariants and business rules for all SMVM schemas to ensure data quality, consistency, and compliance.

## Schema Overview

| Schema | Purpose | Zone | Retention | Critical Fields |
|--------|---------|------|-----------|-----------------|
| `idea.input.json` | Capture user ideas | GREEN | 90 days | description |
| `personas.output.json` | Synthetic personas | AMBER | 365 days | persona_id, demographics |
| `competitors.output.json` | Competitor analysis | AMBER | 365 days | competitor_id, market_position |
| `offers.output.json` | Product/service offers | AMBER | 180 days | offer_id, pricing |
| `simulation.config.json` | Simulation parameters | AMBER | 90 days | scenario, random_seed |
| `simulation.result.json` | Simulation outputs | AMBER | 365 days | performance_metrics |
| `decision.output.json` | Business decisions | AMBER | 365 days | decision_recommendation |

## Global Validation Rules

### Metadata Validation
- [ ] **Run ID Format**: Must match `RUN-YYYYMMDD-HHMMSS-xxxxxxxx`
- [ ] **Span ID Format**: Must match `RUN-YYYYMMDD-HHMMSS-xxxxxxxx-NNNN-XXX`
- [ ] **Timestamp Format**: Must be valid ISO 8601 date-time
- [ ] **Python Version**: Must be `3.12.x` or `3.11.13` (reject ≥3.13)
- [ ] **Hash Format**: All hashes must be 64-character hex strings
- [ ] **Data Zone**: Must be valid enum value (GREEN, AMBER)
- [ ] **Retention Days**: Must be within schema-specific bounds

### Content Hash Verification
- [ ] **Content Hash Match**: Calculated hash must match stored hash
- [ ] **Canonical JSON**: Hash calculated on sorted, normalized JSON
- [ ] **Metadata Exclusion**: Content hash excludes metadata block
- [ ] **Deterministic**: Same content always produces same hash

### Business Logic Invariants
- [ ] **No Future Timestamps**: All timestamps must be ≤ current time
- [ ] **Reasonable Bounds**: All numeric values within business-reasonable ranges
- [ ] **Enum Compliance**: All enum fields use valid values only
- [ ] **Required Fields**: All required fields present and non-null
- [ ] **PII Protection**: Sensitive fields properly flagged and protected

## Schema-Specific Validation Rules

### idea.input.json Validation

#### Field Validations
- [ ] **description**: Non-empty, ≤1000 chars, no HTML/scripting
- [ ] **domain**: Valid enum (finance, healthcare, retail, technology, other)
- [ ] **urgency**: Valid enum (low, medium, high, critical)
- [ ] **additionalProperties**: Must be `false` (reject unknown keys)

#### Business Rules
- [ ] **Minimum Content**: description must be ≥10 characters
- [ ] **No Profanity**: Content must not contain prohibited terms
- [ ] **Format Consistency**: No mixed encoding or control characters
- [ ] **Completeness**: Either description only or all optional fields provided

#### Edge Cases
- [ ] **Empty Description**: Must reject empty/whitespace-only descriptions
- [ ] **Maximum Length**: Must reject descriptions >1000 characters
- [ ] **Invalid Domain**: Must reject unknown domain values
- [ ] **Unknown Fields**: Must reject any fields not in schema

### personas.output.json Validation

#### Field Validations
- [ ] **persona_id**: Must match `P-XX-XXXXXX-XXXX` format
- [ ] **age**: Must be 18-100 (inclusive)
- [ ] **gender**: Valid enum (male, female, non_binary, prefer_not_to_say)
- [ ] **country**: Must be valid ISO 3166-1 alpha-2 code
- [ ] **education_level**: Valid enum (high_school, associate, bachelor, master, doctorate, other)
- [ ] **occupation**: Non-empty, ≤100 characters
- [ ] **income_range**: min ≤ max, both ≥0, multiple of 100
- [ ] **risk_tolerance**: Must be 0.0-10.0 (inclusive)
- [ ] **net_worth**: Must be ≥ -1,000,000 (allows debt)
- [ ] **debt_to_income_ratio**: Must be 0.0-5.0 (inclusive)
- [ ] **savings_rate**: Must be 0.0-1.0 (inclusive)

#### Business Rules
- [ ] **Age Consistency**: Age must be reasonable for education/occupation
- [ ] **Income Logic**: Income range max ≥ min
- [ ] **Geographic Consistency**: Country/region must be valid combination
- [ ] **Economic Coherence**: Net worth, income, debt must be logically consistent
- [ ] **Behavioral Bounds**: Risk tolerance, savings rate within valid ranges

#### Statistical Validations
- [ ] **Distribution Check**: Age distribution should be realistic
- [ ] **Demographic Balance**: Gender distribution should be reasonable
- [ ] **Income Distribution**: Should follow expected wealth distribution
- [ ] **Geographic Coverage**: Should represent target markets appropriately

### competitors.output.json Validation

#### Field Validations
- [ ] **competitor_id**: Must match `C-XX-XXXXXX-XXXX` format
- [ ] **name**: Non-empty, ≤200 characters
- [ ] **industry**: Valid enum (fintech, banking, insurance, investment, cryptocurrency, payments, lending, other)
- [ ] **headquarters.country**: Valid ISO 3166-1 alpha-2 code
- [ ] **founded_year**: Must be 1800-2030
- [ ] **employee_count**: Must be 1-1,000,000
- [ ] **market_share**: Must be 0.0-100.0 (inclusive)
- [ ] **growth_rate**: Must be -100.0-1000.0 (allows decline/rapid growth)
- [ ] **market_size**: Must be ≥0, multiple of 1,000,000
- [ ] **cagr**: Must be -50.0-200.0 (inclusive)

#### Business Rules
- [ ] **Market Share Sum**: Combined market share ≤100% (if same market)
- [ ] **Founded Year Logic**: Founded year ≤ current year
- [ ] **Growth Consistency**: Growth rate should be reasonable for industry
- [ ] **Employee Scale**: Employee count should match company size expectations
- [ ] **Geographic Coverage**: Presence in countries should be realistic

#### Competitive Analysis Rules
- [ ] **Strength/Weakness Balance**: Should have reasonable balance
- [ ] **Market Position Logic**: Market share should align with positioning
- [ ] **Growth Rate Bounds**: Should be within industry-typical ranges
- [ ] **Barrier Assessment**: Barriers should be industry-appropriate

### offers.output.json Validation

#### Field Validations
- [ ] **offer_id**: Must match `O-XX-XXXXXX-XXXX` format
- [ ] **name**: Non-empty, ≤200 characters
- [ ] **category**: Valid enum (checking_account, savings_account, credit_card, loan, investment, insurance, payment_service, fintech_app, other)
- [ ] **description**: ≤500 characters, no free-text outside designated fields
- [ ] **features**: Array of 1-20 items, each ≤100 characters
- [ ] **model**: Valid enum (free, freemium, subscription, transaction_based, tiered, usage_based)
- [ ] **currency**: Valid ISO 4217 code
- [ ] **base_price**: Must be ≥0, multiple of 0.01
- [ ] **monthly_fee**: Must be ≥0, multiple of 0.01
- [ ] **transaction_fee**: percentage 0.0-10.0, fixed_amount ≥0
- [ ] **tier limits**: transactions 0-1,000,000, users 1-100,000

#### Business Rules
- [ ] **Pricing Logic**: Different pricing models have appropriate fields
- [ ] **Feature Consistency**: Features must match category expectations
- [ ] **Tier Progression**: Higher tiers must have better/higher limits
- [ ] **Currency Consistency**: All monetary values use same currency
- [ ] **Fee Structure**: Fees must be logically consistent with model

#### Target Audience Validation
- [ ] **Age Range Logic**: min_age ≤ max_age, both reasonable for product
- [ ] **Income Appropriateness**: Target income matches product category
- [ ] **Segment Consistency**: Behavioral segments appropriate for product
- [ ] **Demographic Coverage**: Target audience should be well-defined

### simulation.config.json Validation

#### Field Validations
- [ ] **scenario**: Valid enum (baseline, optimistic, pessimistic, stress_test, sensitivity_analysis)
- [ ] **model_type**: Valid enum (monte_carlo, historical_backtest, agent_based, system_dynamics, hybrid)
- [ ] **random_seed**: Must be 0-2,147,483,647
- [ ] **confidence_level**: Must be 0.80-0.99
- [ ] **iterations**: Must be 100-100,000
- [ ] **start_date**: Must be valid date, before end_date
- [ ] **end_date**: Must be valid date, after start_date
- [ ] **time_step**: Valid enum (daily, weekly, monthly, quarterly)
- [ ] **warmup_period**: Must be 0-365 days

#### Business Rules
- [ ] **Date Range Logic**: start_date < end_date
- [ ] **Time Step Appropriateness**: Time step should match simulation horizon
- [ ] **Iteration Scale**: Iterations should be appropriate for model type
- [ ] **Confidence Bounds**: Confidence level within statistical standards
- [ ] **Seed Validity**: Random seed should be properly bounded

#### Model-Specific Rules
- [ ] **Monte Carlo**: Requires sufficient iterations (≥1000)
- [ ] **Historical Backtest**: Requires appropriate date range
- [ ] **Agent Based**: May require population_size specification
- [ ] **Hybrid Models**: Should have clear component specifications

### simulation.result.json Validation

#### Field Validations
- [ ] **total_iterations**: Must be 1-100,000
- [ ] **execution_time**: Must be 0.0-86,400.0 seconds
- [ ] **convergence_status**: Valid enum (converged, not_converged, early_termination, numerical_error)
- [ ] **total_return**: Must be -1.0-10.0 (allows extreme outcomes)
- [ ] **annualized_return**: Must be -1.0-5.0
- [ ] **volatility**: Must be 0.0-2.0
- [ ] **value_at_risk**: Must be -1.0-0.0 (negative values)
- [ ] **maximum_drawdown**: Must be -1.0-0.0
- [ ] **sharpe_ratio**: Must be -10.0-10.0
- [ ] **confidence_intervals**: Must have level 0.80-0.99

#### Business Rules
- [ ] **Return Logic**: annualized_return consistent with total_return and time period
- [ ] **Risk Metrics**: Volatility should align with VaR expectations
- [ ] **Convergence**: Should converge for well-specified models
- [ ] **Performance Bounds**: All metrics within theoretically possible ranges
- [ ] **Statistical Validity**: Confidence intervals should be properly calculated

#### Time Series Validation
- [ ] **Timestamp Sequence**: Timestamps must be monotonically increasing
- [ ] **Price Continuity**: Price index should be continuous (no extreme jumps)
- [ ] **Volume Reasonability**: Trading volume should be within market expectations
- [ ] **Data Completeness**: No missing data points in critical periods

### decision.output.json Validation

#### Field Validations
- [ ] **primary_recommendation**: Valid enum (proceed, proceed_with_modifications, delay, pivot, cancel)
- [ ] **confidence_level**: Must be 0.0-1.0
- [ ] **implementation_priority**: Valid enum (critical, high, medium, low)
- [ ] **market_opportunity.size**: Must be ≥0, multiple of 1,000,000
- [ ] **market_opportunity.growth_rate**: Must be -0.50-2.0
- [ ] **time_to_market**: Must be 1-730 days
- [ ] **revenue_forecast**: All values ≥0, year_1 ≤ year_3 ≤ peak
- [ ] **break_even_months**: Must be 1-120
- [ ] **break_even_customers**: Must be 1-1,000,000

#### Business Rules
- [ ] **Recommendation Logic**: Recommendation should align with analysis
- [ ] **Confidence Appropriateness**: Confidence should reflect data quality
- [ ] **Revenue Progression**: Revenue forecasts should show logical growth
- [ ] **Timeline Reasonability**: Timeframes should be achievable
- [ ] **Risk Assessment**: Risk levels should be supported by analysis

#### Financial Validation
- [ ] **Cost Structure**: Fixed + variable costs should be reasonable
- [ ] **Break-even Logic**: Break-even calculations should be mathematically sound
- [ ] **ROI Expectations**: Projections should be conservative but achievable
- [ ] **Cash Flow**: Should account for working capital requirements

## Cross-Schema Validation Rules

### Referential Integrity
- [ ] **ID Consistency**: IDs should be unique across schemas
- [ ] **Timestamp Alignment**: Related records should have consistent timestamps
- [ ] **Version Compatibility**: All schemas should use compatible Python versions
- [ ] **Run Consistency**: Related data should belong to same run

### Business Logic Consistency
- [ ] **Market Sizing**: Market sizes should be consistent across schemas
- [ ] **Competitive Analysis**: Competitor data should align with market analysis
- [ ] **Persona Targeting**: Persona segments should match offer targeting
- [ ] **Simulation Bounds**: Simulation results should respect input constraints

### Data Quality Rules
- [ ] **Completeness**: No missing critical data points
- [ ] **Accuracy**: Data should pass basic sanity checks
- [ ] **Consistency**: Related fields should be logically consistent
- [ ] **Timeliness**: Data should be within acceptable age bounds

## Validation Implementation

### Automated Validation
- [ ] **Schema Compliance**: All data must pass JSON Schema validation
- [ ] **Business Rules**: Custom validators for business logic
- [ ] **Cross-References**: Validation of relationships between schemas
- [ ] **Statistical Checks**: Distribution and outlier detection

### Manual Review Triggers
- [ ] **High-Value Decisions**: Financial projections above threshold
- [ ] **High-Risk Assessments**: Critical or high risk levels
- [ ] **Unusual Patterns**: Statistical outliers or anomalies
- [ ] **Regulatory Impact**: Decisions with regulatory implications

### Validation Reporting
- [ ] **Error Classification**: Categorize validation failures
- [ ] **Impact Assessment**: Assess impact of validation failures
- [ ] **Remediation Guidance**: Provide guidance for fixing issues
- [ ] **Audit Trail**: Maintain complete validation history

## Performance and Scalability

### Validation Performance
- [ ] **Response Time**: Schema validation <100ms per record
- [ ] **Throughput**: Support 1000+ records per second
- [ ] **Memory Usage**: Validation should not exceed 100MB per process
- [ ] **Concurrent Processing**: Support multiple validation threads

### Scalability Considerations
- [ ] **Batch Processing**: Efficient validation of large datasets
- [ ] **Distributed Validation**: Support for distributed processing
- [ ] **Caching**: Cache compiled schemas and validation rules
- [ ] **Incremental Validation**: Validate only changed data

## Compliance and Audit

### Regulatory Compliance
- [ ] **Data Protection**: All validations support GDPR/CCPA requirements
- [ ] **Audit Trail**: Complete record of all validation activities
- [ ] **Data Retention**: Validation results retained per schema requirements
- [ ] **Access Control**: Validation results properly secured

### Quality Assurance
- [ ] **Test Coverage**: All validation rules have corresponding tests
- [ ] **False Positive Rate**: Minimize incorrect rejection of valid data
- [ ] **False Negative Rate**: Minimize acceptance of invalid data
- [ ] **Performance Monitoring**: Monitor validation performance metrics

---

**Validation Checklist Version**: 1.0
**Last Updated**: 2024-12-XX
**Review Frequency**: Quarterly
**Next Review**: 2025-03-XX

*This checklist ensures data quality and consistency across all SMVM schemas.*
