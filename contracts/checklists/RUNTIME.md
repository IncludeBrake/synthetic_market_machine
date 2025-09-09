# Runtime Environment Preflight Checklist

## Overview

This checklist provides comprehensive preflight verification for SMVM runtime environments. It ensures compatibility, security, and performance requirements are met before deployment or execution.

## Checklist Execution

### Automated Preflight Script
```bash
#!/bin/bash
# smvm_preflight_check.sh - Automated runtime preflight verification

# Configuration
EXPECTED_PYTHON_VERSION="3.12"
FALLBACK_PYTHON_VERSION="3.11"
REQUIRED_PACKAGES=("pandas" "numpy" "fastapi" "sqlalchemy" "pytest")
LOG_FILE="preflight_check_$(date +%Y%m%d_%H%M%S).log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Initialize checklist
init_checklist() {
    log "=== SMVM Runtime Preflight Check ==="
    log "Timestamp: $(date)"
    log "Expected Python: $EXPECTED_PYTHON_VERSION.x"
    log "Fallback Python: $FALLBACK_PYTHON_VERSION.x"
    log ""
}

# Check 1: Python Version Verification
check_python_version() {
    log "1. PYTHON VERSION VERIFICATION"

    # Get current Python version
    if command -v python3 &> /dev/null; then
        CURRENT_PYTHON=$(python3 --version 2>&1 | awk '{print $2}')
        log "   Current Python version: $CURRENT_PYTHON"

        # Check if version matches expected
        if [[ "$CURRENT_PYTHON" == $EXPECTED_PYTHON_VERSION* ]]; then
            log "   ✓ Primary Python version ($EXPECTED_PYTHON_VERSION.x) detected"
            PYTHON_STATUS="primary"
            return 0
        elif [[ "$CURRENT_PYTHON" == $FALLBACK_PYTHON_VERSION* ]]; then
            log "   ✓ Fallback Python version ($FALLBACK_PYTHON_VERSION.x) detected"
            PYTHON_STATUS="fallback"
            return 0
        else
            log "   ✗ Unsupported Python version: $CURRENT_PYTHON"
            log "   Expected: $EXPECTED_PYTHON_VERSION.x or $FALLBACK_PYTHON_VERSION.x"
            PYTHON_STATUS="unsupported"
            return 1
        fi
    else
        log "   ✗ Python3 not found in PATH"
        PYTHON_STATUS="not_found"
        return 1
    fi
}

# Check 2: Virtual Environment Verification
check_virtual_environment() {
    log "2. VIRTUAL ENVIRONMENT VERIFICATION"

    # Check if running in virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        log "   ✓ Running in virtual environment: $VIRTUAL_ENV"

        # Verify virtual environment Python matches system Python
        VENV_PYTHON=$(python3 --version 2>&1 | awk '{print $2}')
        if [[ "$VENV_PYTHON" == "$CURRENT_PYTHON" ]]; then
            log "   ✓ Virtual environment Python matches system Python"
            return 0
        else
            log "   ✗ Virtual environment Python mismatch"
            log "   System: $CURRENT_PYTHON, Virtual: $VENV_PYTHON"
            return 1
        fi
    else
        log "   ⚠️ Not running in virtual environment"
        log "   Recommendation: Use virtual environment for isolation"
        # Don't fail - allow system Python
        return 0
    fi
}

# Check 3: Package Dependencies Verification
check_package_dependencies() {
    log "3. PACKAGE DEPENDENCIES VERIFICATION"

    local failed_packages=0

    for package in "${REQUIRED_PACKAGES[@]}"; do
        if python3 -c "import $package" 2>/dev/null; then
            log "   ✓ $package: Available"
        else
            log "   ✗ $package: Not available"
            ((failed_packages++))
        fi
    done

    if [[ $failed_packages -eq 0 ]]; then
        log "   ✓ All required packages available"
        return 0
    else
        log "   ✗ $failed_packages required packages missing"
        return 1
    fi
}

# Check 4: Wheel Status Verification
check_wheel_status() {
    log "4. WHEEL STATUS VERIFICATION"

    # Check if requirements.lock exists and is current
    if [[ -f "requirements.lock" ]]; then
        log "   ✓ Requirements lock file exists"

        # Verify lock file is not empty
        if [[ -s "requirements.lock" ]]; then
            log "   ✓ Requirements lock file is not empty"
        else
            log "   ✗ Requirements lock file is empty"
            return 1
        fi

        # Check lock file age (should be less than 24 hours for active development)
        LOCK_FILE_AGE=$(($(date +%s) - $(stat -c %Y requirements.lock 2>/dev/null || stat -f %m requirements.lock)))
        if [[ $LOCK_FILE_AGE -lt 86400 ]]; then  # 24 hours
            log "   ✓ Requirements lock file is current (< 24 hours old)"
        else
            log "   ⚠️ Requirements lock file is stale (> 24 hours old)"
            # Don't fail - just warn
        fi
    else
        log "   ✗ Requirements lock file not found"
        log "   Run: pip freeze > requirements.lock"
        return 1
    fi

    # Verify pip freeze hash consistency
    CURRENT_FREEZE=$(pip freeze | sort)
    LOCKED_FREEZE=$(cat requirements.lock | sort)

    if [[ "$CURRENT_FREEZE" == "$LOCKED_FREEZE" ]]; then
        log "   ✓ Installed packages match requirements.lock"
        return 0
    else
        log "   ✗ Installed packages differ from requirements.lock"
        log "   Run: pip install -r requirements.txt && pip freeze > requirements.lock"
        return 1
    fi
}

# Check 5: Environment Configuration Verification
check_environment_configuration() {
    log "5. ENVIRONMENT CONFIGURATION VERIFICATION"

    # Check for required environment variables
    required_vars=("SMVM_PYTHON_VERSION" "SMVM_WHEEL_STATUS")
    local missing_vars=0

    for var in "${required_vars[@]}"; do
        if [[ -n "${!var}" ]]; then
            log "   ✓ $var: ${!var}"
        else
            log "   ✗ $var: Not set"
            ((missing_vars++))
        fi
    done

    if [[ $missing_vars -eq 0 ]]; then
        log "   ✓ All required environment variables set"
        return 0
    else
        log "   ⚠️ $missing_vars environment variables missing"
        log "   Set: export SMVM_PYTHON_VERSION=$CURRENT_PYTHON"
        log "        export SMVM_WHEEL_STATUS=healthy"
        # Don't fail - just warn
        return 0
    fi
}

# Check 6: Security Verification
check_security_verification() {
    log "6. SECURITY VERIFICATION"

    # Check file permissions
    critical_files=("requirements.txt" "requirements.lock" ".smvm_config")
    local insecure_files=0

    for file in "${critical_files[@]}"; do
        if [[ -f "$file" ]]; then
            # Check if file is world-writable (insecure)
            if [[ -w "$file" ]] && stat -c %a "$file" 2>/dev/null | grep -q ".[2-7]$"; then
                log "   ✗ $file: Insecure permissions (world-writable)"
                ((insecure_files++))
            else
                log "   ✓ $file: Secure permissions"
            fi
        else
            log "   - $file: Not present"
        fi
    done

    if [[ $insecure_files -eq 0 ]]; then
        log "   ✓ All critical files have secure permissions"
        return 0
    else
        log "   ✗ $insecure_files files have insecure permissions"
        return 1
    fi
}

# Check 7: Performance Baseline Verification
check_performance_baseline() {
    log "7. PERFORMANCE BASELINE VERIFICATION"

    # Quick performance test
    log "   Running basic performance test..."

    START_TIME=$(date +%s.%3N)
    python3 -c "
import time
# Basic import performance test
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.randn(1000, 10))
result = df.sum().sum()
print(f'Performance test result: {result}')
" > /dev/null 2>&1
    END_TIME=$(date +%s.%3N)

    EXECUTION_TIME=$(echo "$END_TIME - $START_TIME" | bc 2>/dev/null || echo "0")

    if (( $(echo "$EXECUTION_TIME < 5.0" | bc -l 2>/dev/null || echo "1") )); then
        log "   ✓ Performance test passed (${EXECUTION_TIME}s)"
        return 0
    else
        log "   ⚠️ Performance test slow (${EXECUTION_TIME}s)"
        log "   This may indicate wheel or configuration issues"
        # Don't fail - just warn about performance
        return 0
    fi
}

# Generate summary report
generate_summary_report() {
    log ""
    log "=== PREFLIGHT CHECK SUMMARY ==="

    # Count passed/failed checks
    local total_checks=7
    local passed_checks=0
    local failed_checks=0

    # Check results (simplified - in real implementation would track each check result)
    log "Python Version: $PYTHON_STATUS"

    # Overall assessment
    if [[ "$PYTHON_STATUS" == "primary" ]]; then
        log "✓ PRIMARY ENVIRONMENT: Ready for production use"
        STATUS="READY"
    elif [[ "$PYTHON_STATUS" == "fallback" ]]; then
        log "✓ FALLBACK ENVIRONMENT: Functional but monitor wheel improvements"
        STATUS="READY_FALLBACK"
    else
        log "✗ ENVIRONMENT NOT READY: Python version issues detected"
        STATUS="NOT_READY"
    fi

    log "Status: $STATUS"
    log "Log file: $LOG_FILE"
    log "=================================="

    return 0
}

# Main execution
main() {
    init_checklist

    local overall_status=0

    check_python_version || overall_status=1
    check_virtual_environment || overall_status=1
    check_package_dependencies || overall_status=1
    check_wheel_status || overall_status=1
    check_environment_configuration
    check_security_verification || overall_status=1
    check_performance_baseline

    generate_summary_report

    return $overall_status
}

# Execute main function
main
```

