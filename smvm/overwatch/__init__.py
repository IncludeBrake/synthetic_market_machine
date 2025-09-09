# SMVM Overwatch Service
# Handles sanity checks, bias detection, realism validation, and token management

"""
SMVM Overwatch Service

Purpose: Provide governance and quality control across all SMVM operations
- Sanity checking and bias detection
- Realism validation and bounds enforcement
- Token ceiling management and enforcement
- Quality assurance and anomaly detection

Data Zone: GREEN (monitoring data) → AMBER (alerts and reports)
Retention: 90 days for monitoring data, indefinite for policy rules
"""

from typing import Dict, List, Optional, Protocol
import logging
from datetime import datetime
from pathlib import Path

# Service metadata
SERVICE_NAME = "overwatch"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"
DATA_ZONE = "GREEN"
RETENTION_DAYS = 90

logger = logging.getLogger(__name__)


class SanityChecker(Protocol):
    """Protocol for sanity checking algorithms"""

    def check_data_sanity(self, data: Dict, rules: Dict) -> Dict:
        """Check data against sanity rules"""
        ...

    def validate_business_logic(self, data: Dict, context: Dict) -> Dict:
        """Validate business logic constraints"""
        ...


class BiasDetector(Protocol):
    """Protocol for bias detection"""

    def detect_systematic_bias(self, data: List[Dict], dimensions: List[str]) -> Dict:
        """Detect systematic bias patterns"""
        ...

    def measure_fairness_metrics(self, predictions: List[Dict], ground_truth: List[Dict]) -> Dict:
        """Measure fairness and bias metrics"""
        ...


class RealismValidator(Protocol):
    """Protocol for realism validation"""

    def validate_scenario_realism(self, scenario: Dict, historical_data: Dict) -> Dict:
        """Validate scenario realism against historical patterns"""
        ...

    def assess_result_plausibility(self, results: Dict, constraints: Dict) -> Dict:
        """Assess plausibility of results"""
        ...


