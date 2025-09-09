#!/usr/bin/env python3
"""
SMVM Retry and Backoff Policy Engine

This module implements intelligent retry and backoff strategies for the SMVM
ingestion system to handle transient failures and respect rate limits.
"""

import json
import hashlib
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
import logging
from enum import Enum

logger = logging.getLogger(__name__)

# Policy metadata
POLICY_NAME = "retry_backoff"
POLICY_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"

class RetryStrategy(Enum):
    """Retry strategy types"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIBONACCI = "fibonacci"

class BackoffStrategy(Enum):
    """Backoff strategy types"""
    FIXED = "fixed"
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    RANDOM = "random"

class ErrorCategory(Enum):
    """Error categories for different retry behaviors"""
    NETWORK = "network"
    RATE_LIMIT = "rate_limit"
    SERVER_ERROR = "server_error"
    CLIENT_ERROR = "client_error"
    TIMEOUT = "timeout"

class RetryBackoffPolicy:
    """
    Intelligent retry and backoff policy engine
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Default retry configuration
        self.retry_config = {
            "max_retries": 5,
            "base_delay": 1.0,  # seconds
            "max_delay": 300.0,  # 5 minutes
            "jitter": True,
            "jitter_factor": 0.1,
            "retry_strategy": RetryStrategy.EXPONENTIAL,
            "backoff_strategy": BackoffStrategy.EXPONENTIAL
        }

        # Error-specific retry configurations
        self.error_configs = {
            ErrorCategory.NETWORK: {
                "max_retries": 3,
                "base_delay": 2.0,
                "retry_strategy": RetryStrategy.EXPONENTIAL
            },
            ErrorCategory.RATE_LIMIT: {
                "max_retries": 5,
                "base_delay": 60.0,  # 1 minute
                "retry_strategy": RetryStrategy.LINEAR,
                "respect_retry_after": True
            },
            ErrorCategory.SERVER_ERROR: {
                "max_retries": 3,
                "base_delay": 5.0,
                "retry_strategy": RetryStrategy.EXPONENTIAL
            },
            ErrorCategory.CLIENT_ERROR: {
                "max_retries": 1,  # Usually don't retry client errors
                "base_delay": 1.0,
                "retry_strategy": RetryStrategy.FIXED
            },
            ErrorCategory.TIMEOUT: {
                "max_retries": 3,
                "base_delay": 3.0,
                "retry_strategy": RetryStrategy.EXPONENTIAL
            }
        }

        # Request history for adaptive behavior
        self.request_history: Dict[str, List[Dict[str, Any]]] = {}
        self.history_window = timedelta(hours=1)

        # Circuit breaker state
        self.circuit_breaker_state: Dict[str, Dict[str, Any]] = {}

    def execute_with_retry(self, operation: Callable, operation_id: str,
                          context: Dict[str, Any] = None) -> Any:
        """
        Execute operation with retry and backoff logic

        Args:
            operation: Callable to execute
            operation_id: Unique identifier for the operation
            context: Additional context for retry decisions

        Returns:
            Operation result

        Raises:
            Last exception if all retries exhausted
        """

        context = context or {}
        attempt = 0
        last_exception = None

        self.logger.info({
            "event_type": "RETRY_EXECUTION_START",
            "operation_id": operation_id,
            "context": context,
            "python_version": PYTHON_VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        while attempt <= self.retry_config["max_retries"]:
            try:
                # Check circuit breaker
                if self._is_circuit_open(operation_id):
                    raise CircuitBreakerOpen(f"Circuit breaker open for {operation_id}")

                # Execute operation
                start_time = time.time()
                result = operation()
                execution_time = time.time() - start_time

                # Record success
                self._record_attempt(operation_id, attempt, True, None, execution_time)

                self.logger.debug({
                    "event_type": "OPERATION_SUCCESS",
                    "operation_id": operation_id,
                    "attempt": attempt,
                    "execution_time": execution_time,
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

                return result

            except Exception as e:
                last_exception = e
                attempt += 1

                # Record failure
                execution_time = time.time() - start_time if 'start_time' in locals() else 0
                self._record_attempt(operation_id, attempt - 1, False, str(e), execution_time)

                # Check if we should retry
                if attempt > self.retry_config["max_retries"]:
                    break

                # Categorize error
                error_category = self._categorize_error(e)

                # Calculate delay
                delay = self._calculate_delay(attempt, error_category, context)

                self.logger.warning({
                    "event_type": "OPERATION_RETRY",
                    "operation_id": operation_id,
                    "attempt": attempt,
                    "error_category": error_category.value,
                    "error_message": str(e),
                    "delay_seconds": delay,
                    "remaining_retries": self.retry_config["max_retries"] - attempt + 1,
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                })

                # Wait before retry
                time.sleep(delay)

        # All retries exhausted
        self.logger.error({
            "event_type": "RETRY_EXHAUSTED",
            "operation_id": operation_id,
            "total_attempts": attempt,
            "final_error": str(last_exception),
            "python_version": PYTHON_VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        raise last_exception

    def _categorize_error(self, exception: Exception) -> ErrorCategory:
        """Categorize exception into error category"""

        error_message = str(exception).lower()
        exception_type = type(exception).__name__.lower()

        # Network errors
        if any(keyword in error_message for keyword in ["connection", "network", "dns", "timeout"]):
            return ErrorCategory.NETWORK
        if "timeout" in exception_type:
            return ErrorCategory.TIMEOUT

        # Rate limit errors
        if any(keyword in error_message for keyword in ["rate limit", "429", "too many requests"]):
            return ErrorCategory.RATE_LIMIT

        # Server errors (5xx)
        if any(keyword in error_message for keyword in ["500", "502", "503", "504", "server error"]):
            return ErrorCategory.SERVER_ERROR

        # Client errors (4xx)
        if any(keyword in error_message for keyword in ["400", "401", "403", "404", "client error"]):
            return ErrorCategory.CLIENT_ERROR

        # Default to network error
        return ErrorCategory.NETWORK

    def _calculate_delay(self, attempt: int, error_category: ErrorCategory,
                        context: Dict[str, Any]) -> float:
        """Calculate delay before next retry attempt"""

        # Get error-specific config
        error_config = self.error_configs.get(error_category, self.retry_config)
        strategy = error_config.get("retry_strategy", self.retry_config["retry_strategy"])

        # Calculate base delay
        if strategy == RetryStrategy.FIXED:
            delay = error_config["base_delay"]
        elif strategy == RetryStrategy.LINEAR:
            delay = error_config["base_delay"] * attempt
        elif strategy == RetryStrategy.EXPONENTIAL:
            delay = error_config["base_delay"] * (2 ** (attempt - 1))
        elif strategy == RetryStrategy.FIBONACCI:
            delay = self._fibonacci(attempt) * error_config["base_delay"]
        else:
            delay = error_config["base_delay"]

        # Apply maximum delay
        max_delay = error_config.get("max_delay", self.retry_config["max_delay"])
        delay = min(delay, max_delay)

        # Apply jitter if enabled
        if self.retry_config.get("jitter", True):
            jitter_factor = self.retry_config.get("jitter_factor", 0.1)
            jitter = random.uniform(-jitter_factor, jitter_factor)
            delay = delay * (1 + jitter)

        # Respect Retry-After header if present
        retry_after = context.get("retry_after")
        if retry_after and error_category == ErrorCategory.RATE_LIMIT:
            delay = max(delay, retry_after)

        return max(delay, 0.1)  # Minimum 100ms delay

    def _fibonacci(self, n: int) -> int:
        """Calculate nth Fibonacci number"""
        if n <= 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b

    def _record_attempt(self, operation_id: str, attempt: int, success: bool,
                       error: Optional[str], execution_time: float):
        """Record attempt in history"""

        if operation_id not in self.request_history:
            self.request_history[operation_id] = []

        # Clean old history
        cutoff_time = datetime.utcnow() - self.history_window
        self.request_history[operation_id] = [
            record for record in self.request_history[operation_id]
            if datetime.fromisoformat(record["timestamp"]) > cutoff_time
        ]

        # Add new record
        record = {
            "attempt": attempt,
            "success": success,
            "error": error,
            "execution_time": execution_time,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        self.request_history[operation_id].append(record)

        # Update circuit breaker
        self._update_circuit_breaker(operation_id, success)

    def _update_circuit_breaker(self, operation_id: str, success: bool):
        """Update circuit breaker state"""

        if operation_id not in self.circuit_breaker_state:
            self.circuit_breaker_state[operation_id] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "success_count": 0
            }

        state = self.circuit_breaker_state[operation_id]

        if success:
            state["success_count"] += 1
            state["failure_count"] = 0  # Reset on success
            if state["state"] == "open":
                state["state"] = "closed"
        else:
            state["failure_count"] += 1
            state["last_failure"] = datetime.utcnow()

            # Open circuit after 5 consecutive failures
            if state["failure_count"] >= 5:
                state["state"] = "open"

    def _is_circuit_open(self, operation_id: str) -> bool:
        """Check if circuit breaker is open"""

        if operation_id not in self.circuit_breaker_state:
            return False

        state = self.circuit_breaker_state[operation_id]

        if state["state"] != "open":
            return False

        # Check if we should try again (half-open state)
        if state["last_failure"]:
            time_since_failure = datetime.utcnow() - state["last_failure"]
            if time_since_failure > timedelta(minutes=1):
                state["state"] = "half-open"
                return False

        return True

    def get_retry_statistics(self, operation_id: str = None) -> Dict[str, Any]:
        """Get retry statistics"""

        if operation_id:
            history = self.request_history.get(operation_id, [])
            circuit_state = self.circuit_breaker_state.get(operation_id, {})

            total_attempts = len(history)
            successful_attempts = len([h for h in history if h["success"]])
            failed_attempts = total_attempts - successful_attempts

            avg_execution_time = sum(h["execution_time"] for h in history) / max(total_attempts, 1)

            return {
                "operation_id": operation_id,
                "total_attempts": total_attempts,
                "successful_attempts": successful_attempts,
                "failed_attempts": failed_attempts,
                "success_rate": successful_attempts / max(total_attempts, 1),
                "average_execution_time": avg_execution_time,
                "circuit_breaker_state": circuit_state.get("state", "unknown"),
                "last_updated": datetime.utcnow().isoformat() + "Z"
            }

        # Global statistics
        all_operations = list(self.request_history.keys())
        total_operations = len(all_operations)

        global_stats = {
            "total_operations": total_operations,
            "operations_with_retries": len([op for op in all_operations if len(self.request_history[op]) > 1]),
            "circuit_breakers_open": len([op for op in all_operations if self._is_circuit_open(op)]),
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

        return global_stats

    def reset_circuit_breaker(self, operation_id: str):
        """Reset circuit breaker for operation"""

        if operation_id in self.circuit_breaker_state:
            self.circuit_breaker_state[operation_id] = {
                "state": "closed",
                "failure_count": 0,
                "last_failure": None,
                "success_count": 0
            }

        self.logger.info({
            "event_type": "CIRCUIT_BREAKER_RESET",
            "operation_id": operation_id,
            "python_version": PYTHON_VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    def get_policy_info(self) -> Dict[str, Any]:
        """Get policy information"""

        return {
            "policy_name": POLICY_NAME,
            "version": POLICY_VERSION,
            "retry_config": self.retry_config,
            "error_configs": {k.value: v for k, v in self.error_configs.items()},
            "active_operations": len(self.request_history),
            "circuit_breakers_open": len([op for op in self.request_history.keys() if self._is_circuit_open(op)]),
            "python_version": PYTHON_VERSION,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }


class CircuitBreakerOpen(Exception):
    """Exception raised when circuit breaker is open"""
    pass


# Policy interface definition
POLICY_INTERFACE = {
    "policy": POLICY_NAME,
    "version": POLICY_VERSION,
    "description": "Intelligent retry and backoff policy for resilient operations",
    "strategies": {
        "retry_strategies": ["fixed", "exponential", "linear", "fibonacci"],
        "backoff_strategies": ["fixed", "exponential", "linear", "random"],
        "error_categories": ["network", "rate_limit", "server_error", "client_error", "timeout"]
    },
    "endpoints": {
        "execute_with_retry": {
            "method": "POST",
            "path": "/api/v1/policies/retry-backoff/execute",
            "input": {
                "operation": "callable function",
                "operation_id": "string",
                "context": "object (optional)"
            },
            "output": {
                "result": "operation result",
                "attempts": "integer",
                "total_delay": "number"
            },
            "token_budget": 100,
            "timeout_seconds": 300
        },
        "get_retry_statistics": {
            "method": "GET",
            "path": "/api/v1/policies/retry-backoff/statistics",
            "input": {
                "operation_id": "string (optional)"
            },
            "output": {
                "statistics": "object with retry metrics"
            },
            "token_budget": 25,
            "timeout_seconds": 10
        }
    },
    "failure_modes": {
        "max_retries_exceeded": "Operation failed after maximum retry attempts",
        "circuit_breaker_open": "Circuit breaker prevents operation execution",
        "invalid_retry_strategy": "Unsupported retry strategy specified",
        "backoff_calculation_error": "Error calculating backoff delay"
    },
    "grounding_sources": [
        "Exponential backoff algorithms",
        "Circuit breaker pattern implementations",
        "HTTP retry specifications",
        "Rate limiting best practices",
        "Resilient system design patterns"
    ],
    "observability": {
        "spans": ["retry_execution", "backoff_calculation", "circuit_breaker_check", "error_categorization"],
        "metrics": ["retry_success_rate", "average_retry_delay", "circuit_breaker_triggers", "error_category_distribution"],
        "logs": ["retry_start", "retry_attempt", "retry_success", "retry_exhausted", "circuit_breaker_state"]
    }
}


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0,
                      strategy: RetryStrategy = RetryStrategy.EXPONENTIAL):
    """
    Decorator for automatic retry with backoff

    Usage:
        @retry_with_backoff(max_retries=5, base_delay=2.0)
        def my_operation():
            # Operation that might fail
            pass
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            policy = RetryBackoffPolicy({})

            # Override default config
            policy.retry_config.update({
                "max_retries": max_retries,
                "base_delay": base_delay,
                "retry_strategy": strategy
            })

            operation_id = f"{func.__name__}_{hash(str(args) + str(kwargs))}"

            return policy.execute_with_retry(
                lambda: func(*args, **kwargs),
                operation_id
            )

        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    policy = RetryBackoffPolicy({})

    def failing_operation():
        """Simulate an operation that fails"""
        if random.random() < 0.7:  # 70% failure rate
            raise ConnectionError("Network timeout")
        return "Success!"

    try:
        result = policy.execute_with_retry(
            failing_operation,
            "test_operation",
            {"source": "example"}
        )
        print(f"Operation succeeded: {result}")
    except Exception as e:
        print(f"Operation failed after retries: {e}")

    # Get statistics
    stats = policy.get_retry_statistics("test_operation")
    print(f"Retry statistics: {stats}")

    # Policy info
    info = policy.get_policy_info()
    print(f"Policy info: {info['active_operations']} active operations")
