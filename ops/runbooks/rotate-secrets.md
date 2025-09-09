# Secret Rotation Procedure

This procedure outlines the process for rotating secrets and credentials in the Synthetic Market Validation Module (SMVM) environment.

## Overview

Secret rotation is critical for maintaining security posture. This procedure ensures:
- **Regular rotation**: Prevent long-term credential exposure
- **Minimal downtime**: Seamless rotation with fallback mechanisms
- **Audit trail**: Complete logging of rotation activities
- **Rollback capability**: Ability to revert if rotation fails

## Prerequisites

### Required Access
- **Administrator role**: For secret management systems
- **Database access**: For updating stored credentials
- **Application restart permissions**: For configuration reload
- **Backup access**: For credential backup and recovery

### Required Tools
- **Secret management CLI**: Vault, AWS Secrets Manager, or equivalent
- **Database client**: For credential updates
- **Backup tools**: For secure credential backup
- **Monitoring tools**: For rotation verification

### Preparation Checklist
- [ ] Rotation schedule communicated to stakeholders
- [ ] Backup of current secrets created
- [ ] Rotation testing completed in non-production
- [ ] Rollback procedure documented and tested
- [ ] Monitoring alerts configured for rotation period

## Rotation Procedure

### Step 1: Pre-Rotation Preparation

#### 1.1 Create Secret Backup
```bash
# Create timestamped backup
BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p backups/secrets/$BACKUP_DATE

# Backup current secrets
cp .env backups/secrets/$BACKUP_DATE/.env.backup
cp secrets/* backups/secrets/$BACKUP_DATE/ 2>/dev/null || true

# Encrypt backup
openssl enc -aes-256-cbc -salt -in backups/secrets/$BACKUP_DATE/.env.backup -out backups/secrets/$BACKUP_DATE/.env.backup.enc -k $BACKUP_KEY

# Log backup creation
echo "$(date): Secret backup created at backups/secrets/$BACKUP_DATE" >> secret_rotation.log
```

#### 1.2 Generate New Secrets
```bash
# Generate new database password
NEW_DB_PASSWORD=$(openssl rand -base64 32)

# Generate new JWT secret
NEW_JWT_SECRET=$(openssl rand -hex 64)

# Generate new API keys
NEW_API_KEY=$(openssl rand -hex 32)

# Store in temporary secure location
cat > new_secrets.temp << EOF
DATABASE_PASSWORD=$NEW_DB_PASSWORD
JWT_SECRET=$NEW_JWT_SECRET
API_KEY=$NEW_API_KEY
EOF

# Encrypt temporary file
openssl enc -aes-256-cbc -salt -in new_secrets.temp -out new_secrets.enc -k $TEMP_KEY
rm new_secrets.temp
```

#### 1.3 Test New Secrets
```bash
# Test database connection with new password
python -c "
import os
os.environ['DATABASE_PASSWORD'] = '$NEW_DB_PASSWORD'
# Test database connection code here
print('✅ Database connection test passed')
"

# Test JWT secret
python -c "
import jwt
secret = '$NEW_JWT_SECRET'
token = jwt.encode({'test': 'data'}, secret, algorithm='HS256')
decoded = jwt.decode(token, secret, algorithms=['HS256'])
print('✅ JWT secret test passed')
"
```

### Step 2: Database Secret Rotation

#### 2.1 Update Database Password
```bash
# Connect to database with current credentials
psql -h $DB_HOST -U $DB_USER -d $DB_NAME << EOF
-- Create new user with new password (if supported)
-- Or update existing user password
ALTER USER smvm_user PASSWORD '$NEW_DB_PASSWORD';

-- Verify password change
SELECT 'Password updated successfully' as status;
EOF

# Log database update
echo "$(date): Database password updated for user smvm_user" >> secret_rotation.log
```

#### 2.2 Update Application Configuration
```bash
# Update environment file
sed -i.bak "s/DATABASE_PASSWORD=.*/DATABASE_PASSWORD=$NEW_DB_PASSWORD/" .env

# Update configuration files
sed -i.bak "s/jwt_secret:.*/jwt_secret: $NEW_JWT_SECRET/" config/secrets.yaml
sed -i.bak "s/api_key:.*/api_key: $NEW_API_KEY/" config/secrets.yaml

# Log configuration updates
echo "$(date): Application configuration updated" >> secret_rotation.log
```