class TokenCeilingManager:
    """
    Token ceiling management and enforcement

    Manages dynamic token limits based on:
    - Service load and performance
    - User behavior patterns
    - System health metrics
    - Business priority levels
    """

    def __init__(self):
        self.base_limits = {
            "ingestion": 1000,
            "personas": 2000,
            "competitors": 1500,
            "simulation": 3000,
            "analysis": 2000,
            "overwatch": 500
        }
        self.dynamic_multipliers = {}
        self.usage_history = []

    def get_dynamic_limit(self, service: str, context: Dict) -> int:
        """Calculate dynamic token limit based on context"""
        base_limit = self.base_limits.get(service, 1000)

        # Apply load-based multiplier
        load_factor = context.get("system_load", 1.0)
        load_multiplier = max(0.5, min(2.0, 1.0 / load_factor))

        # Apply priority multiplier
        priority = context.get("priority", "normal")
        priority_multipliers = {"low": 0.7, "normal": 1.0, "high": 1.3, "critical": 1.5}
        priority_multiplier = priority_multipliers.get(priority, 1.0)

        # Apply user behavior multiplier
        user_history = context.get("user_history", {})
        behavior_score = user_history.get("efficiency_score", 1.0)
        behavior_multiplier = max(0.8, min(1.2, behavior_score))

        dynamic_limit = int(base_limit * load_multiplier * priority_multiplier * behavior_multiplier)

        # Record decision for monitoring
        self.usage_history.append({
            "service": service,
            "base_limit": base_limit,
            "dynamic_limit": dynamic_limit,
            "multipliers": {
                "load": load_multiplier,
                "priority": priority_multiplier,
                "behavior": behavior_multiplier
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        return dynamic_limit

    def enforce_token_limit(self, service: str, requested_tokens: int, context: Dict) -> Dict:
        """Enforce token limit for a service request"""
        allowed_tokens = self.get_dynamic_limit(service, context)

        if requested_tokens <= allowed_tokens:
            return {
                "approved": True,
                "granted_tokens": requested_tokens,
                "remaining_capacity": allowed_tokens - requested_tokens
            }
        else:
            return {
                "approved": False,
                "requested_tokens": requested_tokens,
                "maximum_allowed": allowed_tokens,
                "reduction_suggestion": int(allowed_tokens * 0.8)
            }


class AbstainVetoEngine:
    """
    Abstain/veto decision engine

    Provides automated decision-making for:
    - Request abstention based on risk assessment
    - Veto of high-risk operations
    - Escalation triggers for manual review
    """

    def __init__(self):
        self.risk_thresholds = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.8,
            "critical": 0.95
        }
        self.veto_triggers = {
            "data_sensitivity": 0.9,
            "financial_impact": 0.85,
            "regulatory_risk": 0.95,
            "system_stability": 0.8
        }

    def assess_request_risk(self, request: Dict, context: Dict) -> Dict:
        """Assess risk level of a service request"""
        risk_factors = {
            "data_sensitivity": self._assess_data_sensitivity(request),
            "financial_impact": self._assess_financial_impact(request),
            "regulatory_risk": self._assess_regulatory_risk(request),
            "system_stability": self._assess_system_stability(context),
            "user_reliability": self._assess_user_reliability(context)
        }

        # Calculate overall risk score
        weights = {"data_sensitivity": 0.3, "financial_impact": 0.25, "regulatory_risk": 0.25,
                  "system_stability": 0.15, "user_reliability": 0.05}

        overall_risk = sum(risk_factors[factor] * weights[factor] for factor in risk_factors)

        # Determine risk level
        risk_level = "low"
        for level, threshold in self.risk_thresholds.items():
            if overall_risk >= threshold:
                risk_level = level

        return {
            "overall_risk_score": overall_risk,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendation": self._generate_risk_recommendation(overall_risk, risk_factors)
        }

    def should_abstain_or_veto(self, risk_assessment: Dict) -> Dict:
        """Determine if request should be abstained from or vetoed"""
        risk_score = risk_assessment["overall_risk_score"]
        risk_factors = risk_assessment["risk_factors"]

        # Check veto triggers
        veto_reasons = []
        for trigger, threshold in self.veto_triggers.items():
            if risk_factors.get(trigger, 0) >= threshold:
                veto_reasons.append(f"High {trigger.replace('_', ' ')}: {risk_factors[trigger]:.2f}")

        if veto_reasons:
            return {
                "decision": "veto",
                "reasons": veto_reasons,
                "escalation_required": True,
                "review_priority": "high"
            }

        # Check abstain conditions
        if risk_score >= 0.7:
            return {
                "decision": "abstain",
                "reason": f"High overall risk score: {risk_score:.2f}",
                "suggestion": "Reduce scope or provide additional safeguards",
                "escalation_required": risk_score >= 0.8
            }

        return {
            "decision": "proceed",
            "confidence_level": 1.0 - risk_score,
            "monitoring_level": "standard" if risk_score < 0.4 else "enhanced"
        }

    def _assess_data_sensitivity(self, request: Dict) -> float:
        """Assess data sensitivity risk"""
        sensitive_keywords = ["pii", "financial", "medical", "personal", "confidential"]
        request_str = str(request).lower()

        sensitivity_score = sum(1 for keyword in sensitive_keywords if keyword in request_str) / len(sensitive_keywords)
        return min(1.0, sensitivity_score * 2)  # Scale up for sensitivity

    def _assess_financial_impact(self, request: Dict) -> float:
        """Assess financial impact risk"""
        high_impact_indicators = ["investment", "revenue", "cost", "budget", "financial"]
        request_str = str(request).lower()

        impact_score = sum(1 for indicator in high_impact_indicators if indicator in request_str) / len(high_impact_indicators)
        return min(1.0, impact_score * 1.5)

    def _assess_regulatory_risk(self, request: Dict) -> float:
        """Assess regulatory compliance risk"""
        regulatory_keywords = ["regulation", "compliance", "audit", "legal", "gdpr", "sox"]
        request_str = str(request).lower()

        regulatory_score = sum(1 for keyword in regulatory_keywords if keyword in request_str) / len(regulatory_keywords)
        return min(1.0, regulatory_score * 2)

    def _assess_system_stability(self, context: Dict) -> float:
        """Assess system stability risk"""
        load_factor = context.get("system_load", 1.0)
        error_rate = context.get("recent_error_rate", 0.0)

        stability_risk = (load_factor - 1.0) * 0.3 + error_rate * 0.7
        return min(1.0, max(0.0, stability_risk))

    def _assess_user_reliability(self, context: Dict) -> float:
        """Assess user reliability based on history"""
        success_rate = context.get("user_success_rate", 0.8)
        compliance_score = context.get("compliance_score", 0.9)

        reliability_risk = (1.0 - success_rate) * 0.6 + (1.0 - compliance_score) * 0.4
        return min(1.0, max(0.0, reliability_risk))

    def _generate_risk_recommendation(self, risk_score: float, risk_factors: Dict) -> str:
        """Generate risk mitigation recommendation"""
        if risk_score >= 0.8:
            return "High risk - requires senior approval and enhanced monitoring"
        elif risk_score >= 0.6:
            return "Medium risk - implement additional controls and monitoring"
        elif risk_score >= 0.4:
            return "Moderate risk - standard monitoring recommended"
        else:
            return "Low risk - proceed with standard controls"


class OverwatchService:
    """
    Main overwatch service providing governance and quality control
    """

    def __init__(self, config: Dict):
        self.config = config
        self.sanity_checker: Optional[SanityChecker] = None
        self.bias_detector: Optional[BiasDetector] = None
        self.realism_validator: Optional[RealismValidator] = None
        self.token_manager = TokenCeilingManager()
        self.decision_engine = AbstainVetoEngine()
        self.logger = logging.getLogger(f"{__name__}.OverwatchService")

    def register_components(self,
                          sanity_checker: SanityChecker,
                          bias_detector: BiasDetector,
                          realism_validator: RealismValidator) -> None:
        """Register overwatch components"""
        self.sanity_checker = sanity_checker
        self.bias_detector = bias_detector
        self.realism_validator = realism_validator
        self.logger.info("Registered overwatch components")

    def evaluate_request(self, service_request: Dict, context: Dict) -> Dict:
        """
        Comprehensive evaluation of a service request

        Args:
            service_request: The service request to evaluate
            context: Request context and system state

        Returns:
            Dict containing evaluation results and recommendations
        """
        evaluation = {
            "request_id": service_request.get("id", "unknown"),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "evaluations": {},
            "overall_decision": {},
            "recommendations": []
        }

        # Token ceiling evaluation
        service_name = service_request.get("service", "unknown")
        requested_tokens = service_request.get("token_budget", 1000)
        token_evaluation = self.token_manager.enforce_token_limit(service_name, requested_tokens, context)
        evaluation["evaluations"]["token_ceiling"] = token_evaluation

        # Risk assessment
        risk_assessment = self.decision_engine.assess_request_risk(service_request, context)
        evaluation["evaluations"]["risk_assessment"] = risk_assessment

        # Abstain/veto decision
        decision_result = self.decision_engine.should_abstain_or_veto(risk_assessment)
        evaluation["evaluations"]["decision"] = decision_result

        # Overall decision logic
        if not token_evaluation["approved"]:
            evaluation["overall_decision"] = {
                "action": "reject",
                "reason": "Token limit exceeded",
                "alternative_budget": token_evaluation.get("reduction_suggestion")
            }
        elif decision_result["decision"] == "veto":
            evaluation["overall_decision"] = {
                "action": "veto",
                "reason": decision_result["reason"],
                "requires_escalation": True
            }
        elif decision_result["decision"] == "abstain":
            evaluation["overall_decision"] = {
                "action": "abstain",
                "reason": decision_result["reason"],
                "suggestion": decision_result.get("suggestion")
            }
        else:
            evaluation["overall_decision"] = {
                "action": "approve",
                "confidence": decision_result.get("confidence_level", 0.8),
                "monitoring_level": decision_result.get("monitoring_level", "standard"),
                "approved_budget": token_evaluation["granted_tokens"]
            }

        # Generate recommendations
        evaluation["recommendations"] = self._generate_recommendations(evaluation)

        self.logger.info(f"Evaluated request {evaluation['request_id']}: {evaluation['overall_decision']['action']}")
        return evaluation

    def _generate_recommendations(self, evaluation: Dict) -> List[str]:
        """Generate recommendations based on evaluation results"""
        recommendations = []

        decision = evaluation["overall_decision"]["action"]

        if decision == "reject":
            recommendations.append("Reduce request scope or break into smaller requests")
            recommendations.append("Consider alternative approaches with lower token requirements")

        elif decision == "veto":
            recommendations.append("Request requires senior approval due to high risk factors")
            recommendations.append("Consider implementing additional safeguards or controls")

        elif decision == "abstain":
            recommendations.append("Consider deferring request until risk factors are mitigated")
            recommendations.append("Provide additional context or documentation to reduce uncertainty")

        elif decision == "approve":
            confidence = evaluation["overall_decision"].get("confidence", 0.5)
            if confidence < 0.7:
                recommendations.append("Implement enhanced monitoring for this request")
                recommendations.append("Prepare contingency plans for potential issues")

        return recommendations


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Governance and quality control service for SMVM operations",
    "endpoints": {
        "evaluate_request": {
            "method": "POST",
            "path": "/api/v1/overwatch/evaluate",
            "input": {
                "service_request": "object (service request details)",
                "context": "object (system and user context)"
            },
            "output": {
                "evaluation": "object (comprehensive evaluation)",
                "overall_decision": "object (approve/reject/abstain/veto)",
                "recommendations": "array (suggested actions)"
            },
            "token_budget": 500,
            "timeout_seconds": 30
        },
        "get_token_limits": {
            "method": "GET",
            "path": "/api/v1/overwatch/token-limits",
            "input": {
                "service": "string (service name)"
            },
            "output": {
                "base_limit": "integer",
                "dynamic_limit": "integer",
                "factors": "object (limit calculation factors)"
            },
            "token_budget": 100,
            "timeout_seconds": 10
        }
    },
    "failure_modes": {
        "component_unavailable": "Required validation components not available",
        "context_insufficient": "Insufficient context for reliable evaluation",
        "policy_violation": "Request violates governance policies",
        "system_overload": "Overwatch service overloaded with requests"
    },
    "grounding_sources": [
        "Industry governance frameworks and best practices",
        "Risk management methodologies and standards",
        "Regulatory compliance requirements",
        "Internal security and quality policies",
        "Statistical quality control methods"
    ],
    "redaction_points": [
        "Sensitive risk assessment details",
        "Internal governance decision logic",
        "User behavior analytics and history",
        "Proprietary validation algorithms"
    ],
    "observability": {
        "spans": ["request_evaluation", "risk_assessment", "decision_engine", "token_management"],
        "metrics": ["requests_evaluated", "approval_rate", "veto_rate", "average_evaluation_time"],
        "logs": ["evaluation_results", "policy_violations", "escalation_events", "token_limit_changes"]
    }
}