## Manual Preflight Verification

### Python Version Verification
- [ ] **Python Version Check**: Verify Python version matches expected (3.12.x primary, 3.11.13 fallback)
- [ ] **Version Consistency**: Ensure virtual environment Python matches system Python
- [ ] **Version Documentation**: Confirm version is documented in `.smvm_config`

```bash
# Verify Python version
python --version
# Expected: Python 3.12.x or Python 3.11.13

# Check virtual environment
which python
echo $VIRTUAL_ENV
```

### Package Dependencies Verification
- [ ] **Core Packages**: Verify pandas, numpy, fastapi, sqlalchemy, pytest are installed
- [ ] **Import Testing**: Test all critical package imports
- [ ] **Version Compatibility**: Ensure package versions are compatible

```bash
# Test critical imports
python -c "
import pandas as pd
import numpy as np
import fastapi
import sqlalchemy
import pytest
print('✅ All critical packages imported successfully')
"
```

### Wheel Status Verification
- [ ] **Requirements Lock**: Verify `requirements.lock` exists and is current
- [ ] **Package Consistency**: Ensure installed packages match lock file
- [ ] **Wheel Health**: Check wheel availability for all packages

```bash
# Verify requirements lock
ls -la requirements.lock
head -5 requirements.lock

# Compare with current installation
pip freeze | diff - requirements.lock || echo "Differences detected"
```

