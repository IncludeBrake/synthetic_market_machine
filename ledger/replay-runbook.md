# SMVM Replay Runbook

## Overview

This runbook provides procedures for replaying Synthetic Market Validation Module (SMVM) runs to ensure reproducibility, debugging, and validation of results. Replay enables exact recreation of validation runs using stored seeds, hashes, and environmental parameters.

## Prerequisites

### System Requirements
- **Python Version**: Must match original run's `python_version`
- **Dependencies**: Must match original run's `pip_freeze_hash`
- **Storage Access**: Read access to original run artifacts
- **Permissions**: `replay` role or higher in RBAC system

### Data Requirements
- **Run ID**: Valid `RUN-YYYYMMDD-HHMMSS-xxxxxxxx` format
- **Event Ledger**: Complete event chain for the run
- **Artifact Store**: All generated artifacts from original run
- **Seed Store**: Random seeds used in original run

## Replay Procedures

### 1. Environment Validation

#### Check Python Version Compatibility
```bash
# Extract python version from run metadata
ORIGINAL_PYTHON=$(grep '"python_version"' runs/$RUN_ID/metadata.json | cut -d'"' -f4)
CURRENT_PYTHON=$(python --version | cut -d' ' -f2)

if [ "$ORIGINAL_PYTHON" != "$CURRENT_PYTHON" ]; then
    echo "❌ Python version mismatch: $ORIGINAL_PYTHON required, $CURRENT_PYTHON found"
    echo "🔄 Attempting version override..."
fi
```

#### Validate Dependencies
```bash
# Extract and compare pip freeze hash
ORIGINAL_DEPS_HASH=$(grep '"pip_freeze_hash"' runs/$RUN_ID/metadata.json | cut -d'"' -f4)
CURRENT_DEPS_HASH=$(pip freeze | sha256sum | cut -d' ' -f1)

if [ "$ORIGINAL_DEPS_HASH" != "$CURRENT_DEPS_HASH" ]; then
    echo "⚠️  Dependency hash mismatch detected"
    echo "🔄 Installing original dependencies..."
    pip install -r runs/$RUN_ID/requirements.txt --quiet
fi
```

#### Version Compatibility Check
```python
def check_version_compatibility(original_version: str, current_version: str) -> dict:
    """Check if versions are compatible for replay"""

    orig_parts = [int(x) for x in original_version.split('.')]
    curr_parts = [int(x) for x in current_version.split('.')]

    # Major version must match
    if orig_parts[0] != curr_parts[0]:
        return {
            "compatible": False,
            "reason": f"Major version mismatch: {orig_parts[0]} vs {curr_parts[0]}",
            "requires_override": True
        }

    # Minor version should be >= original
    if curr_parts[1] < orig_parts[1]:
        return {
            "compatible": False,
            "reason": f"Minor version too old: {curr_parts[1]} < {orig_parts[1]}",
            "requires_override": False
        }

    return {"compatible": True}
```

### 2. Run Preparation

#### Load Run Context
```python
def load_run_context(run_id: str) -> dict:
    """Load complete run context for replay"""

    context = {
        "run_id": run_id,
        "metadata": load_json(f"runs/{run_id}/metadata.json"),
        "seeds": load_json(f"runs/{run_id}/seeds.json"),
        "hashes": load_json(f"runs/{run_id}/hashes.json"),
        "artifacts": list_run_artifacts(run_id),
        "events": load_event_chain(run_id)
    }

    # Validate context completeness
    required_keys = ["metadata", "seeds", "hashes", "artifacts", "events"]
    missing_keys = [k for k in required_keys if not context.get(k)]

    if missing_keys:
        raise ValueError(f"Incomplete run context: missing {missing_keys}")

    return context
```