#### 2.3 Verify Database Connectivity
```bash
# Test connection with new password
python -c "
import os
import psycopg2

os.environ['DATABASE_PASSWORD'] = '$NEW_DB_PASSWORD'
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DATABASE_PASSWORD')
    )
    print('✅ New database password working')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"
```

### Step 3: Application Secret Rotation

#### 3.1 Update JWT Secret
```bash
# Update JWT secret in configuration
export JWT_SECRET=$NEW_JWT_SECRET

# Restart application to load new secret
systemctl restart smvm-api  # Linux systemd
# or
docker-compose restart smvm  # Docker

# Wait for restart
sleep 30

# Verify application health
curl -f http://localhost:8000/health || exit 1

echo "$(date): JWT secret rotated and application restarted" >> secret_rotation.log
```

#### 3.2 Update API Keys
```bash
# Update API key in configuration
export API_KEY=$NEW_API_KEY

# Update any external systems using the API key
# Example: Update monitoring systems, external APIs, etc.

# Test API key functionality
curl -H "X-API-Key: $NEW_API_KEY" http://localhost:8000/api/test || exit 1

echo "$(date): API key rotated" >> secret_rotation.log
```

#### 3.3 Update External Integrations
```bash
# Update secrets in external systems
# Example: AWS Secrets Manager, HashiCorp Vault, etc.

# AWS CLI example
aws secretsmanager update-secret \
    --secret-id smvm/database-password \
    --secret-string "$NEW_DB_PASSWORD"

aws secretsmanager update-secret \
    --secret-id smvm/jwt-secret \
    --secret-string "$NEW_JWT_SECRET"

echo "$(date): External integrations updated" >> secret_rotation.log
```

### Step 4: Verification and Testing

#### 4.1 Functional Testing
```bash
# Test all application endpoints
python -m pytest tests/test_api.py -v

# Test database operations
python -c "
# Test database read/write operations
import smvm.database as db
conn = db.get_connection()
# Perform test operations
print('✅ Database operations working')
"

# Test authentication
python -c "
# Test JWT token generation and validation
import smvm.auth as auth
token = auth.generate_token({'user': 'test'})
user = auth.validate_token(token)
print('✅ Authentication working')
"
```

#### 4.2 Security Testing
```bash
# Test old secrets are invalidated
python -c "
# Attempt to use old JWT secret
import jwt
try:
    old_token = jwt.encode({'test': 'data'}, 'old_secret', algorithm='HS256')
    print('❌ Old secret still works - SECURITY ISSUE')
except:
    print('✅ Old secret properly invalidated')
"

# Test new secrets work
python -c "
# Test new JWT secret
import jwt
token = jwt.encode({'test': 'data'}, '$NEW_JWT_SECRET', algorithm='HS256')
decoded = jwt.decode(token, '$NEW_JWT_SECRET', algorithms=['HS256'])
print('✅ New secret working correctly')
"
```

#### 4.3 Performance Testing
```bash
# Test application performance after rotation
ab -n 1000 -c 10 http://localhost:8000/api/test

# Monitor resource usage
top -bn1 | grep python

# Check for any performance degradation
echo "$(date): Performance test completed" >> secret_rotation.log
```

### Step 5: Post-Rotation Cleanup

#### 5.1 Secure Old Secrets
```bash
# Overwrite old secrets in memory
OLD_DB_PASSWORD=""
OLD_JWT_SECRET=""
OLD_API_KEY=""

# Remove temporary files
rm -f new_secrets.enc
shred -u backups/secrets/$BACKUP_DATE/.env.backup

# Log cleanup
echo "$(date): Old secrets securely cleaned up" >> secret_rotation.log
```

#### 5.2 Update Documentation
```bash
# Update secret rotation log
cat >> secret_rotation_history.md << EOF
## Rotation: $(date)

### Secrets Rotated
- Database password: ✅ Rotated
- JWT secret: ✅ Rotated
- API key: ✅ Rotated

### Testing Results
- Functional tests: ✅ Passed
- Security tests: ✅ Passed
- Performance tests: ✅ Passed

### Issues Encountered
- [List any issues and resolutions]

### Next Rotation
- Scheduled: $(date -d '+90 days')
- Responsible: [team member]
EOF
```

#### 5.3 Schedule Next Rotation
```bash
# Add to crontab for automated reminder
(crontab -l ; echo "0 9 $(date -d '+85 days' +%d) $(date -d '+85 days' +%m) * echo 'Secret rotation due in 5 days'") | crontab -

# Update monitoring alerts
# Configure alerts for rotation completion
```

## Monitoring and Alerts