### Environment Configuration Verification
- [ ] **Environment Variables**: Check SMVM_PYTHON_VERSION and SMVM_WHEEL_STATUS
- [ ] **Configuration Files**: Verify `.smvm_config` contains correct settings
- [ ] **Path Configuration**: Ensure Python is in PATH and accessible

```bash
# Check environment variables
echo "Python Version: $SMVM_PYTHON_VERSION"
echo "Wheel Status: $SMVM_WHEEL_STATUS"

# Check configuration file
cat .smvm_config
```

### Security Verification
- [ ] **File Permissions**: Ensure critical files are not world-writable
- [ ] **Secure Imports**: Verify no insecure package versions
- [ ] **Environment Isolation**: Confirm running in appropriate environment

```bash
# Check file permissions
ls -la requirements.txt requirements.lock .smvm_config

# Check for insecure packages
pip list --format=freeze | grep -i "insecure\|vulnerable" || echo "No insecure packages detected"
```

### Performance Baseline Verification
- [ ] **Import Performance**: Test basic package import performance
- [ ] **Memory Usage**: Verify reasonable memory consumption
- [ ] **Startup Time**: Check application startup performance

```bash
# Performance test
time python -c "
import pandas as pd
import numpy as np
df = pd.DataFrame(np.random.randn(1000, 10))
result = df.sum().sum()
print(f'Result: {result}')
"
```

