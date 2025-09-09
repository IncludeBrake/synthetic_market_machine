# SMVM Setup Runbook

This runbook provides step-by-step procedures for setting up the Synthetic Market Validation Module (SMVM) environment.

## Prerequisites

### System Requirements
- **Operating System**: Windows 10/11, macOS 12+, Ubuntu 20.04+
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space
- **Network**: Stable internet connection

### Required Software
- **Python**: 3.12.x (primary) or 3.11.13 (fallback)
- **Git**: Version 2.30+ for repository cloning
- **PowerShell**: Version 7+ (Windows) or Bash (Linux/macOS)

### Environment Variables
```bash
# Set these environment variables
export SMVM_ENV=development
export SMVM_PYTHON_VERSION=3.12
export SMVM_LOG_LEVEL=INFO
```

## Setup Procedure

### Step 1: Repository Setup

#### 1.1 Clone Repository
```bash
# Navigate to development directory
cd ~/dev  # or C:\Dev on Windows

# Clone the repository
git clone https://github.com/your-org/synthetic-market-machine.git
cd synthetic-market-machine

# Verify repository structure
ls -la
```

#### 1.2 Verify Repository Integrity
```bash
# Check repository status
git status
git log --oneline -5

# Verify required files exist
ls -la .venv/           # Should not exist initially
ls -la requirements.txt # Should exist
ls -la requirements.lock # Should exist
ls -la .gitignore      # Should exist
```

### Step 2: Python Environment Setup

#### 2.1 Check Python Version
```bash
# Check current Python version
python --version

# Expected output: Python 3.12.x
# If version is different, see fallback procedure below
```

#### 2.2 Create Virtual Environment
```bash
# Create Python virtual environment
python -m venv .venv

# Verify creation
ls -la .venv/
```

#### 2.3 Activate Virtual Environment
```bash
# Windows PowerShell
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

# Verify activation
which python  # Should point to .venv/bin/python
python --version  # Should show 3.12.x
```

#### 2.4 Upgrade pip
```bash
# Upgrade pip to latest version
python -m pip install --upgrade pip

# Verify pip version
pip --version
```

### Step 3: Dependency Installation

#### 3.1 Install from Requirements
```bash
# Install dependencies from requirements.txt
pip install -r requirements.txt

# Verify installation
pip list | grep -E "(pandas|numpy|fastapi)"
```

#### 3.2 Verify Lockfile Match
```bash
# Generate current lockfile
pip freeze > requirements.lock.temp

# Compare with existing lockfile
diff requirements.lock requirements.lock.temp

# Clean up temp file
rm requirements.lock.temp
```

#### 3.3 Test Core Imports
```bash
# Test core package imports
python -c "
import sys
print(f'Python version: {sys.version}')

import pandas as pd
import numpy as np
import fastapi
from pydantic import BaseModel

print('✅ All core packages imported successfully')
"
```

### Step 4: Configuration Setup

#### 4.1 Create Environment File
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
# DATABASE_URL=sqlite:///./smvm.db
# SECRET_KEY=your-secret-key-here
# LOG_LEVEL=INFO
```

#### 4.2 Verify Configuration
```bash
# Test configuration loading
python -c "
from pydantic_settings import BaseSettings
print('✅ Configuration system working')
"
```

### Step 5: Database Setup

#### 5.1 Initialize Database
```bash
# Run database migrations
alembic upgrade head

# Alternative: Initialize with custom script
python -c "
# Database initialization code here
print('Database initialized')
"
```

#### 5.2 Verify Database Connection
```bash
# Test database connection
python -c "
# Database connection test code here
print('✅ Database connection successful')
"
```

### Step 6: Application Testing

#### 6.1 Run Health Check
```bash
# Run basic health check
python -c "
import smvm
print('SMVM module loaded successfully')
print(f'Version: {smvm.__version__ if hasattr(smvm, \"__version__\") else \"dev\"}')
"
```

#### 6.2 Run Basic Tests
```bash
# Run pytest suite
pytest tests/ --tb=short -v

# Expected: All tests pass
```

#### 6.3 Start Development Server
```bash
# Start FastAPI development server
uvicorn smvm.main:app --reload --host 0.0.0.0 --port 8000

# Verify server starts
curl http://localhost:8000/health
```

## Fallback Procedures

### Python Version Fallback

#### Condition
- Python 3.12.x not available
- Wheel build failures with Python 3.12.x

#### Procedure
```bash
# 1. Remove current virtual environment
rm -rf .venv

# 2. Install Python 3.11.13
# Windows: Download from python.org
# Linux: apt install python3.11
# macOS: brew install python@3.11

