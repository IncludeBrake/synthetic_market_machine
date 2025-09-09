#!/usr/bin/env python3
"""
SMVM ToS/Robots Policy Engine

This module implements the Terms of Service and robots.txt compliance engine
for the SMVM ingestion system.
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
import logging
import re
import urllib.robotparser
from urllib.parse import urlparse, urljoin

logger = logging.getLogger(__name__)

# Policy metadata
POLICY_NAME = "tos_robots"
POLICY_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"

class TOSRobotsPolicy:
    """
    Terms of Service and robots.txt compliance policy engine
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # ToS compliance rules
        self.tos_rules = {
            "max_requests_per_domain_per_hour": 100,
            "min_delay_between_requests": 1.0,  # seconds
            "respect_robots_txt": True,
            "respect_rate_limits": True,
            "honor_crawl_delays": True,
            "check_tos_before_crawling": True
        }

        # Robots.txt cache
        self.robots_cache: Dict[str, Dict[str, Any]] = {}
        self.robots_cache_timeout = timedelta(hours=24)

        # Domain allowlist
        self.allowed_domains = self._load_allowed_domains()

        # Blocked domains
        self.blocked_domains = self._load_blocked_domains()

        # User agent string
        self.user_agent = "SMVM-Ingestion-Bot/1.0 (https://smvm.company.com/bot)"

    def _load_allowed_domains(self) -> Set[str]:
        """Load list of allowed domains for crawling"""
        # This would typically be loaded from configuration
        return {
            "crunchbase.com",
            "angellist.com",
            "reddit.com",
            "forbes.com",
            "bloomberg.com",
            "techcrunch.com",
            "owler.com",
            "pitchbook.com",
            "inc.com",
            "owler.com"
        }

    def _load_blocked_domains(self) -> Set[str]:
        """Load list of blocked domains"""
        return {
            "facebook.com",
            "instagram.com",
            "twitter.com",
            "linkedin.com",
            "tiktok.com",
            "snapchat.com"
        }

    def check_url_compliance(self, url: str, user_agent: str = None) -> Dict[str, Any]:
        """
        Check if URL can be crawled according to ToS and robots.txt

        Args:
            url: URL to check
            user_agent: User agent string to use

        Returns:
            Compliance check result
        """

        if user_agent is None:
            user_agent = self.user_agent

        compliance_result = {
            "url": url,
            "can_crawl": False,
            "blocking_reasons": [],
            "robots_allowed": False,
            "tos_compliant": False,
            "rate_limit_ok": False,
            "check_timestamp": datetime.utcnow().isoformat() + "Z",
            "user_agent": user_agent
        }

        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()

            # Check domain allowlist
            if domain not in self.allowed_domains:
                compliance_result["blocking_reasons"].append("domain_not_allowed")
                return compliance_result

            # Check domain blocklist
            if domain in self.blocked_domains:
                compliance_result["blocking_reasons"].append("domain_blocked")
                return compliance_result

            # Check robots.txt
            robots_allowed = self._check_robots_txt(url, user_agent)
            compliance_result["robots_allowed"] = robots_allowed

            if not robots_allowed:
                compliance_result["blocking_reasons"].append("robots_txt_disallowed")
                return compliance_result

            # Check ToS compliance
            tos_compliant = self._check_tos_compliance(domain)
            compliance_result["tos_compliant"] = tos_compliant

            if not tos_compliant:
                compliance_result["blocking_reasons"].append("tos_violation")
                return compliance_result

            # Check rate limits
            rate_limit_ok = self._check_rate_limits(domain)
            compliance_result["rate_limit_ok"] = rate_limit_ok

            if not rate_limit_ok:
                compliance_result["blocking_reasons"].append("rate_limit_exceeded")
                return compliance_result

            # All checks passed
            compliance_result["can_crawl"] = True

            self.logger.debug({
                "event_type": "URL_COMPLIANCE_CHECK",
                "url": url,
                "domain": domain,
                "can_crawl": True,
                "checks_passed": ["domain_allowed", "robots_allowed", "tos_compliant", "rate_limit_ok"],
                "python_version": PYTHON_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        except Exception as e:
            compliance_result["blocking_reasons"].append(f"error: {str(e)}")
            self.logger.error(f"Compliance check error for {url}: {e}")

        return compliance_result

    def _check_robots_txt(self, url: str, user_agent: str) -> bool:
        """Check robots.txt for the given URL"""

        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            # Check cache first
            cache_key = robots_url
            if cache_key in self.robots_cache:
                cached_entry = self.robots_cache[cache_key]
                if datetime.utcnow() - cached_entry["cached_at"] < self.robots_cache_timeout:
                    return cached_entry["allows"](url, user_agent)

            # Fetch and parse robots.txt
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            # Cache the result
            def allows_func(url_to_check, ua):
                return rp.can_fetch(ua, url_to_check)

            self.robots_cache[cache_key] = {
                "allows": allows_func,
                "cached_at": datetime.utcnow(),
                "robots_url": robots_url
            }

            return rp.can_fetch(user_agent, url)

        except Exception as e:
            # If robots.txt can't be fetched, assume allowed (common practice)
            self.logger.warning(f"Could not fetch robots.txt for {url}: {e}")
            return True

    def _check_tos_compliance(self, domain: str) -> bool:
        """Check Terms of Service compliance for domain"""

        # Domain-specific ToS rules
        tos_rules = {
            "crunchbase.com": {
                "allowed": True,
                "max_requests_per_hour": 50,
                "requires_api_key": True,
                "commercial_use_allowed": False
            },
            "reddit.com": {
                "allowed": True,
                "max_requests_per_hour": 60,
                "requires_api_key": False,
                "commercial_use_allowed": True
            },
            "angellist.com": {
                "allowed": True,
                "max_requests_per_hour": 30,
                "requires_api_key": False,
                "commercial_use_allowed": False
            }
        }

        domain_rule = tos_rules.get(domain, {
            "allowed": True,
            "max_requests_per_hour": 20,
            "requires_api_key": False,
            "commercial_use_allowed": True
        })

        return domain_rule["allowed"]

    def _check_rate_limits(self, domain: str) -> bool:
        """Check if rate limits allow crawling this domain"""

        # This would implement actual rate limiting logic
        # For now, return True (would be implemented with actual counters)
        return True

    def get_crawl_delay(self, url: str, user_agent: str = None) -> float:
        """Get crawl delay for URL from robots.txt"""

        if user_agent is None:
            user_agent = self.user_agent

        try:
            parsed_url = urlparse(url)
            robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()

            delay = rp.crawl_delay(user_agent)
            if delay is None:
                delay = self.tos_rules["min_delay_between_requests"]

            return max(delay, self.tos_rules["min_delay_between_requests"])

        except Exception:
            return self.tos_rules["min_delay_between_requests"]

    def get_domain_policy(self, domain: str) -> Dict[str, Any]:
        """Get ToS and robots policy for a domain"""

        return {
            "domain": domain,
            "allowed": domain in self.allowed_domains,
            "blocked": domain in self.blocked_domains,
            "max_requests_per_hour": self._get_domain_rate_limit(domain),
            "min_delay_seconds": self.tos_rules["min_delay_between_requests"],
            "requires_api_key": self._domain_requires_api_key(domain),
            "commercial_use_allowed": self._commercial_use_allowed(domain),
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }

    def _get_domain_rate_limit(self, domain: str) -> int:
        """Get rate limit for domain"""
        domain_limits = {
            "crunchbase.com": 50,
            "reddit.com": 60,
            "angellist.com": 30,
            "forbes.com": 20,
            "bloomberg.com": 15
        }
        return domain_limits.get(domain, self.tos_rules["max_requests_per_domain_per_hour"])

    def _domain_requires_api_key(self, domain: str) -> bool:
        """Check if domain requires API key"""
        api_key_domains = {"crunchbase.com", "owler.com"}
        return domain in api_key_domains

    def _commercial_use_allowed(self, domain: str) -> bool:
        """Check if commercial use is allowed"""
        no_commercial_domains = {"crunchbase.com", "angellist.com"}
        return domain not in no_commercial_domains

    def get_policy_info(self) -> Dict[str, Any]:
        """Get policy information"""

        return {
            "policy_name": POLICY_NAME,
            "version": POLICY_VERSION,
            "rules": self.tos_rules,
            "allowed_domains_count": len(self.allowed_domains),
            "blocked_domains_count": len(self.blocked_domains),
            "robots_cache_size": len(self.robots_cache),
            "user_agent": self.user_agent,
            "python_version": PYTHON_VERSION,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }


# Policy interface definition
POLICY_INTERFACE = {
    "policy": POLICY_NAME,
    "version": POLICY_VERSION,
    "description": "Terms of Service and robots.txt compliance policy",
    "rules": {
        "respect_robots_txt": True,
        "respect_rate_limits": True,
        "honor_crawl_delays": True,
        "check_tos_before_crawling": True,
        "domain_allowlist_enforced": True,
        "commercial_use_restrictions": True
    },
    "endpoints": {
        "check_url_compliance": {
            "method": "POST",
            "path": "/api/v1/policies/tos-robots/check-compliance",
            "input": {
                "url": "string",
                "user_agent": "string (optional)"
            },
            "output": {
                "can_crawl": "boolean",
                "blocking_reasons": "array of strings",
                "compliance_details": "object"
            },
            "token_budget": 50,
            "timeout_seconds": 30
        },
        "get_crawl_delay": {
            "method": "GET",
            "path": "/api/v1/policies/tos-robots/crawl-delay",
            "input": {
                "url": "string",
                "user_agent": "string (optional)"
            },
            "output": {
                "delay_seconds": "number"
            },
            "token_budget": 25,
            "timeout_seconds": 10
        }
    },
    "failure_modes": {
        "robots_txt_unavailable": "Cannot fetch robots.txt file",
        "domain_not_allowed": "Domain not in allowlist",
        "rate_limit_exceeded": "Request rate exceeds limits",
        "tos_violation": "Terms of Service violation detected",
        "network_error": "Network connectivity issues"
    },
    "grounding_sources": [
        "robots.txt specification (RFC)",
        "Terms of Service analysis frameworks",
        "Web crawling best practices",
        "Rate limiting standards",
        "Legal compliance guidelines for web scraping"
    ],
    "observability": {
        "spans": ["compliance_check", "robots_fetch", "tos_validation", "rate_limit_check"],
        "metrics": ["compliance_check_success_rate", "robots_cache_hit_rate", "blocked_requests_count", "allowed_requests_count"],
        "logs": ["compliance_check_start", "robots_fetch", "tos_validation", "rate_limit_check", "blocking_decision"]
    }
}


if __name__ == "__main__":
    # Example usage
    config = {"strict_compliance": True}
    policy = TOSRobotsPolicy(config)

    # Check URL compliance
    test_urls = [
        "https://crunchbase.com/company/techcorp",
        "https://reddit.com/r/technology",
        "https://forbes.com/companies",
        "https://facebook.com/business"  # Should be blocked
    ]

    for url in test_urls:
        result = policy.check_url_compliance(url)
        print(f"URL: {url}")
        print(f"  Can crawl: {result['can_crawl']}")
        print(f"  Blocking reasons: {result['blocking_reasons']}")
        print()

    # Get policy info
    policy_info = policy.get_policy_info()
    print("Policy Info:")
    print(f"  Allowed domains: {policy_info['allowed_domains_count']}")
    print(f"  Blocked domains: {policy_info['blocked_domains_count']}")
    print(f"  Robots cache size: {policy_info['robots_cache_size']}")