### Rotation Monitoring
```bash
# Set up monitoring for rotation period
cat > monitor_rotation.sh << 'EOF'
#!/bin/bash
# Monitor application health during rotation
while true; do
    if curl -f http://localhost:8000/health > /dev/null; then
        echo "$(date): Application healthy" >> rotation_monitor.log
    else
        echo "$(date): Application unhealthy - ALERT" >> rotation_monitor.log
        # Send alert
        curl -X POST -H 'Content-type: application/json' \
             --data '{"alert": "SMVM rotation issue"}' \
             $ALERT_WEBHOOK
    fi
    sleep 60
done
EOF

chmod +x monitor_rotation.sh
./monitor_rotation.sh &
```

### Alert Configuration
```bash
# Configure alerts for rotation events
cat > alerts/rotation_alerts.yaml << EOF
alerts:
  - name: rotation_started
    condition: rotation_process_begins
    message: "Secret rotation started"
    severity: info

  - name: rotation_completed
    condition: all_tests_pass
    message: "Secret rotation completed successfully"
    severity: info

  - name: rotation_failed
    condition: critical_test_fails
    message: "Secret rotation failed - manual intervention required"
    severity: critical

  - name: application_degraded
    condition: health_check_fails
    message: "Application degraded after rotation"
    severity: warning
EOF
```

## Rollback Procedures

### Emergency Rollback
```bash
# Immediate rollback to backup
cp backups/secrets/$BACKUP_DATE/.env.backup .env
cp backups/secrets/$BACKUP_DATE/secrets/* secrets/

# Restart application
systemctl restart smvm-api

# Verify rollback
curl -f http://localhost:8000/health

echo "$(date): Emergency rollback completed" >> secret_rotation.log
```

### Partial Rollback
```bash
# Rollback specific secrets
# Restore from backup
cp backups/secrets/$BACKUP_DATE/.env.backup .env

# Selective restart
systemctl reload smvm-api

# Test specific functionality
python -m pytest tests/test_auth.py
```

## Troubleshooting

### Common Issues

#### Database Connection Failures
```bash
# Check database logs
tail -f /var/log/postgresql/postgresql.log

# Verify password in database
psql -h $DB_HOST -U postgres -c "SELECT usename, passwd FROM pg_shadow WHERE usename = 'smvm_user';"

# Reset password if needed
psql -h $DB_HOST -U postgres -c "ALTER USER smvm_user PASSWORD '$NEW_DB_PASSWORD';"
```

#### Application Restart Issues
```bash
# Check application logs
tail -f logs/smvm.log

# Verify configuration syntax
python -c "import yaml; yaml.safe_load(open('config/secrets.yaml'))"

# Manual restart
killall python
python -m smvm.main &
```

#### External System Updates
```bash
# Check external system connectivity
curl -f https://external-api.example.com/health

# Verify API key acceptance
curl -H "Authorization: Bearer $NEW_API_KEY" https://external-api.example.com/test

# Update external system configuration
# Follow external system documentation
```

## Success Criteria

### Rotation Completion
- [ ] All secrets successfully rotated
- [ ] Application running with new secrets
- [ ] All tests passing
- [ ] No security alerts triggered
- [ ] Backup created and secured

### Post-Rotation Validation
- [ ] Authentication working correctly
- [ ] Database operations functional
- [ ] External integrations operational
- [ ] Performance within acceptable ranges
- [ ] Monitoring systems updated

## Documentation Requirements

### Rotation Record
```bash
# Maintain comprehensive rotation history
cat >> rotation_audit.md << EOF
# Secret Rotation Audit

## Rotation Event
- Date: $(date)
- Performed by: [operator name]
- Environment: [production/staging/development]
- Duration: [time taken]

## Secrets Rotated
- Database credentials: ✅
- JWT secrets: ✅
- API keys: ✅
- External system credentials: ✅

## Verification Results
- Functional testing: ✅
- Security testing: ✅
- Performance testing: ✅
- Integration testing: ✅

## Issues and Resolutions
- [Issue 1]: [Resolution]
- [Issue 2]: [Resolution]

## Next Steps
- Schedule next rotation: $(date -d '+90 days')
- Update rotation procedures: [any needed changes]
- Team training: [any training needs identified]
EOF
```

---

**Procedure Version**: 1.0
**Last Updated**: 2024-12-XX
**Review Frequency**: Quarterly
**Next Review**: 2025-03-XX

*This procedure must be reviewed and updated after each rotation.*
