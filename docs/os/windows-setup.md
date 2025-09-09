# Windows Setup Guide for SMVM

This guide provides comprehensive setup instructions for running the Synthetic Market Validation Module (SMVM) on Windows systems.

## Prerequisites

### System Requirements
- **OS**: Windows 10 version 1903 or later, Windows 11
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: 10GB+ free space
- **Internet**: Stable broadband connection

### Required Software
- **PowerShell 7+**: Modern PowerShell with enhanced features
- **Git**: Version control system
- **Python**: 3.12.x (primary) or 3.11.13 (fallback)

## PowerShell Setup

### 1. Install PowerShell 7

```powershell
# Check current PowerShell version
$PSVersionTable.PSVersion

# Download and install PowerShell 7 from Microsoft
winget install --id Microsoft.PowerShell --source winget
```

### 2. Configure Execution Policy

```powershell
# Check current execution policy
Get-ExecutionPolicy

# Set execution policy for current user (recommended)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Verify change
Get-ExecutionPolicy -Scope CurrentUser
```

### 3. Update PowerShell Profile

Create or update your PowerShell profile:

```powershell
# Check if profile exists
Test-Path $PROFILE

# Create profile if it doesn't exist
New-Item -Path $PROFILE -ItemType File -Force

# Edit profile (opens in default editor)
notepad $PROFILE
```

Add these lines to your profile:

```powershell
# SMVM Development Environment
function Activate-SMVM {
    param([string]$Path = ".")
    Set-Location $Path
    & ".venv\Scripts\activate"
    Write-Host "SMVM virtual environment activated" -ForegroundColor Green
}

# Useful aliases
Set-Alias -Name activate -Value Activate-SMVM
Set-Alias -Name python -Value python.exe
Set-Alias -Name pip -Value pip.exe
```

## Python Installation

### Option 1: Python 3.12.x (Recommended)

```powershell
# Download Python 3.12.x from python.org
# Or use winget
winget install Python.Python.3.12

# Verify installation
python --version  # Should show 3.12.x
```

### Option 2: Python 3.11.13 (Fallback)

If Python 3.12.x is not available:

```powershell
# Install Python 3.11.13
winget install Python.Python.3.11

# Verify installation
python --version  # Should show 3.11.13
```

### Configure Python Environment

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install virtualenv if not included
python -m pip install virtualenv

# Verify pip installation
pip --version
```

## Long Path Support

Windows has historically limited path lengths to 260 characters. Enable long path support for SMVM:

### Method 1: Registry Edit (Permanent)

```powershell
# Enable long paths via registry
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1 -Type DWord

# Restart PowerShell or system for changes to take effect
```

### Method 2: Group Policy (Enterprise)

1. Open Group Policy Editor: `gpedit.msc`
2. Navigate to: `Computer Configuration > Administrative Templates > System > Filesystem`
3. Enable: `Enable Win32 long paths`
4. Apply and restart

### Method 3: Application Manifest (Per-App)

For applications that support it, use application manifests to enable long paths.

## SMVM Installation

### 1. Clone Repository

```powershell
# Navigate to development directory
Set-Location "C:\Dev"

# Clone SMVM repository
git clone https://github.com/your-org/synthetic-market-machine.git
cd synthetic-market-machine
```

### 2. Create Virtual Environment

```powershell
# Create Python virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Verify activation
python --version  # Should show 3.12.x or 3.11.13
```

### 3. Install Dependencies

```powershell
# Install from requirements.txt
pip install -r requirements.txt

# Or install from lockfile for exact versions
pip install -r requirements.lock

# Verify installation
pip list
```

### 4. Verify Setup

```powershell
# Run basic health check
python -c "import sys; print(f'Python: {sys.version}'); print('SMVM setup complete!')"

# Check key packages
python -c "import pandas, numpy, fastapi; print('Core packages imported successfully')"
```

## Development Environment Setup

### 1. Configure IDE (VS Code Recommended)

```powershell
# Install VS Code extensions
code --install-extension ms-python.python
code --install-extension ms-python.black-formatter
code --install-extension ms-python.isort
code --install-extension ms-python.flake8
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=sqlite:///./smvm.db

# Security
SECRET_KEY=your-development-secret-key
JWT_SECRET=your-jwt-development-secret

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/smvm.log

