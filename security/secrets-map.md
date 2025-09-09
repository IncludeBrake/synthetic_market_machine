# SMVM Secrets Management Map

## Overview

This document defines the complete secrets management strategy for the Synthetic Market Validation Module (SMVM). All secrets must be managed through environment variables with secure storage mechanisms, never stored in code or configuration files.

## Secrets Storage Hierarchy

### Production (Preferred)
```yaml
# HashiCorp Vault
vault:
  address: "https://vault.smvm.company.com"
  auth_method: "kubernetes"
  secrets_path: "secret/data/smvm"
  role: "smvm-service"
```

### Development/Testing (Interim)
```yaml
# Windows Credential Manager
credential_manager:
  target: "SMVM_Development"
  username: "smvm_service"
  persistence: "local_machine"
```

### Migration Path
1. **Phase 1 (Current)**: Windows Credential Manager for local development
2. **Phase 2 (3 months)**: Vault implementation for development
3. **Phase 3 (6 months)**: Vault as default for all environments
4. **Phase 4 (12 months)**: Windows Credential Manager deprecated

## Environment Variables Map

### Database Credentials
| Variable | Description | Owner | Rotation | Storage |
|----------|-------------|-------|----------|---------|
| `SMVM_DB_HOST` | Database hostname | DBA Team | 90 days | Vault |
| `SMVM_DB_PORT` | Database port | DBA Team | N/A | Config |
| `SMVM_DB_NAME` | Database name | DBA Team | N/A | Config |
| `SMVM_DB_USER` | Database username | DBA Team | 90 days | Vault |
| `SMVM_DB_PASSWORD` | Database password | DBA Team | 30 days | Vault |
| `SMVM_DB_SSL_CERT` | SSL certificate path | Security Team | 365 days | Vault |

### API Keys & Tokens
| Variable | Description | Owner | Rotation | Storage |
|----------|-------------|-------|----------|---------|
| `SMVM_TRACTIONBUILD_API_KEY` | TractionBuild integration | Platform Team | 90 days | Vault |
| `SMVM_OPENAI_API_KEY` | OpenAI service access | AI Team | 30 days | Vault |
| `SMVM_SENDGRID_API_KEY` | Email service access | DevOps Team | 90 days | Vault |
| `SMVM_SENTRY_DSN` | Error monitoring | DevOps Team | N/A | Config |
| `SMVM_DATADOG_API_KEY` | Metrics collection | DevOps Team | 90 days | Vault |

### Cloud Service Credentials
| Variable | Description | Owner | Rotation | Storage |
|----------|-------------|-------|----------|---------|
| `AWS_ACCESS_KEY_ID` | AWS access key | Cloud Team | 90 days | Vault |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | Cloud Team | 90 days | Vault |
| `AWS_DEFAULT_REGION` | AWS region | Cloud Team | N/A | Config |
| `AZURE_CLIENT_ID` | Azure service principal | Cloud Team | 90 days | Vault |
| `AZURE_CLIENT_SECRET` | Azure client secret | Cloud Team | 90 days | Vault |
| `AZURE_TENANT_ID` | Azure tenant ID | Cloud Team | N/A | Config |
| `GCP_SERVICE_ACCOUNT_KEY` | GCP service account JSON | Cloud Team | 90 days | Vault |

### Internal Service Secrets
| Variable | Description | Owner | Rotation | Storage |
|----------|-------------|-------|----------|---------|
| `SMVM_JWT_SECRET` | JWT signing secret | Security Team | 30 days | Vault |
| `SMVM_ENCRYPTION_KEY` | Data encryption key | Security Team | 365 days | Vault |
| `SMVM_REDIS_PASSWORD` | Redis cache password | DevOps Team | 90 days | Vault |
| `SMVM_RABBITMQ_PASSWORD` | Message queue password | DevOps Team | 90 days | Vault |

