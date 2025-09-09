# LLM Guardrails Policy

This document establishes guardrails and operational constraints for Large Language Model (LLM) interactions within the Synthetic Market Validation Module (SMVM).

## Token Ceiling Limits

### Global Limits
- **Maximum tokens per request**: 4,096 tokens
- **Maximum tokens per response**: 2,048 tokens
- **Maximum tokens per session**: 16,384 tokens
- **Maximum concurrent sessions**: 10 per user

### Context Window Management
- **System prompt**: ≤ 1,024 tokens
- **User context preservation**: ≤ 2,048 tokens
- **Rolling window**: Maintain last 3 interactions
- **Compression threshold**: 75% of context window

### Rate Limiting
- **Requests per minute**: 60 per user
- **Requests per hour**: 1,000 per user
- **Requests per day**: 5,000 per user
- **Burst limit**: 10 requests within 10 seconds

## Grounding Requirements

### Factual Accuracy
- **Source verification**: All claims must reference authoritative sources
- **Citation requirement**: ≥80% of technical statements must include citations
- **Fact-checking**: Cross-reference with multiple sources when possible
- **Uncertainty disclosure**: Clearly mark speculative or unverified information

### Domain Expertise
- **Financial knowledge**: Must demonstrate understanding of financial markets
- **Technical competence**: Must show proficiency in Python and data science
- **Regulatory awareness**: Must acknowledge relevant financial regulations
- **Industry standards**: Must reference established best practices

### Context Awareness
- **Project scope**: Responses must stay within SMVM objectives
- **Technical constraints**: Must respect Python 3.12.x and architectural decisions
- **Security boundaries**: Must not compromise security or data governance
- **Operational limits**: Must acknowledge system capabilities and limitations

## Refusal Protocols

### Prohibited Actions
- **Code execution**: Never execute or suggest execution of unverified code
- **Data manipulation**: Never modify production data without explicit approval
- **Security bypass**: Never suggest circumventing security controls
- **Regulatory violation**: Never recommend actions that violate regulations

### Refusal Triggers
- **Malicious intent**: Requests showing clear intent for harmful activities
- **Security compromise**: Requests that could compromise system security
- **Regulatory violation**: Requests that conflict with financial regulations
- **Ethical violation**: Requests that raise ethical or legal concerns

### Refusal Response Format
```
I cannot assist with this request because: [specific reason]

Alternative approaches you might consider:
- [Safe alternative 1]
- [Safe alternative 2]

For more information, please refer to: [relevant documentation/policy]
```

## Python Discipline Requirements

### Code Quality Standards
- **PEP 8 compliance**: All code must follow Python style guidelines
- **Type hints**: Required for all function parameters and return values
- **Documentation**: Docstrings required for all public functions and classes
- **Error handling**: Comprehensive exception handling with specific error types

### Version Compatibility
- **Primary target**: Python 3.12.x
- **Fallback support**: Python 3.11.13
- **Blocked versions**: Python ≥3.13.x
- **Deprecation handling**: Clear migration paths for deprecated features

### Dependency Management
- **Pinned versions**: Major versions pinned in `requirements.txt`
- **Lockfile usage**: Exact versions specified in `requirements.lock`
- **Security updates**: Regular security scanning and updates
- **Compatibility testing**: Test against all supported Python versions

## Operational Protocols

### Logging Requirements
- **Structured logging**: All interactions logged with correlation IDs
- **Audit trail**: Complete record of all LLM interactions
- **Error tracking**: Detailed error logging with context
- **Performance monitoring**: Response times and token usage tracked

### Monitoring and Alerting
- **Usage monitoring**: Track token consumption and rate limits
- **Quality monitoring**: Monitor response accuracy and helpfulness
- **Security monitoring**: Alert on suspicious patterns or violations
- **Performance monitoring**: Track response times and system load

### Quality Assurance
- **Response validation**: Automated checks for factual accuracy
- **Code validation**: Syntax and security checks for generated code
- **Compliance validation**: Regulatory compliance verification
- **User feedback**: Mechanisms for reporting issues and improvements

## Violation Handling

### Warning System
- **First violation**: Warning issued with explanation
- **Second violation**: Temporary suspension (1 hour)
- **Third violation**: Temporary suspension (24 hours)
- **Repeated violations**: Permanent suspension review

### Escalation Procedures
- **Security violations**: Immediate suspension and security team notification
- **Regulatory violations**: Legal team notification and compliance review
- **System violations**: Engineering team notification and system review
- **Quality violations**: Quality assurance team review and remediation

### Recovery Procedures
- **Self-service recovery**: Clear instructions for resolving violations
- **Appeals process**: Formal process for disputing violations
- **Rehabilitation**: Required training or verification for reinstatement
- **Monitoring period**: Extended monitoring after reinstatement

## Implementation Requirements

### Technical Controls
- **Input validation**: All inputs validated against guardrails
- **Output filtering**: All outputs checked for compliance
- **Context preservation**: Maintain conversation context within limits
- **Fallback mechanisms**: Graceful degradation when limits exceeded

### Integration Points
- **Authentication**: Integration with SMVM authentication system
- **Authorization**: Role-based access control for different capabilities
- **Audit logging**: Integration with centralized audit system
- **Monitoring**: Integration with observability stack

### Configuration Management
- **Environment-specific**: Different limits for development/production
- **Dynamic adjustment**: Ability to adjust limits based on load
- **Version control**: All guardrail changes version controlled
- **Documentation**: Changes documented with rationale

## Review and Updates

### Regular Review
- **Monthly review**: Usage patterns and effectiveness assessment
- **Quarterly audit**: Comprehensive policy compliance review
- **Annual revision**: Major policy updates based on industry changes
- **Incident-driven**: Immediate review following any violations

### Update Process
- **Change proposal**: Documented rationale for any changes
- **Impact assessment**: Analysis of effects on users and system
- **Testing**: Validation of changes in non-production environment
- **Gradual rollout**: Phased implementation with monitoring

### Metrics and KPIs
- **Violation rate**: Track rate of guardrail violations
- **User satisfaction**: Monitor user feedback on LLM interactions
- **Response quality**: Measure accuracy and helpfulness of responses
- **System performance**: Track impact on system resources and response times

## Emergency Procedures

### System Overload
- **Automatic throttling**: Reduce limits during high load periods
- **Queue management**: Implement request queuing for overload protection
- **User notification**: Inform users of temporary limit reductions
- **Recovery monitoring**: Monitor system recovery after overload

### Security Incidents
- **Immediate suspension**: Suspend LLM access during security incidents
- **Investigation**: Forensic analysis of incident-related interactions
- **Remediation**: Implement fixes for identified vulnerabilities
- **Communication**: Transparent communication with affected users

### Regulatory Changes
- **Immediate assessment**: Evaluate impact of regulatory changes
- **Policy updates**: Rapid policy updates to maintain compliance
- **User communication**: Notify users of policy changes
- **Training updates**: Update training materials as needed

---

*Policy Version: 1.0 | Effective Date: 2024-12-XX | Review Date: 2025-06-XX*

*This policy applies to all LLM interactions within the SMVM ecosystem.*
