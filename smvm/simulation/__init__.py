# SMVM Simulation Service
# Handles market simulation scenarios with seed management and realism bounds

"""
SMVM Simulation Service

Purpose: Execute market simulation scenarios with controlled randomness and realistic constraints
- Scenario definition and execution
- Random seed management for reproducibility
- Realism bounds policy enforcement
- Performance monitoring and validation

Data Zone: AMBER (simulation results) → GREEN (aggregated insights)
Retention: 365 days for detailed results, indefinite for scenario templates
"""

from typing import Dict, List, Optional, Protocol
import logging
from datetime import datetime
from pathlib import Path
import random
import hashlib

# Service metadata
SERVICE_NAME = "simulation"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"  # Must match SMVM requirements
DATA_ZONE = "AMBER"  # Simulation results data
RETENTION_DAYS = 365

logger = logging.getLogger(__name__)


class ScenarioExecutor(Protocol):
    """Protocol for scenario execution engines"""

    def execute_scenario(self, scenario_config: Dict, seed: int) -> Dict:
        """Execute a simulation scenario"""
        ...

    def validate_scenario(self, scenario_config: Dict) -> bool:
        """Validate scenario configuration"""
        ...

    def estimate_runtime(self, scenario_config: Dict) -> int:
        """Estimate scenario execution time in seconds"""
        ...


class RealismBoundsPolicy:
    """
    Realism bounds policy for simulation constraints

    Ensures simulation results remain within:
    - Economic reality bounds
    - Market behavior expectations
    - Statistical plausibility limits
    - Business logic constraints
    """

    # Economic realism bounds
    ECONOMIC_BOUNDS = {
        "interest_rate": {"min": -0.01, "max": 0.25, "description": "Annual interest rate bounds"},
        "inflation_rate": {"min": -0.05, "max": 0.15, "description": "Annual inflation rate bounds"},
        "unemployment_rate": {"min": 0.01, "max": 0.25, "description": "Unemployment rate bounds"},
        "gdp_growth": {"min": -0.10, "max": 0.15, "description": "GDP growth rate bounds"}
    }

    # Market behavior bounds
    MARKET_BOUNDS = {
        "volatility": {"min": 0.05, "max": 0.80, "description": "Market volatility bounds"},
        "correlation": {"min": -1.0, "max": 1.0, "description": "Asset correlation bounds"},
        "liquidity": {"min": 0.1, "max": 1.0, "description": "Market liquidity bounds"},
        "participation_rate": {"min": 0.1, "max": 0.95, "description": "Market participation bounds"}
    }

    # Statistical plausibility bounds
    STATISTICAL_BOUNDS = {
        "confidence_interval": {"min": 0.80, "max": 0.99, "description": "Confidence interval bounds"},
        "p_value_threshold": {"min": 0.001, "max": 0.10, "description": "Statistical significance threshold"},
        "sample_size": {"min": 30, "max": 100000, "description": "Minimum sample size for validity"},
        "effect_size": {"min": 0.01, "max": 2.0, "description": "Minimum detectable effect size"}
    }

    @staticmethod
    def validate_scenario_realism(scenario_config: Dict) -> Dict:
        """Validate scenario configuration against realism bounds"""
        violations = []

        # Check economic parameters
        economic_params = scenario_config.get("market_conditions", {})
        for param, bounds in RealismBoundsPolicy.ECONOMIC_BOUNDS.items():
            if param in economic_params:
                value = economic_params[param]
                if not (bounds["min"] <= value <= bounds["max"]):
                    violations.append({
                        "parameter": param,
                        "value": value,
                        "bounds": bounds,
                        "violation": "out_of_bounds"
                    })

        # Check market parameters
        market_params = scenario_config.get("market_conditions", {}).get("market_volatility", {})
        for param, bounds in RealismBoundsPolicy.MARKET_BOUNDS.items():
            if param in market_params:
                value = market_params[param]
                if not (bounds["min"] <= value <= bounds["max"]):
                    violations.append({
                        "parameter": param,
                        "value": value,
                        "bounds": bounds,
                        "violation": "out_of_bounds"
                    })

        # Check statistical parameters
        validation_params = scenario_config.get("validation_parameters", {})
        for param, bounds in RealismBoundsPolicy.STATISTICAL_BOUNDS.items():
            if param in validation_params:
                value = validation_params[param]
                if not (bounds["min"] <= value <= bounds["max"]):
                    violations.append({
                        "parameter": param,
                        "value": value,
                        "bounds": bounds,
                        "violation": "out_of_bounds"
                    })

        return {
            "is_realistic": len(violations) == 0,
            "violations": violations,
            "recommendations": RealismBoundsPolicy._generate_recommendations(violations)
        }

    @staticmethod
    def _generate_recommendations(violations: List[Dict]) -> List[str]:
        """Generate recommendations for fixing realism violations"""
        recommendations = []

        for violation in violations:
            param = violation["parameter"]
            bounds = violation["bounds"]

            if param in ["interest_rate", "inflation_rate"]:
                recommendations.append(f"Adjust {param} to be within {bounds['min']*100:.1f}% to {bounds['max']*100:.1f}% range")
            elif param == "volatility":
                recommendations.append(f"Set {param} between {bounds['min']:.2f} and {bounds['max']:.2f} for market realism")
            elif param == "confidence_level":
                recommendations.append(f"Use {param} between {bounds['min']:.2f} and {bounds['max']:.2f} for statistical validity")

        return recommendations

    @staticmethod
    def apply_realism_constraints(scenario_config: Dict) -> Dict:
        """Apply automatic realism constraints to scenario configuration"""
        constrained = scenario_config.copy()

        # Apply economic constraints
        economic = constrained.setdefault("market_conditions", {})
        for param, bounds in RealismBoundsPolicy.ECONOMIC_BOUNDS.items():
            if param in economic:
                value = economic[param]
                economic[param] = max(bounds["min"], min(bounds["max"], value))

        # Apply market constraints
        market_vol = economic.setdefault("market_volatility", {})
        for param, bounds in RealismBoundsPolicy.MARKET_BOUNDS.items():
            if param in market_vol:
                value = market_vol[param]
                market_vol[param] = max(bounds["min"], min(bounds["max"], value))

        return constrained


