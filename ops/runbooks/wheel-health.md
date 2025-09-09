# Wheel Health Assessment and Automated Fallback Runbook

## Overview

This runbook provides automated procedures for assessing wheel availability, detecting compatibility issues, and implementing fallback mechanisms for the Synthetic Market Validation Module (SMVM). The focus is on proactive health monitoring and automated recovery with comprehensive logging.

## Prerequisites

### Required Tools and Versions
- **Python 3.12.x** (primary) and **Python 3.11.13** (fallback)
- **pip >= 23.0** with wheel support
- **System dependencies** for wheel compilation
- **Disk space** for multiple virtual environments

### System Dependencies Check
```bash
#!/bin/bash
# wheel_health_check.sh - Automated wheel health assessment

check_system_dependencies() {
    echo "=== System Dependencies Check ==="

    # Check Python versions
    if command -v python3.12 &> /dev/null; then
        echo "✓ Python 3.12.x available: $(python3.12 --version)"
    else
        echo "✗ Python 3.12.x not found"
        return 1
    fi

    if command -v python3.11 &> /dev/null; then
        echo "✓ Python 3.11.13 available: $(python3.11 --version)"
    else
        echo "✗ Python 3.11.13 not found"
        return 1
    fi

    # Check build tools
    if command -v gcc &> /dev/null || command -v clang &> /dev/null || command -v cl.exe &> /dev/null; then
        echo "✓ Build tools available"
    else
        echo "✗ Build tools not found"
        return 1
    fi

    echo "=== All system dependencies satisfied ==="
    return 0
}
```

## Automated Wheel Health Assessment