# Observability
METRICS_PORT=9090
HEALTH_CHECK_INTERVAL=30
```

### 3. Initialize Database

```powershell
# Run database migrations
alembic upgrade head

# Or create initial database
python -c "from smvm.database import init_db; init_db()"
```

## Troubleshooting

### Common Issues

#### 1. Python Not Found
```powershell
# Check Python installation
where python
python --version

# If not found, reinstall Python or update PATH
# Add Python to PATH during installation
```

#### 2. Virtual Environment Issues
```powershell
# Recreate virtual environment
Remove-Item .venv -Recurse -Force
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

#### 3. Permission Errors
```powershell
# Run PowerShell as Administrator
# Or use --user flag for pip installs
pip install --user -r requirements.txt
```

#### 4. Long Path Errors
```powershell
# Enable long paths (requires restart)
Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" -Name "LongPathsEnabled" -Value 1

# Alternative: Use shorter paths
# Move project to root directory (e.g., C:\SMVM)
```

#### 5. Git Issues
```powershell
# Configure Git
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Check Git status
git status
```

### Performance Optimization

#### 1. Windows Defender Exclusions
```powershell
# Add project directory to Windows Defender exclusions
Add-MpPreference -ExclusionPath "C:\Dev\synthetic-market-machine"
```

#### 2. PowerShell Performance
```powershell
# Disable progress bars for faster pip installs
$ProgressPreference = 'SilentlyContinue'
pip install -r requirements.txt
$ProgressPreference = 'Continue'
```

#### 3. Python Performance
```powershell
# Use faster pip mirror
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
```

## Testing Setup

### Run Test Suite
```powershell
# Activate virtual environment
.venv\Scripts\activate

# Run all tests
pytest

# Run with coverage
pytest --cov=smvm --cov-report=html

# Run specific test file
pytest tests/test_validation.py -v
```

### Performance Testing
```powershell
# Run performance benchmarks
python -m pytest tests/ --benchmark-only

# Memory profiling
python -m memory_profiler smvm/main.py
```

## Monitoring and Logs

### View Application Logs
```powershell
# Tail application logs
Get-Content logs/smvm.log -Wait -Tail 50

# Search for errors
Select-String -Path logs/smvm.log -Pattern "ERROR"
```

### System Monitoring
```powershell
# Check system resources
Get-Process python | Select-Object CPU, Memory

# Monitor disk usage
Get-PSDrive C | Select-Object Used, Free
```

## Backup and Recovery

### Backup SMVM Data
```powershell
# Backup virtual environment
Compress-Archive -Path .venv -DestinationPath "backups/venv-$(Get-Date -Format 'yyyyMMdd').zip"

# Backup database
Copy-Item smvm.db "backups/smvm-$(Get-Date -Format 'yyyyMMdd').db"
```

### Restore from Backup
```powershell
# Restore virtual environment
Expand-Archive -Path backups/venv-20231201.zip -DestinationPath .venv

# Restore database
Copy-Item backups/smvm-20231201.db smvm.db
```

## Security Considerations

### 1. File Permissions
```powershell
# Secure sensitive files
icacls .env /inheritance:r /grant:r "$($env:USERNAME):(R)"
icacls secrets/ /inheritance:r /grant:r "$($env:USERNAME):(R)"
```

### 2. Network Security
```powershell
# Configure firewall rules for development
New-NetFirewallRule -DisplayName "SMVM Development" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

### 3. Credential Management
```powershell
# Use Windows Credential Manager for sensitive data
# Or configure environment-specific credential stores
```

## Support and Resources

### Getting Help
- **Documentation**: See main README.md
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **Logs**: Check `logs/smvm.log` for error details

### Useful Commands
```powershell
# Quick health check
python -c "import smvm; print('SMVM import successful')"

# Check dependencies
pip check

# Update all packages
pip install --upgrade -r requirements.txt

# Clean build artifacts
Get-ChildItem -Path . -Include "*.pyc", "*.pyo", "__pycache__" -Recurse | Remove-Item -Force -Recurse
```

---

**Setup Complete** ✅ - Windows environment configured for SMVM development with Python 3.12.x, PowerShell 7+, and long path support.
