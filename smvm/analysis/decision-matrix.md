# SMVM Decision Matrix: Go/Pivot/Kill Framework

## Overview

The SMVM Decision Matrix provides a structured, evidence-based framework for determining Go/Pivot/Kill recommendations for business ideas and product opportunities. This matrix integrates multiple factors including Willingness to Pay (WTP), market opportunity, competitive positioning, technical feasibility, and risk assessment.

## Decision Framework Structure

### Primary Decision Categories

#### GO Decision
**Pursue full development and launch**
- Strong market opportunity with clear competitive advantage
- Validated customer demand and willingness to pay
- Technical feasibility confirmed with manageable risks
- Financial projections support sustainable business model

#### PIVOT Decision
**Modify strategy or product direction**
- Some market validation but requires strategic adjustment
- Core value proposition needs refinement or repositioning
- Technical or market assumptions need validation
- Partial success indicators with clear improvement path

#### KILL Decision
**Discontinue development and reallocate resources**
- Fundamental flaws in market opportunity or business model
- Lack of customer demand or willingness to pay
- Technical feasibility issues cannot be resolved
- Risk/reward ratio unfavorable despite mitigation efforts

## Decision Criteria Matrix

### Core Evaluation Dimensions

| Dimension | Weight | GO Threshold | PIVOT Threshold | KILL Threshold |
|-----------|--------|---------------|-----------------|----------------|
| **Market Opportunity** | 25% | >80% confidence | 50-80% confidence | <50% confidence |
| **WTP Validation** | 20% | >$100 avg WTP | $50-100 avg WTP | <$50 avg WTP |
| **Competitive Position** | 15% | Top 3 positioning | Top 5 positioning | Outside top 10 |
| **Technical Feasibility** | 15% | <6 months build | 6-12 months build | >12 months build |
| **Financial Viability** | 10% | >2.0x ROI potential | 1.2-2.0x ROI potential | <1.2x ROI potential |
| **Risk Assessment** | 10% | <30% critical risks | 30-50% critical risks | >50% critical risks |
| **Team Capability** | 5% | Full capability match | Partial capability gap | Major capability gap |

### Weighted Scoring System

#### Composite Score Calculation
```
Decision_Score = ∑(Dimension_Score × Dimension_Weight)
Where:
- Dimension_Score: 0-100 based on evidence strength
- Dimension_Weight: Percentage weight from matrix above
```

#### Decision Thresholds
- **GO**: Composite Score ≥ 75
- **PIVOT**: Composite Score 45-74
- **KILL**: Composite Score < 45

## Detailed Criteria Definitions

### 1. Market Opportunity Assessment

#### GO Criteria
- **Total Addressable Market (TAM)**: >$1B
- **Serviceable Addressable Market (SAM)**: >$500M
- **Serviceable Obtainable Market (SOM)**: >$100M
- **Market Growth Rate**: >15% CAGR
- **Customer Acquisition Cost**: <$50
- **Customer Lifetime Value**: >$300
- **Market Penetration Potential**: >10% in 3 years

#### PIVOT Criteria
- **TAM**: $500M-$1B
- **SAM**: $200M-$500M
- **SOM**: $25M-$100M
- **Market Growth Rate**: 8-15% CAGR
- **Customer Acquisition Cost**: $50-$100
- **Customer Lifetime Value**: $150-$300
- **Market Penetration Potential**: 3-10% in 3 years

#### KILL Criteria
- **TAM**: <$500M
- **SAM**: <$200M
- **SOM**: <$25M
- **Market Growth Rate**: <8% CAGR
- **Customer Acquisition Cost**: >$100
- **Customer Lifetime Value**: <$150
- **Market Penetration Potential**: <3% in 3 years

### 2. WTP Validation Framework

#### GO Criteria
- **Average WTP**: >$150 per customer
- **WTP Distribution**: >70% above breakeven price
- **Price Elasticity**: -1.5 to -0.5 (optimal range)
- **WTP Confidence Interval**: ±15% or less
- **Segment Coverage**: >80% of target segments
- **Competitive Price Premium**: >20% above market average

#### PIVOT Criteria
- **Average WTP**: $75-$150 per customer
- **WTP Distribution**: 50-70% above breakeven price
- **Price Elasticity**: -2.5 to -1.5 or -0.5 to 0 (needs adjustment)
- **WTP Confidence Interval**: ±15-25%
- **Segment Coverage**: 60-80% of target segments
- **Competitive Price Premium**: 5-20% above market average

