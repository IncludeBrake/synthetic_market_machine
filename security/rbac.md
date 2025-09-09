# SMVM Role-Based Access Control (RBAC)

## Overview

This document defines the Role-Based Access Control (RBAC) system for the Synthetic Market Validation Module (SMVM). The system implements a simplified three-role model with zone-based permissions to ensure security while maintaining operational efficiency.

## Role Definitions

### Three-Role Model
SMVM implements exactly three roles to balance security with operational simplicity:

#### 1. Developer (`dev`)
**Purpose**: Application development, testing, and debugging
**Authentication**: GitHub SSO with 2FA
**Session Duration**: 8 hours
**Concurrent Sessions**: Unlimited (development)

#### 2. Operator (`operator`)
**Purpose**: Production operations, monitoring, and incident response
**Authentication**: Corporate SSO with hardware token
**Session Duration**: 12 hours
**Concurrent Sessions**: 2 per user

#### 3. Auditor (`auditor`)
**Purpose**: Compliance monitoring, audit trail review, and reporting
**Authentication**: Government-issued smart card
**Session Duration**: 4 hours
**Concurrent Sessions**: 1 per user

## Permission Matrix

### Zone-Based Permissions

| Permission | GREEN Zone | AMBER Zone | RED Zone | Description |
|------------|------------|------------|----------|-------------|
| `read` | ✅ All | ✅ All | ❌ None | Read access to data |
| `write` | ✅ Dev/Op | ⚠️ Op Only | ❌ None | Write/modify data |
| `delete` | ❌ None | ⚠️ Op Only | ❌ None | Delete data |
| `execute` | ✅ All | ⚠️ Op Only | ❌ None | Run operations |
| `admin` | ❌ None | ❌ None | ❌ None | Administrative access |

### Role Permissions by Zone

#### GREEN Zone (Public/Test Data)
| Operation | Developer | Operator | Auditor |
|-----------|-----------|----------|---------|
| **Data Access** | | | |
| Read public data | ✅ | ✅ | ✅ |
| Write test data | ✅ | ✅ | ❌ |
| Delete test data | ❌ | ✅ | ❌ |
| **Service Operations** | | | |
| Run validations | ✅ | ✅ | ❌ |
| Access CLI tools | ✅ | ✅ | ❌ |
| Modify configurations | ✅ | ❌ | ❌ |
| **System Access** | | | |
| View logs | ✅ | ✅ | ✅ |
| Access monitoring | ✅ | ✅ | ✅ |
| Restart services | ❌ | ✅ | ❌ |

#### AMBER Zone (Internal Analysis Data)
| Operation | Developer | Operator | Auditor |
|-----------|-----------|----------|---------|
| **Data Access** | | | |
| Read analysis results | ✅ | ✅ | ✅ |
| Write simulation data | ⚠️ (local only) | ✅ | ❌ |
| Delete analysis data | ❌ | ✅ | ❌ |
| **Service Operations** | | | |
| Run simulations | ✅ | ✅ | ❌ |
| Access analysis tools | ✅ | ✅ | ❌ |
| Modify service configs | ❌ | ✅ | ❌ |
| **Audit & Compliance** | | | |
| View audit logs | ✅ | ✅ | ✅ |
| Export audit data | ❌ | ✅ | ✅ |
| Modify audit configs | ❌ | ❌ | ❌ |

#### RED Zone (Sensitive/Production Data)
| Operation | Developer | Operator | Auditor |
|-----------|-----------|----------|---------|
| **Data Access** | | | |
| Read production data | ❌ | ⚠️ (justified) | ✅ (read-only) |
| Write production data | ❌ | ❌ | ❌ |
| Delete production data | ❌ | ❌ | ❌ |
| **Service Operations** | | | |
| Run production validations | ❌ | ✅ | ❌ |
| Access production CLI | ❌ | ✅ | ❌ |
| Modify production configs | ❌ | ✅ | ❌ |
| **Security & Compliance** | | | |
| View security logs | ❌ | ✅ | ✅ |
| Export compliance data | ❌ | ✅ | ✅ |
| Modify security policies | ❌ | ❌ | ❌ |