#### Validate Run Integrity
```python
def validate_run_integrity(run_context: dict) -> dict:
    """Validate run data integrity using stored hashes"""

    validation_results = {
        "metadata_integrity": False,
        "artifact_integrity": False,
        "event_chain_integrity": False,
        "seed_consistency": False
    }

    # Check metadata hash
    metadata_hash = calculate_hash(run_context["metadata"])
    stored_hash = run_context["hashes"]["metadata"]
    validation_results["metadata_integrity"] = metadata_hash == stored_hash

    # Check artifact hashes
    for artifact_path in run_context["artifacts"]:
        artifact_hash = calculate_file_hash(artifact_path)
        stored_hash = run_context["hashes"]["artifacts"].get(artifact_path)
        if artifact_hash != stored_hash:
            validation_results["artifact_integrity"] = False
            break
    else:
        validation_results["artifact_integrity"] = True

    # Check event chain consistency
    event_hashes = [calculate_hash(event) for event in run_context["events"]]
    stored_event_hashes = run_context["hashes"]["events"]
    validation_results["event_chain_integrity"] = event_hashes == stored_event_hashes

    # Check seed consistency
    seed_hash = calculate_hash(run_context["seeds"])
    stored_seed_hash = run_context["hashes"]["seeds"]
    validation_results["seed_consistency"] = seed_hash == stored_seed_hash

    return validation_results
```

### 3. Replay Execution

#### Initialize Replay Environment
```python
def initialize_replay_environment(run_context: dict, override_flags: dict = None) -> dict:
    """Initialize environment for replay execution"""

    override_flags = override_flags or {}

    # Set up isolated environment
    replay_env = {
        "run_id": f"{run_context['run_id']}-replay-{generate_timestamp()}",
        "original_run_id": run_context["run_id"],
        "seeds": run_context["seeds"],
        "python_version": run_context["metadata"]["python_version"],
        "pip_freeze_hash": run_context["metadata"]["pip_freeze_hash"],
        "override_flags": override_flags,
        "replay_mode": True
    }

    # Apply overrides
    if override_flags.get("ignore_version_check"):
        replay_env["python_version"] = get_current_python_version()

    if override_flags.get("use_current_dependencies"):
        replay_env["pip_freeze_hash"] = get_current_pip_freeze_hash()

    return replay_env
```

#### Execute Replay
```python
def execute_replay(run_context: dict, replay_env: dict) -> dict:
    """Execute the replay of a validation run"""

    replay_results = {
        "replay_id": replay_env["run_id"],
        "original_run_id": run_context["run_id"],
        "start_time": datetime.utcnow().isoformat() + "Z",
        "status": "running",
        "stages": [],
        "metrics": {},
        "artifacts": []
    }

    try:
        # Replay ingestion stage
        ingestion_result = replay_ingestion_stage(run_context, replay_env)
        replay_results["stages"].append(ingestion_result)

        # Replay personas stage
        personas_result = replay_personas_stage(run_context, replay_env)
        replay_results["stages"].append(personas_result)

        # Replay competitors stage
        competitors_result = replay_competitors_stage(run_context, replay_env)
        replay_results["stages"].append(competitors_result)

        # Replay simulation stage
        simulation_result = replay_simulation_stage(run_context, replay_env)
        replay_results["stages"].append(simulation_result)

        # Replay analysis stage
        analysis_result = replay_analysis_stage(run_context, replay_env)
        replay_results["stages"].append(analysis_result)

        # Replay decision stage
        decision_result = replay_decision_stage(run_context, replay_env)
        replay_results["stages"].append(decision_result)

        # Validate replay results
        validation_result = validate_replay_results(run_context, replay_results)
        replay_results["validation"] = validation_result

        replay_results["status"] = "completed" if validation_result["passed"] else "validation_failed"

    except Exception as e:
        replay_results["status"] = "error"
        replay_results["error"] = str(e)
        logger.error(f"Replay execution failed: {e}")

    finally:
        replay_results["end_time"] = datetime.utcnow().isoformat() + "Z"
        replay_results["duration_seconds"] = calculate_duration(
            replay_results["start_time"], replay_results["end_time"]
        )

    return replay_results
```

