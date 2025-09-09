# SMVM Personas Service
# Handles synthetic persona generation and bias mitigation

"""
SMVM Personas Service

Purpose: Generate synthetic market personas with controlled bias and demographic balance
- Statistical persona synthesis from market data
- Bias detection and mitigation algorithms
- Demographic balancing and diversity controls
- Persona validation against real-world distributions

Data Zone: AMBER (internal analysis) → GREEN (aggregated insights)
Retention: 365 days for individual personas, indefinite for synthesis models
"""

from typing import Dict, List, Optional, Tuple, Protocol
import logging
from datetime import datetime
from pathlib import Path
import random
import hashlib

# Service metadata
SERVICE_NAME = "personas"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"  # Must match SMVM requirements
DATA_ZONE = "AMBER"  # Internal analysis data
RETENTION_DAYS = 365

logger = logging.getLogger(__name__)


class BiasDetector(Protocol):
    """Protocol for bias detection algorithms"""

    def detect_bias(self, personas: List[Dict]) -> Dict[str, float]:
        """Detect bias patterns in persona set"""
        ...

    def calculate_diversity_score(self, personas: List[Dict]) -> float:
        """Calculate diversity score (0.0-1.0)"""
        ...

    def suggest_corrections(self, bias_metrics: Dict[str, float]) -> List[Dict]:
        """Suggest bias correction adjustments"""
        ...


class PersonaGenerator(Protocol):
    """Protocol for persona generation algorithms"""

    def generate_persona(self, constraints: Dict) -> Dict:
        """Generate a single synthetic persona"""
        ...

    def validate_persona(self, persona: Dict) -> bool:
        """Validate persona against business rules"""
        ...

    def estimate_confidence(self, persona: Dict) -> float:
        """Estimate confidence in persona realism (0.0-1.0)"""
        ...


class BiasControlPolicy:
    """
    Bias control and mitigation policy

    Ensures synthetic personas represent target populations without:
    - Demographic skewing
    - Economic bias
    - Behavioral distortion
    - Geographic misrepresentation
    """

    # Demographic balance targets (based on general population statistics)
    DEMOGRAPHIC_TARGETS = {
        "gender": {"male": 0.49, "female": 0.49, "non_binary": 0.02},
        "age_groups": {
            "18-24": 0.12, "25-34": 0.18, "35-44": 0.17,
            "45-54": 0.16, "55-64": 0.14, "65+": 0.23
        },
        "education_levels": {
            "high_school": 0.25, "associate": 0.10, "bachelor": 0.30,
            "master": 0.20, "doctorate": 0.05, "other": 0.10
        },
        "income_distribution": {
            "low": 0.20, "middle": 0.50, "high": 0.30
        }
    }

    @staticmethod
    def assess_bias(personas: List[Dict]) -> Dict[str, float]:
        """Assess bias across multiple dimensions"""
        if not personas:
            return {"overall_bias": 1.0}

        bias_scores = {}

        # Gender bias
        gender_counts = {}
        for persona in personas:
            gender = persona.get("demographics", {}).get("gender", "unknown")
            gender_counts[gender] = gender_counts.get(gender, 0) + 1

        total = len(personas)
        for gender, target_pct in BiasControlPolicy.DEMOGRAPHIC_TARGETS["gender"].items():
            actual_pct = gender_counts.get(gender, 0) / total
            bias_scores[f"gender_{gender}"] = abs(actual_pct - target_pct)

        # Age group bias
        age_counts = {}
        for persona in personas:
            age = persona.get("demographics", {}).get("age", 0)
            if 18 <= age <= 24:
                age_group = "18-24"
            elif 25 <= age <= 34:
                age_group = "25-34"
            elif 35 <= age <= 44:
                age_group = "35-44"
            elif 45 <= age <= 54:
                age_group = "45-54"
            elif 55 <= age <= 64:
                age_group = "55-64"
            else:
                age_group = "65+"
            age_counts[age_group] = age_counts.get(age_group, 0) + 1

        for age_group, target_pct in BiasControlPolicy.DEMOGRAPHIC_TARGETS["age_groups"].items():
            actual_pct = age_counts.get(age_group, 0) / total
            bias_scores[f"age_{age_group}"] = abs(actual_pct - target_pct)

        # Overall bias score (0.0 = no bias, 1.0 = maximum bias)
        bias_scores["overall_bias"] = sum(bias_scores.values()) / len(bias_scores)

        return bias_scores

    @staticmethod
    def generate_correction_factors(bias_scores: Dict[str, float]) -> Dict[str, float]:
        """Generate correction factors to reduce bias"""
        corrections = {}

        for bias_type, score in bias_scores.items():
            if bias_type.startswith("gender_"):
                gender = bias_type.split("_")[1]
                corrections[f"gender_{gender}"] = 1.0 + (score * 0.5)  # Boost underrepresented
            elif bias_type.startswith("age_"):
                age_group = "_".join(bias_type.split("_")[1:])
                corrections[f"age_{age_group}"] = 1.0 + (score * 0.3)

        return corrections