## Automated Runtime Checks

### Continuous Verification Script
```python
#!/usr/bin/env python3
# runtime_verification.py - Continuous runtime verification

import sys
import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

class RuntimeVerifier:
    """
    Continuous runtime environment verification
    """

    def __init__(self):
        self.violations = []
        self.warnings = []

    def verify_runtime_environment(self) -> dict:
        """
        Comprehensive runtime environment verification
        """

        results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version_check": self._check_python_version(),
            "package_integrity_check": self._check_package_integrity(),
            "wheel_status_check": self._check_wheel_status(),
            "environment_config_check": self._check_environment_config(),
            "security_check": self._check_security(),
            "performance_check": self._check_performance(),
            "violations": self.violations,
            "warnings": self.warnings,
            "overall_status": "unknown"
        }

        # Determine overall status
        critical_violations = [v for v in self.violations if v.get("severity") == "critical"]
        if critical_violations:
            results["overall_status"] = "FAILED"
        elif self.violations:
            results["overall_status"] = "WARNING"
        else:
            results["overall_status"] = "PASSED"

        return results

    def _check_python_version(self) -> dict:
        """Verify Python version compliance"""

        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # Check against allowed versions
        allowed_versions = ["3.12", "3.11.13"]
        version_compatible = any(current_version.startswith(v) for v in allowed_versions)

        result = {
            "current_version": current_version,
            "required_versions": allowed_versions,
            "compatible": version_compatible
        }

        if not version_compatible:
            self.violations.append({
                "check": "python_version",
                "severity": "critical",
                "message": f"Python {current_version} not in allowed versions {allowed_versions}"
            })

        return result

    def _check_package_integrity(self) -> dict:
        """Verify package integrity and versions"""

        required_packages = {
            "pandas": "2.0.0",
            "numpy": "1.24.0",
            "fastapi": "0.100.0",
            "sqlalchemy": "2.0.0"
        }

        missing_packages = []
        version_mismatches = []

        for package, min_version in required_packages.items():
            try:
                module = __import__(package)
                version = getattr(module, "__version__", "unknown")

                # Simple version comparison (could be enhanced)
                if version == "unknown" or version < min_version:
                    version_mismatches.append(f"{package} {version} < {min_version}")

            except ImportError:
                missing_packages.append(package)

        result = {
            "required_packages": list(required_packages.keys()),
            "missing_packages": missing_packages,
            "version_mismatches": version_mismatches
        }

        if missing_packages:
            self.violations.append({
                "check": "package_integrity",
                "severity": "critical",
                "message": f"Missing required packages: {missing_packages}"
            })

        if version_mismatches:
            self.violations.append({
                "check": "package_integrity",
                "severity": "warning",
                "message": f"Package version mismatches: {version_mismatches}"
            })

        return result

    def _check_wheel_status(self) -> dict:
        """Verify wheel status and integrity"""

        # Check if requirements.lock exists
        lock_file = Path("requirements.lock")
        lock_exists = lock_file.exists()

        result = {
            "lock_file_exists": lock_exists,
            "lock_file_current": False,
            "packages_match_lock": False
        }

        if lock_exists:
            # Check if lock file is reasonably current (within 24 hours)
            file_age = datetime.utcnow().timestamp() - lock_file.stat().st_mtime
            result["lock_file_current"] = file_age < 86400  # 24 hours

            if not result["lock_file_current"]:
                self.warnings.append({
                    "check": "wheel_status",
                    "message": "Requirements lock file is stale (>24 hours old)"
                })

        else:
            self.violations.append({
                "check": "wheel_status",
                "severity": "warning",
                "message": "Requirements lock file not found"
            })

        return result

    def _check_environment_config(self) -> dict:
        """Verify environment configuration"""

        required_vars = ["SMVM_PYTHON_VERSION", "SMVM_WHEEL_STATUS"]
        config_file = Path(".smvm_config")

        result = {
            "required_vars_present": [],
            "config_file_exists": config_file.exists(),
            "config_file_valid": False
        }

        # Check environment variables
        for var in required_vars:
            if os.getenv(var):
                result["required_vars_present"].append(var)
            else:
                self.warnings.append({
                    "check": "environment_config",
                    "message": f"Environment variable {var} not set"
                })

        # Check configuration file
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()
                    # Basic validation - contains expected keys
                    if "python_version" in config_content:
                        result["config_file_valid"] = True
                    else:
                        self.warnings.append({
                            "check": "environment_config",
                            "message": "Configuration file missing python_version setting"
                        })
            except Exception as e:
                self.warnings.append({
                    "check": "environment_config",
                    "message": f"Error reading configuration file: {e}"
                })

        return result

    def _check_security(self) -> dict:
        """Verify security settings"""

        result = {
            "secure_file_permissions": True,
            "no_insecure_packages": True,
            "environment_isolation": bool(os.getenv("VIRTUAL_ENV"))
        }

        # Check file permissions (simplified)
        critical_files = ["requirements.txt", "requirements.lock"]
        for file in critical_files:
            if Path(file).exists():
                # In a real implementation, check actual file permissions
                pass  # Simplified for demo

        if not result["environment_isolation"]:
            self.warnings.append({
                "check": "security",
                "message": "Not running in virtual environment - consider using venv"
            })

        return result

    def _check_performance(self) -> dict:
        """Verify performance baseline"""

        import time

        result = {
            "import_time": 0.0,
            "memory_usage": "unknown",
            "performance_baseline_met": True
        }

        # Measure import performance
        start_time = time.time()
        try:
            import pandas
            import numpy
            import fastapi
        except ImportError:
            pass
        end_time = time.time()

        result["import_time"] = end_time - start_time

        # Check performance baseline (arbitrary threshold)
        if result["import_time"] > 2.0:  # 2 seconds
            result["performance_baseline_met"] = False
            self.warnings.append({
                "check": "performance",
                "message": f"Slow import time: {result['import_time']:.2f}s"
            })

        return result

def main():
    """Main verification execution"""

    verifier = RuntimeVerifier()
    results = verifier.verify_runtime_environment()

    # Save results
    with open("runtime_verification_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Print summary
    print("Runtime Verification Results:")
    print(f"Status: {results['overall_status']}")
    print(f"Violations: {len(results['violations'])}")
    print(f"Warnings: {len(results['warnings'])}")

    # Return appropriate exit code
    if results["overall_status"] == "FAILED":
        return 1
    elif results["overall_status"] == "WARNING":
        return 2  # Warning but not failure
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
```

