#!/usr/bin/env python3
"""
SMVM Token Monitor - Runtime Token Enforcement

This module provides runtime token counting and ceiling enforcement for the
Synthetic Market Validation Module. It halts execution on token ceiling breaches
and provides comprehensive monitoring and alerting capabilities.
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import hashlib

# Service metadata
SERVICE_NAME = "token-monitor"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"
DATA_ZONE = "GREEN"
RETENTION_DAYS = 30

logger = logging.getLogger(__name__)


class TokenCeilingBreach(Exception):
    """Exception raised when token ceiling is breached"""

    def __init__(self, service: str, requested: int, ceiling: int, context: Dict = None):
        self.service = service
        self.requested = requested
        self.ceiling = ceiling
        self.context = context or {}
        self.timestamp = datetime.utcnow().isoformat() + "Z"

        message = (f"Token ceiling breach in {service}: requested {requested} tokens, "
                  f"ceiling is {ceiling}")
        super().__init__(message)


class TokenCounter:
    """
    Thread-safe token counter with ceiling enforcement
    """

    def __init__(self, service_name: str, ceiling: int, alert_threshold: float = 0.8):
        self.service_name = service_name
        self.ceiling = ceiling
        self.alert_threshold = alert_threshold
        self._lock = threading.RLock()
        self._counters = {
            "current": 0,
            "total_allocated": 0,
            "total_consumed": 0,
            "peak_usage": 0,
            "breach_count": 0,
            "alert_count": 0
        }
        self._history = []
        self._alert_callbacks: List[Callable] = []

    def allocate_tokens(self, amount: int, context: Dict = None) -> bool:
        """
        Allocate tokens with ceiling enforcement

        Args:
            amount: Number of tokens to allocate
            context: Additional context for logging/alerting

        Returns:
            True if allocation successful, False if would exceed ceiling

        Raises:
            TokenCeilingBreach: If allocation would exceed ceiling
        """
        context = context or {}

        with self._lock:
            projected_total = self._counters["current"] + amount

            # Check for breach
            if projected_total > self.ceiling:
                self._counters["breach_count"] += 1
                breach_info = {
                    "service": self.service_name,
                    "requested": amount,
                    "ceiling": self.ceiling,
                    "current": self._counters["current"],
                    "projected": projected_total,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

                logger.error(f"Token ceiling breach: {breach_info}")
                self._log_breach_event(breach_info)

                raise TokenCeilingBreach(
                    service=self.service_name,
                    requested=amount,
                    ceiling=self.ceiling,
                    context=context
                )

            # Check for alert threshold
            alert_level = int(self.ceiling * self.alert_threshold)
            if projected_total > alert_level and self._counters["current"] <= alert_level:
                self._counters["alert_count"] += 1
                alert_info = {
                    "service": self.service_name,
                    "alert_level": alert_level,
                    "projected": projected_total,
                    "ceiling": self.ceiling,
                    "context": context,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }

                logger.warning(f"Token alert threshold reached: {alert_info}")
                self._trigger_alert_callbacks(alert_info)

            # Allocate tokens
            self._counters["current"] += amount
            self._counters["total_allocated"] += amount
            self._counters["peak_usage"] = max(self._counters["peak_usage"], self._counters["current"])

            allocation_info = {
                "service": self.service_name,
                "allocated": amount,
                "current": self._counters["current"],
                "ceiling": self.ceiling,
                "utilization_percent": (self._counters["current"] / self.ceiling) * 100,
                "context": context,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            self._history.append(allocation_info)
            logger.debug(f"Tokens allocated: {allocation_info}")

            return True

    def consume_tokens(self, amount: int, context: Dict = None) -> bool:
        """
        Consume allocated tokens

        Args:
            amount: Number of tokens to consume

        Returns:
            True if consumption successful, False if insufficient tokens
        """
        context = context or {}

        with self._lock:
            if self._counters["current"] < amount:
                logger.error(f"Insufficient tokens for consumption: requested {amount}, available {self._counters['current']}")
                return False

            self._counters["current"] -= amount
            self._counters["total_consumed"] += amount

            consumption_info = {
                "service": self.service_name,
                "consumed": amount,
                "remaining": self._counters["current"],
                "ceiling": self.ceiling,
                "context": context,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            self._history.append(consumption_info)
            logger.debug(f"Tokens consumed: {consumption_info}")

            return True

    def release_tokens(self, amount: int, context: Dict = None) -> bool:
        """
        Release allocated tokens back to pool

        Args:
            amount: Number of tokens to release

        Returns:
            True if release successful
        """
        context = context or {}

        with self._lock:
            if amount > self._counters["current"]:
                logger.warning(f"Attempted to release more tokens than allocated: {amount} > {self._counters['current']}")
                amount = self._counters["current"]

            self._counters["current"] -= amount

            release_info = {
                "service": self.service_name,
                "released": amount,
                "remaining": self._counters["current"],
                "ceiling": self.ceiling,
                "context": context,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            self._history.append(release_info)
            logger.debug(f"Tokens released: {release_info}")

            return True

    def get_status(self) -> Dict:
        """Get current token counter status"""
        with self._lock:
            return {
                "service": self.service_name,
                "current": self._counters["current"],
                "ceiling": self.ceiling,
                "utilization_percent": (self._counters["current"] / self.ceiling) * 100 if self.ceiling > 0 else 0,
                "total_allocated": self._counters["total_allocated"],
                "total_consumed": self._counters["total_consumed"],
                "peak_usage": self._counters["peak_usage"],
                "breach_count": self._counters["breach_count"],
                "alert_count": self._counters["alert_count"],
                "available": self.ceiling - self._counters["current"]
            }

    def reset(self) -> None:
        """Reset counter to zero (use with caution)"""
        with self._lock:
            reset_info = {
                "service": self.service_name,
                "action": "reset",
                "previous_current": self._counters["current"],
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }

            self._history.append(reset_info)
            self._counters["current"] = 0

            logger.warning(f"Token counter reset: {reset_info}")

    def add_alert_callback(self, callback: Callable) -> None:
        """Add callback function for alert events"""
        self._alert_callbacks.append(callback)

    def _trigger_alert_callbacks(self, alert_info: Dict) -> None:
        """Trigger all registered alert callbacks"""
        for callback in self._alert_callbacks:
            try:
                callback(alert_info)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")

    def _log_breach_event(self, breach_info: Dict) -> None:
        """Log token ceiling breach event"""
        breach_event = {
            "event_type": "TOKEN_CEILING_BREACH",
            "service": breach_info["service"],
            "breach_details": {
                "requested": breach_info["requested"],
                "ceiling": breach_info["ceiling"],
                "current": breach_info["current"],
                "projected": breach_info["projected"],
                "breach_amount": breach_info["projected"] - breach_info["ceiling"]
            },
            "context": breach_info.get("context", {}),
            "timestamp": breach_info["timestamp"]
        }

        logger.critical(f"TOKEN CEILING BREACH: {breach_event}")

        # Could write to external monitoring system here
        # self._write_to_monitoring_system(breach_event)


class TokenMonitor:
    """
    Central token monitoring and enforcement system
    """

    def __init__(self, config: Dict):
        self.config = config
        self.counters: Dict[str, TokenCounter] = {}
        self._lock = threading.RLock()
        self._monitoring_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Initialize counters for all services
        self._initialize_counters()

        # Start monitoring thread
        self._start_monitoring()

    def _initialize_counters(self) -> None:
        """Initialize token counters for all SMVM services"""
        service_ceilings = self.config.get("service_ceilings", {
            "ingestion": 1000,
            "personas": 2000,
            "competitors": 1500,
            "simulation": 3000,
            "analysis": 2000,
            "overwatch": 500,
            "memory": 300,
            "cli": 100
        })

        for service, ceiling in service_ceilings.items():
            alert_threshold = self.config.get("alert_threshold", 0.8)
            self.counters[service] = TokenCounter(service, ceiling, alert_threshold)

            # Add default alert callback
            self.counters[service].add_alert_callback(self._default_alert_handler)

    def allocate_tokens(self, service: str, amount: int, context: Dict = None) -> bool:
        """
        Allocate tokens for a service

        Args:
            service: Service name
            amount: Number of tokens to allocate
            context: Additional context

        Returns:
            True if allocation successful

        Raises:
            TokenCeilingBreach: If ceiling would be exceeded
        """
        if service not in self.counters:
            raise ValueError(f"Unknown service: {service}")

        return self.counters[service].allocate_tokens(amount, context)

    def consume_tokens(self, service: str, amount: int, context: Dict = None) -> bool:
        """
        Consume tokens for a service

        Args:
            service: Service name
            amount: Number of tokens to consume
            context: Additional context

        Returns:
            True if consumption successful
        """
        if service not in self.counters:
            raise ValueError(f"Unknown service: {service}")

        return self.counters[service].consume_tokens(amount, context)

    def release_tokens(self, service: str, amount: int, context: Dict = None) -> bool:
        """
        Release tokens for a service

        Args:
            service: Service name
            amount: Number of tokens to release
            context: Additional context

        Returns:
            True if release successful
        """
        if service not in self.counters:
            raise ValueError(f"Unknown service: {service}")

        return self.counters[service].release_tokens(amount, context)

    def get_service_status(self, service: str) -> Dict:
        """Get status for a specific service"""
        if service not in self.counters:
            raise ValueError(f"Unknown service: {service}")

        return self.counters[service].get_status()

    def get_all_status(self) -> Dict:
        """Get status for all services"""
        return {
            service: counter.get_status()
            for service, counter in self.counters.items()
        }

    def get_system_status(self) -> Dict:
        """Get overall system status"""
        all_status = self.get_all_status()

        total_allocated = sum(status["total_allocated"] for status in all_status.values())
        total_consumed = sum(status["total_consumed"] for status in all_status.values())
        total_current = sum(status["current"] for status in all_status.values())
        total_ceiling = sum(status["ceiling"] for status in all_status.values())

        breach_services = [s for s, status in all_status.items() if status["breach_count"] > 0]

        return {
            "total_allocated": total_allocated,
            "total_consumed": total_consumed,
            "total_current": total_current,
            "total_ceiling": total_ceiling,
            "system_utilization_percent": (total_current / total_ceiling) * 100 if total_ceiling > 0 else 0,
            "services_with_breaches": breach_services,
            "total_breaches": sum(status["breach_count"] for status in all_status.values()),
            "service_count": len(all_status),
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

    def reset_service(self, service: str) -> None:
        """Reset token counter for a service (admin only)"""
        if service not in self.counters:
            raise ValueError(f"Unknown service: {service}")

        logger.warning(f"Resetting token counter for service: {service}")
        self.counters[service].reset()

    def _default_alert_handler(self, alert_info: Dict) -> None:
        """Default handler for token alerts"""
        alert_event = {
            "event_type": "TOKEN_ALERT",
            "service": alert_info["service"],
            "alert_level": alert_info["alert_level"],
            "projected_usage": alert_info["projected"],
            "ceiling": alert_info["ceiling"],
            "context": alert_info.get("context", {}),
            "timestamp": alert_info["timestamp"]
        }

        logger.warning(f"TOKEN ALERT: {alert_event}")

        # Could integrate with external alerting system here
        # self._send_external_alert(alert_event)

    def _start_monitoring(self) -> None:
        """Start background monitoring thread"""
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True,
            name="token-monitor"
        )
        self._monitoring_thread.start()

    def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        monitoring_interval = self.config.get("monitoring_interval_seconds", 60)

        while not self._shutdown_event.is_set():
            try:
                # Collect and log system status
                system_status = self.get_system_status()

                if system_status["system_utilization_percent"] > 80:
                    logger.warning(f"High system utilization: {system_status['system_utilization_percent']:.1f}%")

                if system_status["services_with_breaches"]:
                    logger.error(f"Services with breaches: {system_status['services_with_breaches']}")

                # Could write metrics to external system here
                # self._write_metrics(system_status)

                time.sleep(monitoring_interval)

            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(5)  # Brief pause before retry

    def shutdown(self) -> None:
        """Shutdown the token monitor"""
        logger.info("Shutting down token monitor...")
        self._shutdown_event.set()

        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=5)

        logger.info("Token monitor shutdown complete")


# Context manager for token allocation
class TokenAllocation:
    """
    Context manager for safe token allocation and automatic cleanup
    """

    def __init__(self, monitor: TokenMonitor, service: str, amount: int, context: Dict = None):
        self.monitor = monitor
        self.service = service
        self.amount = amount
        self.context = context or {}
        self.allocated = False

    def __enter__(self):
        """Allocate tokens on context entry"""
        self.monitor.allocate_tokens(self.service, self.amount, self.context)
        self.allocated = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Release tokens on context exit"""
        if self.allocated:
            try:
                self.monitor.release_tokens(self.service, self.amount, {
                    **self.context,
                    "released_on_exit": True,
                    "exception_occurred": exc_type is not None
                })
            except Exception as e:
                logger.error(f"Failed to release tokens in context manager: {e}")


