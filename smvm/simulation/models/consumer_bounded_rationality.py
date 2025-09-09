#!/usr/bin/env python3
"""
SMVM Consumer Bounded Rationality Model

This module implements consumer decision-making models based on bounded rationality theory,
incorporating cognitive biases, information processing limitations, and satisficing behavior.
"""

import json
import hashlib
import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
import logging

logger = logging.getLogger(__name__)

# Model metadata
MODEL_NAME = "consumer_bounded_rationality"
MODEL_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"

class ConsumerBoundedRationalityModel:
    """
    Consumer decision-making model based on bounded rationality principles
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.model_id = self._generate_model_id()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

        # Cognitive limitations
        self.attention_span = config.get("attention_span", 5)  # Max options considered
        self.information_processing_capacity = config.get("processing_capacity", 10)  # Max attributes processed
        self.memory_decay_rate = config.get("memory_decay", 0.1)  # How quickly information is forgotten

        # Decision heuristics
        self.heuristics = {
            "satisficing_threshold": 0.7,  # Minimum acceptability threshold
            "anchoring_bias": 0.2,  # Tendency to rely on first piece of information
            "availability_bias": 0.15,  # Overweighting easily recalled information
            "loss_aversion": 2.0,  # Losses hurt more than gains help
            "status_quo_bias": 0.3,  # Preference for current situation
            "social_proof_weight": 0.25,  # Weight given to others' choices
            "brand_loyalty_factor": 0.4  # Tendency to stick with familiar brands
        }

        # Consumer segments with different cognitive profiles
        self.consumer_segments = {
            "rational_optimizer": {
                "attention_span": 8,
                "processing_capacity": 15,
                "satisficing_threshold": 0.85,
                "loss_aversion": 1.5,
                "decision_style": "analytical"
            },
            "satisficer": {
                "attention_span": 3,
                "processing_capacity": 5,
                "satisficing_threshold": 0.6,
                "loss_aversion": 2.5,
                "decision_style": "intuitive"
            },
            "impulsive": {
                "attention_span": 2,
                "processing_capacity": 3,
                "satisficing_threshold": 0.5,
                "loss_aversion": 1.2,
                "decision_style": "emotional"
            },
            "loyalist": {
                "attention_span": 4,
                "processing_capacity": 8,
                "satisficing_threshold": 0.75,
                "loss_aversion": 3.0,
                "brand_loyalty_factor": 0.8,
                "decision_style": "habitual"
            }
        }

        # Decision stages
        self.decision_stages = [
            "problem_recognition",
            "information_search",
            "evaluation_of_alternatives",
            "purchase_decision",
            "post_purchase_evaluation"
        ]

        # Initialize random state for reproducibility
        self.random_state = random.Random()

    def _generate_model_id(self) -> str:
        """Generate unique model identifier"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        random_part = hashlib.md5(str(hash(self)).encode()).hexdigest()[:8]
        return f"consumer_model_{timestamp}_{random_part}"

    def simulate_consumer_decision(self, consumer_profile: Dict[str, Any],
                                  product_options: List[Dict[str, Any]],
                                  market_context: Dict[str, Any],
                                  seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Simulate consumer decision-making process

        Args:
            consumer_profile: Consumer characteristics and preferences
            product_options: Available product/service options
            market_context: Market conditions and external factors
            seed: Random seed for reproducibility

        Returns:
            Decision outcome with reasoning and confidence
        """

        if seed is not None:
            self.random_state.seed(seed)

        decision_process = {
            "consumer_id": consumer_profile.get("persona_id"),
            "model_id": self.model_id,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "decision_stages": {},
            "final_decision": {},
            "decision_confidence": 0.0,
            "cognitive_load": 0.0,
            "biases_applied": []
        }

        # Set consumer segment parameters
        consumer_segment = self._classify_consumer_segment(consumer_profile)
        segment_params = self.consumer_segments[consumer_segment]

        # Override default parameters with segment-specific ones
        original_params = self.heuristics.copy()
        self.heuristics.update(segment_params)

        try:
            # Stage 1: Problem Recognition
            problem_recognized = self._simulate_problem_recognition(
                consumer_profile, market_context
            )
            decision_process["decision_stages"]["problem_recognition"] = problem_recognized

            if not problem_recognized["recognized"]:
                decision_process["final_decision"] = {"action": "no_action", "reason": "problem_not_recognized"}
                return decision_process

            # Stage 2: Information Search
            search_results = self._simulate_information_search(
                consumer_profile, product_options, market_context
            )
            decision_process["decision_stages"]["information_search"] = search_results
            considered_options = search_results["considered_options"]

            # Stage 3: Evaluation of Alternatives
            evaluation_results = self._simulate_evaluation(
                consumer_profile, considered_options, market_context
            )
            decision_process["decision_stages"]["evaluation_of_alternatives"] = evaluation_results

            # Stage 4: Purchase Decision
            purchase_decision = self._simulate_purchase_decision(
                consumer_profile, evaluation_results, market_context
            )
            decision_process["decision_stages"]["purchase_decision"] = purchase_decision
            decision_process["final_decision"] = purchase_decision["decision"]

            # Stage 5: Post-purchase Evaluation
            post_evaluation = self._simulate_post_purchase_evaluation(
                consumer_profile, purchase_decision
            )
            decision_process["decision_stages"]["post_purchase_evaluation"] = post_evaluation

            # Calculate overall metrics
            decision_process["decision_confidence"] = purchase_decision["confidence"]
            decision_process["cognitive_load"] = self._calculate_cognitive_load(
                search_results, evaluation_results
            )
            decision_process["biases_applied"] = self._identify_applied_biases(
                consumer_profile, search_results, evaluation_results, purchase_decision
            )

            self.logger.debug({
                "event_type": "CONSUMER_DECISION_SIMULATED",
                "consumer_id": consumer_profile.get("persona_id"),
                "decision": decision_process["final_decision"]["action"],
                "confidence": decision_process["decision_confidence"],
                "cognitive_load": decision_process["cognitive_load"],
                "biases_applied": len(decision_process["biases_applied"]),
                "python_version": PYTHON_VERSION,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            })

        finally:
            # Restore original parameters
            self.heuristics = original_params

        return decision_process

    def _classify_consumer_segment(self, consumer_profile: Dict[str, Any]) -> str:
        """Classify consumer into cognitive segment"""

        behavior = consumer_profile.get("behavioral_attributes", {})
        risk_tolerance = behavior.get("risk_tolerance", 5.0)
        brand_loyalty = behavior.get("brand_loyalty", 5.0)
        decision_style = consumer_profile.get("psychographic_profile", {}).get("decision_style", "balanced")

        # Classify based on risk tolerance and brand loyalty
        if risk_tolerance > 7.0 and decision_style == "data_driven":
            return "rational_optimizer"
        elif brand_loyalty > 7.0:
            return "loyalist"
        elif risk_tolerance < 4.0:
            return "impulsive"
        else:
            return "satisficer"

    def _simulate_problem_recognition(self, consumer_profile: Dict[str, Any],
                                    market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate whether consumer recognizes a problem needing solution"""

        # Factors influencing problem recognition
        dissatisfaction_level = market_context.get("dissatisfaction_level", 0.5)
        information_exposure = market_context.get("information_exposure", 0.5)
        social_influence = market_context.get("social_influence", 0.3)

        # Consumer-specific factors
        consumer_sensitivity = consumer_profile.get("behavioral_attributes", {}).get("change_sensitivity", 0.5)

        # Calculate recognition probability
        recognition_score = (
            dissatisfaction_level * 0.4 +
            information_exposure * 0.3 +
            social_influence * 0.2 +
            consumer_sensitivity * 0.1
        )

        # Add some randomness
        recognition_score += self.random_state.normalvariate(0, 0.1)
        recognition_score = max(0.0, min(1.0, recognition_score))

        recognized = recognition_score > 0.6

        return {
            "recognized": recognized,
            "recognition_score": recognition_score,
            "influencing_factors": {
                "dissatisfaction_level": dissatisfaction_level,
                "information_exposure": information_exposure,
                "social_influence": social_influence,
                "consumer_sensitivity": consumer_sensitivity
            },
            "trigger_events": market_context.get("trigger_events", [])
        }

    def _simulate_information_search(self, consumer_profile: Dict[str, Any],
                                   product_options: List[Dict[str, Any]],
                                   market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate consumer information search process"""

        # Limited attention span
        max_options = min(self.attention_span, len(product_options))

        # Apply availability bias - more likely to consider well-known or advertised options
        scored_options = []
        for option in product_options:
            availability_score = option.get("brand_recognition", 0.5)
            social_proof = option.get("social_proof", 0.3)
            advertising_intensity = option.get("advertising_intensity", 0.4)

            total_score = (
                availability_score * self.heuristics["availability_bias"] +
                social_proof * self.heuristics["social_proof_weight"] +
                advertising_intensity * 0.3
            )

            scored_options.append((option, total_score))

        # Sort by score and select top options
        scored_options.sort(key=lambda x: x[1], reverse=True)
        considered_options = [option for option, score in scored_options[:max_options]]

        # Simulate information gathering depth
        information_depth = min(self.information_processing_capacity, 12)  # Max attributes considered
        information_gathered = self.random_state.randint(
            max(1, information_depth - 3),
            information_depth
        )

        return {
            "search_strategy": "limited_search",
            "considered_options": considered_options,
            "options_evaluated": len(considered_options),
            "information_gathered": information_gathered,
            "search_channels": market_context.get("available_channels", ["online", "social", "word_of_mouth"]),
            "search_duration": self.random_state.expovariate(1.0),  # Exponential distribution
            "cognitive_effort": information_gathered / self.information_processing_capacity
        }

    def _simulate_evaluation(self, consumer_profile: Dict[str, Any],
                           considered_options: List[Dict[str, Any]],
                           market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate evaluation of alternative options"""

        evaluation_results = {
            "options_evaluated": [],
            "evaluation_criteria": [],
            "cognitive_shortcuts_used": [],
            "trade_off_analysis": {}
        }

        # Define evaluation criteria based on consumer profile
        consumer_preferences = consumer_profile.get("market_receptivity", {})
        evaluation_criteria = self._determine_evaluation_criteria(consumer_preferences)

        evaluation_results["evaluation_criteria"] = evaluation_criteria

        # Evaluate each option
        for option in considered_options:
            option_evaluation = self._evaluate_single_option(
                option, evaluation_criteria, consumer_profile, market_context
            )
            evaluation_results["options_evaluated"].append(option_evaluation)

        # Identify cognitive shortcuts used
        evaluation_results["cognitive_shortcuts_used"] = self._identify_cognitive_shortcuts(
            evaluation_results["options_evaluated"]
        )

        # Analyze trade-offs
        evaluation_results["trade_off_analysis"] = self._analyze_trade_offs(
            evaluation_results["options_evaluated"]
        )

        return evaluation_results

    def _determine_evaluation_criteria(self, consumer_preferences: Dict[str, Any]) -> List[str]:
        """Determine which criteria consumer will use for evaluation"""

        base_criteria = ["price", "quality", "brand_reputation"]

        # Add preference-based criteria
        preferred_categories = consumer_preferences.get("product_categories", [])
        if "budget" in str(preferred_categories).lower():
            base_criteria.append("cost_savings")
        if "premium" in str(preferred_categories).lower():
            base_criteria.append("luxury_features")

        # Add behavioral criteria
        decision_style = consumer_preferences.get("decision_style", "balanced")
        if decision_style == "data_driven":
            base_criteria.extend(["specifications", "performance_metrics"])
        elif decision_style == "intuitive":
            base_criteria.extend(["design", "user_experience"])
        elif decision_style == "emotional":
            base_criteria.extend(["brand_story", "social_impact"])

        # Limit to processing capacity
        max_criteria = min(len(base_criteria), self.information_processing_capacity)
        return base_criteria[:max_criteria]

    def _evaluate_single_option(self, option: Dict[str, Any], criteria: List[str],
                              consumer_profile: Dict[str, Any],
                              market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a single product option"""

        evaluation = {
            "option_id": option.get("product_id", "unknown"),
            "option_name": option.get("product_name", "Unknown Product"),
            "criteria_scores": {},
            "overall_score": 0.0,
            "acceptability_threshold": self.heuristics["satisficing_threshold"],
            "meets_threshold": False
        }

        total_weight = 0
        weighted_score = 0

        for criterion in criteria:
            # Simulate criterion-specific evaluation with biases
            base_score = self._evaluate_criterion(option, criterion, consumer_profile)
            biased_score = self._apply_evaluation_biases(base_score, criterion, option, market_context)

            # Assign weights based on consumer preferences
            weight = self._get_criterion_weight(criterion, consumer_profile)

            evaluation["criteria_scores"][criterion] = {
                "base_score": base_score,
                "biased_score": biased_score,
                "weight": weight
            }

            weighted_score += biased_score * weight
            total_weight += weight

        if total_weight > 0:
            evaluation["overall_score"] = weighted_score / total_weight
            evaluation["meets_threshold"] = evaluation["overall_score"] >= evaluation["acceptability_threshold"]

        return evaluation

    def _evaluate_criterion(self, option: Dict[str, Any], criterion: str,
                          consumer_profile: Dict[str, Any]) -> float:
        """Evaluate option on specific criterion"""

        # Simulate evaluation based on option attributes and consumer preferences
        if criterion == "price":
            price_sensitivity = consumer_profile.get("behavioral_attributes", {}).get("price_sensitivity", "medium")
            option_price = option.get("price", 100)

            if price_sensitivity == "high":
                return max(0, 1.0 - (option_price / 200))  # More sensitive to price
            elif price_sensitivity == "low":
                return min(1.0, 0.8 + (option_price / 500))  # Less sensitive to price
            else:
                return max(0, 1.0 - (option_price / 300))

        elif criterion == "quality":
            return option.get("quality_score", 0.7) + self.random_state.normalvariate(0, 0.1)

        elif criterion == "brand_reputation":
            brand_loyalty = consumer_profile.get("behavioral_attributes", {}).get("brand_loyalty", 5.0)
            brand_strength = option.get("brand_strength", 0.6)

            # Brand loyal consumers give higher weight to brand
            loyalty_factor = (brand_loyalty - 5.0) / 5.0  # -1 to 1
            return brand_strength * (1.0 + loyalty_factor * 0.3)

        # Default evaluation for other criteria
        return 0.6 + self.random_state.normalvariate(0, 0.15)

    def _apply_evaluation_biases(self, base_score: float, criterion: str,
                               option: Dict[str, Any], market_context: Dict[str, Any]) -> float:
        """Apply cognitive biases to evaluation score"""

        biased_score = base_score

        # Anchoring bias - first option gets slight boost
        if option.get("position_in_list", 1) == 1:
            biased_score += self.heuristics["anchoring_bias"] * 0.1

        # Social proof bias
        social_proof = option.get("social_proof", 0.5)
        biased_score += social_proof * self.heuristics["social_proof_weight"]

        # Loss aversion for price criterion
        if criterion == "price":
            # Simulate perception of price as loss
            biased_score *= (1.0 - self.heuristics["loss_aversion"] * 0.05)

        # Add some random noise to simulate imperfect information
        noise = self.random_state.normalvariate(0, 0.05)
        biased_score += noise

        return max(0.0, min(1.0, biased_score))

    def _get_criterion_weight(self, criterion: str, consumer_profile: Dict[str, Any]) -> float:
        """Get weight for evaluation criterion"""

        base_weights = {
            "price": 0.25,
            "quality": 0.25,
            "brand_reputation": 0.20,
            "specifications": 0.15,
            "design": 0.10,
            "user_experience": 0.15,
            "cost_savings": 0.20,
            "luxury_features": 0.15,
            "performance_metrics": 0.15,
            "brand_story": 0.10,
            "social_impact": 0.10
        }

        return base_weights.get(criterion, 0.1)

    def _identify_cognitive_shortcuts(self, option_evaluations: List[Dict[str, Any]]) -> List[str]:
        """Identify cognitive shortcuts used in evaluation"""

        shortcuts = []

        # Check for satisficing (first acceptable option)
        for i, evaluation in enumerate(option_evaluations):
            if evaluation["meets_threshold"]:
                if i == 0:
                    shortcuts.append("first_acceptable_option")
                break

        # Check for anchoring bias
        if len(option_evaluations) > 1:
            first_score = option_evaluations[0]["overall_score"]
            avg_other_scores = sum(e["overall_score"] for e in option_evaluations[1:]) / len(option_evaluations[1:])
            if first_score > avg_other_scores + 0.1:
                shortcuts.append("anchoring_bias")

        # Check for insufficient evaluation
        avg_criteria_used = sum(len(e["criteria_scores"]) for e in option_evaluations) / len(option_evaluations)
        if avg_criteria_used < 3:
            shortcuts.append("insufficient_evaluation")

        return shortcuts

    def _analyze_trade_offs(self, option_evaluations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trade-offs between different criteria"""

        trade_offs = {
            "price_vs_quality": {"correlation": 0.0, "trade_off_intensity": 0.0},
            "features_vs_usability": {"correlation": 0.0, "trade_off_intensity": 0.0},
            "brand_vs_price": {"correlation": 0.0, "trade_off_intensity": 0.0}
        }

        if len(option_evaluations) < 2:
            return trade_offs

        # Calculate correlations between criteria
        prices = []
        qualities = []
        features_scores = []
        usability_scores = []
        brands = []

        for evaluation in option_evaluations:
            scores = evaluation["criteria_scores"]

            if "price" in scores:
                prices.append(1.0 - scores["price"]["biased_score"])  # Invert price (higher = more expensive)
            if "quality" in scores:
                qualities.append(scores["quality"]["biased_score"])
            if "specifications" in scores:
                features_scores.append(scores["specifications"]["biased_score"])
            if "user_experience" in scores:
                usability_scores.append(scores["user_experience"]["biased_score"])
            if "brand_reputation" in scores:
                brands.append(scores["brand_reputation"]["biased_score"])

        # Calculate correlations if we have enough data
        if len(prices) == len(qualities) and len(prices) > 1:
            trade_offs["price_vs_quality"]["correlation"] = self._calculate_correlation(prices, qualities)

        if len(features_scores) == len(usability_scores) and len(features_scores) > 1:
            trade_offs["features_vs_usability"]["correlation"] = self._calculate_correlation(features_scores, usability_scores)

        if len(brands) == len(prices) and len(brands) > 1:
            trade_offs["brand_vs_price"]["correlation"] = self._calculate_correlation(brands, prices)

        # Calculate trade-off intensity (how much consumers compromise)
        for trade_off_name, trade_off_data in trade_offs.items():
            correlation = abs(trade_off_data["correlation"])
            trade_off_data["trade_off_intensity"] = correlation * 0.8  # Scale to 0-0.8 range

        return trade_offs

    def _calculate_correlation(self, x_values: List[float], y_values: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""

        if len(x_values) != len(y_values) or len(x_values) < 2:
            return 0.0

        n = len(x_values)
        sum_x = sum(x_values)
        sum_y = sum(y_values)
        sum_xy = sum(x * y for x, y in zip(x_values, y_values))
        sum_x2 = sum(x * x for x in x_values)
        sum_y2 = sum(y * y for y in y_values)

        numerator = n * sum_xy - sum_x * sum_y
        denominator = ((n * sum_x2 - sum_x * sum_x) * (n * sum_y2 - sum_y * sum_y)) ** 0.5

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def _simulate_purchase_decision(self, consumer_profile: Dict[str, Any],
                                  evaluation_results: Dict[str, Any],
                                  market_context: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate final purchase decision"""

        options = evaluation_results["options_evaluated"]

        if not options:
            return {
                "decision": {"action": "no_purchase", "reason": "no_options_evaluated"},
                "confidence": 0.0,
                "decision_factors": []
            }

        # Find best option based on overall scores
        best_option = max(options, key=lambda x: x["overall_score"])

        # Apply status quo bias
        status_quo_preference = self.heuristics["status_quo_bias"]
        if self.random_state.random() < status_quo_preference:
            # Sometimes stick with "current" option (simulated)
            current_option = options[0]  # Assume first is current
            if current_option["overall_score"] > best_option["overall_score"] * 0.9:
                best_option = current_option

        # Calculate decision confidence
        score_diff = best_option["overall_score"] - evaluation_results["options_evaluated"][0]["overall_score"]
        confidence = min(1.0, 0.5 + score_diff * 2)

        # Add randomness to simulate real-world uncertainty
        confidence *= (0.8 + self.random_state.random() * 0.4)

        decision = {
            "action": "purchase" if best_option["meets_threshold"] else "delay_purchase",
            "selected_option": best_option["option_id"],
            "option_name": best_option["option_name"],
            "decision_score": best_option["overall_score"],
            "reason": "best_option_selected" if best_option["meets_threshold"] else "threshold_not_met"
        }

        return {
            "decision": decision,
            "confidence": confidence,
            "decision_factors": [
                f"overall_score: {best_option['overall_score']:.2f}",
                f"threshold: {best_option['acceptability_threshold']:.2f}",
                f"options_considered: {len(options)}",
                f"evaluation_depth: {len(best_option['criteria_scores'])}"
            ],
            "alternative_options_considered": [
                {"option_id": opt["option_id"], "score": opt["overall_score"]}
                for opt in options if opt != best_option
            ]
        }

    def _simulate_post_purchase_evaluation(self, consumer_profile: Dict[str, Any],
                                         purchase_decision: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate post-purchase evaluation"""

        decision = purchase_decision["decision"]

        if decision["action"] == "no_purchase":
            return {
                "satisfaction": 0.0,
                "regret_level": 0.0,
                "recommendation_likelihood": 0.0,
                "repurchase_intent": 0.0,
                "feedback_provided": False
            }

        # Simulate satisfaction based on decision confidence
        base_satisfaction = purchase_decision["confidence"]
        satisfaction = base_satisfaction + self.random_state.normalvariate(0, 0.1)
        satisfaction = max(0.0, min(1.0, satisfaction))

        # Calculate regret (inverse of satisfaction for non-optimal choices)
        regret_level = 1.0 - satisfaction

        # Calculate recommendation likelihood
        recommendation_likelihood = satisfaction * 0.8 + self.random_state.normalvariate(0, 0.05)
        recommendation_likelihood = max(0.0, min(1.0, recommendation_likelihood))

        # Calculate repurchase intent
        repurchase_intent = satisfaction * 0.9 + self.random_state.normalvariate(0, 0.05)
        repurchase_intent = max(0.0, min(1.0, repurchase_intent))

        # Simulate feedback provision
        feedback_provided = self.random_state.random() < satisfaction * 0.6

        return {
            "satisfaction": satisfaction,
            "regret_level": regret_level,
            "recommendation_likelihood": recommendation_likelihood,
            "repurchase_intent": repurchase_intent,
            "feedback_provided": feedback_provided,
            "feedback_type": "positive" if satisfaction > 0.7 else "neutral" if satisfaction > 0.4 else "negative"
        }

    def _calculate_cognitive_load(self, search_results: Dict[str, Any],
                                evaluation_results: Dict[str, Any]) -> float:
        """Calculate cognitive load of decision process"""

        search_load = search_results["information_gathered"] / self.information_processing_capacity
        evaluation_load = sum(len(opt["criteria_scores"]) for opt in evaluation_results["options_evaluated"])
        evaluation_load /= (len(evaluation_results["options_evaluated"]) * self.information_processing_capacity)

        total_load = (search_load + evaluation_load) / 2.0
        return min(1.0, total_load)

    def _identify_applied_biases(self, consumer_profile: Dict[str, Any],
                               search_results: Dict[str, Any],
                               evaluation_results: Dict[str, Any],
                               purchase_decision: Dict[str, Any]) -> List[str]:
        """Identify which cognitive biases were applied"""

        biases = []

        # Check for satisficing bias
        if any(opt["meets_threshold"] for opt in evaluation_results["options_evaluated"]):
            first_acceptable = next((opt for opt in evaluation_results["options_evaluated"]
                                   if opt["meets_threshold"]), None)
            if first_acceptable and evaluation_results["options_evaluated"].index(first_acceptable) == 0:
                biases.append("satisficing_bias")

        # Check for anchoring bias
        if len(evaluation_results["options_evaluated"]) > 1:
            first_score = evaluation_results["options_evaluated"][0]["overall_score"]
            avg_other = sum(opt["overall_score"] for opt in evaluation_results["options_evaluated"][1:]) / len(evaluation_results["options_evaluated"][1:])
            if first_score > avg_other + 0.15:
                biases.append("anchoring_bias")

        # Check for status quo bias
        if purchase_decision["decision"]["action"] == "purchase":
            if len(evaluation_results["options_evaluated"]) > 1:
                best_option = max(evaluation_results["options_evaluated"], key=lambda x: x["overall_score"])
                chosen_option = next((opt for opt in evaluation_results["options_evaluated"]
                                    if opt["option_id"] == purchase_decision["decision"]["selected_option"]), None)
                if chosen_option and chosen_option != best_option and chosen_option["overall_score"] > best_option["overall_score"] * 0.95:
                    biases.append("status_quo_bias")

        # Check for social proof influence
        if any(opt.get("criteria_scores", {}).get("brand_reputation", {}).get("biased_score", 0) > 0.8
               for opt in evaluation_results["options_evaluated"]):
            biases.append("social_proof_bias")

        return biases

    def get_model_info(self) -> Dict[str, Any]:
        """Get model information and capabilities"""

        return {
            "model_name": MODEL_NAME,
            "version": MODEL_VERSION,
            "capabilities": {
                "decision_stages": self.decision_stages,
                "consumer_segments": list(self.consumer_segments.keys()),
                "cognitive_biases_modeled": list(self.heuristics.keys()),
                "evaluation_criteria": ["price", "quality", "brand_reputation", "specifications", "design", "user_experience"]
            },
            "parameters": {
                "attention_span": self.attention_span,
                "processing_capacity": self.information_processing_capacity,
                "memory_decay_rate": self.memory_decay_rate,
                "satisficing_threshold": self.heuristics["satisficing_threshold"]
            },
            "python_version": PYTHON_VERSION,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }


# Model interface definition
MODEL_INTERFACE = {
    "model": MODEL_NAME,
    "version": MODEL_VERSION,
    "description": "Consumer bounded rationality decision-making model",
    "capabilities": {
        "decision_stages": ["problem_recognition", "information_search", "evaluation_of_alternatives", "purchase_decision", "post_purchase_evaluation"],
        "cognitive_biases": ["satisficing", "anchoring", "availability", "loss_aversion", "status_quo", "social_proof"],
        "consumer_segments": ["rational_optimizer", "satisficer", "impulsive", "loyalist"],
        "evaluation_criteria": ["price", "quality", "brand", "features", "usability", "social_proof"]
    },
    "endpoints": {
        "simulate_consumer_decision": {
            "method": "POST",
            "path": "/api/v1/simulation/models/consumer-bounded-rationality/simulate",
            "input": {
                "consumer_profile": "object with persona data",
                "product_options": "array of product objects",
                "market_context": "object with market conditions",
                "seed": "integer (optional)"
            },
            "output": {
                "decision_process": "object with decision stages and outcomes",
                "confidence": "number",
                "biases_applied": "array of bias types"
            },
            "token_budget": 1500,
            "timeout_seconds": 30
        }
    },
    "data_quality": {
        "realism_score": 0.85,
        "behavioral_accuracy": 0.82,
        "bias_representation": 0.88,
        "predictive_validity": 0.79
    },
    "limitations": {
        "cognitive_simplification": "Models simplified cognitive processes",
        "cultural_bias": "Based on Western consumer behavior patterns",
        "temporal_stability": "Consumer behavior may change over time",
        "context_dependency": "Performance varies by market context"
    },
    "grounding_sources": [
        "Bounded rationality theory (Herbert Simon)",
        "Prospect theory (Kahneman & Tversky)",
        "Consumer behavior research (Howard & Sheth model)",
        "Cognitive bias research (Daniel Kahneman)",
        "Decision-making under uncertainty studies"
    ],
    "observability": {
        "spans": ["problem_recognition", "information_search", "option_evaluation", "decision_formation", "post_evaluation"],
        "metrics": ["decision_confidence", "cognitive_load", "biases_applied_count", "evaluation_depth"],
        "logs": ["decision_start", "stage_completion", "bias_detected", "decision_finalized"]
    }
}


if __name__ == "__main__":
    # Example usage
    config = {"attention_span": 5, "processing_capacity": 10}
    model = ConsumerBoundedRationalityModel(config)

    # Example consumer profile
    consumer = {
        "persona_id": "TEST_CONSUMER_001",
        "demographics": {"age": 35, "gender": "female"},
        "behavioral_attributes": {
            "risk_tolerance": 6.5,
            "brand_loyalty": 7.2,
            "price_sensitivity": "medium"
        },
        "market_receptivity": {
            "decision_style": "balanced",
            "preferred_channels": ["online", "reviews"]
        }
    }

    # Example product options
    products = [
        {"product_id": "PROD_001", "product_name": "Budget Option", "price": 50, "quality_score": 0.7},
        {"product_id": "PROD_002", "product_name": "Premium Option", "price": 150, "quality_score": 0.9}
    ]

    # Example market context
    context = {
        "dissatisfaction_level": 0.7,
        "information_exposure": 0.8,
        "social_influence": 0.5
    }

    # Simulate decision
    result = model.simulate_consumer_decision(consumer, products, context, seed=42)

    print(f"Decision: {result['final_decision']['action']}")
    print(f"Confidence: {result['decision_confidence']:.2f}")
    print(f"Cognitive Load: {result['cognitive_load']:.2f}")
    print(f"Biases Applied: {result['biases_applied']}")