class SeedManagementSystem:
    """
    Random seed management for reproducible simulations

    Ensures:
    - Seed uniqueness across runs
    - Seed traceability and auditability
    - Seed collision detection
    - Seed quality validation
    """

    def __init__(self):
        self.used_seeds = set()
        self.seed_history = []

    def generate_seed(self, run_id: str, scenario_name: str) -> int:
        """Generate a unique, deterministic seed for a simulation run"""
        # Create deterministic seed from run context
        seed_input = f"{run_id}:{scenario_name}:{datetime.utcnow().isoformat()}"
        seed_hash = hashlib.sha256(seed_input.encode()).hexdigest()

        # Convert first 8 characters of hash to integer
        seed = int(seed_hash[:8], 16)

        # Ensure uniqueness
        original_seed = seed
        while seed in self.used_seeds:
            seed = (seed + 1) % (2**32)  # Increment and wrap around

        if seed != original_seed:
            logger.warning(f"Seed collision detected, using alternative seed: {seed}")

        self.used_seeds.add(seed)
        self.seed_history.append({
            "seed": seed,
            "run_id": run_id,
            "scenario_name": scenario_name,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        })

        return seed

    def validate_seed(self, seed: int) -> bool:
        """Validate seed quality and uniqueness"""
        # Check range
        if not (0 <= seed <= 2**32 - 1):
            return False

        # Check for obvious patterns (all same digits, sequential, etc.)
        seed_str = str(seed)

        # Check for repeated digits
        if len(set(seed_str)) <= 2:  # Only 1-2 unique digits
            return False

        # Check for sequential patterns
        if seed_str in ['12345678', '87654321', '13579246', '24680135']:
            return False

        return True

    def get_seed_history(self, run_id: Optional[str] = None) -> List[Dict]:
        """Get seed generation history"""
        if run_id:
            return [entry for entry in self.seed_history if entry["run_id"] == run_id]
        return self.seed_history.copy()