# Global token monitor instance
_monitor_instance: Optional[TokenMonitor] = None
_monitor_lock = threading.Lock()


def get_token_monitor(config: Dict = None) -> TokenMonitor:
    """
    Get or create global token monitor instance

    Args:
        config: Token monitor configuration

    Returns:
        TokenMonitor instance
    """
    global _monitor_instance

    if _monitor_instance is None:
        with _monitor_lock:
            if _monitor_instance is None:
                default_config = {
                    "service_ceilings": {
                        "ingestion": 1000,
                        "personas": 2000,
                        "competitors": 1500,
                        "simulation": 3000,
                        "analysis": 2000,
                        "overwatch": 500,
                        "memory": 300,
                        "cli": 100
                    },
                    "alert_threshold": 0.8,
                    "monitoring_interval_seconds": 60
                }

                if config:
                    default_config.update(config)

                _monitor_instance = TokenMonitor(default_config)

    return _monitor_instance


def allocate_tokens_context(service: str, amount: int, context: Dict = None):
    """
    Context manager for token allocation with automatic cleanup

    Usage:
        with allocate_tokens_context("simulation", 1000, {"run_id": "test"}):
            # Use allocated tokens
            pass
        # Tokens automatically released
    """
    monitor = get_token_monitor()
    return TokenAllocation(monitor, service, amount, context)