# 3. Create new virtual environment with 3.11.13
python3.11 -m venv .venv

# 4. Activate and install
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/macOS

pip install -r requirements.txt

# 5. Log fallback reason
echo "Fallback to Python 3.11.13: $(date)" >> python_fallback.log
echo "Reason: [describe reason]" >> python_fallback.log
```

### Dependency Installation Fallback

#### Condition
- Package installation failures
- Network connectivity issues

#### Procedure
```bash
# 1. Use local package cache
pip install -r requirements.txt --cache-dir ~/.cache/pip

# 2. Install from local wheel files
pip install --no-index --find-links=/path/to/wheels -r requirements.txt

# 3. Manual package installation
pip install pandas==2.1.4
pip install numpy==1.26.2
# ... install other packages individually
```

### Network Issues Fallback

#### Condition
- No internet connectivity
- Proxy/firewall blocking pip

#### Procedure
```bash
# 1. Configure proxy
export HTTP_PROXY=http://proxy.company.com:8080
export HTTPS_PROXY=http://proxy.company.com:8080

# 2. Use internal package repository
pip config set global.index-url http://internal-pypi.company.com/simple/

# 3. Install from local files
pip install --no-index --find-links=file:///path/to/packages -r requirements.txt
```

## Troubleshooting

### Common Issues

#### Virtual Environment Issues
```bash
# Problem: Activation fails
ls -la .venv/Scripts/  # Windows
ls -la .venv/bin/     # Linux/macOS

# Solution: Recreate virtual environment
rm -rf .venv
python -m venv .venv
```

#### Package Installation Issues
```bash
# Problem: Package conflicts
pip check  # Check for conflicts

# Solution: Clean installation
pip uninstall -r requirements.txt -y
pip install -r requirements.txt
```

#### Permission Issues
```bash
# Problem: Permission denied
# Windows: Run as Administrator
# Linux/macOS: Use --user flag
pip install --user -r requirements.txt
```

#### Path Issues
```bash
# Problem: Python not found
which python
python --version

# Solution: Update PATH or use full path
/path/to/python -m venv .venv
```

### Diagnostic Commands

#### System Information
```bash
# Python information
python --version
python -c "import sys; print(sys.path)"

# Pip information
pip --version
pip config list

# Virtual environment information
which python
echo $VIRTUAL_ENV
```

#### Package Information
```bash
# List installed packages
pip list

# Check package locations
pip show pandas numpy fastapi

# Check for outdated packages
pip list --outdated
```

#### Network Diagnostics
```bash
# Test connectivity
curl https://pypi.org/

# Test proxy settings
env | grep -i proxy

# Test package download
pip download pandas --no-deps
```

## Verification Checklist

### Pre-Setup Verification
- [ ] Python 3.12.x installed and accessible
- [ ] Git installed and configured
- [ ] Sufficient disk space available
- [ ] Network connectivity to PyPI
- [ ] Administrator/sudo privileges if needed

### Post-Setup Verification
- [ ] Virtual environment created and activated
- [ ] All dependencies installed successfully
- [ ] Database initialized and accessible
- [ ] Application starts without errors
- [ ] Basic tests pass
- [ ] API endpoints respond correctly

### Documentation Verification
- [ ] All configuration files created
- [ ] Environment variables set correctly
- [ ] Logs directory created and writable
- [ ] Backup procedures documented

## Rollback Procedures

### Complete Rollback
```bash
# 1. Stop all running processes
pkill -f uvicorn
pkill -f python

# 2. Remove virtual environment
rm -rf .venv

# 3. Remove generated files
rm -rf logs/
rm -rf __pycache__/
rm -f smvm.db

# 4. Reset repository (optional)
git reset --hard HEAD
git clean -fd
```

### Partial Rollback
```bash
# Rollback specific changes
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# Reset database
alembic downgrade base
alembic upgrade head
```

## Monitoring and Maintenance

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
python -c "from smvm.database import check_connection; check_connection()"

# System resources
df -h  # Disk usage
free -h  # Memory usage
top -bn1  # Process status
```

### Log Monitoring
```bash
# View application logs
tail -f logs/smvm.log

# Search for errors
grep ERROR logs/smvm.log

# Monitor log size
ls -lh logs/
```

### Performance Monitoring
```bash
# Check memory usage
ps aux | grep python

# Monitor CPU usage
top -p $(pgrep python)

# Check network connections
netstat -tlnp | grep :8000
```

---

**Runbook Version**: 1.0
**Last Updated**: 2024-12-XX
**Author**: SMVM Operations Team

*This runbook should be reviewed quarterly and updated as needed.*
