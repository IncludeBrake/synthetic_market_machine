# SMVM Analysis Service
# Handles market analysis with WTP, elasticity, ROI, and decision matrix

"""
SMVM Analysis Service

Purpose: Perform advanced market analysis including willingness to pay, price elasticity,
ROI calculations, and decision matrix analysis for business decisions

Data Zone: AMBER (analysis results) → GREEN (decision insights)
Retention: 365 days for detailed analysis, indefinite for decision models
"""

from typing import Dict, List, Optional, Protocol
import logging
from datetime import datetime
from pathlib import Path

# Service metadata
SERVICE_NAME = "analysis"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"
DATA_ZONE = "AMBER"
RETENTION_DAYS = 365

logger = logging.getLogger(__name__)


class ElasticityAnalyzer(Protocol):
    """Protocol for price elasticity analysis"""

    def calculate_elasticity(self, price_data: List[Dict], demand_data: List[Dict]) -> Dict:
        """Calculate price elasticity of demand"""
        ...

    def analyze_sensitivity(self, parameters: Dict, scenarios: List[Dict]) -> Dict:
        """Analyze parameter sensitivity"""
        ...


class WTPAnalyzer(Protocol):
    """Protocol for willingness to pay analysis"""

    def estimate_wtp(self, survey_data: List[Dict], market_context: Dict) -> Dict:
        """Estimate willingness to pay from survey data"""
        ...

    def segment_wtp(self, customer_segments: List[Dict], product_attributes: Dict) -> Dict:
        """Segment willingness to pay by customer characteristics"""
        ...


class ROICalculator(Protocol):
    """Protocol for ROI analysis"""

    def calculate_roi(self, investment_data: Dict, revenue_projections: Dict) -> Dict:
        """Calculate return on investment"""
        ...

    def analyze_payback_period(self, cash_flows: List[Dict]) -> Dict:
        """Analyze investment payback period"""
        ...


class DecisionMatrixEngine:
    """
    Decision matrix analysis engine

    Provides structured decision-making framework:
    - Multi-criteria decision analysis
    - Weighted scoring algorithms
    - Sensitivity analysis
    - Recommendation generation
    """

    @staticmethod
    def create_decision_matrix(options: List[Dict], criteria: List[Dict], weights: Dict) -> Dict:
        """Create and analyze decision matrix"""
        matrix = {
            "options": options,
            "criteria": criteria,
            "weights": weights,
            "scores": {},
            "recommendations": {}
        }

        # Calculate weighted scores for each option
        for option in options:
            option_id = option.get("id", str(hash(str(option))))
            scores = {}

            for criterion in criteria:
                criterion_id = criterion.get("id", criterion.get("name", ""))
                option_value = option.get("criteria_values", {}).get(criterion_id, 0)
                weight = weights.get(criterion_id, 1.0)

                # Apply criterion-specific scoring logic
                if criterion.get("type") == "benefit":  # Higher values are better
                    score = option_value * weight
                elif criterion.get("type") == "cost":  # Lower values are better
                    max_value = criterion.get("max_value", option_value)
                    score = (1 - option_value/max_value) * weight if max_value > 0 else 0
                else:
                    score = option_value * weight

                scores[criterion_id] = score

            matrix["scores"][option_id] = {
                "criteria_scores": scores,
                "total_score": sum(scores.values()),
                "rank": 0  # Will be set after all calculations
            }

        # Rank options by total score
        sorted_scores = sorted(matrix["scores"].items(), key=lambda x: x[1]["total_score"], reverse=True)
        for rank, (option_id, _) in enumerate(sorted_scores, 1):
            matrix["scores"][option_id]["rank"] = rank

        # Generate recommendations
        top_score = sorted_scores[0][1]["total_score"]
        matrix["recommendations"] = {
            "top_choice": sorted_scores[0][0],
            "confidence_level": min(1.0, top_score / sum(weights.values())),
            "alternatives": [option_id for option_id, _ in sorted_scores[1:3]],
            "decision_criteria": [c.get("name", c.get("id", "")) for c in criteria]
        }

        return matrix

    @staticmethod
    def perform_sensitivity_analysis(matrix: Dict, sensitivity_range: float = 0.1) -> Dict:
        """Perform sensitivity analysis on decision matrix"""
        base_scores = matrix["scores"]
        sensitivity_results = {}

        weights = matrix["weights"]

        # Test weight variations
        for criterion_id, base_weight in weights.items():
            variations = []

            # Test weight reduction
            reduced_weight = base_weight * (1 - sensitivity_range)
            test_weights = weights.copy()
            test_weights[criterion_id] = reduced_weight

            # Recalculate scores with reduced weight
            reduced_scores = {}
            for option_id, option_data in base_scores.items():
                criteria_scores = option_data["criteria_scores"]
                new_total = sum(score * (test_weights[cid] / weights[cid] if cid == criterion_id else 1.0)
                              for cid, score in criteria_scores.items())
                reduced_scores[option_id] = new_total

            variations.append({
                "weight_change": -sensitivity_range,
                "scores": reduced_scores,
                "rank_changes": DecisionMatrixEngine._analyze_rank_changes(base_scores, reduced_scores)
            })

            sensitivity_results[criterion_id] = {
                "base_weight": base_weight,
                "variations": variations,
                "stability_score": DecisionMatrixEngine._calculate_stability_score(variations)
            }

        return sensitivity_results

    @staticmethod
    def _analyze_rank_changes(base_scores: Dict, new_scores: Dict) -> Dict:
        """Analyze ranking changes due to weight variations"""
        base_ranks = {oid: data["rank"] for oid, data in base_scores.items()}
        new_ranks = {}

        # Calculate new ranks
        sorted_new = sorted(new_scores.items(), key=lambda x: x[1], reverse=True)
        for rank, (option_id, _) in enumerate(sorted_new, 1):
            new_ranks[option_id] = rank

        # Analyze changes
        changes = {}
        for option_id in base_ranks:
            rank_change = new_ranks[option_id] - base_ranks[option_id]
            changes[option_id] = rank_change

        return changes

    @staticmethod
    def _calculate_stability_score(variations: List[Dict]) -> float:
        """Calculate decision stability score"""
        if not variations:
            return 1.0

        total_rank_changes = 0
        total_options = len(variations[0]["rank_changes"])

        for variation in variations:
            rank_changes = variation["rank_changes"]
            total_rank_changes += sum(abs(change) for change in rank_changes.values())

        # Normalize to 0-1 scale (lower changes = higher stability)
        max_possible_changes = len(variations) * total_options * 5  # Assume max rank change of 5
        stability = 1.0 - min(1.0, total_rank_changes / max_possible_changes)

        return stability