### Third-Party Service Credentials
| Variable | Description | Owner | Rotation | Storage |
|----------|-------------|-------|----------|---------|
| `SMVM_STRIPE_SECRET_KEY` | Payment processing | Finance Team | 90 days | Vault |
| `SMVM_TWILIO_ACCOUNT_SID` | SMS service | DevOps Team | 90 days | Vault |
| `SMVM_TWILIO_AUTH_TOKEN` | SMS auth token | DevOps Team | 90 days | Vault |
| `SMVM_SLACK_BOT_TOKEN` | Slack notifications | DevOps Team | 90 days | Vault |

## Secret Access Patterns

### Environment Variable Access
```python
import os
from typing import Optional

def get_secret(key: str, default: Optional[str] = None) -> str:
    """Get secret from environment variable with validation"""
    value = os.getenv(key, default)

    if value is None:
        raise ValueError(f"Required secret '{key}' not found in environment")

    # Validate secret format (basic checks)
    if key.endswith('_KEY') or key.endswith('_SECRET'):
        if len(value) < 16:
            raise ValueError(f"Secret '{key}' appears to be too short")

    return value

# Usage examples
db_password = get_secret('SMVM_DB_PASSWORD')
api_key = get_secret('SMVM_OPENAI_API_KEY')
```

### Vault Integration
```python
import hvac
import os

class VaultClient:
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_ADDR'),
            token=os.getenv('VAULT_TOKEN')
        )

    def get_secret(self, path: str, key: str) -> str:
        """Retrieve secret from Vault"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data'][key]
        except Exception as e:
            logger.error(f"Failed to retrieve secret from Vault: {e}")
            raise

# Usage
vault = VaultClient()
db_password = vault.get_secret('secret/data/smvm/database', 'password')
```

### Windows Credential Manager (Development Only)
```python
import keyring
import os

def get_credential(service: str, username: str) -> str:
    """Get credential from Windows Credential Manager"""
    password = keyring.get_password(service, username)

    if password is None:
        # Fallback to environment variable
        env_key = f"{service.upper()}_{username.upper()}_PASSWORD"
        password = os.getenv(env_key)

        if password is None:
            raise ValueError(f"Credential not found for {service}/{username}")

    return password

# Usage
db_password = get_credential('SMVM_Database', 'smvm_user')
```

## Rotation Procedures

### Automated Rotation
```python
import boto3
from datetime import datetime, timedelta

def rotate_database_credentials():
    """Automated database credential rotation"""
    rds = boto3.client('rds')

    # Generate new password
    new_password = generate_secure_password()

    # Update database user
    rds.modify_db_instance(
        DBInstanceIdentifier='smvm-database',
        MasterUserPassword=new_password,
        ApplyImmediately=True
    )

    # Update Vault
    vault_client.write_secret(
        path='secret/data/smvm/database',
        data={'password': new_password}
    )

    # Update application configuration
    update_application_config('SMVM_DB_PASSWORD', new_password)

    # Log rotation event
    logger.info("Database credentials rotated successfully")
```

### Manual Rotation Checklist
1. **Generate New Secret**
   ```bash
   # Generate secure password
   openssl rand -base64 32
   ```

2. **Update Storage**
   ```bash
   # Update Vault
   vault kv put secret/smvm/api_keys/openai key=new_key_value

   # Update Windows Credential Manager (dev only)
   python -c "import keyring; keyring.set_password('SMVM_API', 'openai', 'new_key')"
   ```

3. **Update Application**
   ```bash
   # Restart services
   docker-compose restart smvm-services

   # Verify functionality
   curl -H "Authorization: Bearer $NEW_TOKEN" https://api.smvm.company.com/health
   ```

4. **Revoke Old Secret**
   ```bash
   # Disable old API key
   curl -X DELETE https://api.openai.com/v1/keys/$OLD_KEY_ID \
        -H "Authorization: Bearer $MASTER_KEY"

   # Remove from Vault history
   vault kv metadata delete secret/smvm/api_keys/openai
   ```

5. **Verification**
   ```bash
   # Check application logs
   kubectl logs -l app=smvm-api

   # Verify metrics
   curl https://monitoring.smvm.company.com/metrics | grep secret_rotation
   ```

## Monitoring & Alerting