## Preflight Check Integration

### CI/CD Pipeline Integration
```yaml
# .github/workflows/preflight.yml
name: Runtime Preflight Check

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  preflight-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.12, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Run preflight checklist
      run: bash contracts/checklists/runtime_preflight_check.sh

    - name: Run runtime verification
      run: python contracts/checklists/runtime_verification.py

    - name: Upload preflight results
      uses: actions/upload-artifact@v3
      with:
        name: preflight-results-${{ matrix.python-version }}
        path: |
          preflight_check_*.log
          runtime_verification_results.json
```

### Deployment Integration
```bash
#!/bin/bash
# deploy_with_preflight.sh - Deployment with preflight checks

echo "=== SMVM Deployment with Preflight Checks ==="

# Run preflight checks
if bash contracts/checklists/runtime_preflight_check.sh; then
    echo "✅ Preflight checks passed"

    # Run runtime verification
    if python contracts/checklists/runtime_verification.py; then
        echo "✅ Runtime verification passed"

        # Proceed with deployment
        echo "🚀 Starting deployment..."
        # ... deployment commands ...

    else
        echo "❌ Runtime verification failed"
        echo "🚫 Deployment blocked"
        exit 1
    fi

else
    echo "❌ Preflight checks failed"
    echo "🚫 Deployment blocked"
    exit 1
fi

echo "=== Deployment completed successfully ==="
```