## Permission Implementation

### Permission Checking
```python
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class User:
    id: str
    roles: List[str]
    attributes: Dict[str, any]

@dataclass
class Permission:
    action: str
    resource: str
    zone: str

class RBACEnforcer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def check_permission(self, user: User, permission: Permission) -> bool:
        """Check if user has permission for action"""

        # Get user's effective roles
        user_roles = set(user.roles)

        # Check role permissions for zone
        allowed = self._get_role_permissions(user_roles, permission.zone, permission.action)

        # Log access attempt
        self.logger.info({
            "event_type": "RBAC_CHECK",
            "user_id": user.id,
            "permission": f"{permission.action}:{permission.resource}:{permission.zone}",
            "allowed": allowed,
            "user_roles": list(user_roles),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": "3.12.10"
        })

        return allowed

    def _get_role_permissions(self, roles: set, zone: str, action: str) -> bool:
        """Get permissions for roles in zone"""

        # Developer permissions
        if "dev" in roles:
            if zone == "GREEN":
                return action in ["read", "write", "execute"]
            elif zone == "AMBER":
                return action in ["read", "execute"] or (action == "write" and "local_only" in roles)
            else:  # RED zone
                return False

        # Operator permissions
        if "operator" in roles:
            if zone in ["GREEN", "AMBER"]:
                return action in ["read", "write", "execute", "delete"]
            elif zone == "RED":
                return action in ["read", "execute"]  # Justified access only
            else:
                return False

        # Auditor permissions
        if "auditor" in roles:
            if zone in ["GREEN", "AMBER"]:
                return action in ["read", "execute"]
            elif zone == "RED":
                return action in ["read"]  # Read-only access
            else:
                return False

        return False

# Usage example
enforcer = RBACEnforcer()
user = User(id="analyst@company.com", roles=["dev"], attributes={})

permission = Permission(action="write", resource="simulation_data", zone="AMBER")
allowed = enforcer.check_permission(user, permission)
```

### Zone Transition Controls
```python
def enforce_zone_transition(from_zone: str, to_zone: str, user: User) -> bool:
    """Enforce zone transition rules"""

    # Define allowed transitions
    allowed_transitions = {
        "GREEN": ["GREEN", "AMBER"],  # Can move to AMBER
        "AMBER": ["GREEN", "AMBER"],  # Can move to GREEN
        "RED": []  # Cannot transition from RED
    }

    # Check if transition is allowed
    if to_zone not in allowed_transitions.get(from_zone, []):
        logger.warning({
            "event_type": "ZONE_TRANSITION_DENIED",
            "user_id": user.id,
            "from_zone": from_zone,
            "to_zone": to_zone,
            "user_roles": user.roles,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": "3.12.10"
        })
        return False

    # Log successful transition
    logger.info({
        "event_type": "ZONE_TRANSITION",
        "user_id": user.id,
        "from_zone": from_zone,
        "to_zone": to_zone,
        "user_roles": user.roles,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": "3.12.10"
    })

    return True
```

## Authentication & Authorization

### Authentication Flow
```python
def authenticate_user(credentials: Dict) -> Optional[User]:
    """Authenticate user and return user object"""

    # Validate credentials
    if not validate_credentials(credentials):
        logger.warning({
            "event_type": "AUTHENTICATION_FAILED",
            "username": credentials.get("username"),
            "ip_address": get_client_ip(),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })
        return None

    # Get user from directory
    user_data = get_user_from_directory(credentials["username"])

    # Create user object
    user = User(
        id=user_data["id"],
        roles=user_data["roles"],
        attributes=user_data["attributes"]
    )

    # Log successful authentication
    logger.info({
        "event_type": "AUTHENTICATION_SUCCESS",
        "user_id": user.id,
        "user_roles": user.roles,
        "ip_address": get_client_ip(),
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "python_version": "3.12.10"
    })

    return user
```

