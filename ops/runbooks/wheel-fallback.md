# Wheel Fallback Runbook

This runbook provides procedures for handling wheel build failures and implementing fallback mechanisms for the Synthetic Market Validation Module (SMVM).

## Overview

Wheel files are pre-built Python packages that can fail to install due to:
- **Architecture incompatibility**: Platform-specific binaries
- **Python version mismatch**: Compiled extensions for different Python versions
- **Missing system dependencies**: Required libraries not installed
- **Corrupted cache**: Stale or corrupted wheel cache

## Prerequisites

### Required Tools
- **Python versions**: Both 3.12.x and 3.11.13 installed
- **pip tools**: Latest version with wheel support
- **System packages**: Development headers and libraries
- **Disk space**: Additional space for multiple virtual environments

### System Dependencies
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential python3-dev python3.11-dev

# macOS
xcode-select --install
brew install python@3.11

# Windows
# Visual Studio Build Tools required for compilation
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

## Wheel Check Procedure

### Step 1: Initial Wheel Assessment

#### 1.1 Check Python Version Compatibility
```bash
# Check current Python version
python --version

# Check pip version
pip --version

# List available Python versions
where python  # Windows
which python  # Linux/macOS
```

#### 1.2 Test Wheel Installation
```bash
# Attempt to install with wheel preference
pip install --prefer-binary -r requirements.txt

# Check installation status
pip list | wc -l

# Test imports
python -c "
try:
    import pandas, numpy, scipy
    print('✅ Binary packages installed successfully')
except ImportError as e:
    print(f'❌ Import failed: {e}')
"
```

#### 1.3 Analyze Wheel Cache
```bash
# Check wheel cache location
pip cache dir

# List cached wheels
pip cache list

# Check cache size
du -sh $(pip cache dir)
```

### Step 2: Wheel Failure Diagnosis

#### 2.1 Identify Failure Patterns
```bash
# Attempt installation with verbose output
pip install -r requirements.txt -v 2>&1 | tee wheel_install.log

# Analyze error patterns
grep -i "error\|failed\|wheel" wheel_install.log

# Check specific package failures
pip install pandas --dry-run
```

#### 2.2 Check System Compatibility
```bash
# Check platform information
python -c "import platform; print(platform.platform())"

# Check architecture
uname -m  # Linux/macOS
echo %PROCESSOR_ARCHITECTURE%  # Windows

# Check available memory
free -h  # Linux
systeminfo | findstr Memory  # Windows
```

#### 2.3 Test Individual Packages
```bash
# Test core scientific packages
pip install numpy --only-binary=all
pip install pandas --only-binary=all
pip install scipy --only-binary=all

# Check which packages fail
for package in $(cat requirements.txt); do
    echo "Testing $package..."
    pip install "$package" --dry-run 2>/dev/null && echo "✅ $package" || echo "❌ $package"
done
```

## Fallback Implementation

### Step 3: Prepare Fallback Environment

#### 3.1 Backup Current Environment
```bash
# Create backup of current environment
cp -r .venv .venv.backup.$(date +%Y%m%d_%H%M%S)

# Document current state
pip freeze > requirements.frozen.$(date +%Y%m%d_%H%M%S)

# Log fallback initiation
echo "$(date): Initiating wheel fallback procedure" >> wheel_fallback.log
echo "Primary Python: $(python --version)" >> wheel_fallback.log
echo "Failure reason: [describe reason]" >> wheel_fallback.log
```

#### 3.2 Create Python 3.11.13 Environment
```bash
# Remove failed environment
rm -rf .venv

# Create new environment with Python 3.11.13
python3.11 -m venv .venv

# Activate new environment
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Verify Python version
python --version  # Should show 3.11.13
```

#### 3.3 Update Python Version Tracking
```bash
# Update environment variable
export SMVM_PYTHON_VERSION=3.11

# Update configuration file
echo "python_version=3.11.13" >> .smvm_config
echo "fallback_reason=wheel_failure" >> .smvm_config
echo "fallback_date=$(date)" >> .smvm_config
```

### Step 4: Install Dependencies with Fallback

#### 4.1 Attempt Wheel Installation
```bash
# Try installation with Python 3.11.13
pip install -r requirements.txt

# Check success rate
pip list | wc -l

# Verify critical packages
python -c "
import sys
print(f'Python version: {sys.version}')
import pandas as pd
import numpy as np
print('✅ Core packages working')
"
```

#### 4.2 Handle Remaining Failures
```bash
# Identify packages that still fail
pip install --dry-run -r requirements.txt 2>&1 | grep "would install" -A 100 | grep -v "would install" > installable_packages.txt

# Install working packages first
pip install -r installable_packages.txt

# Handle problematic packages individually
pip install pandas --no-binary pandas  # Force source installation
pip install numpy --no-binary numpy    # Force source installation
```

#### 4.3 Source Installation Fallback
```bash
# For packages that fail binary installation
pip install --no-binary :all: pandas numpy scipy

# Install build dependencies if needed
pip install setuptools wheel

# Use specific versions known to work
pip install pandas==2.1.4 numpy==1.26.2
```

### Step 5: Verification and Testing

#### 5.1 Verify Installation
```bash
# Generate new lockfile
pip freeze > requirements.lock

# Compare with original requirements
diff requirements.txt <(pip freeze | cut -d= -f1) || echo "Some packages may have different versions"

# Test all imports
python -c "
import pandas as pd
import numpy as np
import fastapi
import sqlalchemy
print('✅ All critical imports successful')
"
```

#### 5.2 Run Test Suite
```bash
# Run basic tests
pytest tests/ -x --tb=short

# Run import tests
python -c "
import smvm
print('SMVM module imports successfully')
"
```