#### KILL Criteria
- **Average WTP**: <$75 per customer
- **WTP Distribution**: <50% above breakeven price
- **Price Elasticity**: >-2.5 or <0 (too elastic/inelastic)
- **WTP Confidence Interval**: >±25%
- **Segment Coverage**: <60% of target segments
- **Competitive Price Premium**: <5% above market average

### 3. Competitive Positioning Matrix

#### Competitive Advantage Assessment
```
Competitive_Score = (Feature_Advantage × 0.3) + (Brand_Advantage × 0.2) +
                   (Cost_Advantage × 0.2) + (Market_Reach × 0.15) +
                   (Innovation_Advantage × 0.15)
```

#### GO Criteria
- **Competitive Score**: >75/100
- **Market Position**: #1 or #2 in target segment
- **Unique Value Proposition**: Clear differentiation
- **Barriers to Entry**: High for new competitors
- **Sustainable Advantage**: >2 year advantage window
- **Customer Switching Cost**: High (>$200)

#### PIVOT Criteria
- **Competitive Score**: 50-75/100
- **Market Position**: #3-5 in target segment
- **Unique Value Proposition**: Partial differentiation
- **Barriers to Entry**: Medium for new competitors
- **Sustainable Advantage**: 1-2 year advantage window
- **Customer Switching Cost**: Medium ($50-$200)

#### KILL Criteria
- **Competitive Score**: <50/100
- **Market Position**: Outside top 5
- **Unique Value Proposition**: Weak differentiation
- **Barriers to Entry**: Low for new competitors
- **Sustainable Advantage**: <1 year advantage window
- **Customer Switching Cost**: Low (<$50)

### 4. Technical Feasibility Assessment

#### GO Criteria
- **Technical Readiness Level**: 7-9 (TRL scale)
- **Development Timeline**: <6 months to MVP
- **Resource Requirements**: Within team capabilities
- **Technology Maturity**: Proven and stable
- **Integration Complexity**: Low to medium
- **Scalability**: Proven at required scale

#### PIVOT Criteria
- **Technical Readiness Level**: 5-7
- **Development Timeline**: 6-12 months to MVP
- **Resource Requirements**: Requires additional hiring/training
- **Technology Maturity**: Emerging but viable
- **Integration Complexity**: Medium to high
- **Scalability**: Unproven but theoretically possible

#### KILL Criteria
- **Technical Readiness Level**: <5
- **Development Timeline**: >12 months to MVP
- **Resource Requirements**: Requires major capability build
- **Technology Maturity**: Experimental or unproven
- **Integration Complexity**: Very high
- **Scalability**: Fundamental scalability concerns

### 5. Financial Viability Analysis

#### Unit Economics Assessment
```
Unit_Margin = (Average_Revenue_per_User - Customer_Acquisition_Cost - Cost_per_User) / Average_Revenue_per_User
Payback_Period = Customer_Acquisition_Cost / Monthly_Revenue_per_User
Customer_Lifetime_Value = Average_Revenue_per_User × Customer_Lifespan × Gross_Margin
```

#### GO Criteria
- **Unit Margin**: >50%
- **Payback Period**: <6 months
- **Customer Lifetime Value**: >$500
- **Monthly Recurring Revenue**: Predictable and growing
- **Cash Flow Positive**: Within 12 months
- **Funding Requirements**: <$2M seed/Series A

#### PIVOT Criteria
- **Unit Margin**: 30-50%
- **Payback Period**: 6-12 months
- **Customer Lifetime Value**: $200-$500
- **Monthly Recurring Revenue**: Some predictability
- **Cash Flow Positive**: Within 18-24 months
- **Funding Requirements**: $2-5M seed/Series A

#### KILL Criteria
- **Unit Margin**: <30%
- **Payback Period**: >12 months
- **Customer Lifetime Value**: <$200
- **Monthly Recurring Revenue**: Unpredictable
- **Cash Flow Positive**: Beyond 24 months
- **Funding Requirements**: >$5M seed/Series A

### 6. Risk Assessment Framework

#### Risk Categorization
- **Critical Risk**: Probability >50% with major impact
- **High Risk**: Probability 25-50% with major impact
- **Medium Risk**: Probability 10-25% or moderate impact
- **Low Risk**: Probability <10% with minor impact

#### GO Criteria
- **Critical Risks**: 0 identified
- **High Risks**: <2 with mitigation plans
- **Medium Risks**: <5 with monitoring
- **Risk Mitigation Budget**: <20% of development budget
- **Contingency Plans**: Comprehensive for all high risks
- **Insurance Coverage**: Available for major risks