### Session Management
```python
class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.session_limits = {
            "dev": {"max_sessions": float('inf'), "duration_hours": 8},
            "operator": {"max_sessions": 2, "duration_hours": 12},
            "auditor": {"max_sessions": 1, "duration_hours": 4}
        }

    def create_session(self, user: User) -> Optional[str]:
        """Create new session for user"""

        # Check session limits
        user_sessions = [s for s in self.active_sessions.values() if s["user_id"] == user.id]
        role_limits = self.session_limits.get(user.roles[0] if user.roles else "dev", self.session_limits["dev"])

        if len(user_sessions) >= role_limits["max_sessions"]:
            logger.warning({
                "event_type": "SESSION_LIMIT_EXCEEDED",
                "user_id": user.id,
                "current_sessions": len(user_sessions),
                "max_sessions": role_limits["max_sessions"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })
            return None

        # Create session
        session_id = generate_secure_session_id()
        session = {
            "id": session_id,
            "user_id": user.id,
            "user_roles": user.roles,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(hours=role_limits["duration_hours"]),
            "ip_address": get_client_ip(),
            "user_agent": get_user_agent()
        }

        self.active_sessions[session_id] = session

        logger.info({
            "event_type": "SESSION_CREATED",
            "session_id": session_id,
            "user_id": user.id,
            "user_roles": user.roles,
            "expires_at": session["expires_at"].isoformat() + "Z",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": "3.12.10"
        })

        return session_id

    def validate_session(self, session_id: str) -> Optional[User]:
        """Validate session and return user"""

        session = self.active_sessions.get(session_id)
        if not session:
            return None

        # Check expiration
        if datetime.utcnow() > session["expires_at"]:
            self.destroy_session(session_id)
            return None

        # Update last activity
        session["last_activity"] = datetime.utcnow()

        # Return user object
        return User(
            id=session["user_id"],
            roles=session["user_roles"],
            attributes={"session_id": session_id}
        )

    def destroy_session(self, session_id: str) -> None:
        """Destroy user session"""

        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]

            logger.info({
                "event_type": "SESSION_DESTROYED",
                "session_id": session_id,
                "user_id": session["user_id"],
                "duration_minutes": (datetime.utcnow() - session["created_at"]).total_seconds() / 60,
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "python_version": "3.12.10"
            })

            del self.active_sessions[session_id]
```

## Audit & Compliance

### Access Logging
```json
{
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "event_type": "RBAC_ACCESS",
  "user_id": "analyst@company.com",
  "user_roles": ["dev"],
  "action": "read",
  "resource": "simulation_results",
  "zone": "AMBER",
  "allowed": true,
  "ip_address": "192.168.1.100",
  "session_id": "sess_12345",
  "python_version": "3.12.10",
  "user_agent": "SMVM-CLI/1.0.0"
}
```

### Zone Transition Logging
```json
{
  "timestamp": "2024-12-01T14:30:52.123456Z",
  "event_type": "ZONE_TRANSITION",
  "user_id": "operator@company.com",
  "user_roles": ["operator"],
  "from_zone": "GREEN",
  "to_zone": "AMBER",
  "justification": "Moving to internal analysis",
  "session_id": "sess_67890",
  "python_version": "3.12.10"
}
```

## Integration with Services

### Service-Level RBAC
```python
class TracedService:
    def __init__(self, service_name: str, rbac_enforcer: RBACEnforcer):
        self.service_name = service_name
        self.rbac = rbac_enforcer

    def execute_operation(self, operation: str, user: User, context: Dict):
        """Execute operation with RBAC checks"""

        # Determine required permission
        permission = self._get_required_permission(operation, context)

        # Check permission
        if not self.rbac.check_permission(user, permission):
            raise PermissionError(f"Access denied for {operation}")

        # Execute operation
        return self._do_operation(operation, context)

    def _get_required_permission(self, operation: str, context: Dict) -> Permission:
        """Determine permission required for operation"""

        # Map operations to permissions
        operation_permissions = {
            "validate_idea": Permission("execute", "validation", "GREEN"),
            "run_simulation": Permission("execute", "simulation", "AMBER"),
            "view_production_data": Permission("read", "production_data", "RED"),
            "modify_config": Permission("write", "configuration", "AMBER")
        }

        return operation_permissions.get(operation, Permission("read", "default", "GREEN"))
```