### 4. Result Validation

#### Compare Results
```python
def validate_replay_results(original_context: dict, replay_results: dict) -> dict:
    """Validate that replay results match original run"""

    validation = {
        "passed": True,
        "differences": [],
        "confidence_score": 1.0,
        "stage_validation": {}
    }

    # Compare stage outputs
    for i, (original_stage, replay_stage) in enumerate(zip(
        original_context["stages"], replay_results["stages"]
    )):
        stage_validation = validate_stage_results(original_stage, replay_stage)
        validation["stage_validation"][f"stage_{i}"] = stage_validation

        if not stage_validation["matched"]:
            validation["passed"] = False
            validation["differences"].append({
                "stage": i,
                "type": "output_mismatch",
                "details": stage_validation["differences"]
            })

    # Check hash consistency
    original_hashes = original_context["hashes"]
    replay_hashes = calculate_replay_hashes(replay_results)

    for hash_type, original_hash in original_hashes.items():
        replay_hash = replay_hashes.get(hash_type)
        if original_hash != replay_hash:
            validation["passed"] = False
            validation["differences"].append({
                "type": "hash_mismatch",
                "hash_type": hash_type,
                "original": original_hash,
                "replay": replay_hash
            })

    return validation
```

#### Stage-by-Stage Validation
```python
def validate_stage_results(original_stage: dict, replay_stage: dict) -> dict:
    """Validate individual stage results"""

    validation = {
        "matched": True,
        "differences": [],
        "confidence": 1.0
    }

    # Compare key outputs
    key_fields = ["result", "metrics", "artifacts"]

    for field in key_fields:
        if field in original_stage and field in replay_stage:
            original_value = original_stage[field]
            replay_value = replay_stage[field]

            if not deep_compare(original_value, replay_value):
                validation["matched"] = False
                validation["differences"].append({
                    "field": field,
                    "original_type": type(original_value).__name__,
                    "replay_type": type(replay_value).__name__,
                    "match_type": "value_mismatch"
                })
                validation["confidence"] *= 0.8  # Reduce confidence

    return validation
```

## Override Mechanisms

### Version Override
```python
def apply_version_override(replay_env: dict, target_version: str) -> dict:
    """Apply version compatibility override"""

    override_env = replay_env.copy()

    # Log override application
    logger.warning(f"Applying version override: {replay_env['python_version']} -> {target_version}")

    # Update environment
    override_env["python_version"] = target_version
    override_env["overrides_applied"] = override_env.get("overrides_applied", [])
    override_env["overrides_applied"].append({
        "type": "version_override",
        "original_version": replay_env["python_version"],
        "override_version": target_version,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "justification": "User-approved version compatibility override"
    })

    return override_env
```

### Dependency Override
```python
def apply_dependency_override(replay_env: dict) -> dict:
    """Apply dependency compatibility override"""

    override_env = replay_env.copy()

    current_hash = get_current_pip_freeze_hash()

    logger.warning(f"Applying dependency override: {replay_env['pip_freeze_hash']} -> {current_hash}")

    override_env["pip_freeze_hash"] = current_hash
    override_env["overrides_applied"] = override_env.get("overrides_applied", [])
    override_env["overrides_applied"].append({
        "type": "dependency_override",
        "original_hash": replay_env["pip_freeze_hash"],
        "override_hash": current_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "justification": "User-approved dependency compatibility override"
    })

    return override_env
```

## Error Handling & Recovery

### Replay Failure Scenarios
1. **Version Incompatibility**
   ```
   Solution: Apply version override or use compatible environment
   Prevention: Maintain multiple Python version environments
   ```

2. **Dependency Mismatch**
   ```
   Solution: Apply dependency override or recreate original environment
   Prevention: Use containerized environments with exact dependency versions
   ```

3. **Data Corruption**
   ```
   Solution: Restore from backup or use alternative run
   Prevention: Implement redundant storage and integrity checking
   ```