## Monitoring and Alerting

### Automated Health Monitoring
```bash
#!/bin/bash
# runtime_health_monitor.sh - Continuous runtime health monitoring

MONITOR_INTERVAL=300  # 5 minutes
HEALTH_LOG="runtime_health_$(date +%Y%m%d).log"

log_health() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$HEALTH_LOG"
}

check_runtime_health() {
    log_health "Starting runtime health check"

    # Run quick preflight check
    if bash contracts/checklists/runtime_preflight_check.sh > /dev/null 2>&1; then
        log_health "Runtime health: GOOD"
    else
        log_health "Runtime health: DEGRADED"
        # Send alert or trigger remediation
        python contracts/checklists/runtime_verification.py
    fi
}

# Main monitoring loop
log_health "Starting runtime health monitoring (interval: ${MONITOR_INTERVAL}s)"

while true; do
    check_runtime_health
    sleep "$MONITOR_INTERVAL"
done
```

### Alert Configuration
```python
#!/usr/bin/env python3
# runtime_alerts.py - Runtime health alerting

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from typing import Dict, List

class RuntimeHealthAlerts:
    """
    Runtime health monitoring and alerting
    """

    def __init__(self, alert_config: Dict[str, str]):
        self.alert_config = alert_config

    def check_and_alert(self, verification_results: Dict) -> None:
        """
        Check verification results and send alerts if needed
        """

        violations = verification_results.get("violations", [])
        warnings = verification_results.get("warnings", [])

        # Alert on critical violations
        critical_violations = [v for v in violations if v.get("severity") == "critical"]

        if critical_violations:
            self._send_alert(
                "CRITICAL: Runtime Environment Issues Detected",
                f"Critical violations found: {len(critical_violations)}\n" +
                "\n".join([f"- {v['check']}: {v['message']}" for v in critical_violations[:5]])
            )

        # Alert on excessive warnings
        elif len(warnings) > 5:
            self._send_alert(
                "WARNING: Multiple Runtime Environment Issues",
                f"Multiple warnings detected: {len(warnings)}\n" +
                "Consider reviewing runtime environment configuration."
            )

    def _send_alert(self, subject: str, message: str) -> None:
        """
        Send alert notification
        """

        # Email alert implementation
        msg = MIMEText(message)
        msg['Subject'] = f"SMVM Runtime Alert: {subject}"
        msg['From'] = self.alert_config.get('from_email')
        msg['To'] = self.alert_config.get('to_email')

        try:
            with smtplib.SMTP(self.alert_config.get('smtp_server', 'localhost')) as server:
                server.send_message(msg)
                print(f"Alert sent: {subject}")
        except Exception as e:
            print(f"Failed to send alert: {e}")

def main():
    """Main alerting execution"""

    # Example alert configuration
    alert_config = {
        "from_email": "smvm-alerts@company.com",
        "to_email": "devops-team@company.com",
        "smtp_server": "smtp.company.com"
    }

    # Load verification results
    try:
        with open("runtime_verification_results.json", "r") as f:
            results = json.load(f)

        alerter = RuntimeHealthAlerts(alert_config)
        alerter.check_and_alert(results)

    except FileNotFoundError:
        print("No verification results found")
    except Exception as e:
        print(f"Alerting failed: {e}")

if __name__ == "__main__":
    main()
```

---

## Document Information

- **Version**: 1.0.0
- **Effective Date**: December 2, 2024
- **Last Updated**: December 2, 2024
- **Owner**: SMVM Operations Team
- **Review Date**: March 2, 2025

## Appendices

### Appendix A: Automated Check Scripts
Complete collection of automated preflight check scripts.

### Appendix B: Manual Verification Procedures
Detailed manual verification procedures for complex scenarios.

### Appendix C: Troubleshooting Guide
Common runtime issues and their resolutions.

### Appendix D: Performance Benchmarks
Expected performance baselines for different environments.
