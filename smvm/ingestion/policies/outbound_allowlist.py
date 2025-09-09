#!/usr/bin/env python3
"""
SMVM Outbound Allowlist Policy Engine

This module implements outbound traffic allowlisting for the SMVM ingestion system
to ensure only approved destinations are accessed and prevent data exfiltration.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import logging
import ipaddress
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# Policy metadata
POLICY_NAME = "outbound_allowlist"
POLICY_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"

class OutboundNotAllowed(Exception):
    """Exception raised when outbound destination is not allowed"""
    pass

class OutboundAllowlistPolicy:
    """
    Outbound traffic allowlisting policy engine
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Domain allowlist
        self.allowed_domains = self._load_domain_allowlist()

        # IP allowlist
        self.allowed_ip_ranges = self._load_ip_allowlist()

        # Port restrictions
        self.allowed_ports = self._load_port_restrictions()

        # Protocol restrictions
        self.allowed_protocols = {"http", "https"}

        # Content type restrictions
        self.allowed_content_types = {
            "application/json",
            "application/xml",
            "text/plain",
            "text/html",
            "text/xml",
            "application/rss+xml",
            "application/atom+xml"
        }

        # Request size limits
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_response_size = 50 * 1024 * 1024  # 50MB

        # Request history for analysis
        self.request_history: Dict[str, List[Dict[str, Any]]] = {}

    def _load_domain_allowlist(self) -> Set[str]:
        """Load list of allowed domains"""

        # Production allowlist - only approved business domains
        return {
            # Public data sources
            "crunchbase.com",
            "angellist.com",
            "owler.com",
            "pitchbook.com",
            "forbes.com",
            "bloomberg.com",
            "techcrunch.com",
            "reuters.com",
            "wsj.com",
            "ft.com",

            # Social media (read-only)
            "reddit.com",
            "twitter.com",  # For public API access only
            "linkedin.com",

            # Industry directories
            "inc.com",
            "owler.com",
            "cbinsights.com",
            "gartner.com",
            "forrester.com",

            # Government/business registries
            "sec.gov",
            "edgar.sec.gov",
            "data.gov",
            "census.gov",

            # CDN and supporting infrastructure
            "cdn.jsdelivr.net",
            "cdnjs.cloudflare.com",
            "fonts.googleapis.com",
            "fonts.gstatic.com"
        }

    def _load_ip_allowlist(self) -> List[ipaddress.IPv4Network]:
        """Load list of allowed IP ranges"""

        # For production, only allow known service IPs
        # This would be populated with actual service IP ranges
        return [
            # Example IP ranges - would be replaced with actual service IPs
            # ipaddress.IPv4Network("192.168.1.0/24"),  # Internal
            # ipaddress.IPv4Network("10.0.0.0/8"),      # Internal
        ]

    def _load_port_restrictions(self) -> Set[int]:
        """Load allowed destination ports"""

        return {
            80,     # HTTP
            443,    # HTTPS
            22,     # SSH (for secure admin access)
            53      # DNS
        }

    def check_outbound_access(self, url: str, method: str = "GET",
                            content_type: str = None, request_size: int = 0) -> Dict[str, Any]:
        """
        Check if outbound access to URL is allowed

        Args:
            url: Target URL
            method: HTTP method
            content_type: Content type header
            request_size: Size of request payload

        Returns:
            Access check result
        """

        access_result = {
            "allowed": False,
            "url": url,
            "method": method,
            "blocking_reasons": [],
            "warnings": [],
            "check_timestamp": datetime.utcnow().isoformat() + "Z"
        }

        try:
            parsed_url = urlparse(url)

            # Check protocol
            if parsed_url.scheme not in self.allowed_protocols:
                access_result["blocking_reasons"].append(
                    f"protocol_not_allowed: {parsed_url.scheme}"
                )

            # Check domain
            domain = parsed_url.netloc.lower()
            if not self._is_domain_allowed(domain):
                access_result["blocking_reasons"].append(
                    f"domain_not_allowed: {domain}"
                )

            # Check port
            if parsed_url.port and parsed_url.port not in self.allowed_ports:
                access_result["blocking_reasons"].append(
                    f"port_not_allowed: {parsed_url.port}"
                )

            # Check request size
            if request_size > self.max_request_size:
                access_result["blocking_reasons"].append(
                    f"request_too_large: {request_size} > {self.max_request_size}"
                )

            # Check content type (if provided)
            if content_type and content_type not in self.allowed_content_types:
                access_result["warnings"].append(
                    f"unusual_content_type: {content_type}"
                )

            # Check for suspicious patterns
            suspicious_patterns = self._check_suspicious_patterns(url)
            if suspicious_patterns:
                access_result["blocking_reasons"].extend(suspicious_patterns)

            # If no blocking reasons, allow access
            if not access_result["blocking_reasons"]:
                access_result["allowed"] = True

            # Log access attempt
            log_level = "WARNING" if access_result["blocking_reasons"] else "DEBUG"
            self.logger.log(
                getattr(logging, log_level),
                {
                    "event_type": "OUTBOUND_ACCESS_CHECK",
                    "url": url,
                    "method": method,
                    "allowed": access_result["allowed"],
                    "blocking_reasons": access_result["blocking_reasons"],
                    "warnings": access_result["warnings"],
                    "domain": domain,
                    "python_version": PYTHON_VERSION,
                    "timestamp": datetime.utcnow().isoformat() + "Z"
                }
            )

        except Exception as e:
            access_result["blocking_reasons"].append(f"error: {str(e)}")
            self.logger.error(f"Outbound access check error for {url}: {e}")

        return access_result

    def _is_domain_allowed(self, domain: str) -> bool:
        """Check if domain is in allowlist"""

        # Exact match
        if domain in self.allowed_domains:
            return True

        # Subdomain check (e.g., api.crunchbase.com matches crunchbase.com)
        for allowed_domain in self.allowed_domains:
            if domain.endswith(f".{allowed_domain}"):
                return True

        # Check IP ranges (if domain resolves to IP)
        try:
            import socket
            ip = socket.gethostbyname(domain)
            ip_addr = ipaddress.IPv4Address(ip)

            for ip_range in self.allowed_ip_ranges:
                if ip_addr in ip_range:
                    return True
        except:
            pass  # DNS resolution failure - deny access

        return False

    def _check_suspicious_patterns(self, url: str) -> List[str]:
        """Check URL for suspicious patterns"""

        suspicious_reasons = []

        # Check for IP addresses in URL (often malicious)
        if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', url):
            suspicious_reasons.append("ip_address_in_url")

        # Check for unusual ports
        parsed = urlparse(url)
        if parsed.port and parsed.port not in [80, 443]:
            suspicious_reasons.append(f"unusual_port: {parsed.port}")

        # Check for very long URLs
        if len(url) > 2048:
            suspicious_reasons.append("url_too_long")

        # Check for suspicious query parameters
        if parsed.query:
            suspicious_params = ["exec", "cmd", "shell", "eval"]
            for param in suspicious_params:
                if param in parsed.query.lower():
                    suspicious_reasons.append(f"suspicious_query_param: {param}")

        return suspicious_reasons

    def record_outbound_request(self, url: str, method: str, status_code: int,
                              response_size: int, duration: float) -> None:
        """
        Record outbound request for monitoring and analysis

        Args:
            url: Requested URL
            method: HTTP method
            status_code: HTTP response status code
            response_size: Size of response
            duration: Request duration in seconds
        """

        domain = urlparse(url).netloc.lower()

        request_record = {
            "url": url,
            "domain": domain,
            "method": method,
            "status_code": status_code,
            "response_size": response_size,
            "duration": duration,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        if domain not in self.request_history:
            self.request_history[domain] = []

        self.request_history[domain].append(request_record)

        # Keep only recent history (last 1000 requests per domain)
        if len(self.request_history[domain]) > 1000:
            self.request_history[domain] = self.request_history[domain][-1000:]

        # Log successful request
        self.logger.debug({
            "event_type": "OUTBOUND_REQUEST_RECORDED",
            "url": url,
            "domain": domain,
            "method": method,
            "status_code": status_code,
            "response_size": response_size,
            "duration": duration,
            "python_version": PYTHON_VERSION,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

    def get_domain_statistics(self, domain: str) -> Dict[str, Any]:
        """Get access statistics for a domain"""

        if domain not in self.request_history:
            return {"domain": domain, "total_requests": 0}

        requests = self.request_history[domain]
        total_requests = len(requests)

        if total_requests == 0:
            return {"domain": domain, "total_requests": 0}

        # Calculate statistics
        status_codes = {}
        total_response_size = 0
        total_duration = 0

        for req in requests:
            status_codes[req["status_code"]] = status_codes.get(req["status_code"], 0) + 1
            total_response_size += req["response_size"]
            total_duration += req["duration"]

        # Get recent requests (last hour)
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_requests = [
            req for req in requests
            if datetime.fromisoformat(req["timestamp"]) > one_hour_ago
        ]

        return {
            "domain": domain,
            "total_requests": total_requests,
            "recent_requests": len(recent_requests),
            "status_code_distribution": status_codes,
            "average_response_size": total_response_size / total_requests,
            "average_duration": total_duration / total_requests,
            "success_rate": (sum(count for code, count in status_codes.items() if 200 <= code < 300) / total_requests) * 100,
            "last_request": requests[-1]["timestamp"] if requests else None
        }

    def add_allowed_domain(self, domain: str, justification: str) -> bool:
        """
        Add domain to allowlist (requires approval)

        Args:
            domain: Domain to add
            justification: Business justification

        Returns:
            True if added successfully
        """

        # In production, this would require approval workflow
        if self._validate_domain_addition(domain, justification):
            self.allowed_domains.add(domain)

            self.logger.info({
                "event_type": "DOMAIN_ADDED_TO_ALLOWLIST",
                "domain": domain,
                "justification": justification,
                "python_version": PYTHON_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

            return True

        return False

    def _validate_domain_addition(self, domain: str, justification: str) -> bool:
        """Validate domain addition request"""

        # Basic validation
        if not domain or len(domain) < 4:
            return False

        # Check if already allowed
        if domain in self.allowed_domains:
            return False

        # Require justification
        if not justification or len(justification) < 10:
            return False

        # In production, this would trigger approval workflow
        return True

    def get_policy_info(self) -> Dict[str, Any]:
        """Get policy information"""

        return {
            "policy_name": POLICY_NAME,
            "version": POLICY_VERSION,
            "allowed_domains_count": len(self.allowed_domains),
            "allowed_ip_ranges_count": len(self.allowed_ip_ranges),
            "allowed_ports_count": len(self.allowed_ports),
            "allowed_protocols": list(self.allowed_protocols),
            "max_request_size_mb": self.max_request_size / (1024 * 1024),
            "max_response_size_mb": self.max_response_size / (1024 * 1024),
            "monitored_domains_count": len(self.request_history),
            "python_version": PYTHON_VERSION,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }


# Policy interface definition
POLICY_INTERFACE = {
    "policy": POLICY_NAME,
    "version": POLICY_VERSION,
    "description": "Outbound traffic allowlisting to prevent unauthorized access",
    "controls": {
        "domain_allowlist": True,
        "ip_restrictions": True,
        "port_restrictions": True,
        "protocol_filtering": True,
        "content_type_validation": True,
        "size_limits": True
    },
    "endpoints": {
        "check_outbound_access": {
            "method": "POST",
            "path": "/api/v1/policies/outbound-allowlist/check",
            "input": {
                "url": "string",
                "method": "string (optional)",
                "content_type": "string (optional)",
                "request_size": "integer (optional)"
            },
            "output": {
                "allowed": "boolean",
                "blocking_reasons": "array of strings",
                "warnings": "array of strings"
            },
            "token_budget": 20,
            "timeout_seconds": 5
        },
        "get_domain_statistics": {
            "method": "GET",
            "path": "/api/v1/policies/outbound-allowlist/domain-stats",
            "input": {
                "domain": "string"
            },
            "output": {
                "domain": "string",
                "total_requests": "integer",
                "success_rate": "number"
            },
            "token_budget": 10,
            "timeout_seconds": 5
        }
    },
    "failure_modes": {
        "domain_not_allowed": "Requested domain not in allowlist",
        "protocol_not_supported": "Protocol not in allowed list",
        "port_not_allowed": "Destination port not permitted",
        "content_suspicious": "URL contains suspicious patterns",
        "size_limit_exceeded": "Request/response size exceeds limits"
    },
    "grounding_sources": [
        "Zero Trust Network Access principles",
        "Network segmentation best practices",
        "Web application firewall patterns",
        "DDoS protection strategies",
        "Data exfiltration prevention techniques"
    ],
    "observability": {
        "spans": ["access_check", "domain_validation", "suspicious_pattern_detection", "statistics_collection"],
        "metrics": ["allowed_requests_total", "blocked_requests_total", "domain_access_frequency", "suspicious_patterns_detected"],
        "logs": ["access_check", "domain_blocked", "suspicious_pattern", "statistics_update", "domain_added"]
    }
}


def outbound_allowed(url: str, method: str = "GET"):
    """
    Decorator for outbound access control

    Usage:
        @outbound_allowed
        def fetch_external_data(url):
            # Only allowed URLs will be accessed
            pass
    """

    def decorator(func):
        policy = OutboundAllowlistPolicy({})

        def wrapper(*args, **kwargs):
            # Extract URL from arguments
            target_url = kwargs.get('url') or (args[0] if args else None)

            if not target_url:
                raise ValueError("URL parameter required")

            # Check access
            access_result = policy.check_outbound_access(target_url, method)

            if not access_result["allowed"]:
                raise OutboundNotAllowed(
                    f"Outbound access denied: {access_result['blocking_reasons']}"
                )

            # Execute function
            result = func(*args, **kwargs)

            # Record successful request (would need actual metrics)
            # policy.record_outbound_request(target_url, method, 200, 0, 0.1)

            return result

        return wrapper
    return decorator


if __name__ == "__main__":
    # Example usage
    policy = OutboundAllowlistPolicy({})

    # Test URLs
    test_urls = [
        "https://crunchbase.com/company/techcorp",  # Should be allowed
        "https://reddit.com/r/technology",          # Should be allowed
        "https://facebook.com/business",            # Should be blocked
        "https://malicious-site.com/data",          # Should be blocked
        "http://internal.corp.com/api"              # Should be blocked
    ]

    for url in test_urls:
        result = policy.check_outbound_access(url)
        print(f"URL: {url}")
        print(f"  Allowed: {result['allowed']}")
        print(f"  Blocking reasons: {result['blocking_reasons']}")
        print()

    # Get policy info
    policy_info = policy.get_policy_info()
    print("Policy Info:")
    print(f"  Allowed domains: {policy_info['allowed_domains_count']}")
    print(f"  Allowed ports: {policy_info['allowed_ports_count']}")
    print(f"  Protocols: {policy_info['allowed_protocols']}")
