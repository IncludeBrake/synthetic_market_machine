# SMVM ID Strategy and Conventions

This document defines the ID strategy, hashing conventions, and naming standards for the Synthetic Market Validation Module (SMVM) to ensure traceable, replayable artifacts.

## Core ID Types

### Run ID (`run_id`)
**Purpose**: Uniquely identifies an execution run or workflow
**Format**: `RUN-{timestamp}-{random_suffix}`
**Components**:
- `RUN`: Fixed prefix
- `timestamp`: ISO 8601 format `YYYYMMDD-HHMMSS` (UTC)
- `random_suffix`: 8-character hexadecimal string
**Example**: `RUN-20241201-143052-a1b2c3d4`
**Length**: 32 characters
**Scope**: Global across all SMVM operations

### Span ID (`span_id`)
**Purpose**: Identifies a specific operation or step within a run
**Format**: `{run_id}-{sequence}-{operation}`
**Components**:
- `run_id`: Parent run identifier
- `sequence`: Zero-padded 4-digit sequence number (0001, 0002, etc.)
- `operation`: 3-letter operation code (VAL=validation, SIM=simulation, DEC=decision, etc.)
**Example**: `RUN-20241201-143052-a1b2c3d4-0001-VAL`
**Length**: 40 characters
**Scope**: Local to parent run

### Artifact ID (`artifact_id`)
**Purpose**: Identifies specific data artifacts or outputs
**Format**: `{span_id}-{artifact_type}-{hash_suffix}`
**Components**:
- `span_id`: Parent span identifier
- `artifact_type`: 3-letter artifact type (INP=input, OUT=output, CFG=config, etc.)
- `hash_suffix`: 8-character hash of artifact content
**Example**: `RUN-20241201-143052-a1b2c3d4-0001-VAL-OUT-f5a2b3c4`
**Length**: 49 characters

## Hash Formats

### Content Hash (`content_hash`)
**Algorithm**: SHA-256
**Input**: Canonical JSON representation of data
**Output Format**: Hexadecimal string (64 characters)
**Purpose**: Verify data integrity and detect changes
**Usage**: Stamp all artifacts and validate during replay

### Composite Hash (`composite_hash`)
**Algorithm**: SHA-256
**Input**: Concatenated string of multiple hashes
**Components**:
- Content hash
- Python version
- Dependencies hash
- Timestamp
**Format**: SHA-256 hex (64 characters)
**Purpose**: Ensure reproducible executions

### Python Environment Hash (`python_env_hash`)
**Algorithm**: SHA-256
**Input**: Sorted list of installed packages with versions
**Source**: `pip freeze` output (sorted, normalized)
**Format**: SHA-256 hex (64 characters)
**Purpose**: Track Python environment for reproducibility

## Filename Conventions

### Schema Files
**Pattern**: `{schema_name}.{direction}.{format}`
**Components**:
- `schema_name`: Descriptive name (personas, competitors, offers, etc.)
- `direction`: input/output/config/result
- `format`: json (only JSON supported)
**Examples**:
- `idea.input.json`
- `personas.output.json`
- `simulation.config.json`
- `decision.output.json`

### Artifact Files
**Pattern**: `{artifact_id}.{extension}`
**Components**:
- `artifact_id`: Full artifact identifier
- `extension`: json, yaml, csv, etc.
**Examples**:
- `RUN-20241201-143052-a1b2c3d4-0001-VAL-OUT-f5a2b3c4.json`
- `RUN-20241201-143052-a1b2c3d4-0002-SIM-CFG-a2b3c4d5.yaml`

### Log Files
**Pattern**: `{run_id}.{component}.{timestamp}.{extension}`
**Components**:
- `run_id`: Parent run identifier
- `component`: Component name (api, validation, simulation, etc.)
- `timestamp`: ISO 8601 timestamp
- `extension`: log
**Example**: `RUN-20241201-143052-a1b2c3d4.api.2024-12-01T14:30:52Z.log`

### Test Fixture Files
**Pattern**: `fixture.{schema_name}.{scenario}.{extension}`
**Components**:
- `fixture`: Fixed prefix
- `schema_name`: Schema name
- `scenario`: Test scenario (valid, invalid, edge_case, etc.)
- `extension`: json
**Examples**:
- `fixture.idea.valid.json`
- `fixture.personas.edge_case.json`
- `fixture.simulation.invalid.json`

## Python Version Stamping

### Version Format
**Format**: `{major}.{minor}.{patch}[-{suffix}]`
**Examples**:
- `3.12.10` (production)
- `3.11.13` (fallback)
- `3.12.0-alpha.1` (development)

### Version Validation Rules
- **Primary**: Must be `3.12.x` (x ≥ 0)
- **Fallback**: Must be exactly `3.11.13`
- **Blocked**: Any version ≥ `3.13.0`
- **Stamping**: Include in all artifacts and logs

