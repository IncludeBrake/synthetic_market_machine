# Python Interpreter Discipline Policy

## Overview

This policy establishes strict discipline for Python interpreter management within the Synthetic Market Validation Module (SMVM) ecosystem. The goal is to ensure reproducible, reliable execution while maintaining compatibility and preventing unintended version drift.

## Core Principles

### Primary Interpreter
- **Python 3.12.x**: The primary and preferred interpreter version
- **Justification**: Latest stable release with optimal performance and security features
- **Support Period**: Until Python 3.13.x reaches GA stability (approximately 6 months)

### Fallback Interpreter
- **Python 3.11.13**: The designated fallback interpreter
- **Justification**: Stable LTS-equivalent version with proven compatibility
- **Purpose**: Ensures continuity when 3.12.x wheels are unavailable

### Prohibited Versions
- **Python ≥3.13**: Blocked until thoroughly tested and approved
- **Python <3.11**: Unsupported due to security and feature gaps
- **Development/RC Versions**: Strictly prohibited in production

## Version Management Rules

### Interpreter Changes
**Prohibited Without Approval:**
- Any change to Python interpreter version
- Modification of version constraints in CI/CD pipelines
- Updates to fallback interpreter versions

**Required Approval Process:**
1. **Technical Review**: Engineering team evaluates compatibility impact
2. **CI Validation**: All tests pass on new interpreter version
3. **Integration Testing**: TractionBuild integration verified
4. **Documentation Update**: This policy document updated
5. **CAB Approval**: Change Advisory Board approval obtained

### Version Drift Prevention

#### Runtime Checks
- **Entry Point Validation**: Every execution validates interpreter version
- **Dependency Consistency**: `pip freeze` hash must match expected value
- **Wheel Availability**: Required wheels must be available for current interpreter

#### CI/CD Enforcement
- **Matrix Validation**: CI pipeline tests all supported versions
- **Failure Blocking**: Interpreter drift causes immediate build failure
- **Version Pinning**: All dependencies pinned to specific versions

## Implementation Guidelines

### Development Environment
```bash
# Create virtual environment with primary interpreter
python3.12 -m venv .venv

# Activate and verify
source .venv/bin/activate
python --version  # Must be 3.12.x

# Install dependencies
pip install -r requirements.txt

# Verify wheel availability
python -c "import smvm; print('All wheels available')"
```

### Production Deployment
```bash
# Pre-deployment checks
python ops/scripts/version_check.py

# Fallback procedure (if primary fails)
python3.11.13 -m venv .venv_fallback
source .venv_fallback/bin/activate

# Log wheel status
echo "wheel_status: fallback_to_3.11.13" >> deployment.log
```

### Wheel Management

#### Primary Interpreter Wheels
- **Build Priority**: All dependencies must have Python 3.12 wheels
- **Fallback Strategy**: Automatic fallback to 3.11.13 if wheels unavailable
- **Monitoring**: Continuous monitoring of wheel availability

#### Fallback Interpreter Wheels
- **Compatibility Guarantee**: All dependencies must support 3.11.13
- **Performance Baseline**: Establish performance benchmarks for fallback
- **Transition Planning**: Regular assessment of 3.12 wheel maturity

## Operational Procedures

### Version Verification
```python
# Runtime version check
import sys
from smvm.overwatch.version_check import VersionChecker

checker = VersionChecker()
result = checker.verify_environment()

if not result["version_compatible"]:
    print(f"ERROR: Python {result['current_version']} not supported")
    print(f"Required: {result['required_version']}")
    sys.exit(1)
```

### Wheel Health Assessment
```bash
# Check wheel availability
python ops/runbooks/wheel_health.py

# Output example:
# Python 3.12.0: All wheels available ✓
# smvm package: Compatible ✓
# Critical dependencies: Available ✓
```

### Emergency Fallback
```bash
# Automated fallback procedure
if [ "$(python ops/scripts/check_wheels.py)" = "failed" ]; then
    echo "Primary interpreter wheels unavailable, initiating fallback"

    # Create fallback environment
    python3.11.13 -m venv .venv_fallback

    # Update configuration
    sed -i 's/python_version: "3.12.x"/python_version: "3.11.13"/' config.yaml

    # Log incident
    echo "$(date): Interpreter fallback to 3.11.13" >> incident.log
fi
```

## Monitoring and Alerting

### Runtime Monitoring
- **Version Drift Detection**: Log warnings when version doesn't match expected
- **Wheel Status Tracking**: Monitor wheel availability across environments
- **Performance Impact**: Track performance differences between versions

### CI/CD Monitoring
- **Build Failure Alerts**: Immediate notification of interpreter-related failures
- **Version Compatibility**: Regular validation of version matrix
- **Dependency Updates**: Automated testing of dependency compatibility

### Alert Thresholds
- **Critical**: Interpreter version mismatch in production
- **Warning**: Wheel unavailability for primary interpreter
- **Info**: Successful fallback to secondary interpreter

## Compliance and Enforcement