4. **Resource Exhaustion**
   ```
   Solution: Reduce replay scope or use resource-limited environment
   Prevention: Monitor resource usage during replay execution
   ```

### Recovery Procedures
```python
def recover_from_replay_failure(replay_results: dict, failure_type: str) -> dict:
    """Recover from replay failure using appropriate strategy"""

    recovery_strategies = {
        "version_incompatibility": recover_version_incompatibility,
        "dependency_mismatch": recover_dependency_mismatch,
        "data_corruption": recover_data_corruption,
        "resource_exhaustion": recover_resource_exhaustion
    }

    if failure_type in recovery_strategies:
        return recovery_strategies[failure_type](replay_results)
    else:
        return {
            "recovery_status": "failed",
            "error": f"No recovery strategy for failure type: {failure_type}"
        }
```

## Performance Optimization

### Selective Replay
```python
def selective_replay(run_context: dict, stages_to_replay: list) -> dict:
    """Replay only selected stages for faster validation"""

    replay_env = initialize_replay_environment(run_context)

    # Only replay specified stages
    replay_results = {
        "replay_id": replay_env["run_id"],
        "selective_replay": True,
        "stages_replayed": stages_to_replay,
        "stages": []
    }

    for stage_name in stages_to_replay:
        stage_result = replay_single_stage(run_context, replay_env, stage_name)
        replay_results["stages"].append(stage_result)

    return replay_results
```

### Parallel Execution
```python
def parallel_replay(run_context: dict) -> dict:
    """Execute replay stages in parallel where possible"""

    # Identify parallelizable stages
    parallel_stages = ["personas", "competitors"]  # Can run in parallel
    sequential_stages = ["ingestion", "simulation", "analysis", "decision"]

    # Execute parallel stages concurrently
    with ThreadPoolExecutor(max_workers=2) as executor:
        parallel_futures = [
            executor.submit(replay_single_stage, run_context, stage_name)
            for stage_name in parallel_stages
        ]

    # Wait for parallel completion, then execute sequential
    parallel_results = [future.result() for future in parallel_futures]

    # Execute sequential stages
    sequential_results = []
    for stage_name in sequential_stages:
        result = replay_single_stage(run_context, stage_name)
        sequential_results.append(result)

    return {
        "parallel_results": parallel_results,
        "sequential_results": sequential_results,
        "total_duration": calculate_total_duration(parallel_results + sequential_results)
    }
```

## Monitoring & Alerting

### Replay Metrics
- **Success Rate**: Percentage of successful replays
- **Duration**: Average replay execution time
- **Resource Usage**: CPU, memory, and storage consumption
- **Failure Patterns**: Common failure modes and frequencies

### Alert Conditions
- Replay failure rate > 5%
- Average replay duration > 2x original run
- Version compatibility issues > 10% of attempts
- Override usage > 20% of replays

## Compliance & Audit

### Replay Audit Trail
```json
{
  "replay_id": "RUN-20241201-143052-replay-a1b2c3d4",
  "original_run_id": "RUN-20241201-143052-a1b2c3d4",
  "replay_timestamp": "2024-12-01T15:30:52.123456Z",
  "user_id": "analyst@company.com",
  "overrides_applied": [
    {
      "type": "version_override",
      "justification": "Python 3.12.10 compatibility",
      "approval_reference": "APPROVAL-2024-001"
    }
  ],
  "validation_results": {
    "hash_consistency": true,
    "output_consistency": true,
    "performance_consistency": false
  }
}
```

### Regulatory Compliance
- **Data Privacy**: Ensure PII redaction during replay
- **Audit Trail**: Complete record of all replay activities
- **Access Control**: Role-based permissions for replay operations
- **Retention**: Replay results retained per regulatory requirements

---

**Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Last Updated**: 2024-12-XX

*This replay runbook ensures complete reproducibility and validation of SMVM runs.*
