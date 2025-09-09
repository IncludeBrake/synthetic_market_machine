#!/usr/bin/env python3
"""
SMVM Rate Limiting Policy Engine

This module implements comprehensive rate limiting for the SMVM ingestion system
to prevent abuse, respect external service limits, and ensure fair resource usage.
"""

import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from collections import defaultdict
import threading

logger = logging.getLogger(__name__)

# Policy metadata
POLICY_NAME = "rate_limits"
POLICY_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"

class RateLimitExceeded(Exception):
    """Exception raised when rate limit is exceeded"""
    pass

class RateLimitPolicy:
    """
    Comprehensive rate limiting policy engine
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Rate limit storage
        self.request_counts: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.lock = threading.RLock()

        # Default rate limits
        self.default_limits = {
            "requests_per_second": 10,
            "requests_per_minute": 100,
            "requests_per_hour": 1000,
            "requests_per_day": 5000,
            "burst_limit": 50
        }

        # Service-specific limits
        self.service_limits = {
            "google_trends": {
                "requests_per_hour": 100,
                "burst_limit": 10
            },
            "crunchbase": {
                "requests_per_hour": 50,
                "burst_limit": 5
            },
            "reddit": {
                "requests_per_hour": 60,
                "burst_limit": 6
            },
            "angellist": {
                "requests_per_hour": 30,
                "burst_limit": 3
            },
            "general_api": {
                "requests_per_second": 5,
                "requests_per_minute": 50,
                "burst_limit": 20
            }
        }

        # User-specific limits
        self.user_limits = {
            "default": {
                "requests_per_minute": 30,
                "requests_per_hour": 200,
                "concurrent_requests": 5
            },
            "premium": {
                "requests_per_minute": 100,
                "requests_per_hour": 1000,
                "concurrent_requests": 20
            },
            "enterprise": {
                "requests_per_minute": 500,
                "requests_per_hour": 5000,
                "concurrent_requests": 100
            }
        }

        # Active requests tracking
        self.active_requests: Dict[str, set] = defaultdict(set)

        # Cleanup interval
        self.cleanup_interval = 300  # 5 minutes
        self._start_cleanup_thread()

    def check_rate_limit(self, identifier: str, service: str = "general_api",
                        user_tier: str = "default") -> Dict[str, Any]:
        """
        Check if request is within rate limits

        Args:
            identifier: Unique identifier (IP, user ID, API key)
            service: Service being accessed
            user_tier: User tier for limit determination

        Returns:
            Rate limit check result
        """

        with self.lock:
            current_time = time.time()

            # Get applicable limits
            service_limit = self.service_limits.get(service, self.default_limits)
            user_limit = self.user_limits.get(user_tier, self.user_limits["default"])

            # Combine limits (most restrictive applies)
            effective_limits = {
                "requests_per_second": min(
                    service_limit.get("requests_per_second", self.default_limits["requests_per_second"]),
                    user_limit.get("requests_per_second", self.default_limits["requests_per_second"])
                ),
                "requests_per_minute": min(
                    service_limit.get("requests_per_minute", self.default_limits["requests_per_minute"]),
                    user_limit.get("requests_per_minute", self.default_limits["requests_per_minute"])
                ),
                "requests_per_hour": min(
                    service_limit.get("requests_per_hour", self.default_limits["requests_per_hour"]),
                    user_limit.get("requests_per_hour", self.default_limits["requests_per_hour"])
                ),
                "burst_limit": min(
                    service_limit.get("burst_limit", self.default_limits["burst_limit"]),
                    user_limit.get("burst_limit", self.default_limits["burst_limit"])
                ),
                "concurrent_requests": user_limit.get("concurrent_requests", 5)
            }

            # Check concurrent requests
            active_count = len(self.active_requests[identifier])
            if active_count >= effective_limits["concurrent_requests"]:
                return self._create_limit_result(
                    False, "concurrent_limit_exceeded",
                    {"active_requests": active_count, "limit": effective_limits["concurrent_requests"]}
                )

            # Initialize request tracking if needed
            if identifier not in self.request_counts:
                self.request_counts[identifier] = {
                    "second_window": {"count": 0, "window_start": current_time},
                    "minute_window": {"count": 0, "window_start": current_time},
                    "hour_window": {"count": 0, "window_start": current_time},
                    "burst_count": 0,
                    "last_request": 0
                }

            tracker = self.request_counts[identifier]

            # Reset windows if needed
            self._reset_windows(tracker, current_time)

            # Check rate limits
            limits_exceeded = []

            # Per-second limit
            if tracker["second_window"]["count"] >= effective_limits["requests_per_second"]:
                limits_exceeded.append("requests_per_second")

            # Per-minute limit
            if tracker["minute_window"]["count"] >= effective_limits["requests_per_minute"]:
                limits_exceeded.append("requests_per_minute")

            # Per-hour limit
            if tracker["hour_window"]["count"] >= effective_limits["requests_per_hour"]:
                limits_exceeded.append("requests_per_hour")

            # Burst limit
            if tracker["burst_count"] >= effective_limits["burst_limit"]:
                limits_exceeded.append("burst_limit")

            if limits_exceeded:
                return self._create_limit_result(
                    False, "rate_limit_exceeded",
                    {"exceeded_limits": limits_exceeded, "limits": effective_limits}
                )

            return self._create_limit_result(True, "allowed", {"limits": effective_limits})

    def record_request(self, identifier: str, service: str = "general_api",
                      user_tier: str = "default") -> Dict[str, Any]:
        """
        Record a request for rate limiting purposes

        Args:
            identifier: Unique identifier
            service: Service being accessed
            user_tier: User tier

        Returns:
            Request recording result
        """

        with self.lock:
            current_time = time.time()

            # Check limits first
            check_result = self.check_rate_limit(identifier, service, user_tier)

            if not check_result["allowed"]:
                self.logger.warning({
                    "event_type": "RATE_LIMIT_EXCEEDED",
                    "identifier": identifier,
                    "service": service,
                    "user_tier": user_tier,
                    "reason": check_result["reason"],
                    "details": check_result["details"],
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })
                raise RateLimitExceeded(f"Rate limit exceeded: {check_result['reason']}")

            # Record the request
            tracker = self.request_counts[identifier]

            # Update counters
            tracker["second_window"]["count"] += 1
            tracker["minute_window"]["count"] += 1
            tracker["hour_window"]["count"] += 1
            tracker["burst_count"] += 1
            tracker["last_request"] = current_time

            # Track active request
            request_id = f"{identifier}_{current_time}_{hash(str(current_time))}"
            self.active_requests[identifier].add(request_id)

            self.logger.debug({
                "event_type": "REQUEST_RECORDED",
                "identifier": identifier,
                "service": service,
                "user_tier": user_tier,
                "request_id": request_id,
                "current_counts": {
                    "per_second": tracker["second_window"]["count"],
                    "per_minute": tracker["minute_window"]["count"],
                    "per_hour": tracker["hour_window"]["count"],
                    "burst": tracker["burst_count"]
                },
                "python_version": PYTHON_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

            return {
                "recorded": True,
                "request_id": request_id,
                "current_counts": {
                    "per_second": tracker["second_window"]["count"],
                    "per_minute": tracker["minute_window"]["count"],
                    "per_hour": tracker["hour_window"]["count"],
                    "burst": tracker["burst_count"]
                }
            }

    def complete_request(self, identifier: str, request_id: str):
        """
        Mark a request as completed

        Args:
            identifier: Unique identifier
            request_id: Request ID from record_request
        """

        with self.lock:
            if identifier in self.active_requests and request_id in self.active_requests[identifier]:
                self.active_requests[identifier].remove(request_id)

                self.logger.debug({
                    "event_type": "REQUEST_COMPLETED",
                    "identifier": identifier,
                    "request_id": request_id,
                    "remaining_active": len(self.active_requests[identifier]),
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

    def get_rate_limit_status(self, identifier: str, service: str = "general_api",
                            user_tier: str = "default") -> Dict[str, Any]:
        """
        Get current rate limit status for an identifier
        """

        with self.lock:
            current_time = time.time()

            if identifier not in self.request_counts:
                return self._create_limit_result(True, "no_history", {})

            tracker = self.request_counts[identifier]
            self._reset_windows(tracker, current_time)

            # Get applicable limits
            service_limit = self.service_limits.get(service, self.default_limits)
            user_limit = self.user_limits.get(user_tier, self.user_limits["default"])

            effective_limits = {
                "requests_per_second": min(
                    service_limit.get("requests_per_second", self.default_limits["requests_per_second"]),
                    user_limit.get("requests_per_second", self.default_limits["requests_per_second"])
                ),
                "requests_per_minute": min(
                    service_limit.get("requests_per_minute", self.default_limits["requests_per_minute"]),
                    user_limit.get("requests_per_minute", self.default_limits["requests_per_minute"])
                ),
                "requests_per_hour": min(
                    service_limit.get("requests_per_hour", self.default_limits["requests_per_hour"]),
                    user_limit.get("requests_per_hour", self.default_limits["requests_per_hour"])
                ),
                "burst_limit": min(
                    service_limit.get("burst_limit", self.default_limits["burst_limit"]),
                    user_limit.get("burst_limit", self.default_limits["burst_limit"])
                ),
                "concurrent_requests": user_limit.get("concurrent_requests", 5)
            }

            current_counts = {
                "per_second": tracker["second_window"]["count"],
                "per_minute": tracker["minute_window"]["count"],
                "per_hour": tracker["hour_window"]["count"],
                "burst": tracker["burst_count"],
                "active": len(self.active_requests[identifier])
            }

            # Calculate remaining capacity
            remaining = {
                "per_second": max(0, effective_limits["requests_per_second"] - current_counts["per_second"]),
                "per_minute": max(0, effective_limits["requests_per_minute"] - current_counts["per_minute"]),
                "per_hour": max(0, effective_limits["requests_per_hour"] - current_counts["per_hour"]),
                "burst": max(0, effective_limits["burst_limit"] - current_counts["burst"]),
                "concurrent": max(0, effective_limits["concurrent_requests"] - current_counts["active"])
            }

            return {
                "identifier": identifier,
                "service": service,
                "user_tier": user_tier,
                "limits": effective_limits,
                "current_counts": current_counts,
                "remaining": remaining,
                "reset_times": {
                    "second_window": tracker["second_window"]["window_start"] + 1,
                    "minute_window": tracker["minute_window"]["window_start"] + 60,
                    "hour_window": tracker["hour_window"]["window_start"] + 3600
                },
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }

    def _reset_windows(self, tracker: Dict[str, Any], current_time: float):
        """Reset rate limit windows as needed"""

        # Second window
        if current_time - tracker["second_window"]["window_start"] >= 1:
            tracker["second_window"] = {"count": 0, "window_start": current_time}

        # Minute window
        if current_time - tracker["minute_window"]["window_start"] >= 60:
            tracker["minute_window"] = {"count": 0, "window_start": current_time}

        # Hour window
        if current_time - tracker["hour_window"]["window_start"] >= 3600:
            tracker["hour_window"] = {"count": 0, "window_start": current_time}

        # Burst reset (reset every minute)
        if current_time - tracker.get("burst_reset_time", 0) >= 60:
            tracker["burst_count"] = 0
            tracker["burst_reset_time"] = current_time

    def _create_limit_result(self, allowed: bool, reason: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Create standardized rate limit result"""

        return {
            "allowed": allowed,
            "reason": reason,
            "details": details,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def _start_cleanup_thread(self):
        """Start background cleanup thread"""

        def cleanup_worker():
            while True:
                time.sleep(self.cleanup_interval)
                self._cleanup_old_data()

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()

    def _cleanup_old_data(self):
        """Clean up old rate limit data"""

        with self.lock:
            current_time = time.time()
            cutoff_time = current_time - 3600  # 1 hour ago

            # Remove old request counts
            identifiers_to_remove = []
            for identifier, tracker in self.request_counts.items():
                if tracker["last_request"] < cutoff_time:
                    identifiers_to_remove.append(identifier)

            for identifier in identifiers_to_remove:
                del self.request_counts[identifier]

            # Remove old active requests
            for identifier in list(self.active_requests.keys()):
                if not self.active_requests[identifier]:
                    del self.active_requests[identifier]

            if identifiers_to_remove:
                self.logger.info({
                    "event_type": "RATE_LIMIT_CLEANUP",
                    "removed_identifiers": len(identifiers_to_remove),
                    "remaining_identifiers": len(self.request_counts),
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

    def reset_limits(self, identifier: str):
        """Reset rate limits for an identifier (admin function)"""

        with self.lock:
            if identifier in self.request_counts:
                del self.request_counts[identifier]

            if identifier in self.active_requests:
                self.active_requests[identifier].clear()

            self.logger.info({
                "event_type": "RATE_LIMIT_RESET",
                "identifier": identifier,
                "python_version": PYTHON_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

    def get_policy_info(self) -> Dict[str, Any]:
        """Get policy information"""

        with self.lock:
            return {
                "policy_name": POLICY_NAME,
                "version": POLICY_VERSION,
                "active_identifiers": len(self.request_counts),
                "active_requests": sum(len(requests) for requests in self.active_requests.values()),
                "service_limits_count": len(self.service_limits),
                "user_tiers_count": len(self.user_limits),
                "cleanup_interval": self.cleanup_interval,
                "python_version": PYTHON_VERSION,
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }


# Policy interface definition
POLICY_INTERFACE = {
    "policy": POLICY_NAME,
    "version": POLICY_VERSION,
    "description": "Comprehensive rate limiting to prevent abuse and respect limits",
    "limits": {
        "time_windows": ["per_second", "per_minute", "per_hour", "per_day"],
        "user_tiers": ["default", "premium", "enterprise"],
        "services": ["google_trends", "crunchbase", "reddit", "angellist", "general_api"]
    },
    "endpoints": {
        "check_rate_limit": {
            "method": "GET",
            "path": "/api/v1/policies/rate-limits/check",
            "input": {
                "identifier": "string",
                "service": "string (optional)",
                "user_tier": "string (optional)"
            },
            "output": {
                "allowed": "boolean",
                "reason": "string",
                "details": "object"
            },
            "token_budget": 10,
            "timeout_seconds": 5
        },
        "get_rate_limit_status": {
            "method": "GET",
            "path": "/api/v1/policies/rate-limits/status",
            "input": {
                "identifier": "string",
                "service": "string (optional)",
                "user_tier": "string (optional)"
            },
            "output": {
                "limits": "object",
                "current_counts": "object",
                "remaining": "object"
            },
            "token_budget": 15,
            "timeout_seconds": 5
        }
    },
    "failure_modes": {
        "rate_limit_exceeded": "Request exceeds configured rate limits",
        "concurrent_limit_exceeded": "Too many concurrent requests",
        "service_unavailable": "Rate limiting service temporarily unavailable",
        "invalid_parameters": "Invalid rate limit parameters provided"
    },
    "grounding_sources": [
        "Token bucket algorithms",
        "Leaky bucket algorithms",
        "Rate limiting best practices",
        "API gateway patterns",
        "Distributed rate limiting techniques"
    ],
    "observability": {
        "spans": ["rate_limit_check", "window_reset", "limit_enforcement", "cleanup_operation"],
        "metrics": ["rate_limit_hit_rate", "throttled_requests", "active_identifiers", "window_resets"],
        "logs": ["limit_check", "limit_exceeded", "window_reset", "cleanup_complete", "limit_reset"]
    }
}


def rate_limited(service: str = "general_api", user_tier: str = "default"):
    """
    Decorator for automatic rate limiting

    Usage:
        @rate_limited(service="google_trends", user_tier="premium")
        def my_api_call():
            pass
    """

    def decorator(func):
        policy = RateLimitPolicy({})

        def wrapper(*args, **kwargs):
            # Extract identifier (could be from request context)
            identifier = kwargs.get('identifier', 'anonymous')

            # Record request
            request_info = policy.record_request(identifier, service, user_tier)

            try:
                # Execute function
                result = func(*args, **kwargs)

                # Complete request
                policy.complete_request(identifier, request_info["request_id"])

                return result

            except Exception as e:
                # Complete request on error too
                policy.complete_request(identifier, request_info["request_id"])
                raise

        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    policy = RateLimitPolicy({})

    # Check rate limit
    identifier = "user_123"

    for i in range(5):
        try:
            result = policy.record_request(identifier, "google_trends", "default")
            print(f"Request {i+1} allowed: {result}")
        except RateLimitExceeded as e:
            print(f"Request {i+1} blocked: {e}")

        # Simulate some processing time
        time.sleep(0.1)

    # Check status
    status = policy.get_rate_limit_status(identifier, "google_trends", "default")
    print(f"Rate limit status: {status}")

    # Policy info
    info = policy.get_policy_info()
    print(f"Policy info: {info['active_identifiers']} active identifiers")