### Automated Enforcement
```yaml
# CI/CD Pipeline Rules
version_check:
  - name: "Verify Python Version"
    run: |
      python_version=$(python --version | cut -d' ' -f2)
      if [[ "$python_version" != 3.12* ]] && [[ "$python_version" != 3.11.13 ]]; then
        echo "ERROR: Unsupported Python version: $python_version"
        exit 1
      fi

wheel_check:
  - name: "Verify Wheel Availability"
    run: |
      if ! python -c "import smvm"; then
        echo "ERROR: SMVM wheels not available"
        exit 1
      fi
```

### Manual Verification
```bash
# Pre-deployment checklist
checklist_version_compliance() {
    echo "=== Python Interpreter Compliance Check ==="

    # Check current version
    current=$(python --version 2>&1 | awk '{print $2}')
    echo "Current Python version: $current"

    # Verify compatibility
    case $current in
        3.12.*)
            echo "✓ Primary interpreter (3.12.x)"
            ;;
        3.11.13)
            echo "✓ Fallback interpreter (3.11.13)"
            ;;
        *)
            echo "✗ Unsupported interpreter version"
            return 1
            ;;
    esac

    # Check wheel availability
    if python -c "import smvm" 2>/dev/null; then
        echo "✓ All wheels available"
    else
        echo "✗ Missing wheels - fallback required"
        return 1
    fi

    echo "=== Compliance check passed ==="
    return 0
}
```

## Exception Handling

### Emergency Exceptions
**Approved Scenarios:**
- **Security Vulnerabilities**: Immediate upgrade to patched interpreter
- **Critical Compatibility**: Blocking issues preventing operation
- **Vendor Requirements**: Third-party system compatibility mandates

**Exception Process:**
1. **Incident Declaration**: Security/incident response team declares emergency
2. **CAB Emergency Meeting**: Change Advisory Board convenes within 2 hours
3. **Temporary Approval**: CAB grants temporary exception (max 72 hours)
4. **Root Cause Analysis**: Engineering team investigates and proposes permanent solution
5. **CAB Final Review**: Full approval process for permanent change

### Gradual Migration
**Version Upgrade Process:**
1. **Testing Phase**: New version tested in staging environment (2 weeks)
2. **Gradual Rollout**: 10% of workloads migrated to new version
3. **Monitoring Period**: Performance and compatibility monitoring (1 week)
4. **Full Migration**: Complete rollout if no issues detected
5. **Rollback Plan**: Ability to rollback within 1 hour if issues arise

## Audit and Compliance

### Audit Trail
- **Version Changes**: All interpreter changes logged with justification
- **Fallback Events**: Automatic logging of fallback activations
- **Compliance Checks**: Regular audits of version compliance
- **Incident Reports**: Documentation of any version-related incidents

### Compliance Metrics
- **Version Compliance Rate**: Percentage of deployments using approved interpreters
- **Fallback Frequency**: Rate of automatic fallback activations
- **Incident Response Time**: Time to resolve version-related issues
- **Wheel Availability**: Percentage of time all wheels are available

## Future Considerations

### Version Support Timeline
- **Python 3.13**: Target support date - 6 months after GA release
- **Python 3.14**: Planning begins 12 months before GA release
- **End-of-Life Planning**: 18 months advance notice for unsupported versions

### Technology Evolution
- **Performance Monitoring**: Track performance improvements with new versions
- **Security Assessment**: Evaluate security improvements in newer versions
- **Compatibility Testing**: Automated testing against multiple interpreter versions
- **Migration Automation**: Scripts and tools to facilitate version transitions

## Document Information

- **Version**: 1.0.0
- **Effective Date**: December 2, 2024
- **Review Date**: March 2, 2025
- **Last Updated**: December 2, 2024
- **Owner**: SMVM Platform Team
- **Approvers**: Technical Architecture Board, Change Advisory Board

## Appendices

### Appendix A: Supported Python Versions
Detailed list of all supported Python versions and their specific patch levels.

### Appendix B: Version Compatibility Matrix
Matrix showing compatibility between SMVM components and Python versions.

### Appendix C: Wheel Availability Checklist
Comprehensive checklist for verifying wheel availability across all dependencies.

### Appendix D: Emergency Fallback Procedures
Detailed step-by-step procedures for emergency interpreter fallback scenarios.

---

## Policy Compliance Checklist

**For Development Teams:**
- [ ] Use only approved Python versions (3.12.x primary, 3.11.13 fallback)
- [ ] Include version checks in all deployment scripts
- [ ] Test against both primary and fallback interpreters
- [ ] Document any interpreter-related issues immediately

**For CI/CD Pipelines:**
- [ ] Include version validation in all build steps
- [ ] Test against full version matrix before deployment
- [ ] Block deployments with unsupported interpreters
- [ ] Alert on wheel availability issues

**For Operations Teams:**
- [ ] Monitor interpreter versions in production
- [ ] Have fallback procedures ready for wheel issues
- [ ] Log all version-related events and incidents
- [ ] Regular compliance audits and reporting

**For Security Teams:**
- [ ] Monitor for unsupported interpreter usage
- [ ] Verify security patches are applied to approved versions
- [ ] Review interpreter changes for security implications
- [ ] Ensure secure fallback procedures are in place