class PersonaSynthesisService:
    """
    Main persona synthesis service

    Generates synthetic market personas with:
    - Demographic balance
    - Behavioral realism
    - Economic coherence
    - Bias mitigation
    """

    def __init__(self, config: Dict):
        self.config = config
        self.bias_detector: Optional[BiasDetector] = None
        self.persona_generator: Optional[PersonaGenerator] = None
        self.logger = logging.getLogger(f"{__name__}.PersonaSynthesisService")

    def register_components(self,
                          bias_detector: BiasDetector,
                          persona_generator: PersonaGenerator) -> None:
        """Register bias detector and persona generator components"""
        self.bias_detector = bias_detector
        self.persona_generator = persona_generator
        self.logger.info("Registered persona synthesis components")

    def synthesize_personas(self,
                          target_count: int,
                          constraints: Dict,
                          seed: Optional[int] = None) -> Dict:
        """
        Synthesize a set of personas with bias control

        Args:
            target_count: Number of personas to generate
            constraints: Generation constraints and parameters
            seed: Random seed for reproducibility

        Returns:
            Dict containing personas and synthesis metadata
        """
        if not self.persona_generator or not self.bias_detector:
            raise ValueError("Synthesis components not registered")

        # Set random seed for reproducibility
        if seed is not None:
            random.seed(seed)

        personas = []
        max_iterations = target_count * 3  # Allow retries for bias correction
        iteration = 0

        while len(personas) < target_count and iteration < max_iterations:
            # Generate candidate persona
            candidate = self.persona_generator.generate_persona(constraints)

            # Validate persona
            if self.persona_generator.validate_persona(candidate):
                personas.append(candidate)

            iteration += 1

        # Apply bias correction if needed
        if len(personas) >= 10:  # Only check bias for meaningful sample
            bias_scores = BiasControlPolicy.assess_bias(personas)

            if bias_scores.get("overall_bias", 0) > 0.1:  # Significant bias detected
                self.logger.warning(f"Bias detected: {bias_scores}")
                corrections = BiasControlPolicy.generate_correction_factors(bias_scores)

                # Apply corrections (simplified implementation)
                corrected_personas = self._apply_bias_corrections(personas, corrections)
                personas = corrected_personas

        # Calculate final quality metrics
        quality_metrics = self._calculate_quality_metrics(personas)

        # Create result
        result = {
            "personas": personas,
            "metadata": {
                "synthesis_timestamp": datetime.utcnow().isoformat() + "Z",
                "target_count": target_count,
                "actual_count": len(personas),
                "random_seed": seed,
                "service_version": SERVICE_VERSION,
                "python_version": PYTHON_VERSION,
                "quality_metrics": quality_metrics,
                "bias_assessment": BiasControlPolicy.assess_bias(personas) if len(personas) >= 10 else {},
                "diversity_score": self.bias_detector.calculate_diversity_score(personas) if self.bias_detector else 0.0
            }
        }

        self.logger.info(f"Successfully synthesized {len(personas)} personas")
        return result

    def _apply_bias_corrections(self, personas: List[Dict], corrections: Dict[str, float]) -> List[Dict]:
        """Apply bias corrections to persona set"""
        # Simplified bias correction - in practice, this would be more sophisticated
        corrected = personas.copy()

        # Add correction metadata
        for persona in corrected:
            persona["_bias_corrections"] = corrections

        return corrected

    def _calculate_quality_metrics(self, personas: List[Dict]) -> Dict:
        """Calculate quality metrics for synthesized personas"""
        if not personas:
            return {"completeness": 0.0, "consistency": 0.0, "realism": 0.0}

        metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "realism": 0.0
        }

        total_personas = len(personas)

        for persona in personas:
            # Completeness check
            required_fields = ["persona_id", "demographics", "behavioral_attributes", "economic_profile"]
            completeness = sum(1 for field in required_fields if field in persona) / len(required_fields)
            metrics["completeness"] += completeness

            # Consistency check (simplified)
            demographics = persona.get("demographics", {})
            if demographics:
                metrics["consistency"] += 0.5  # Basic demographic consistency

            # Realism check (simplified)
            if self.persona_generator:
                confidence = self.persona_generator.estimate_confidence(persona)
                metrics["realism"] += confidence

        # Average the metrics
        for key in metrics:
            metrics[key] /= total_personas

        return metrics


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Synthetic persona generation with bias control and demographic balancing",
    "endpoints": {
        "synthesize": {
            "method": "POST",
            "path": "/api/v1/personas/synthesize",
            "input": {
                "target_count": "integer (1-10000)",
                "constraints": "object (generation parameters)",
                "seed": "integer (optional random seed)"
            },
            "output": {
                "personas": "array (synthetic personas)",
                "metadata": "object (synthesis metadata and quality metrics)"
            },
            "token_budget": 2000,
            "timeout_seconds": 600
        },
        "assess_bias": {
            "method": "POST",
            "path": "/api/v1/personas/assess-bias",
            "input": {
                "personas": "array (persona data)"
            },
            "output": {
                "bias_scores": "object (bias metrics)",
                "diversity_score": "number (0.0-1.0)",
                "recommendations": "array (bias mitigation suggestions)"
            },
            "token_budget": 500,
            "timeout_seconds": 120
        },
        "validate_persona": {
            "method": "POST",
            "path": "/api/v1/personas/validate",
            "input": {
                "persona": "object (persona data)"
            },
            "output": {
                "valid": "boolean",
                "errors": "array (validation issues)",
                "confidence_score": "number (0.0-1.0)"
            },
            "token_budget": 300,
            "timeout_seconds": 30
        }
    },
    "failure_modes": {
        "insufficient_data": "Not enough source data for synthesis",
        "bias_uncorrectable": "Bias cannot be mitigated within constraints",
        "validation_failed": "Generated personas fail quality validation",
        "diversity_threshold_not_met": "Diversity score below minimum threshold",
        "generation_timeout": "Persona generation exceeds time limits"
    },
    "grounding_sources": [
        "Census data and demographic statistics",
        "Economic surveys and market research",
        "Behavioral psychology research",
        "Industry diversity benchmarks",
        "Statistical distribution models"
    ],
    "redaction_points": [
        "Individual persona identifiers in logs",
        "Sensitive demographic data in error messages",
        "Economic profile details in debug output",
        "Behavioral attribute correlations in metrics"
    ],
    "observability": {
        "spans": ["persona_generation", "bias_assessment", "quality_validation", "diversity_calculation"],
        "metrics": ["personas_generated", "bias_score_avg", "diversity_score", "quality_score_avg"],
        "logs": ["synthesis_progress", "bias_detection", "correction_applied", "validation_results"]
    }
}