#### PIVOT Criteria
- **Critical Risks**: 1-2 identified
- **High Risks**: 2-4 with mitigation plans
- **Medium Risks**: 5-8 with monitoring
- **Risk Mitigation Budget**: 20-30% of development budget
- **Contingency Plans**: Developed for high risks
- **Insurance Coverage**: Partial coverage available

#### KILL Criteria
- **Critical Risks**: >2 identified
- **High Risks**: >4 without full mitigation
- **Medium Risks**: >8 unaddressed
- **Risk Mitigation Budget**: >30% of development budget
- **Contingency Plans**: Insufficient for major risks
- **Insurance Coverage**: Limited or unavailable

### 7. Team Capability Assessment

#### GO Criteria
- **Technical Skills**: 100% coverage of required skills
- **Domain Expertise**: Deep understanding of target market
- **Execution Experience**: Proven track record in similar projects
- **Team Stability**: <10% annual turnover
- **Resource Availability**: Full-time dedicated team
- **Growth Capacity**: Can scale with business growth

#### PIVOT Criteria
- **Technical Skills**: 80-100% coverage with training plan
- **Domain Expertise**: Good understanding with advisors
- **Execution Experience**: Some experience in related areas
- **Team Stability**: 10-20% annual turnover
- **Resource Availability**: Mostly dedicated with some matrixed
- **Growth Capacity**: Can scale with additional hiring

#### KILL Criteria
- **Technical Skills**: <80% coverage without feasible training
- **Domain Expertise**: Limited understanding of target market
- **Execution Experience**: No relevant experience
- **Team Stability**: >20% annual turnover
- **Resource Availability**: Significant matrixed/shared resources
- **Growth Capacity**: Cannot scale without major restructuring

## Decision Validation Framework

### Evidence Requirements

#### GO Decision Validation
- **Primary Evidence**: 3+ independent data sources
- **Statistical Confidence**: >80% for key metrics
- **Expert Validation**: 2+ domain experts consulted
- **Historical Analogues**: 2+ comparable successful cases
- **Sensitivity Analysis**: Robust under ±20% parameter changes

#### PIVOT Decision Validation
- **Primary Evidence**: 2+ independent data sources
- **Statistical Confidence**: 60-80% for key metrics
- **Expert Validation**: 1+ domain experts consulted
- **Historical Analogues**: 1+ comparable cases with mixed results
- **Sensitivity Analysis**: Robust under ±30% parameter changes

#### KILL Decision Validation
- **Primary Evidence**: 2+ independent data sources showing negative indicators
- **Statistical Confidence**: Any confidence level with negative results
- **Expert Validation**: 1+ domain experts confirm concerns
- **Historical Analogues**: Similar failed initiatives identified
- **Sensitivity Analysis**: Negative results persist under parameter changes

### Decision Review Process

#### Phase 1: Individual Assessment
- **Timeframe**: 2-4 hours per evaluator
- **Required**: Score all 7 dimensions independently
- **Documentation**: Rationale for each dimension score
- **Calibration**: Review against historical decisions

#### Phase 2: Cross-Functional Review
- **Timeframe**: 4-6 hours team discussion
- **Required**: Discuss discrepancies and edge cases
- **Documentation**: Meeting notes and decision adjustments
- **Calibration**: Ensure consistency across evaluators

#### Phase 3: Executive Validation
- **Timeframe**: 1-2 hours executive review
- **Required**: Challenge assumptions and validate logic
- **Documentation**: Executive approval and additional requirements
- **Calibration**: Align with strategic objectives

#### Phase 4: Implementation Planning
- **Timeframe**: 2-4 hours planning session
- **Required**: Define next steps and resource allocation
- **Documentation**: Action items and timeline commitments
- **Calibration**: Ensure feasibility of recommended actions

## Implementation Guidelines