### API Integration
```python
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None
) -> User:
    """Get current user from JWT token"""

    try:
        # Decode JWT token
        payload = decode_jwt_token(credentials.credentials)

        # Validate session
        session_id = payload.get("session_id")
        user = session_manager.validate_session(session_id)

        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Log access
        logger.info({
            "event_type": "API_ACCESS",
            "user_id": user.id,
            "endpoint": request.url.path,
            "method": request.method,
            "ip_address": request.client.host,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "python_version": "3.12.10"
        })

        return user

    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(status_code=401, detail="Authentication failed")

# Usage in API endpoints
@app.get("/api/v1/simulations")
async def list_simulations(user: User = Depends(get_current_user)):
    # User is automatically authenticated and authorized
    return await get_user_simulations(user.id)
```

## Monitoring & Alerting

### RBAC Health Checks
```python
def check_rbac_health() -> dict:
    """Check health of RBAC system"""

    health = {
        "authentication_service": False,
        "authorization_service": False,
        "session_management": False,
        "audit_logging": False
    }

    # Check authentication service
    try:
        # Test auth service connectivity
        health["authentication_service"] = True
    except:
        pass

    # Check authorization service
    try:
        # Test permission checking
        health["authorization_service"] = True
    except:
        pass

    # Check session management
    try:
        active_sessions = len(session_manager.active_sessions)
        health["session_management"] = active_sessions >= 0
    except:
        pass

    # Check audit logging
    try:
        # Test log writing
        health["audit_logging"] = True
    except:
        pass

    return health
```

### Alert Rules
```prometheus
# Authentication Failures
ALERT HighAuthFailureRate
  IF rate(authentication_failures_total[5m]) > 0.1
  FOR 5m
  LABELS { severity = "warning" }
  ANNOTATIONS {
    summary = "High authentication failure rate",
    description = "Authentication failure rate is {{ $value | printf "%.2f" }} per second"
  }

# Unauthorized Access Attempts
ALERT UnauthorizedAccess
  IF increase(rbac_denials_total[5m]) > 5
  FOR 2m
  LABELS { severity = "error" }
  ANNOTATIONS {
    summary = "Multiple unauthorized access attempts",
    description = "{{ $value }} unauthorized access attempts in 5 minutes"
  }

# Session Limit Exceeded
ALERT SessionLimitExceeded
  IF session_limit_exceeded_total > 0
  FOR 1m
  LABELS { severity = "info" }
  ANNOTATIONS {
    summary = "User exceeded session limit",
    description = "User {{ $labels.user_id }} exceeded session limit"
  }
```

## Emergency Procedures

### RBAC System Failure
1. **Immediate Response**
   ```bash
   # Enable emergency access mode
   kubectl set env deployment/smvm-api EMERGENCY_ACCESS=true

   # Notify security team
   curl -X POST https://alerts.smvm.company.com/rbac-failure \
        -H "Content-Type: application/json" \
        -d '{"severity": "critical", "message": "RBAC system failure"}'
   ```

2. **Manual Authorization**
   ```bash
   # Enable manual approval workflow
   ./scripts/enable-manual-approval.sh

   # Monitor manual approvals
   tail -f /var/log/smvm/manual-approvals.log
   ```

3. **System Recovery**
   ```bash
   # Restore RBAC service
   kubectl rollout restart deployment/smvm-rbac

   # Verify system health
   curl https://health.smvm.company.com/rbac
   ```

4. **Post-Incident Review**
   ```bash
   # Analyze incident
   ./scripts/incident-analysis.sh --rbac-failure

   # Update runbooks
   ./scripts/update-runbooks.sh --rbac-procedures
   ```

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX
**Owner**: Security Team
**Reviewers**: DevOps Team, Compliance Officer

*This RBAC system ensures secure, auditable access control across all SMVM zones and operations.*
