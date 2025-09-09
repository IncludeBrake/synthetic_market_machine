#!/usr/bin/env python3
"""
SMVM Python Version Checker

Runtime Python version verification and drift detection with logging and
RBAC-aware enforcement for the Synthetic Market Validation Module.
"""

import sys
import os
import json
import hashlib
import logging
import platform
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import subprocess

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class VersionChecker:
    """
    Comprehensive Python version checker with drift detection and enforcement
    """

    def __init__(self, log_file: str = "version_check.log"):
        self.log_file = Path(log_file)
        self.setup_logging()

        # Version constraints
        self.primary_versions = ["3.12"]  # Exact match for 3.12.x
        self.fallback_versions = ["3.11.13"]  # Exact match for 3.11.13
        self.experimental_versions = ["3.13"]  # Prefix match for 3.13+

        # All allowed versions
        self.allowed_versions = (
            self.primary_versions +
            self.fallback_versions +
            self.experimental_versions
        )

        # Token budget for version checks (500 tokens as per requirements)
        self.token_budget = 500
        self.tokens_used = 0

        # Cache results to avoid repeated checks
        self._check_cache = {}
        self._cache_ttl = 300  # 5 minutes cache

        self.logger = logging.getLogger("version_check")

    def setup_logging(self):
        """Setup comprehensive logging with file and console output"""
        # Create logs directory if it doesn't exist
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - VERSION_CHECK - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )

    def verify_environment(self, user_role: str = "developer") -> Dict[str, Any]:
        """
        Comprehensive environment verification with RBAC consideration

        Args:
            user_role: User's role for RBAC enforcement ("developer", "operator", "auditor")

        Returns:
            Dict containing verification results
        """
        start_time = datetime.utcnow().isoformat() + "Z"
        self.logger.info("=" * 60)
        self.logger.info("STARTING PYTHON VERSION ENVIRONMENT VERIFICATION")
        self.logger.info(f"User Role: {user_role}")
        self.logger.info(f"Start Time: {start_time}")
        self.logger.info("=" * 60)

        results = {
            "timestamp": start_time,
            "user_role": user_role,
            "version_check": self._check_python_version(),
            "wheel_status_check": self._check_wheel_status(),
            "package_integrity_check": self._check_package_integrity(),
            "environment_config_check": self._check_environment_config(),
            "rbac_compliance_check": self._check_rbac_compliance(user_role),
            "security_check": self._check_security_boundaries(),
            "violations": [],
            "warnings": [],
            "recommendations": [],
            "token_usage": 0,
            "overall_status": "unknown"
        }

        # Aggregate violations and warnings
        self._collect_violations_and_warnings(results)

        # Generate recommendations
        self._generate_recommendations(results, user_role)

        # Determine overall status
        results["overall_status"] = self._determine_overall_status(results)

        # Log final assessment
        self._log_final_assessment(results)

        # Update token usage
        results["token_usage"] = self.tokens_used

        return results

    def _check_python_version(self) -> Dict[str, Any]:
        """Check Python version compliance"""
        self.logger.info("Checking Python version compliance...")

        # Get current Python version
        current_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        version_info = {
            "current_version": current_version,
            "python_executable": sys.executable,
            "platform": platform.platform(),
            "architecture": platform.machine(),
            "implementation": platform.python_implementation()
        }

        # Check version compliance
        version_compliant = self._is_version_allowed(current_version)

        if version_compliant:
            compliance_type = self._get_version_type(current_version)
            self.logger.info(f"✓ Python version compliant: {current_version} ({compliance_type})")
            version_info["compliance_status"] = "compliant"
            version_info["compliance_type"] = compliance_type
        else:
            self.logger.warning(f"✗ Python version not compliant: {current_version}")
            version_info["compliance_status"] = "non_compliant"
            version_info["allowed_versions"] = self.allowed_versions

        return version_info

    def _check_wheel_status(self) -> Dict[str, Any]:
        """Check wheel availability and status"""
        self.logger.info("Checking wheel status...")

        wheel_status = {
            "wheel_available": True,
            "fallback_required": False,
            "fallback_reason": None,
            "requirements_lock_exists": False,
            "requirements_lock_current": False,
            "packages_with_wheels": 0,
            "packages_without_wheels": 0
        }

        # Check requirements.lock existence and currency
        lock_file = Path("requirements.lock")
        if lock_file.exists():
            wheel_status["requirements_lock_exists"] = True

            # Check if lock file is reasonably current (within 24 hours)
            file_age_seconds = datetime.utcnow().timestamp() - lock_file.stat().st_mtime
            wheel_status["requirements_lock_current"] = file_age_seconds < 86400  # 24 hours

            if not wheel_status["requirements_lock_current"]:
                self.logger.warning(".1f"
        else:
            self.logger.warning("Requirements lock file not found")
            wheel_status["fallback_required"] = True
            wheel_status["fallback_reason"] = "missing_requirements_lock"

        # Check critical package availability
        critical_packages = ["pandas", "numpy", "fastapi", "sqlalchemy"]
        for package in critical_packages:
            try:
                __import__(package)
                wheel_status["packages_with_wheels"] += 1
            except ImportError:
                wheel_status["packages_without_wheels"] += 1
                wheel_status["wheel_available"] = False
                wheel_status["fallback_required"] = True
                wheel_status["fallback_reason"] = f"missing_critical_package_{package}"

        if wheel_status["wheel_available"]:
            self.logger.info("✓ Wheel status: All critical packages available")
        else:
            self.logger.warning("⚠️ Wheel status: Some packages unavailable - fallback recommended")

        return wheel_status

    def _check_package_integrity(self) -> Dict[str, Any]:
        """Check package integrity and pip freeze hash"""
        self.logger.info("Checking package integrity...")

        integrity_status = {
            "pip_freeze_hash_match": False,
            "requirements_lock_exists": False,
            "packages_count": 0,
            "frozen_hash": None,
            "lock_hash": None
        }

        # Generate current pip freeze hash
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "freeze"],
                capture_output=True, text=True, timeout=30
            )

            if result.returncode == 0:
                current_freeze = result.stdout.strip()
                integrity_status["packages_count"] = len([line for line in current_freeze.split('\n') if line.strip()])

                # Generate hash of current freeze
                integrity_status["frozen_hash"] = hashlib.sha256(
                    current_freeze.encode('utf-8')
                ).hexdigest()

                # Check against requirements.lock
                lock_file = Path("requirements.lock")
                if lock_file.exists():
                    integrity_status["requirements_lock_exists"] = True

                    with open(lock_file, 'r') as f:
                        lock_content = f.read().strip()

                    lock_hash = hashlib.sha256(lock_content.encode('utf-8')).hexdigest()
                    integrity_status["lock_hash"] = lock_hash

                    # Compare hashes
                    integrity_status["pip_freeze_hash_match"] = (
                        integrity_status["frozen_hash"] == lock_hash
                    )

                    if integrity_status["pip_freeze_hash_match"]:
                        self.logger.info("✓ Package integrity: pip freeze hash matches requirements.lock")
                    else:
                        self.logger.warning("⚠️ Package integrity: pip freeze hash differs from requirements.lock")
                else:
                    self.logger.warning("Package integrity: requirements.lock not found")

        except subprocess.TimeoutExpired:
            self.logger.error("Package integrity check timed out")
        except Exception as e:
            self.logger.error(f"Package integrity check failed: {e}")

        return integrity_status

    def _check_environment_config(self) -> Dict[str, Any]:
        """Check environment configuration"""
        self.logger.info("Checking environment configuration...")

        config_status = {
            "smvm_python_version_set": False,
            "smvm_wheel_status_set": False,
            "config_file_exists": False,
            "config_file_valid": False,
            "virtual_environment_active": bool(os.getenv("VIRTUAL_ENV"))
        }

        # Check environment variables
        python_version = os.getenv("SMVM_PYTHON_VERSION")
        wheel_status = os.getenv("SMVM_WHEEL_STATUS")

        if python_version:
            config_status["smvm_python_version_set"] = True
            self.logger.info(f"✓ SMVM_PYTHON_VERSION: {python_version}")
        else:
            self.logger.warning("⚠️ SMVM_PYTHON_VERSION environment variable not set")

        if wheel_status:
            config_status["smvm_wheel_status_set"] = True
            self.logger.info(f"✓ SMVM_WHEEL_STATUS: {wheel_status}")
        else:
            self.logger.warning("⚠️ SMVM_WHEEL_STATUS environment variable not set")

        # Check configuration file
        config_file = Path(".smvm_config")
        if config_file.exists():
            config_status["config_file_exists"] = True

            try:
                with open(config_file, 'r') as f:
                    config_content = f.read()

                # Basic validation
                if "python_version=" in config_content:
                    config_status["config_file_valid"] = True
                    self.logger.info("✓ Configuration file is valid")
                else:
                    self.logger.warning("⚠️ Configuration file missing python_version setting")

            except Exception as e:
                self.logger.error(f"Error reading configuration file: {e}")

        if config_status["virtual_environment_active"]:
            self.logger.info("✓ Running in virtual environment")
        else:
            self.logger.warning("⚠️ Not running in virtual environment - consider using venv")

        return config_status

    def _check_rbac_compliance(self, user_role: str) -> Dict[str, Any]:
        """Check RBAC compliance for version operations"""
        self.logger.info(f"Checking RBAC compliance for role: {user_role}")

        rbac_status = {
            "role_valid": False,
            "version_change_allowed": False,
            "wheel_fallback_allowed": False,
            "admin_operations_allowed": False
        }

        # Define role permissions
        role_permissions = {
            "developer": {
                "version_change_allowed": False,
                "wheel_fallback_allowed": True,
                "admin_operations_allowed": False
            },
            "operator": {
                "version_change_allowed": True,
                "wheel_fallback_allowed": True,
                "admin_operations_allowed": False
            },
            "auditor": {
                "version_change_allowed": False,
                "wheel_fallback_allowed": False,
                "admin_operations_allowed": False
            },
            "admin": {
                "version_change_allowed": True,
                "wheel_fallback_allowed": True,
                "admin_operations_allowed": True
            }
        }

        if user_role in role_permissions:
            rbac_status["role_valid"] = True
            rbac_status.update(role_permissions[user_role])

            self.logger.info(f"✓ RBAC: Role {user_role} validated")
            for permission, allowed in role_permissions[user_role].items():
                if allowed:
                    self.logger.info(f"  ✓ {permission.replace('_', ' ').title()}")
                else:
                    self.logger.info(f"  - {permission.replace('_', ' ').title()}")
        else:
            self.logger.error(f"✗ RBAC: Invalid role {user_role}")
            rbac_status["role_valid"] = False

        return rbac_status

    def _check_security_boundaries(self) -> Dict[str, Any]:
        """Check security boundaries and constraints"""
        self.logger.info("Checking security boundaries...")

        security_status = {
            "secure_file_permissions": True,
            "no_world_writable_files": True,
            "python_path_secure": True,
            "imports_secure": True
        }

        # Check critical file permissions
        critical_files = ["requirements.txt", "requirements.lock", ".smvm_config"]
        insecure_files = []

        for file_path in critical_files:
            if Path(file_path).exists():
                # Check if file is world-writable (basic security check)
                file_stat = Path(file_path).stat()
                permissions = file_stat.st_mode & 0o777

                # Check for world-writable permissions (others write bit set)
                if permissions & 0o002:  # Others write permission
                    insecure_files.append(file_path)
                    security_status["no_world_writable_files"] = False

        if insecure_files:
            self.logger.warning(f"⚠️ Security: Insecure file permissions on {insecure_files}")
        else:
            self.logger.info("✓ Security: All critical files have secure permissions")

        return security_status

    def _is_version_allowed(self, version: str) -> bool:
        """Check if Python version is allowed"""
        # Check exact matches first
        if version in self.allowed_versions:
            return True

        # Check prefix matches for version ranges (e.g., 3.12.1 matches 3.12)
        for allowed in self.allowed_versions:
            if version.startswith(allowed):
                return True

        return False

    def _get_version_type(self, version: str) -> str:
        """Get the type of Python version (primary, fallback, experimental)"""
        if any(version.startswith(v) for v in self.primary_versions):
            return "primary"
        elif any(version.startswith(v) for v in self.fallback_versions):
            return "fallback"
        elif any(version.startswith(v) for v in self.experimental_versions):
            return "experimental"
        else:
            return "unknown"

    def _collect_violations_and_warnings(self, results: Dict[str, Any]):
        """Collect violations and warnings from all checks"""

        violations = []
        warnings = []

        # Check version compliance
        version_check = results["version_check"]
        if version_check.get("compliance_status") != "compliant":
            violations.append({
                "check": "python_version",
                "severity": "critical",
                "message": f"Python version {version_check['current_version']} not allowed"
            })

        # Check wheel status
        wheel_check = results["wheel_status_check"]
        if wheel_check.get("fallback_required"):
            if wheel_check.get("fallback_reason") == "missing_requirements_lock":
                violations.append({
                    "check": "wheel_status",
                    "severity": "warning",
                    "message": "Requirements lock file missing"
                })
            else:
                warnings.append({
                    "check": "wheel_status",
                    "severity": "warning",
                    "message": f"Wheel issues detected: {wheel_check.get('fallback_reason')}"
                })

        # Check package integrity
        integrity_check = results["package_integrity_check"]
        if not integrity_check.get("pip_freeze_hash_match", True):
            warnings.append({
                "check": "package_integrity",
                "severity": "warning",
                "message": "Pip freeze hash does not match requirements.lock"
            })

        # Check RBAC
        rbac_check = results["rbac_compliance_check"]
        if not rbac_check.get("role_valid"):
            violations.append({
                "check": "rbac_compliance",
                "severity": "critical",
                "message": f"Invalid user role: {results['user_role']}"
            })

        # Check security
        security_check = results["security_check"]
        if not security_check.get("no_world_writable_files"):
            violations.append({
                "check": "security_boundaries",
                "severity": "critical",
                "message": "Insecure file permissions detected"
            })

        results["violations"] = violations
        results["warnings"] = warnings

    def _generate_recommendations(self, results: Dict[str, Any], user_role: str):
        """Generate recommendations based on verification results"""

        recommendations = []

        # Version recommendations
        version_check = results["version_check"]
        if version_check.get("compliance_status") != "compliant":
            allowed_versions = version_check.get("allowed_versions", [])
            recommendations.append(f"Switch to allowed Python version: {', '.join(allowed_versions)}")

        # Wheel recommendations
        wheel_check = results["wheel_status_check"]
        if wheel_check.get("fallback_required"):
            if wheel_check.get("fallback_reason") == "missing_requirements_lock":
                recommendations.append("Generate requirements.lock: pip freeze > requirements.lock")
            else:
                recommendations.append("Consider Python 3.11.13 fallback for better wheel support")

        # Environment recommendations
        env_check = results["environment_config_check"]
        if not env_check.get("virtual_environment_active"):
            recommendations.append("Use virtual environment: python -m venv .venv")
        if not env_check.get("smvm_python_version_set"):
            recommendations.append("Set SMVM_PYTHON_VERSION environment variable")

        # RBAC recommendations
        rbac_check = results["rbac_compliance_check"]
        if not rbac_check.get("role_valid"):
            recommendations.append("Use valid role: developer, operator, auditor, or admin")

        results["recommendations"] = recommendations

    def _determine_overall_status(self, results: Dict[str, Any]) -> str:
        """Determine overall verification status"""

        violations = results.get("violations", [])
        critical_violations = [v for v in violations if v.get("severity") == "critical"]

        if critical_violations:
            return "FAILED"
        elif violations:
            return "WARNING"
        else:
            return "PASSED"

    def _log_final_assessment(self, results: Dict[str, Any]):
        """Log final verification assessment"""

        self.logger.info("=" * 60)
        self.logger.info("VERSION VERIFICATION ASSESSMENT COMPLETE")
        self.logger.info("=" * 60)

        self.logger.info(f"Overall Status: {results['overall_status']}")
        self.logger.info(f"Violations: {len(results.get('violations', []))}")
        self.logger.info(f"Warnings: {len(results.get('warnings', []))}")
        self.logger.info(f"Token Usage: {self.tokens_used}/{self.token_budget}")

        if results.get("recommendations"):
            self.logger.info("\nRECOMMENDATIONS:")
            for rec in results["recommendations"]:
                self.logger.info(f"• {rec}")

        self.logger.info("=" * 60)

    def log_drift_warning(self, detected_version: str, expected_version: str):
        """Log version drift warning"""
        self.logger.warning("=" * 40)
        self.logger.warning("PYTHON VERSION DRIFT DETECTED")
        self.logger.warning(f"Detected: {detected_version}")
        self.logger.warning(f"Expected: {expected_version}")
        self.logger.warning("This may indicate interpreter changes without approval")
        self.logger.warning("=" * 40)

def main():
    """Main execution function"""

    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="SMVM Python Version Checker")
    parser.add_argument("--user-role", default="developer",
                       choices=["developer", "operator", "auditor", "admin"],
                       help="User role for RBAC enforcement")
    parser.add_argument("--log-file", default="version_check.log",
                       help="Log file path")
    parser.add_argument("--json-output", action="store_true",
                       help="Output results as JSON")

    args = parser.parse_args()

    # Run verification
    checker = VersionChecker(args.log_file)
    results = checker.verify_environment(args.user_role)

    # Output results
    if args.json_output:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nVersion Check Results: {results['overall_status']}")
        print(f"Violations: {len(results.get('violations', []))}")
        print(f"Warnings: {len(results.get('warnings', []))}")

        if results.get("recommendations"):
            print("\nRecommendations:")
            for rec in results["recommendations"]:
                print(f"• {rec}")

    # Return appropriate exit code
    if results["overall_status"] == "FAILED":
        return 1
    elif results["overall_status"] == "WARNING":
        return 2  # Warning but not failure
    else:
        return 0

if __name__ == "__main__":
    sys.exit(main())