class AnalysisService:
    """
    Main analysis service providing comprehensive market analysis capabilities
    """

    def __init__(self, config: Dict):
        self.config = config
        self.elasticity_analyzer: Optional[ElasticityAnalyzer] = None
        self.wtp_analyzer: Optional[WTPAnalyzer] = None
        self.roi_calculator: Optional[ROICalculator] = None
        self.logger = logging.getLogger(f"{__name__}.AnalysisService")

    def register_analyzers(self,
                          elasticity_analyzer: ElasticityAnalyzer,
                          wtp_analyzer: WTPAnalyzer,
                          roi_calculator: ROICalculator) -> None:
        """Register analysis components"""
        self.elasticity_analyzer = elasticity_analyzer
        self.wtp_analyzer = wtp_analyzer
        self.roi_calculator = roi_calculator
        self.logger.info("Registered analysis components")

    def perform_comprehensive_analysis(self, analysis_request: Dict) -> Dict:
        """
        Perform comprehensive market analysis

        Args:
            analysis_request: Analysis parameters and data

        Returns:
            Dict containing all analysis results
        """
        analysis_type = analysis_request.get("analysis_type", "comprehensive")

        results = {
            "analysis_type": analysis_type,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "results": {},
            "metadata": {
                "service_version": SERVICE_VERSION,
                "python_version": PYTHON_VERSION
            }
        }

        # Perform elasticity analysis
        if analysis_type in ["comprehensive", "elasticity"] and self.elasticity_analyzer:
            price_data = analysis_request.get("price_data", [])
            demand_data = analysis_request.get("demand_data", [])
            results["results"]["elasticity"] = self.elasticity_analyzer.calculate_elasticity(price_data, demand_data)

        # Perform WTP analysis
        if analysis_type in ["comprehensive", "wtp"] and self.wtp_analyzer:
            survey_data = analysis_request.get("survey_data", [])
            market_context = analysis_request.get("market_context", {})
            results["results"]["wtp"] = self.wtp_analyzer.estimate_wtp(survey_data, market_context)

        # Perform ROI analysis
        if analysis_type in ["comprehensive", "roi"] and self.roi_calculator:
            investment_data = analysis_request.get("investment_data", {})
            revenue_projections = analysis_request.get("revenue_projections", {})
            results["results"]["roi"] = self.roi_calculator.calculate_roi(investment_data, revenue_projections)

        # Perform decision matrix analysis
        if "decision_options" in analysis_request:
            options = analysis_request["decision_options"]
            criteria = analysis_request.get("decision_criteria", [])
            weights = analysis_request.get("criteria_weights", {})

            decision_matrix = DecisionMatrixEngine.create_decision_matrix(options, criteria, weights)
            results["results"]["decision_matrix"] = decision_matrix

            # Add sensitivity analysis if requested
            if analysis_request.get("include_sensitivity", False):
                sensitivity = DecisionMatrixEngine.perform_sensitivity_analysis(decision_matrix)
                results["results"]["sensitivity_analysis"] = sensitivity

        self.logger.info(f"Completed {analysis_type} analysis")
        return results

    def analyze_market_opportunity(self, market_data: Dict) -> Dict:
        """Analyze market opportunity with WTP and elasticity insights"""
        opportunity_analysis = {
            "market_size": market_data.get("market_size", 0),
            "growth_rate": market_data.get("growth_rate", 0),
            "competition_level": market_data.get("competition_level", "medium"),
            "insights": {}
        }

        # Calculate opportunity score
        market_size_score = min(1.0, market_data.get("market_size", 0) / 1000000000)  # Normalize to $1B
        growth_score = min(1.0, max(0, market_data.get("growth_rate", 0)) / 0.20)  # Normalize to 20% growth
        competition_modifier = {"low": 1.0, "medium": 0.7, "high": 0.4}.get(
            market_data.get("competition_level", "medium"), 0.7)

        opportunity_analysis["opportunity_score"] = (market_size_score + growth_score) * competition_modifier

        return opportunity_analysis


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Advanced market analysis with WTP, elasticity, ROI, and decision matrix",
    "endpoints": {
        "comprehensive_analysis": {
            "method": "POST",
            "path": "/api/v1/analysis/comprehensive",
            "input": {
                "analysis_type": "string (comprehensive/elasticity/wtp/roi)",
                "market_data": "object (market analysis data)",
                "decision_options": "array (optional decision options)"
            },
            "output": {
                "results": "object (analysis results by type)",
                "metadata": "object (analysis metadata)"
            },
            "token_budget": 2000,
            "timeout_seconds": 600
        },
        "elasticity_analysis": {
            "method": "POST",
            "path": "/api/v1/analysis/elasticity",
            "input": {
                "price_data": "array (price points)",
                "demand_data": "array (demand observations)"
            },
            "output": {
                "elasticity_coefficient": "number",
                "confidence_interval": "object",
                "sensitivity_analysis": "object"
            },
            "token_budget": 800,
            "timeout_seconds": 180
        },
        "decision_matrix": {
            "method": "POST",
            "path": "/api/v1/analysis/decision-matrix",
            "input": {
                "options": "array (decision options)",
                "criteria": "array (evaluation criteria)",
                "weights": "object (criteria weights)"
            },
            "output": {
                "matrix": "object (decision matrix)",
                "recommendations": "object (decision recommendations)",
                "sensitivity_analysis": "object (optional)"
            },
            "token_budget": 600,
            "timeout_seconds": 120
        }
    },
    "failure_modes": {
        "insufficient_data": "Not enough data points for reliable analysis",
        "statistical_insignificance": "Analysis results lack statistical significance",
        "model_convergence_failure": "Mathematical models fail to converge",
        "data_quality_issues": "Input data quality below acceptable thresholds",
        "parameter_out_of_bounds": "Analysis parameters outside valid ranges"
    },
    "grounding_sources": [
        "Econometric theory and statistical methods",
        "Consumer behavior research and surveys",
        "Financial modeling and valuation frameworks",
        "Decision theory and multi-criteria analysis",
        "Industry benchmarking and market research"
    ],
    "redaction_points": [
        "Proprietary pricing models and elasticity calculations",
        "Sensitive customer survey responses",
        "Confidential financial projections",
        "Internal decision-making algorithms"
    ],
    "observability": {
        "spans": ["data_preprocessing", "model_execution", "result_validation", "recommendation_generation"],
        "metrics": ["analyses_completed", "model_accuracy", "computation_time", "error_rate"],
        "logs": ["analysis_parameters", "model_convergence", "result_quality", "performance_metrics"]
    }
}