### Decision Matrix Application
```python
def evaluate_business_opportunity(opportunity_data, market_data, technical_data, team_data):
    scores = {}

    # Calculate dimension scores
    scores['market_opportunity'] = calculate_market_score(opportunity_data, market_data)
    scores['wtp_validation'] = calculate_wtp_score(opportunity_data)
    scores['competitive_position'] = calculate_competitive_score(market_data)
    scores['technical_feasibility'] = calculate_technical_score(technical_data)
    scores['financial_viability'] = calculate_financial_score(opportunity_data, market_data)
    scores['risk_assessment'] = calculate_risk_score(opportunity_data, technical_data)
    scores['team_capability'] = calculate_team_score(team_data)

    # Calculate weighted composite score
    weights = {
        'market_opportunity': 0.25,
        'wtp_validation': 0.20,
        'competitive_position': 0.15,
        'technical_feasibility': 0.15,
        'financial_viability': 0.10,
        'risk_assessment': 0.10,
        'team_capability': 0.05
    }

    composite_score = sum(scores[dimension] * weights[dimension] for dimension in scores)

    # Determine recommendation
    if composite_score >= 75:
        recommendation = 'GO'
        confidence = (composite_score - 75) / 25 * 100
    elif composite_score >= 45:
        recommendation = 'PIVOT'
        confidence = 100 - abs(composite_score - 60) / 15 * 100
    else:
        recommendation = 'KILL'
        confidence = (45 - composite_score) / 45 * 100

    return {
        'composite_score': composite_score,
        'recommendation': recommendation,
        'confidence': min(100, max(0, confidence)),
        'dimension_scores': scores,
        'critical_factors': identify_critical_factors(scores),
        'recommended_actions': get_recommended_actions(recommendation, scores)
    }
```

### Confidence Level Interpretation
- **90-100%**: Very High - Strong evidence supports decision
- **75-89%**: High - Good evidence with minor uncertainties
- **60-74%**: Moderate - Reasonable evidence with some concerns
- **45-59%**: Low - Weak evidence, decision should be treated cautiously
- **0-44%**: Very Low - Significant uncertainties, may require additional analysis

## Risk Management

### Decision Quality Risks
- **Confirmation Bias**: Tendency to seek evidence supporting preferred outcome
- **Anchoring Bias**: Over-reliance on initial assumptions or data
- **Availability Bias**: Over-weighting easily available information
- **Overconfidence**: Underestimating uncertainty in estimates

### Mitigation Strategies
- **Structured Process**: Use standardized decision matrix for all evaluations
- **Diverse Perspectives**: Include multiple stakeholders in evaluation process
- **Evidence-Based**: Require empirical data for key assumptions
- **Sensitivity Testing**: Test robustness of decision under different scenarios
- **Regular Calibration**: Review past decisions against actual outcomes

### Appeal Process
1. **Initial Appeal**: Submit additional evidence within 48 hours
2. **Review Committee**: Cross-functional team reviews appeal
3. **Executive Override**: Final decision authority with documentation
4. **Implementation Delay**: Maximum 1-week delay for appeals process

## Performance Tracking

### Decision Quality Metrics
- **Accuracy Rate**: Percentage of decisions validated by actual outcomes
- **Time to Decision**: Average time from analysis completion to final decision
- **Stakeholder Satisfaction**: Survey-based assessment of decision process
- **Resource Efficiency**: Cost per decision evaluation

### Continuous Improvement
- **Decision Log**: Maintain database of all decisions with outcomes
- **Pattern Analysis**: Identify common factors in successful/unsuccessful decisions
- **Process Refinement**: Update matrix based on validation results
- **Training Updates**: Modify training based on decision quality trends

## Integration with SMVM Pipeline

### Data Flow Integration
1. **Input Data**: WTP estimates, market analysis, competitive intelligence
2. **Processing**: Apply decision matrix scoring algorithm
3. **Output Generation**: Structured recommendation with evidence
4. **Report Creation**: Automated validation report generation
5. **Audit Trail**: Complete provenance and decision rationale

### API Integration Points
- **WTP Service**: Retrieve willingness to pay estimates
- **Market Analysis**: Access market sizing and opportunity data
- **Competitor Intelligence**: Get competitive positioning data
- **Technical Assessment**: Retrieve feasibility analysis results
- **Financial Modeling**: Access unit economics and projections

## Conclusion

The SMVM Decision Matrix provides a rigorous, evidence-based framework for Go/Pivot/Kill decisions. By integrating multiple evaluation dimensions with clear thresholds and validation requirements, the matrix ensures consistent, high-quality strategic decisions that balance opportunity, feasibility, and risk.

## Document Information

- **Version**: 1.0.0
- **Last Updated**: December 1, 2024
- **Review Cycle**: Quarterly
- **Owner**: SMVM Strategy Team
- **Approval**: Executive Review Board

## Appendices

### Appendix A: Scoring Methodology
Detailed scoring rubrics for each evaluation dimension.

### Appendix B: Case Study Examples
Real-world examples of Go/Pivot/Kill decisions using this framework.

### Appendix C: Decision Tree Logic
Programmatic implementation of decision logic and edge cases.