### Version Detection
```python
import sys
python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
# Validate against allowed versions
assert python_version.startswith("3.12.") or python_version == "3.11.13"
assert not python_version.startswith("3.13.")
```

## Timestamp Conventions

### Primary Timestamp Format
**Format**: ISO 8601 with timezone
**Pattern**: `YYYY-MM-DDTHH:MM:SSZ` (UTC)
**Example**: `2024-12-01T14:30:52Z`
**Purpose**: All system timestamps

### Compact Timestamp Format
**Format**: Compact for IDs and filenames
**Pattern**: `YYYYMMDD-HHMMSS`
**Example**: `20241201-143052`
**Purpose**: ID components and filenames

### Unix Timestamp (Secondary)
**Format**: Seconds since Unix epoch
**Pattern**: Integer (10 digits)
**Example**: `1733063452`
**Purpose**: Performance metrics and internal calculations

## Hash Calculation Examples

### Content Hash
```python
import hashlib
import json

def calculate_content_hash(data: dict) -> str:
    # Canonical JSON for consistent hashing
    canonical_json = json.dumps(data, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(canonical_json.encode('utf-8')).hexdigest()

# Example
data = {"name": "test", "value": 123}
content_hash = calculate_content_hash(data)  # "a1b2c3d4..."
```

### Composite Hash
```python
def calculate_composite_hash(content_hash: str, python_version: str, deps_hash: str, timestamp: str) -> str:
    composite_input = f"{content_hash}|{python_version}|{deps_hash}|{timestamp}"
    return hashlib.sha256(composite_input.encode('utf-8')).hexdigest()

# Example
composite_hash = calculate_composite_hash(
    content_hash="a1b2c3d4...",
    python_version="3.12.10",
    deps_hash="f5a2b3c4...",
    timestamp="2024-12-01T14:30:52Z"
)
```

### Python Environment Hash
```python
import subprocess
import hashlib

def calculate_python_env_hash() -> str:
    # Get pip freeze output
    result = subprocess.run(['pip', 'freeze'], capture_output=True, text=True)
    packages = sorted(result.stdout.strip().split('\n'))
    env_string = '\n'.join(packages)
    return hashlib.sha256(env_string.encode('utf-8')).hexdigest()

# Example
env_hash = calculate_python_env_hash()  # "f5a2b3c4..."
```

## Artifact Metadata Structure

### Standard Metadata Block
```json
{
  "metadata": {
    "run_id": "RUN-20241201-143052-a1b2c3d4",
    "span_id": "RUN-20241201-143052-a1b2c3d4-0001-VAL",
    "artifact_id": "RUN-20241201-143052-a1b2c3d4-0001-VAL-OUT-f5a2b3c4",
    "timestamp": "2024-12-01T14:30:52Z",
    "python_version": "3.12.10",
    "python_env_hash": "f5a2b3c4e5d6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "content_hash": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2",
    "composite_hash": "b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3",
    "schema_version": "1.0",
    "data_zone": "AMBER",
    "retention_days": 365
  }
}
```

### Validation Rules
- **Required Fields**: All metadata fields must be present
- **Format Validation**: All IDs must match specified patterns
- **Hash Verification**: Content hash must match actual content
- **Version Validation**: Python version must be allowed
- **Timestamp Validation**: Must be valid ISO 8601 format

## Directory Structure

```
contracts/
├── ids.md                           # This document
├── schemas/
│   ├── idea.input.json
│   ├── personas.output.json
│   ├── competitors.output.json
│   ├── offers.output.json
│   ├── simulation.config.json
│   ├── simulation.result.json
│   └── decision.output.json
├── fixtures/
│   ├── fixture.idea.valid.json
│   ├── fixture.personas.valid.json
│   ├── fixture.competitors.valid.json
│   ├── fixture.offers.valid.json
│   ├── fixture.simulation.valid.json
│   └── fixture.decision.valid.json
└── checklists/
    └── VALIDATION.md
```

## Implementation Guidelines

### ID Generation
- Use cryptographically secure random number generation
- Ensure global uniqueness across distributed systems
- Include timestamp for debugging and ordering
- Validate format compliance before use

### Hash Calculation
- Always use canonical JSON for content hashing
- Sort keys to ensure consistent ordering
- Include all relevant metadata in composite hashes
- Store hashes separately from content for integrity checks

### Naming Conventions
- Use consistent case (lowercase with hyphens)
- Include version numbers in schema names
- Use descriptive names that indicate purpose
- Keep names under 255 characters for filesystem compatibility

### Version Management
- Stamp all artifacts with Python version
- Validate version compatibility before processing
- Include version in hash calculations for reproducibility
- Log version mismatches as warnings

---

**Document Version**: 1.0
**Effective Date**: 2024-12-XX
**Review Date**: 2025-06-XX
**Author**: SMVM Development Team