# Convenience functions
def quick_allocate(service: str, amount: int, context: Dict = None) -> bool:
    """Quick token allocation without context manager"""
    monitor = get_token_monitor()
    return monitor.allocate_tokens(service, amount, context)


def quick_consume(service: str, amount: int, context: Dict = None) -> bool:
    """Quick token consumption"""
    monitor = get_token_monitor()
    return monitor.consume_tokens(service, amount, context)


def quick_release(service: str, amount: int, context: Dict = None) -> bool:
    """Quick token release"""
    monitor = get_token_monitor()
    return monitor.release_tokens(service, amount, context)


def get_status(service: str = None) -> Dict:
    """Get token status"""
    monitor = get_token_monitor()
    if service:
        return monitor.get_service_status(service)
    else:
        return monitor.get_system_status()


# Cleanup function
def shutdown_monitor() -> None:
    """Shutdown the global token monitor"""
    global _monitor_instance

    if _monitor_instance:
        _monitor_instance.shutdown()
        _monitor_instance = None


# Example usage and testing
if __name__ == "__main__":
    # Initialize monitor
    monitor = get_token_monitor()

    # Example token operations
    try:
        # Allocate tokens
        monitor.allocate_tokens("simulation", 500, {"operation": "test_run"})

        # Use context manager for safe allocation
        with allocate_tokens_context("analysis", 200, {"run_id": "test-123"}):
            print("Tokens allocated for analysis")
            # Simulate work
            time.sleep(1)

        print("Tokens automatically released")

        # Check status
        status = monitor.get_system_status()
        print(f"System status: {status}")

    except TokenCeilingBreach as e:
        print(f"Token ceiling breach: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        shutdown_monitor()