### Secret Health Checks
```python
def check_secret_health() -> dict:
    """Check health of secret management system"""
    health = {
        'vault_accessible': False,
        'secrets_rotated_recently': False,
        'no_expired_secrets': False,
        'backup_current': False
    }

    # Check Vault accessibility
    try:
        vault_client.is_authenticated()
        health['vault_accessible'] = True
    except:
        pass

    # Check rotation status
    last_rotation = get_last_secret_rotation()
    if datetime.now() - last_rotation < timedelta(days=30):
        health['secrets_rotated_recently'] = True

    # Check for expired secrets
    expired_secrets = get_expired_secrets()
    if not expired_secrets:
        health['no_expired_secrets'] = True

    return health
```

### Alert Rules
```prometheus
# Vault Inaccessible
ALERT VaultInaccessible
  IF vault_up == 0
  FOR 5m
  LABELS { severity = "critical" }
  ANNOTATIONS {
    summary = "Vault service is inaccessible",
    description = "SMVM cannot access secrets from Vault"
  }

# Secrets Expiring Soon
ALERT SecretsExpiring
  IF secrets_days_until_expiry < 7
  FOR 1h
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary = "Secrets expiring within 7 days",
    description = "{{ $value }} secrets will expire soon"
  }

# Secret Rotation Failed
ALERT SecretRotationFailed
  IF increase(secret_rotation_failures_total[1h]) > 0
  FOR 5m
  LABELS { severity = "error" }
  ANNOTATIONS {
    summary = "Secret rotation has failed",
    description = "Automatic secret rotation failed for {{ $labels.secret_type }}"
  }
```

## Compliance & Audit

### Access Logging
```json
{
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "event_type": "SECRET_ACCESS",
  "user_id": "analyst@company.com",
  "service": "simulation",
  "secret_key": "SMVM_OPENAI_API_KEY",
  "access_type": "read",
  "success": true,
  "ip_address": "192.168.1.100",
  "user_agent": "SMVM-CLI/1.0.0"
}
```

### Compliance Checks
- **PCI DSS**: No cardholder data in logs
- **SOX**: Audit trail of all secret access
- **GDPR**: Data encryption and access controls
- **ISO 27001**: Systematic secret management

## Emergency Procedures

### Secret Compromise Response
1. **Immediate Actions**
   ```bash
   # Revoke compromised secret
   vault kv delete secret/smvm/api_keys/compromised_key

   # Generate emergency replacement
   new_secret = generate_emergency_secret()

   # Update with emergency credentials
   vault kv put secret/smvm/api_keys/compromised_key value=$new_secret
   ```

2. **Investigation**
   ```bash
   # Check access logs
   grep "compromised_key" /var/log/smvm/audit.log

   # Identify affected systems
   kubectl get pods -l secret=compromised_key
   ```

3. **Recovery**
   ```bash
   # Rotate all related secrets
   ./scripts/rotate-secrets.sh --emergency

   # Update application configurations
   kubectl rollout restart deployment/smvm-api
   ```

4. **Post-Incident Review**
   ```bash
   # Analyze incident timeline
   ./scripts/incident-analysis.sh --secret-compromise

   # Update security controls
   ./scripts/update-security-policies.sh
   ```

## Development Guidelines

### Local Development Setup
```bash
# Create local secrets file (NEVER commit)
touch .env.local
echo "SMVM_DB_PASSWORD=dev_password_123" >> .env.local
echo "SMVM_OPENAI_API_KEY=sk-dev-..." >> .env.local

# Load environment
export $(cat .env.local | xargs)

# Verify secrets loaded
python -c "import os; print('Secrets loaded:', bool(os.getenv('SMVM_DB_PASSWORD')))"
```

### Testing with Secrets
```python
import pytest
from unittest.mock import patch

@patch.dict(os.environ, {
    'SMVM_DB_PASSWORD': 'test_password',
    'SMVM_OPENAI_API_KEY': 'test_key'
})
def test_with_mocked_secrets():
    """Test function with mocked secrets"""
    from smvm.config import get_database_config

    config = get_database_config()
    assert config['password'] == 'test_password'
```

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX
**Owner**: Security Team
**Reviewers**: DevOps Team, Compliance Officer

*This secrets management map ensures secure, auditable, and compliant secret handling across all SMVM environments.*