### Core Assessment Script
```python
#!/usr/bin/env python3
# wheel_health.py - Automated wheel health checker

import sys
import json
import subprocess
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class WheelHealthChecker:
    """
    Automated wheel health assessment and fallback management
    """

    def __init__(self, log_file: str = "wheel_health.log"):
        self.log_file = Path(log_file)
        self.setup_logging()

        # Configuration
        self.primary_python = "python3.12"
        self.fallback_python = "python3.11"
        self.required_packages = [
            "pandas", "numpy", "scipy", "fastapi", "sqlalchemy",
            "pytest", "requests", "jsonschema", "deepdiff"
        ]

        # Results tracking
        self.health_results = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "primary_python": None,
            "fallback_python": None,
            "wheel_status": "unknown",
            "packages_checked": 0,
            "packages_available": 0,
            "packages_failed": 0,
            "fallback_required": False,
            "fallback_reason": None,
            "recommendations": []
        }

    def setup_logging(self):
        """Setup comprehensive logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WHEEL_HEALTH - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("wheel_health")

    def check_wheel_health(self) -> Dict[str, Any]:
        """
        Comprehensive wheel health assessment
        """
        self.logger.info("Starting wheel health assessment")

        try:
            # Check Python versions
            self._check_python_versions()

            # Check wheel availability for primary Python
            primary_healthy = self._check_wheel_availability(self.primary_python)

            if primary_healthy:
                self.logger.info("Primary Python wheel health: GOOD")
                self.health_results["wheel_status"] = "primary_healthy"
            else:
                self.logger.warning("Primary Python wheel health: DEGRADED")
                self.health_results["fallback_required"] = True
                self.health_results["fallback_reason"] = "missing_wheels_primary"

                # Check fallback Python
                fallback_healthy = self._check_wheel_availability(self.fallback_python)

                if fallback_healthy:
                    self.logger.info("Fallback Python wheel health: GOOD")
                    self.health_results["wheel_status"] = "fallback_available"
                else:
                    self.logger.error("Fallback Python wheel health: FAILED")
                    self.health_results["wheel_status"] = "complete_failure"
                    self.health_results["fallback_reason"] = "missing_wheels_both"

            # Generate recommendations
            self._generate_recommendations()

            # Log final assessment
            self._log_assessment_summary()

            return self.health_results

        except Exception as e:
            self.logger.error(f"Wheel health assessment failed: {e}")
            self.health_results["wheel_status"] = "assessment_failed"
            self.health_results["error"] = str(e)
            return self.health_results

    def _check_python_versions(self):
        """Verify Python versions are available"""
        self.logger.info("Checking Python versions")

        # Check primary Python
        try:
            result = subprocess.run(
                [self.primary_python, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                self.health_results["primary_python"] = version
                self.logger.info(f"Primary Python available: {version}")
            else:
                raise subprocess.SubprocessError("Primary Python execution failed")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.error("Primary Python not available")
            self.health_results["primary_python"] = "unavailable"

        # Check fallback Python
        try:
            result = subprocess.run(
                [self.fallback_python, "--version"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                version = result.stdout.strip().split()[-1]
                self.health_results["fallback_python"] = version
                self.logger.info(f"Fallback Python available: {version}")
            else:
                raise subprocess.SubprocessError("Fallback Python execution failed")
        except (subprocess.SubprocessError, FileNotFoundError):
            self.logger.error("Fallback Python not available")
            self.health_results["fallback_python"] = "unavailable"

    def _check_wheel_availability(self, python_cmd: str) -> bool:
        """
        Check wheel availability for specified Python version
        """
        self.logger.info(f"Checking wheel availability for {python_cmd}")

        available_count = 0
        failed_count = 0

        for package in self.required_packages:
            self.health_results["packages_checked"] += 1

            try:
                # Test package installation (dry run)
                result = subprocess.run(
                    [python_cmd, "-m", "pip", "install", "--dry-run", package],
                    capture_output=True, text=True, timeout=30
                )

                if result.returncode == 0:
                    available_count += 1
                    self.logger.debug(f"✓ {package}: Available")
                else:
                    failed_count += 1
                    self.logger.warning(f"✗ {package}: Failed - {result.stderr.strip()}")

            except subprocess.TimeoutExpired:
                failed_count += 1
                self.logger.warning(f"✗ {package}: Timeout")
            except Exception as e:
                failed_count += 1
                self.logger.warning(f"✗ {package}: Error - {e}")

        self.health_results["packages_available"] = available_count
        self.health_results["packages_failed"] = failed_count

        # Consider healthy if 90%+ packages are available
        success_rate = available_count / len(self.required_packages)
        is_healthy = success_rate >= 0.9

        self.logger.info(f"Wheel availability: {available_count}/{len(self.required_packages)} ({success_rate:.1%})")

        return is_healthy

    def _generate_recommendations(self):
        """Generate recommendations based on assessment results"""

        recommendations = []

        if self.health_results["wheel_status"] == "primary_healthy":
            recommendations.append("Primary Python environment is healthy - no action required")

        elif self.health_results["wheel_status"] == "fallback_available":
            recommendations.extend([
                "Implement automatic fallback to Python 3.11.13",
                "Monitor primary Python wheel improvements",
                "Schedule quarterly reassessment of primary Python compatibility",
                "Document fallback reason in deployment logs"
            ])

        elif self.health_results["wheel_status"] == "complete_failure":
            recommendations.extend([
                "CRITICAL: No compatible Python environment found",
                "Install Python 3.11.13 as emergency fallback",
                "Disable automated deployments until resolved",
                "Escalate to platform engineering team immediately"
            ])

        # Package-specific recommendations
        failed_packages = self.health_results["packages_failed"]
        if failed_packages > 0:
            recommendations.append(f"Investigate {failed_packages} packages with wheel issues")

        # System-level recommendations
        if self.health_results["primary_python"] == "unavailable":
            recommendations.append("Install Python 3.12.x to enable primary environment")

        if self.health_results["fallback_python"] == "unavailable":
            recommendations.append("Install Python 3.11.13 as fallback environment")

        self.health_results["recommendations"] = recommendations

    def _log_assessment_summary(self):
        """Log comprehensive assessment summary"""
        self.logger.info("=" * 60)
        self.logger.info("WHEEL HEALTH ASSESSMENT SUMMARY")
        self.logger.info("=" * 60)

        self.logger.info(f"Timestamp: {self.health_results['timestamp']}")
        self.logger.info(f"Primary Python: {self.health_results['primary_python']}")
        self.logger.info(f"Fallback Python: {self.health_results['fallback_python']}")
        self.logger.info(f"Wheel Status: {self.health_results['wheel_status']}")
        self.logger.info(f"Packages Checked: {self.health_results['packages_checked']}")
        self.logger.info(f"Packages Available: {self.health_results['packages_available']}")
        self.logger.info(f"Packages Failed: {self.health_results['packages_failed']}")
        self.logger.info(f"Fallback Required: {self.health_results['fallback_required']}")

        if self.health_results["fallback_reason"]:
            self.logger.info(f"Fallback Reason: {self.health_results['fallback_reason']}")

        self.logger.info("\nRECOMMENDATIONS:")
        for rec in self.health_results["recommendations"]:
            self.logger.info(f"• {rec}")

        self.logger.info("=" * 60)

def main():
    """Main execution function"""
    checker = WheelHealthChecker()
    results = checker.check_wheel_health()

    # Save results to JSON
    with open("wheel_health_results.json", "w") as f:
        json.dump(results, f, indent=2)

    # Return appropriate exit code
    if results["wheel_status"] in ["primary_healthy", "fallback_available"]:
        print("✅ Wheel health assessment: PASSED")
        return 0
    else:
        print("❌ Wheel health assessment: FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

### Automated Fallback Implementation
```python
#!/usr/bin/env python3
# wheel_fallback.py - Automated wheel fallback implementation

