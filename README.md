# Synthetic Market Validation Module (SMVM)

[![Python Version](https://img.shields.io/badge/python-3.12.x-blue.svg)](https://www.python.org/downloads/)
[![CI Status](https://github.com/your-org/synthetic-market-machine/workflows/CI/badge.svg)](https://github.com/your-org/synthetic-market-machine/actions)

A comprehensive validation framework for synthetic market data generation, analysis, and governance.

## Overview

The Synthetic Market Validation Module (SMVM) provides a secure, reproducible environment for validating synthetic market data against real-world financial scenarios. This module ensures data quality, regulatory compliance, and operational integrity through automated testing, observability, and governance controls.

## Architecture

```
SMVM/
├── .venv/                    # Python 3.12.x virtual environment
├── contracts/               # Data contracts and schemas
├── policies/                # Governance and security policies
├── observability/           # Logging and monitoring components
├── tests/                   # Validation test suites
├── docs/                    # Documentation and runbooks
└── ops/                     # Operational procedures
```

## Python Protocol

- **Primary**: Python 3.12.x (required)
- **Fallback**: Python 3.11.13 (allowed)
- **Blocked**: Python ≥3.13.x
- **Virtual Environment**: Required (.venv)
- **Dependencies**: Pinned major versions in `requirements.txt`
- **Lockfile**: Exact versions in `requirements.lock`

## Phase Gates

### Phase 0: Foundation ✅
- [x] Python 3.12.x virtual environment setup
- [x] Governance policies and security guardrails
- [x] CI/CD pipeline configuration
- [x] Documentation framework established

### Phase 1: Core Infrastructure
- [ ] Data pipeline architecture
- [ ] Synthetic data generation engine
- [ ] Validation framework
- [ ] Basic observability setup

### Phase 2: Advanced Features
- [ ] Market simulation models
- [ ] Risk assessment algorithms
- [ ] Performance optimization
- [ ] Scalability testing

### Phase 3: Production Readiness
- [ ] Enterprise integration
- [ ] Regulatory compliance validation
- [ ] Disaster recovery procedures
- [ ] Performance benchmarking

## Quick Start

### Prerequisites

- Python 3.12.x installed
- Git for version control
- PowerShell 7+ (Windows)

### Setup

1. **Clone and navigate**:
   ```bash
   git clone <repository-url>
   cd synthetic-market-machine
   ```

2. **Activate virtual environment**:
   ```bash
   # Windows PowerShell
   .venv\Scripts\activate

   # Linux/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify setup**:
   ```bash
   python --version  # Should show 3.12.x
   pip list         # Verify installed packages
   ```

### Running SMVM

```bash
# Run validation suite
python -m pytest tests/ -v

# Start development server
uvicorn app.main:app --reload

# Run data validation
python -m smvm validate --config config/validation.yaml
```

## Documentation Structure

| Document | Purpose | Location |
|----------|---------|----------|
| Architecture Decisions | Technical choices and rationale | `docs/architecture/` |
| Policies | Governance and security rules | `docs/policies/` |
| Setup Guides | Platform-specific setup | `docs/os/` |
| Runbooks | Operational procedures | `ops/runbooks/` |
| Reports | Phase outputs and metrics | `reports/` |

## Key Policies

### Security & Compliance
- **No secrets** committed to repository
- **RBAC** enforced for all operations
- **Data zones**: RED (untrusted) → AMBER (validated) → GREEN (approved)
- **Incident response** procedures documented

### Development Standards
- **Type hints** required for all new code
- **Tests** must achieve 80%+ coverage
- **Documentation** updated with code changes
- **Code review** required for all changes

### Observability Requirements
- **Structured logging** with correlation IDs
- **Health endpoints** exposed on all services
- **Metrics collection** for performance monitoring
- **Error tracking** with detailed context

## Development Workflow

### Branch Strategy
```
main          # Production-ready code
├── develop     # Integration branch
│   ├── feature/*  # Feature branches
│   └── hotfix/*   # Emergency fixes
```

### Commit Convention
```
WHY: Brief reason for change
WHAT: What was changed
HOW: Implementation approach
RISK: Potential impact
VERIFY: How to test/verify
```

### Testing Strategy
- **Unit tests**: Individual component validation
- **Integration tests**: End-to-end workflow validation
- **Performance tests**: Load and scalability validation
- **Security tests**: Vulnerability and compliance checks

## API Reference

### Core Endpoints

- `GET /health` - Service health check
- `POST /validate` - Run data validation
- `GET /metrics` - Performance metrics
- `POST /simulate` - Market simulation

### Configuration

All configuration is managed through environment variables and `.env` files:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/smvm

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret

# Observability
LOG_LEVEL=INFO
METRICS_PORT=9090
```

## Troubleshooting

### Common Issues

1. **Python version conflicts**:
   ```bash
   # Check version
   python --version

   # Recreate virtual environment
   rm -rf .venv
   python -m venv .venv
   ```

2. **Dependency conflicts**:
   ```bash
   # Reinstall from lockfile
   pip install -r requirements.lock
   ```

3. **Permission errors**:
   ```bash
   # Windows: Run as administrator
   # Linux/macOS: Check file permissions
   ```

### Logs and Debugging

```bash
# View application logs
tail -f logs/smvm.log

# Enable debug mode
export LOG_LEVEL=DEBUG
python -m smvm
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes following the coding standards
4. Add tests for new functionality
5. Update documentation
6. Submit a pull request

### Code Quality Gates

- ✅ Linting passes (`flake8`)
- ✅ Type checking passes (`mypy`)
- ✅ Tests pass (80%+ coverage)
- ✅ Security scan passes
- ✅ Documentation updated

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See `docs/` directory
- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Security**: See `docs/policies/SECURITY.md` for vulnerability reporting

---

**Phase 0 Complete** ✅ - Foundation established with Python 3.12.x, governance policies, and CI pipeline.