#### 5.3 Performance Validation
```bash
# Test basic functionality
time python -c "import pandas as pd; df = pd.DataFrame({'a': range(1000000)}); print(df.sum())"

# Compare with expected performance
# Log performance metrics
echo "Fallback performance test: $(date)" >> performance.log
```

## Logging and Documentation

### Step 6: Document Fallback

#### 6.1 Update Fallback Log
```bash
# Comprehensive logging
cat >> wheel_fallback.log << EOF
=== Wheel Fallback Completed ===
Date: $(date)
Original Python: 3.12.x
Fallback Python: 3.11.13
Reason: [detailed reason]
Packages affected: [list problematic packages]
Resolution: [describe solution]
Performance impact: [note any performance changes]
Recommendations: [future improvement suggestions]
EOF
```

#### 6.2 Update Runbook
```bash
# Document this specific fallback case
cat >> fallback_incidents.md << EOF
## Incident: $(date)
- Python versions: 3.12.x → 3.11.13
- Trigger: Wheel installation failures
- Affected packages: [list]
- Resolution: [steps taken]
- Outcome: [success/failure]
- Prevention: [future recommendations]
EOF
```

#### 6.3 Notify Stakeholders
```bash
# Generate summary report
cat > fallback_report.md << EOF
# SMVM Wheel Fallback Report

## Incident Summary
- Date: $(date)
- Environment: [development/production]
- Primary Python: 3.12.x
- Fallback Python: 3.11.13

## Root Cause
[detailed analysis]

## Resolution Steps
1. [step 1]
2. [step 2]
3. [step 3]

## Impact Assessment
- Functionality: [affected/not affected]
- Performance: [impact level]
- Timeline: [duration of fallback]

## Recommendations
1. [recommendation 1]
2. [recommendation 2]
3. [recommendation 3]
EOF
```

## Recovery Procedures

### Step 7: Monitor and Recovery

#### 7.1 Monitor Fallback Environment
```bash
# Set up monitoring
echo "*/5 * * * * /path/to/health_check.sh" | crontab -

# Health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
source .venv/bin/activate
python -c "
import pandas, numpy, fastapi
print('Health check passed at $(date)')
" >> health.log 2>&1
EOF
chmod +x health_check.sh
```

#### 7.2 Plan Primary Environment Recovery
```bash
# Document recovery steps
cat > recovery_plan.md << EOF
# Recovery Plan: Return to Python 3.12.x

## Prerequisites
- [ ] Python 3.12.x wheel compatibility improved
- [ ] System dependencies updated
- [ ] Test environment available

## Recovery Steps
1. [step 1]
2. [step 2]
3. [step 3]

## Testing
- [ ] All packages install successfully
- [ ] Test suite passes
- [ ] Performance meets requirements

## Rollback Plan
- [ ] Quick rollback to 3.11.13 if issues arise
- [ ] Data backup and restore procedures
EOF
```

#### 7.3 Schedule Re-evaluation
```bash
# Set reminder for re-evaluation
echo "0 9 * * 1 echo 'Review Python 3.12.x compatibility'" | crontab -

# Track compatibility status
cat > compatibility_tracking.md << EOF
# Python Version Compatibility Tracking

## Current Status
- Python 3.12.x: Limited wheel support
- Python 3.11.13: Full wheel support
- Last evaluation: $(date)

## Known Issues
- [issue 1]
- [issue 2]

## Workarounds
- [workaround 1]
- [workaround 2]

## Future Plans
- Monitor Python 3.12.x wheel improvements
- Test quarterly for compatibility improvements
EOF
```

## Advanced Troubleshooting

### Complex Wheel Issues

#### Compiler Issues
```bash
# Check compiler availability
gcc --version  # Linux
clang --version  # macOS
cl.exe  # Windows

# Install missing compilers
sudo apt install gcc g++  # Linux
xcode-select --install     # macOS
# Install Visual Studio Build Tools  # Windows
```

#### Library Dependencies
```bash
# Check system libraries
ldd $(python -c "import numpy; print(numpy.__file__)")  # Linux

# Install missing libraries
sudo apt install libblas-dev liblapack-dev  # Linux
brew install openblas lapack  # macOS
```

#### Cache Corruption
```bash
# Clear pip cache
pip cache purge

# Clear system package cache
sudo apt clean  # Linux
brew cleanup    # macOS

# Rebuild from scratch
rm -rf .venv
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Performance Optimization

#### Wheel Preferences
```bash
# Prefer binary wheels when available
pip install --prefer-binary -r requirements.txt

# Allow source fallback for specific packages
pip install --only-binary=all pandas numpy || pip install pandas numpy
```

#### Parallel Installation
```bash
# Use multiple processes for installation
pip install -r requirements.txt --no-cache-dir -j 4

# Install in dependency order
pip install --constraint requirements.txt --requirement requirements.txt
```

## Emergency Procedures

### Complete Environment Reset
```bash
# Emergency reset procedure
rm -rf .venv
rm -rf __pycache__
rm -rf *.egg-info
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete

# Reinitialize
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Vendor Support Escalation
```bash
# Document for vendor support
cat > vendor_support.md << EOF
Package: [problematic package]
Version: [version]
Python: 3.11.13
Platform: [platform details]
Error: [error message]
Steps tried: [list of attempted solutions]
Business impact: [describe impact]
EOF
```

---

**Runbook Version**: 1.0
**Last Updated**: 2024-12-XX
**Author**: SMVM Operations Team

*This runbook should be updated when new wheel compatibility issues are discovered.*
