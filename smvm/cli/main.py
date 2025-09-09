#!/usr/bin/env python3
"""
SMVM CLI - Synthetic Market Validation Module Command Line Interface

This is the main entry point for the SMVM CLI, providing single-command E2E execution
with safe retries and TractionBuild integration.
"""

import argparse
import json
import logging
import os
import sys
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import SMVM modules (will be implemented)
try:
    from smvm.validation import IdeaValidator
    from smvm.ingestion import DataIngestor
    from smvm.personas import PersonaSynthesizer
    from smvm.competitors import CompetitorSynthesizer
    from smvm.simulation import SimulationEngine
    from smvm.analysis import DecisionAnalyzer
    from smvm.reporting import ReportGenerator
    from smvm.orchestration import PipelineOrchestrator
    from smvm.monitoring import TokenMonitor, EventLogger
except ImportError:
    # Mock implementations for development
    pass

class SMVMCLI:
    """
    SMVM Command Line Interface main class
    """

    def __init__(self):
        self.logger = self._setup_logging()
        self.config = self._load_config()
        self.token_monitor = TokenMonitor(
            budget_per_step=self.config.get('token_budgets', {}),
            global_budget=self.config.get('max_tokens_per_run', 10000)
        )
        self.event_logger = EventLogger()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, os.getenv('SMVM_LOG_LEVEL', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger('smvm.cli')

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or defaults"""
        config_path = os.getenv('SMVM_CONFIG_PATH', 'configs/dev.yaml')

        if os.path.exists(config_path):
            try:
                import yaml
                with open(config_path, 'r') as f:
                    return yaml.safe_load(f)
            except ImportError:
                self.logger.warning("PyYAML not available, using default config")
            except Exception as e:
                self.logger.error(f"Error loading config: {e}")

        # Default configuration
        return {
            'max_tokens_per_run': 10000,
            'timeout_seconds': 3600,
            'retry_attempts': 3,
            'log_level': 'INFO',
            'token_budgets': {
                'validate_idea': 500,
                'ingest_data': 2000,
                'synthesize_personas': 3000,
                'synthesize_competitors': 3000,
                'run_simulation': 5000,
                'analyze_results': 4000,
                'generate_report': 2000
            }
        }

    def run(self):
        """Main CLI entry point"""
        parser = self._create_parser()
        args = parser.parse_args()

        if not hasattr(args, 'command'):
            parser.print_help()
            return 1

        try:
            # Set random seed for reproducibility
            if hasattr(args, 'seed') and args.seed:
                random.seed(args.seed)

            # Generate or use run_id
            run_id = getattr(args, 'run_id', None) or f"run_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"

            # Log command start
            self.event_logger.log_event(
                run_id=run_id,
                step_name='cli_command',
                event_type='COMMAND_START',
                message=f"Starting command: {args.command}",
                metadata={
                    'command': args.command,
                    'args': vars(args),
                    'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
                }
            )

            # Execute command
            start_time = time.time()
            result = self._execute_command(args, run_id)
            execution_time = time.time() - start_time

            # Log command completion
            self.event_logger.log_event(
                run_id=run_id,
                step_name='cli_command',
                event_type='COMMAND_SUCCESS',
                message=f"Command completed successfully: {args.command}",
                metadata={
                    'execution_time': execution_time,
                    'result': result
                }
            )

            return 0

        except Exception as e:
            self.logger.error(f"Command failed: {e}")
            self.event_logger.log_event(
                run_id=getattr(args, 'run_id', 'unknown'),
                step_name='cli_command',
                event_type='COMMAND_FAILURE',
                message=f"Command failed: {args.command}",
                metadata={
                    'error': str(e),
                    'error_type': type(e).__name__
                }
            )
            return 1

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with all commands"""
        parser = argparse.ArgumentParser(
            description='SMVM CLI - Synthetic Market Validation Module',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )

        # Global arguments
        parser.add_argument('--run-id', help='Unique run identifier')
        parser.add_argument('--seed', type=int, help='Random seed for reproducibility')
        parser.add_argument('--config', default='configs/dev.yaml', help='Configuration file path')
        parser.add_argument('--max-tokens-per-step', type=int, help='Maximum tokens per step')
        parser.add_argument('--dry-run', action='store_true', help='Execute without external calls')
        parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
        parser.add_argument('--log-level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR'],
                          help='Logging level')

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # validate-idea command
        validate_parser = subparsers.add_parser('validate-idea', help='Validate business idea')
        validate_parser.add_argument('idea_file', help='Path to idea JSON file')
        validate_parser.add_argument('--output-dir', help='Output directory')
        validate_parser.add_argument('--skip-validation', action='store_true', help='Skip schema validation')

        # ingest command
        ingest_parser = subparsers.add_parser('ingest', help='Ingest market data')
        ingest_parser.add_argument('sources', nargs='*', help='Data sources to ingest',
                                 choices=['trends', 'forums', 'competitor_pages', 'directories'])
        ingest_parser.add_argument('--sources-config', help='Sources configuration file')
        ingest_parser.add_argument('--batch-size', type=int, default=100, help='Batch size')
        ingest_parser.add_argument('--rate-limit', type=int, default=60, help='Rate limit (requests/min)')
        ingest_parser.add_argument('--retry-attempts', type=int, default=3, help='Retry attempts')

        # synthesize command
        synthesize_parser = subparsers.add_parser('synthesize', help='Synthesize personas and competitors')
        synthesize_parser.add_argument('--persona-count', type=int, default=5, help='Number of personas')
        synthesize_parser.add_argument('--competitor-count', type=int, default=10, help='Number of competitors')
        synthesize_parser.add_argument('--bias-controls', help='Bias control configuration')
        synthesize_parser.add_argument('--confidence-threshold', type=float, default=0.7, help='Confidence threshold')

        # simulate command
        simulate_parser = subparsers.add_parser('simulate', help='Run market simulation')
        simulate_parser.add_argument('--simulation-config', help='Simulation configuration file')
        simulate_parser.add_argument('--iterations', type=int, default=1000, help='Number of iterations')
        simulate_parser.add_argument('--scenario', choices=['price_cut', 'feature_launch', 'downturn', 'hype_cycle', 'seasonality'],
                                   help='Simulation scenario')
        simulate_parser.add_argument('--parallel-jobs', type=int, default=4, help='Number of parallel jobs')
        simulate_parser.add_argument('--memory-limit', type=int, default=512, help='Memory limit per job (MB)')

        # analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze simulation results')
        analyze_parser.add_argument('--simulation-results', help='Path to simulation results')
        analyze_parser.add_argument('--analysis-config', help='Analysis configuration')
        analyze_parser.add_argument('--confidence-intervals', action='store_true', help='Calculate confidence intervals')
        analyze_parser.add_argument('--sensitivity-analysis', action='store_true', help='Perform sensitivity analysis')
        analyze_parser.add_argument('--report-format', choices=['json', 'markdown', 'both'], default='both',
                                  help='Output format')

        # report command
        report_parser = subparsers.add_parser('report', help='Generate validation report')
        report_parser.add_argument('--decision-data', help='Path to decision output file')
        report_parser.add_argument('--template', default='validation_report.md', help='Report template')
        report_parser.add_argument('--include-evidence', action='store_true', help='Include evidence sections')
        report_parser.add_argument('--redact-sensitive', action='store_true', help='Redact sensitive information')
        report_parser.add_argument('--output-format', choices=['markdown', 'pdf', 'html'], default='markdown',
                                 help='Report format')

        # replay command
        replay_parser = subparsers.add_parser('replay', help='Replay previous run')
        replay_parser.add_argument('run_id', help='Run ID to replay')
        replay_parser.add_argument('--from-step', help='Step to start replay from')
        replay_parser.add_argument('--to-step', help='Step to end replay at')
        replay_parser.add_argument('--force-regeneration', action='store_true', help='Force regeneration')
        replay_parser.add_argument('--compare-results', action='store_true', help='Compare with stored results')

        return parser

    def _execute_command(self, args: argparse.Namespace, run_id: str) -> Any:
        """Execute the specified command"""

        command = args.command

        # Create run directory for commands that need it
        if command in ['validate-idea', 'ingest', 'synthesize', 'simulate', 'analyze', 'report']:
            run_dir = self._create_run_directory(run_id, args)
            self._setup_run_metadata(run_dir, args, run_id)

        if command == 'validate-idea':
            return self._cmd_validate_idea(args, run_id, run_dir)
        elif command == 'ingest':
            return self._cmd_ingest(args, run_id, run_dir)
        elif command == 'synthesize':
            return self._cmd_synthesize(args, run_id, run_dir)
        elif command == 'simulate':
            return self._cmd_simulate(args, run_id, run_dir)
        elif command == 'analyze':
            return self._cmd_analyze(args, run_id, run_dir)
        elif command == 'report':
            return self._cmd_report(args, run_id, run_dir)
        elif command == 'replay':
            return self._cmd_replay(args, run_id)
        else:
            raise ValueError(f"Unknown command: {command}")

    def _create_run_directory(self, run_id: str, args: argparse.Namespace) -> str:
        """Create run directory structure"""

        # Use output-dir if specified, otherwise create standard structure
        if hasattr(args, 'output_dir') and args.output_dir:
            run_dir = args.output_dir
        else:
            # Create project-based directory structure
            project_id = getattr(args, 'project_id', 'default') if hasattr(args, 'project_id') else 'default'
            run_dir = f"runs/{project_id}/validation/{run_id}"

        # Create directory structure
        os.makedirs(run_dir, exist_ok=True)
        os.makedirs(f"{run_dir}/inputs", exist_ok=True)
        os.makedirs(f"{run_dir}/outputs", exist_ok=True)
        os.makedirs(f"{run_dir}/reports", exist_ok=True)

        self.logger.info(f"Created run directory: {run_dir}")
        return run_dir

    def _setup_run_metadata(self, run_dir: str, args: argparse.Namespace, run_id: str):
        """Setup run metadata file"""

        metadata = {
            'run_id': run_id,
            'command': args.command,
            'start_time': datetime.utcnow().isoformat() + 'Z',
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'python_env_hash': hashlib.sha256(str(os.environ).encode()).hexdigest()[:64],
            'config': self.config,
            'args': vars(args),
            'working_directory': os.getcwd(),
            'run_directory': run_dir,
            'data_zone': 'GREEN',
            'retention_days': 90
        }

        with open(f"{run_dir}/meta.json", 'w') as f:
            json.dump(metadata, f, indent=2, default=str)

    def _cmd_validate_idea(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute validate-idea command"""

        self.logger.info(f"Validating idea from: {args.idea_file}")

        # Check token budget
        if not self.token_monitor.check_step_budget('validate_idea', 500):
            raise RuntimeError("Token budget exceeded for validate_idea step")

        # Load and validate idea file
        with open(args.idea_file, 'r') as f:
            idea_data = json.load(f)

        # Mock validation (replace with actual implementation)
        validation_result = {
            'is_valid': True,
            'schema_compliant': True,
            'business_model_viable': True,
            'market_potential': 'medium',
            'risk_level': 'medium',
            'recommendations': [
                'Consider expanding target market segments',
                'Validate pricing assumptions with customer research'
            ]
        }

        # Save validation result
        with open(f"{run_dir}/validation_result.json", 'w') as f:
            json.dump(validation_result, f, indent=2, default=str)

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='validate_idea',
            event_type='STEP_SUCCESS',
            message="Idea validation completed successfully",
            metadata={'validation_result': validation_result}
        )

        # Record token usage
        self.token_monitor.record_usage('validate_idea', 350)

        return validation_result

    def _cmd_ingest(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute ingest command"""

        sources = args.sources or ['trends', 'forums', 'competitor_pages', 'directories']
        self.logger.info(f"Ingesting data from sources: {sources}")

        # Check token budget
        if not self.token_monitor.check_step_budget('ingest_data', 2000):
            raise RuntimeError("Token budget exceeded for ingest_data step")

        ingestion_results = {}

        for source in sources:
            self.logger.info(f"Ingesting from: {source}")

            # Mock ingestion (replace with actual implementation)
            if source == 'trends':
                mock_data = {
                    'source': 'trends',
                    'records_ingested': 150,
                    'data_quality_score': 0.85,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                with open(f"{run_dir}/inputs/trends_normalized.json", 'w') as f:
                    json.dump(mock_data, f, indent=2)

            elif source == 'forums':
                mock_data = {
                    'source': 'forums',
                    'records_ingested': 200,
                    'data_quality_score': 0.78,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                with open(f"{run_dir}/inputs/forums_normalized.json", 'w') as f:
                    json.dump(mock_data, f, indent=2)

            elif source == 'competitor_pages':
                mock_data = {
                    'source': 'competitor_pages',
                    'records_ingested': 50,
                    'data_quality_score': 0.92,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                with open(f"{run_dir}/inputs/competitor_normalized.json", 'w') as f:
                    json.dump(mock_data, f, indent=2)

            elif source == 'directories':
                mock_data = {
                    'source': 'directories',
                    'records_ingested': 75,
                    'data_quality_score': 0.88,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
                with open(f"{run_dir}/inputs/directory_normalized.json", 'w') as f:
                    json.dump(mock_data, f, indent=2)

            ingestion_results[source] = mock_data

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='ingest_data',
            event_type='STEP_SUCCESS',
            message=f"Data ingestion completed for {len(sources)} sources",
            metadata={'sources_processed': sources, 'results': ingestion_results}
        )

        # Record token usage
        self.token_monitor.record_usage('ingest_data', 1250)

        return ingestion_results

    def _cmd_synthesize(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute synthesize command"""

        self.logger.info(f"Synthesizing personas and competitors")

        # Check token budget
        if not self.token_monitor.check_step_budget('synthesize_personas', 3000):
            raise RuntimeError("Token budget exceeded for synthesize steps")

        # Mock persona synthesis
        personas_data = {
            'personas': [
                {
                    'id': f'persona_{i}',
                    'demographics': {'age': 25 + i * 5, 'income': 50000 + i * 10000},
                    'psychographics': {'tech_savvy': True, 'risk_tolerance': 0.7},
                    'behavioral': {'purchase_frequency': 'monthly', 'brand_loyalty': 0.8}
                } for i in range(args.persona_count)
            ],
            'confidence_score': 0.82,
            'bias_controls_applied': True,
            'diversity_score': 0.75
        }

        # Mock competitor synthesis
        competitors_data = {
            'competitors': [
                {
                    'id': f'competitor_{i}',
                    'company_info': {'name': f'Competitor {i}', 'size': 'medium'},
                    'market_position': {'share': 0.15 - i * 0.02, 'growth_rate': 0.08},
                    'competitive_analysis': {'strengths': ['feature_a'], 'weaknesses': ['feature_b']}
                } for i in range(args.competitor_count)
            ],
            'market_coverage': 0.85,
            'analysis_depth': 'comprehensive'
        }

        # Save outputs
        with open(f"{run_dir}/outputs/personas.output.json", 'w') as f:
            json.dump(personas_data, f, indent=2)

        with open(f"{run_dir}/outputs/competitors.output.json", 'w') as f:
            json.dump(competitors_data, f, indent=2)

        # Log events
        self.event_logger.log_event(
            run_id=run_id,
            step_name='synthesize_personas',
            event_type='STEP_SUCCESS',
            message=f"Generated {args.persona_count} personas",
            metadata={'persona_count': args.persona_count, 'confidence': personas_data['confidence_score']}
        )

        self.event_logger.log_event(
            run_id=run_id,
            step_name='synthesize_competitors',
            event_type='STEP_SUCCESS',
            message=f"Analyzed {args.competitor_count} competitors",
            metadata={'competitor_count': args.competitor_count, 'market_coverage': competitors_data['market_coverage']}
        )

        # Record token usage
        self.token_monitor.record_usage('synthesize_personas', 1800)
        self.token_monitor.record_usage('synthesize_competitors', 1800)

        return {
            'personas': personas_data,
            'competitors': competitors_data
        }

    def _cmd_simulate(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute simulate command"""

        self.logger.info(f"Running simulation with {args.iterations} iterations")

        # Check token budget
        if not self.token_monitor.check_step_budget('run_simulation', 5000):
            raise RuntimeError("Token budget exceeded for run_simulation step")

        # Mock simulation
        simulation_result = {
            'simulation_metadata': {
                'iterations': args.iterations,
                'scenario': args.scenario or 'baseline',
                'parallel_jobs': args.parallel_jobs,
                'execution_time': 450.5,
                'seed': getattr(args, 'seed', None)
            },
            'aggregate_metrics': {
                'total_revenue': 2500000,
                'market_share': 0.15,
                'customer_acquisition_cost': 85,
                'customer_lifetime_value': 450,
                'conversion_rate': 0.08,
                'churn_rate': 0.12
            },
            'confidence_intervals': {
                'revenue_ci': [2200000, 2800000],
                'market_share_ci': [0.12, 0.18],
                'conversion_ci': [0.06, 0.10]
            },
            'sensitivity_analysis': {
                'price_elasticity': -1.2,
                'market_growth_sensitivity': 0.85,
                'competition_intensity_sensitivity': 0.92
            },
            'determinism_check': {
                'passed': True,
                'same_seed_same_results': True,
                'variance_threshold': 0.01
            }
        }

        # Save simulation result
        with open(f"{run_dir}/outputs/simulation.result.json", 'w') as f:
            json.dump(simulation_result, f, indent=2)

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='run_simulation',
            event_type='STEP_SUCCESS',
            message=f"Simulation completed with {args.iterations} iterations",
            metadata={
                'iterations': args.iterations,
                'scenario': args.scenario,
                'execution_time': simulation_result['simulation_metadata']['execution_time']
            }
        )

        # Record token usage
        self.token_monitor.record_usage('run_simulation', 3200)

        return simulation_result

    def _cmd_analyze(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute analyze command"""

        self.logger.info("Analyzing simulation results")

        # Check token budget
        if not self.token_monitor.check_step_budget('analyze_results', 4000):
            raise RuntimeError("Token budget exceeded for analyze_results step")

        # Mock analysis
        decision_output = {
            'decision_metadata': {
                'decision_id': f"decision_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.utcnow().isoformat() + 'Z',
                'run_id': run_id,
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
                'data_zone': 'GREEN',
                'retention_days': 90
            },
            'decision_analysis': {
                'composite_score': 48.75,
                'dimension_scores': {
                    'market_opportunity': {'score': 45, 'confidence': 0.75},
                    'wtp_validation': {'score': 35, 'confidence': 0.80},
                    'competitive_position': {'score': 50, 'confidence': 0.70},
                    'technical_feasibility': {'score': 75, 'confidence': 0.85},
                    'financial_viability': {'score': 40, 'confidence': 0.75},
                    'risk_assessment': {'score': 45, 'confidence': 0.70},
                    'team_capability': {'score': 65, 'confidence': 0.80}
                }
            },
            'decision_recommendation': {
                'recommendation': 'PIVOT',
                'confidence': 0.75,
                'rationale': 'Market potential exists but requires strategic adjustments'
            }
        }

        # Save decision output
        with open(f"{run_dir}/outputs/decision.output.json", 'w') as f:
            json.dump(decision_output, f, indent=2)

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='analyze_results',
            event_type='STEP_SUCCESS',
            message="Analysis completed with PIVOT recommendation",
            metadata={
                'composite_score': decision_output['decision_analysis']['composite_score'],
                'recommendation': decision_output['decision_recommendation']['recommendation'],
                'confidence': decision_output['decision_recommendation']['confidence']
            }
        )

        # Record token usage
        self.token_monitor.record_usage('analyze_results', 2800)

        return decision_output

    def _cmd_report(self, args: argparse.Namespace, run_id: str, run_dir: str) -> Dict[str, Any]:
        """Execute report command"""

        self.logger.info("Generating validation report")

        # Check token budget
        if not self.token_monitor.check_step_budget('generate_report', 2000):
            raise RuntimeError("Token budget exceeded for generate_report step")

        # Mock report generation
        report_result = {
            'report_metadata': {
                'generated_at': datetime.utcnow().isoformat() + 'Z',
                'format': args.output_format,
                'template_used': args.template,
                'redaction_applied': args.redact_sensitive,
                'evidence_included': args.include_evidence
            },
            'report_stats': {
                'total_sections': 11,
                'word_count': 2500,
                'evidence_sources': 8,
                'recommendations_count': 5
            }
        }

        # Save report
        with open(f"{run_dir}/reports/validation_report.md", 'w') as f:
            f.write("# SMVM Validation Report\n\n**Recommendation: PIVOT**\n\n*Report generated automatically*")

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='generate_report',
            event_type='STEP_SUCCESS',
            message=f"Report generated in {args.output_format} format",
            metadata=report_result
        )

        # Record token usage
        self.token_monitor.record_usage('generate_report', 1200)

        return report_result

    def _cmd_replay(self, args: argparse.Namespace, run_id: str) -> Dict[str, Any]:
        """Execute replay command"""

        self.logger.info(f"Replaying run: {args.run_id}")

        # Mock replay (would load and re-execute previous run)
        replay_result = {
            'original_run_id': args.run_id,
            'new_run_id': run_id,
            'steps_replayed': ['validate_idea', 'ingest', 'synthesize', 'simulate', 'analyze'],
            'results_comparison': {
                'identical_results': True,
                'variance_detected': False,
                'performance_delta': -5.2  # 5.2% faster
            },
            'replay_metadata': {
                'from_step': args.from_step,
                'to_step': args.to_step,
                'force_regeneration': args.force_regeneration,
                'comparison_performed': args.compare_results
            }
        }

        # Log event
        self.event_logger.log_event(
            run_id=run_id,
            step_name='replay',
            event_type='STEP_SUCCESS',
            message=f"Successfully replayed run {args.run_id}",
            metadata=replay_result
        )

        return replay_result


class TokenMonitor:
    """Token usage monitoring and enforcement"""

    def __init__(self, budget_per_step: Dict[str, int], global_budget: int):
        self.budget_per_step = budget_per_step
        self.global_budget = global_budget
        self.step_usage = {}
        self.total_usage = 0

    def check_step_budget(self, step_name: str, requested_tokens: int) -> bool:
        """Check if step can use requested tokens"""
        if step_name not in self.budget_per_step:
            return True  # No specific limit

        available_budget = self.budget_per_step[step_name] - self.step_usage.get(step_name, 0)
        return requested_tokens <= available_budget

    def check_global_budget(self, requested_tokens: int) -> bool:
        """Check if global budget allows additional tokens"""
        return (self.total_usage + requested_tokens) <= self.global_budget

    def record_usage(self, step_name: str, tokens_used: int):
        """Record token usage"""
        self.step_usage[step_name] = self.step_usage.get(step_name, 0) + tokens_used
        self.total_usage += tokens_used


class EventLogger:
    """Event logging for observability"""

    def __init__(self):
        self.events = []

    def log_event(self, run_id: str, step_name: str, event_type: str,
                  message: str, metadata: Optional[Dict[str, Any]] = None):
        """Log an event"""
        event = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'run_id': run_id,
            'step_name': step_name,
            'event_type': event_type,
            'level': 'INFO',
            'message': message,
            'metadata': metadata or {},
            'context': {
                'user_id': 'system',
                'correlation_id': f"corr_{datetime.utcnow().strftime('%H%M%S%f')}"
            }
        }

        self.events.append(event)
        print(f"[{event_type}] {step_name}: {message}")


def main():
    """Main entry point"""
    cli = SMVMCLI()
    exit_code = cli.run()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