class SimulationService:
    """
    Main simulation service

    Provides:
    - Scenario execution with seed management
    - Realism bounds enforcement
    - Performance monitoring
    - Result validation and quality assessment
    """

    def __init__(self, config: Dict):
        self.config = config
        self.scenario_executor: Optional[ScenarioExecutor] = None
        self.seed_manager = SeedManagementSystem()
        self.logger = logging.getLogger(f"{__name__}.SimulationService")

    def register_scenario_executor(self, executor: ScenarioExecutor) -> None:
        """Register scenario execution component"""
        self.scenario_executor = executor
        self.logger.info("Registered scenario executor")

    def execute_simulation(self, scenario_config: Dict, run_context: Dict) -> Dict:
        """
        Execute a market simulation scenario

        Args:
            scenario_config: Scenario configuration parameters
            run_context: Run context information

        Returns:
            Dict containing simulation results and metadata
        """
        if not self.scenario_executor:
            raise ValueError("Scenario executor not registered")

        run_id = run_context.get("run_id", "unknown")
        scenario_name = scenario_config.get("simulation_parameters", {}).get("scenario", "default")

        # Validate scenario realism
        realism_check = RealismBoundsPolicy.validate_scenario_realism(scenario_config)
        if not realism_check["is_realistic"]:
            self.logger.warning(f"Scenario realism violations: {realism_check['violations']}")
            if self.config.get("enforce_realism", True):
                # Apply automatic constraints
                scenario_config = RealismBoundsPolicy.apply_realism_constraints(scenario_config)
                self.logger.info("Applied automatic realism constraints")

        # Generate or validate seed
        provided_seed = scenario_config.get("simulation_parameters", {}).get("random_seed")
        if provided_seed:
            if not self.seed_manager.validate_seed(provided_seed):
                raise ValueError(f"Invalid or poor quality seed: {provided_seed}")
            seed = provided_seed
        else:
            seed = self.seed_manager.generate_seed(run_id, scenario_name)

        # Execute scenario
        start_time = datetime.utcnow()
        try:
            results = self.scenario_executor.execute_scenario(scenario_config, seed)
            execution_status = "success"
        except Exception as e:
            self.logger.error(f"Scenario execution failed: {e}")
            results = {"error": str(e), "partial_results": {}}
            execution_status = "failed"

        end_time = datetime.utcnow()
        execution_time = (end_time - start_time).total_seconds()

        # Validate results
        result_quality = self._assess_result_quality(results, scenario_config)

        # Create comprehensive result
        simulation_result = {
            "simulation_results": results,
            "execution_metadata": {
                "run_id": run_id,
                "scenario_name": scenario_name,
                "random_seed": seed,
                "execution_status": execution_status,
                "execution_time_seconds": execution_time,
                "start_time": start_time.isoformat() + "Z",
                "end_time": end_time.isoformat() + "Z"
            },
            "quality_assessment": result_quality,
            "realism_validation": realism_check,
            "service_metadata": {
                "service_version": SERVICE_VERSION,
                "python_version": PYTHON_VERSION,
                "executor_info": str(type(self.scenario_executor).__name__) if self.scenario_executor else "none"
            }
        }

        self.logger.info(f"Simulation completed in {execution_time:.2f}s with status: {execution_status}")
        return simulation_result

    def validate_scenario_config(self, scenario_config: Dict) -> Dict:
        """Validate scenario configuration before execution"""
        validation_result = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "recommendations": []
        }

        # Check required fields
        required_fields = ["simulation_parameters", "market_conditions", "time_parameters"]
        for field in required_fields:
            if field not in scenario_config:
                validation_result["errors"].append(f"Missing required field: {field}")
                validation_result["is_valid"] = False

        # Validate simulation parameters
        sim_params = scenario_config.get("simulation_parameters", {})
        if "iterations" in sim_params:
            iterations = sim_params["iterations"]
            if not (100 <= iterations <= 100000):
                validation_result["warnings"].append(f"Iterations {iterations} outside recommended range 100-100000")

        # Check realism bounds
        realism_check = RealismBoundsPolicy.validate_scenario_realism(scenario_config)
        if not realism_check["is_realistic"]:
            validation_result["warnings"].extend([f"Realism violation: {v['parameter']}" for v in realism_check["violations"]])
            validation_result["recommendations"].extend(realism_check["recommendations"])

        return validation_result

    def _assess_result_quality(self, results: Dict, scenario_config: Dict) -> Dict:
        """Assess quality of simulation results"""
        quality_metrics = {
            "completeness": 0.0,
            "consistency": 0.0,
            "statistical_validity": 0.0,
            "business_logic_compliance": 0.0
        }

        # Check result completeness
        expected_keys = ["performance_metrics", "market_outcomes", "execution_metadata"]
        quality_metrics["completeness"] = sum(1 for key in expected_keys if key in results) / len(expected_keys)

        # Check statistical validity
        perf_metrics = results.get("performance_metrics", {})
        if "returns" in perf_metrics and "risk_measures" in perf_metrics:
            quality_metrics["statistical_validity"] = 0.8
        elif "returns" in perf_metrics or "risk_measures" in perf_metrics:
            quality_metrics["statistical_validity"] = 0.5

        # Check consistency with scenario config
        sim_params = scenario_config.get("simulation_parameters", {})
        if "scenario" in sim_params:
            quality_metrics["consistency"] = 0.9

        # Business logic compliance (simplified check)
        market_outcomes = results.get("market_outcomes", {})
        if "market_states" in market_outcomes:
            quality_metrics["business_logic_compliance"] = 0.8

        # Overall quality score
        quality_metrics["overall_quality"] = sum(quality_metrics.values()) / len(quality_metrics)

        return quality_metrics


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Market simulation execution with seed management and realism bounds",
    "endpoints": {
        "execute_simulation": {
            "method": "POST",
            "path": "/api/v1/simulation/execute",
            "input": {
                "scenario_config": "object (simulation scenario configuration)",
                "run_context": "object (run metadata and context)"
            },
            "output": {
                "simulation_results": "object (simulation outputs)",
                "execution_metadata": "object (execution details)",
                "quality_assessment": "object (result quality metrics)"
            },
            "token_budget": 3000,
            "timeout_seconds": 1800
        },
        "validate_scenario": {
            "method": "POST",
            "path": "/api/v1/simulation/validate",
            "input": {
                "scenario_config": "object (scenario configuration)"
            },
            "output": {
                "is_valid": "boolean",
                "warnings": "array (validation warnings)",
                "errors": "array (validation errors)",
                "recommendations": "array (improvement suggestions)"
            },
            "token_budget": 500,
            "timeout_seconds": 60
        },
        "generate_seed": {
            "method": "POST",
            "path": "/api/v1/simulation/generate-seed",
            "input": {
                "run_id": "string",
                "scenario_name": "string"
            },
            "output": {
                "seed": "integer (random seed)",
                "quality_score": "number (seed quality metric)"
            },
            "token_budget": 200,
            "timeout_seconds": 10
        }
    },
    "failure_modes": {
        "realism_bounds_exceeded": "Scenario parameters exceed realism constraints",
        "seed_generation_failed": "Unable to generate valid random seed",
        "execution_timeout": "Simulation exceeds maximum execution time",
        "numerical_instability": "Simulation becomes numerically unstable",
        "memory_exhaustion": "Simulation exceeds memory limits",
        "convergence_failure": "Simulation fails to converge within iteration limit"
    },
    "grounding_sources": [
        "Historical market data and statistical models",
        "Economic theory and market microstructure research",
        "Industry-standard simulation methodologies",
        "Regulatory stress testing frameworks",
        "Academic research in financial modeling"
    ],
    "redaction_points": [
        "Random seeds in logs (may compromise reproducibility)",
        "Proprietary model parameters",
        "Sensitive market simulation inputs",
        "Internal validation thresholds and bounds"
    ],
    "observability": {
        "spans": ["scenario_validation", "seed_generation", "simulation_execution", "result_validation"],
        "metrics": ["simulations_executed", "execution_time_avg", "success_rate", "quality_score_avg"],
        "logs": ["scenario_configuration", "execution_progress", "error_conditions", "performance_metrics"]
    }
}