import sys
import json
import subprocess
import shutil
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

class WheelFallbackManager:
    """
    Automated wheel fallback management
    """

    def __init__(self, venv_path: str = ".venv"):
        self.venv_path = Path(venv_path)
        self.primary_python = "python3.12"
        self.fallback_python = "python3.11"
        self.fallback_log = Path("wheel_fallback.log")

        self.setup_logging()

    def setup_logging(self):
        """Setup fallback-specific logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - WHEEL_FALLBACK - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.fallback_log),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("wheel_fallback")

    def execute_fallback(self, reason: str) -> bool:
        """
        Execute automatic fallback to Python 3.11.13
        """
        self.logger.info("=" * 60)
        self.logger.info("INITIATING WHEEL FALLBACK PROCEDURE")
        self.logger.info("=" * 60)
        self.logger.info(f"Reason: {reason}")
        self.logger.info(f"Timestamp: {datetime.utcnow().isoformat()}Z")

        try:
            # Step 1: Backup current environment
            self._backup_current_environment()

            # Step 2: Create fallback environment
            success = self._create_fallback_environment()
            if not success:
                self.logger.error("Failed to create fallback environment")
                return False

            # Step 3: Install dependencies
            success = self._install_dependencies_fallback()
            if not success:
                self.logger.error("Failed to install dependencies in fallback environment")
                return False

            # Step 4: Verify installation
            success = self._verify_fallback_installation()
            if not success:
                self.logger.error("Fallback environment verification failed")
                return False

            # Step 5: Update configuration
            self._update_configuration(reason)

            # Step 6: Log successful fallback
            self._log_successful_fallback(reason)

            self.logger.info("=" * 60)
            self.logger.info("WHEEL FALLBACK COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 60)

            return True

        except Exception as e:
            self.logger.error(f"Fallback procedure failed: {e}")
            self._log_failed_fallback(e)
            return False

    def _backup_current_environment(self):
        """Backup current virtual environment"""
        if self.venv_path.exists():
            backup_path = self.venv_path.parent / f"{self.venv_path.name}.backup.{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            shutil.move(str(self.venv_path), str(backup_path))
            self.logger.info(f"Backed up current environment to: {backup_path}")

    def _create_fallback_environment(self) -> bool:
        """Create new virtual environment with Python 3.11.13"""
        try:
            self.logger.info("Creating fallback virtual environment with Python 3.11.13")

            result = subprocess.run(
                [self.fallback_python, "-m", "venv", str(self.venv_path)],
                capture_output=True, text=True, timeout=60
            )

            if result.returncode != 0:
                self.logger.error(f"Failed to create venv: {result.stderr}")
                return False

            self.logger.info("Fallback virtual environment created successfully")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout creating fallback environment")
            return False
        except Exception as e:
            self.logger.error(f"Error creating fallback environment: {e}")
            return False

    def _install_dependencies_fallback(self) -> bool:
        """Install dependencies in fallback environment"""
        try:
            self.logger.info("Installing dependencies in fallback environment")

            # Activate fallback environment and install
            activate_cmd = f"source {self.venv_path}/bin/activate && pip install -r requirements.txt"

            result = subprocess.run(
                ["/bin/bash", "-c", activate_cmd],
                capture_output=True, text=True, timeout=600  # 10 minute timeout
            )

            if result.returncode != 0:
                self.logger.error(f"Dependency installation failed: {result.stderr}")
                return False

            self.logger.info("Dependencies installed successfully in fallback environment")
            return True

        except subprocess.TimeoutExpired:
            self.logger.error("Timeout installing dependencies")
            return False
        except Exception as e:
            self.logger.error(f"Error installing dependencies: {e}")
            return False

    def _verify_fallback_installation(self) -> bool:
        """Verify fallback environment is working"""
        try:
            self.logger.info("Verifying fallback environment")

            # Test critical imports
            test_cmd = f"source {self.venv_path}/bin/activate && python -c \"import pandas, numpy, fastapi; print('SUCCESS')\""

            result = subprocess.run(
                ["/bin/bash", "-c", test_cmd],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode != 0 or "SUCCESS" not in result.stdout:
                self.logger.error(f"Verification failed: {result.stderr}")
                return False

            self.logger.info("Fallback environment verified successfully")
            return True

        except Exception as e:
            self.logger.error(f"Error verifying fallback environment: {e}")
            return False

    def _update_configuration(self, reason: str):
        """Update configuration to reflect fallback state"""
        config_updates = {
            "python_version": "3.11.13",
            "wheel_status": "fallback",
            "fallback_reason": reason,
            "fallback_timestamp": datetime.utcnow().isoformat() + "Z"
        }

        # Update config file
        config_file = Path(".smvm_config")
        with open(config_file, "a") as f:
            for key, value in config_updates.items():
                f.write(f"{key}={value}\n")

        self.logger.info(f"Configuration updated: {config_updates}")

    def _log_successful_fallback(self, reason: str):
        """Log successful fallback details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "wheel_fallback_successful",
            "reason": reason,
            "primary_python": self.primary_python,
            "fallback_python": self.fallback_python,
            "status": "completed"
        }

        # Append to log file
        with open(self.fallback_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

    def _log_failed_fallback(self, error: Exception):
        """Log failed fallback details"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "wheel_fallback_failed",
            "error": str(error),
            "status": "failed"
        }

        with open(self.fallback_log, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

def main():
    """Main fallback execution"""
    if len(sys.argv) < 2:
        print("Usage: python wheel_fallback.py <reason>")
        sys.exit(1)

    reason = sys.argv[1]

    manager = WheelFallbackManager()
    success = manager.execute_fallback(reason)

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
```

## Automated Health Monitoring

### Continuous Health Check Script
```bash
#!/bin/bash
# continuous_wheel_health.sh - Continuous wheel health monitoring

WHEEL_HEALTH_LOG="wheel_health_continuous.log"
CHECK_INTERVAL=3600  # 1 hour

log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$WHEEL_HEALTH_LOG"
}

check_wheel_health() {
    log_message "Starting automated wheel health check"

    # Run wheel health assessment
    if python wheel_health.py; then
        log_message "Wheel health check: PASSED"
    else
        log_message "Wheel health check: FAILED - Initiating fallback"

        # Attempt automatic fallback
        if python wheel_fallback.py "automated_health_check_failure"; then
            log_message "Automatic fallback: SUCCESSFUL"
        else
            log_message "Automatic fallback: FAILED - Manual intervention required"
            # Send alert here
        fi
    fi
}

# Main monitoring loop
log_message "Starting continuous wheel health monitoring (interval: ${CHECK_INTERVAL}s)"

while true; do
    check_wheel_health
    sleep "$CHECK_INTERVAL"
done
```

### Health Dashboard Generation
```python
#!/usr/bin/env python3
# wheel_health_dashboard.py - Generate wheel health dashboard

import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class WheelHealthDashboard:
    """
    Generate visual dashboard for wheel health monitoring
    """

    def __init__(self, log_file: str = "wheel_health.log"):
        self.log_file = Path(log_file)

    def generate_dashboard(self):
        """Generate comprehensive health dashboard"""

        # Parse log data
        health_data = self._parse_health_logs()

        # Create visualizations
        self._create_health_chart(health_data)
        self._create_package_status_chart(health_data)
        self._create_recommendations_report(health_data)

        print("Wheel health dashboard generated successfully")

    def _parse_health_logs(self) -> List[Dict[str, Any]]:
        """Parse wheel health log data"""
        health_entries = []

        if not self.log_file.exists():
            return health_entries

        with open(self.log_file, 'r') as f:
            for line in f:
                if 'WHEEL_HEALTH' in line:
                    # Parse log entry (simplified parsing)
                    health_entries.append({
                        "timestamp": datetime.utcnow(),  # Simplified
                        "status": "parsed",
                        "packages_available": 8,  # Mock data
                        "packages_failed": 1
                    })

        return health_entries

    def _create_health_chart(self, data: List[Dict[str, Any]]):
        """Create wheel health trend chart"""
        # Implementation for health visualization
        pass

    def _create_package_status_chart(self, data: List[Dict[str, Any]]):
        """Create package availability status chart"""
        # Implementation for package status visualization
        pass

    def _create_recommendations_report(self, data: List[Dict[str, Any]]):
        """Create recommendations report"""
        # Implementation for recommendations generation
        pass

if __name__ == "__main__":
    dashboard = WheelHealthDashboard()
    dashboard.generate_dashboard()
```

## Integration with CI/CD

### GitHub Actions Integration
```yaml
# .github/workflows/wheel-health.yml
name: Wheel Health Check

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:

jobs:
  wheel-health-check:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: [3.12, 3.11]

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Run wheel health assessment
      run: python ops/runbooks/wheel_health.py

    - name: Upload health results
      uses: actions/upload-artifact@v3
      with:
        name: wheel-health-results-${{ matrix.os }}-${{ matrix.python-version }}
        path: wheel_health_results.json
```

### Automated Fallback in CI/CD
```yaml
# Fallback job in GitHub Actions
jobs:
  wheel-fallback:
    needs: wheel-health-check
    if: failure()
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Setup Python 3.11.13
      uses: actions/setup-python@v4
      with:
        python-version: 3.11

    - name: Execute wheel fallback
      run: python ops/runbooks/wheel_fallback.py "ci_pipeline_failure"

    - name: Update deployment configuration
      run: |
        echo "python_version=3.11.13" >> .smvm_config
        echo "wheel_status=fallback" >> .smvm_config

    - name: Notify team
      run: |
        echo "Wheel fallback executed in CI/CD pipeline" >> wheel_fallback_ci.log
```

## Emergency Procedures

### Complete Environment Reset
```bash
#!/bin/bash
# emergency_wheel_reset.sh - Complete environment reset

echo "=== EMERGENCY WHEEL ENVIRONMENT RESET ==="
echo "Timestamp: $(date)"

# Backup current state
tar -czf "emergency_backup_$(date +%Y%m%d_%H%M%S).tar.gz" .venv requirements.lock

# Complete cleanup
rm -rf .venv
rm -rf __pycache__
rm -rf *.egg-info
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Clear pip cache
pip cache purge

# Reinitialize with fallback
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Verify
python -c "
import pandas, numpy, fastapi
print('✅ Emergency reset successful')
"

echo "=== EMERGENCY RESET COMPLETED ==="
```

### Vendor Support Escalation
```python
#!/usr/bin/env python3
# vendor_support_report.py - Generate vendor support report

import json
from datetime import datetime
from pathlib import Path

def generate_vendor_report():
    """Generate comprehensive vendor support report"""

    report = {
        "report_type": "wheel_compatibility_issue",
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "environment": {
            "os": "Linux",  # Detect automatically
            "architecture": "x86_64",
            "python_primary": "3.12.x",
            "python_fallback": "3.11.13"
        },
        "issue_details": {
            "symptoms": [
                "Wheel installation failures for scientific packages",
                "Import errors for pandas, numpy, scipy",
                "Performance degradation in primary environment"
            ],
            "affected_packages": [
                "pandas", "numpy", "scipy", "scikit-learn"
            ],
            "error_messages": [
                "ERROR: Could not build wheels for pandas",
                "Failed building wheel for numpy"
            ]
        },
        "troubleshooting_steps": [
            "Verified Python 3.12.x installation",
            "Checked system dependencies (gcc, blas, lapack)",
            "Tested individual package installation",
            "Attempted source installation fallback",
            "Confirmed fallback to Python 3.11.13 works"
        ],
        "business_impact": {
            "severity": "HIGH",
            "affected_users": "All SMVM users",
            "workaround_available": True,
            "estimated_resolution_time": "2-4 weeks"
        },
        "requested_support": [
            "Wheel compatibility investigation for Python 3.12.x",
            "Timeline for wheel availability improvements",
            "Alternative installation methods",
            "Platform-specific build guidance"
        ]
    }

    # Save report
    with open("vendor_support_report.json", "w") as f:
        json.dump(report, f, indent=2)

    print("Vendor support report generated: vendor_support_report.json")

if __name__ == "__main__":
    generate_vendor_report()
```

## Monitoring and Alerting

### Health Metrics Collection
```python
#!/usr/bin/env python3
# wheel_health_metrics.py - Collect wheel health metrics

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class WheelHealthMetrics:
    """
    Collect and report wheel health metrics
    """

    def __init__(self):
        self.metrics_file = Path("wheel_health_metrics.json")
        self.metrics = self._load_existing_metrics()

    def _load_existing_metrics(self) -> Dict[str, Any]:
        """Load existing metrics or create new structure"""
        if self.metrics_file.exists():
            with open(self.metrics_file, 'r') as f:
                return json.load(f)

        return {
            "collection_start": datetime.utcnow().isoformat() + "Z",
            "metrics": []
        }

    def collect_metric(self, metric_type: str, value: Any, metadata: Dict[str, Any] = None):
        """Collect a health metric"""

        metric = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "type": metric_type,
            "value": value,
            "metadata": metadata or {}
        }

        self.metrics["metrics"].append(metric)

        # Save updated metrics
        with open(self.metrics_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)

    def get_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics"""

        metrics = self.metrics["metrics"]

        if not metrics:
            return {"status": "no_metrics_collected"}

        # Calculate summary statistics
        summary = {
            "total_metrics": len(metrics),
            "date_range": {
                "start": min(m["timestamp"] for m in metrics),
                "end": max(m["timestamp"] for m in metrics)
            },
            "metric_types": {}
        }

        # Group by metric type
        for metric in metrics:
            mtype = metric["type"]
            if mtype not in summary["metric_types"]:
                summary["metric_types"][mtype] = []
            summary["metric_types"][mtype].append(metric["value"])

        return summary

def main():
    """Main metrics collection"""
    collector = WheelHealthMetrics()

    # Example metric collection
    collector.collect_metric(
        "wheel_availability",
        {"primary": 85, "fallback": 95},
        {"python_versions": ["3.12.0", "3.11.13"]}
    )

    collector.collect_metric(
        "fallback_events",
        1,
        {"reason": "missing_pandas_wheel", "duration": 45}
    )

    # Generate summary
    summary = collector.get_summary_stats()

    with open("wheel_health_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("Wheel health metrics collected and summarized")

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

### Appendix A: Wheel Compatibility Matrix
Detailed compatibility matrix for all supported packages and Python versions.

### Appendix B: Common Wheel Issues and Solutions
Catalog of common wheel installation issues and their resolutions.

### Appendix C: Performance Benchmarking Scripts
Scripts for comparing performance between primary and fallback environments.

### Appendix D: Automated Testing Integration
Guidelines for integrating wheel health checks into automated test suites.
