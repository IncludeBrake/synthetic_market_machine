# SMVM Ingestion Service
# Handles data ingestion and normalization from external sources

"""
SMVM Ingestion Service

Purpose: Ingest and normalize external data sources for market validation
- Adapter pattern for multiple data sources (APIs, files, databases)
- Schema validation and normalization to internal formats
- Data quality assessment and cleansing
- Integration with TractionBuild data pipelines

Data Zone: GREEN (public data) → AMBER (validated data)
Retention: 90 days for raw data, 365 days for normalized data
"""

from typing import Dict, List, Optional, Protocol
import logging
from datetime import datetime
from pathlib import Path

# Service metadata
SERVICE_NAME = "ingestion"
SERVICE_VERSION = "1.0.0"
PYTHON_VERSION = "3.12.10"  # Must match SMVM requirements
DATA_ZONE = "GREEN"  # Input data zone
RETENTION_DAYS = 90

logger = logging.getLogger(__name__)


class DataAdapter(Protocol):
    """Protocol for data source adapters"""

    def connect(self) -> bool:
        """Establish connection to data source"""
        ...

    def fetch_data(self, query: Dict) -> List[Dict]:
        """Fetch data from source"""
        ...

    def validate_schema(self, data: List[Dict]) -> bool:
        """Validate incoming data schema"""
        ...

    def disconnect(self) -> None:
        """Clean up connections"""
        ...


class NormalizationContract:
    """
    Normalization contract for ingested data

    Ensures consistent data format across all sources:
    - Standard field naming conventions
    - Data type normalization
    - Missing value handling
    - Quality validation
    """

    @staticmethod
    def normalize_record(record: Dict) -> Dict:
        """Normalize a single data record"""
        normalized = {}

        # Required field mappings
        field_mappings = {
            # Standard SMVM field names
            "id": ["id", "ID", "identifier", "uuid"],
            "name": ["name", "Name", "title", "label"],
            "description": ["description", "desc", "summary", "details"],
            "created_at": ["created_at", "timestamp", "date", "created"],
            "updated_at": ["updated_at", "modified", "last_modified"],
            "source": ["source", "provider", "origin"],
            "confidence": ["confidence", "certainty", "quality_score"]
        }

        # Apply field mappings
        for standard_field, source_fields in field_mappings.items():
            for source_field in source_fields:
                if source_field in record:
                    normalized[standard_field] = record[source_field]
                    break

        # Add metadata
        normalized["_metadata"] = {
            "normalized_at": datetime.utcnow().isoformat() + "Z",
            "normalization_version": "1.0.0",
            "original_fields": list(record.keys()),
            "data_quality_score": NormalizationContract._calculate_quality_score(record)
        }

        return normalized

    @staticmethod
    def _calculate_quality_score(record: Dict) -> float:
        """Calculate data quality score (0.0-1.0)"""
        score = 0.0
        total_checks = 0

        # Completeness check
        required_fields = ["id", "name", "description"]
        for field in required_fields:
            total_checks += 1
            if field in record and record[field]:
                score += 0.3

        # Type consistency check
        if "id" in record:
            total_checks += 1
            if isinstance(record["id"], (str, int)):
                score += 0.2

        # Timeliness check
        if "created_at" in record or "updated_at" in record:
            total_checks += 1
            score += 0.2

        # Source attribution check
        if "source" in record:
            total_checks += 1
            score += 0.3

        return min(1.0, score / max(1, total_checks))


class IngestionService:
    """
    Main ingestion service class

    Handles:
    - Data source management
    - Normalization pipeline
    - Quality validation
    - Error handling and recovery
    """

    def __init__(self, config: Dict):
        self.config = config
        self.adapters: Dict[str, DataAdapter] = {}
        self.logger = logging.getLogger(f"{__name__}.IngestionService")

    def register_adapter(self, name: str, adapter: DataAdapter) -> None:
        """Register a data source adapter"""
        self.adapters[name] = adapter
        self.logger.info(f"Registered adapter: {name}")

    def ingest_data(self, source_name: str, query: Dict) -> Dict:
        """
        Ingest data from specified source

        Args:
            source_name: Name of registered adapter
            query: Query parameters for data retrieval

        Returns:
            Dict containing normalized data and metadata
        """
        if source_name not in self.adapters:
            raise ValueError(f"Unknown adapter: {source_name}")

        adapter = self.adapters[source_name]

        # Establish connection
        if not adapter.connect():
            raise ConnectionError(f"Failed to connect to {source_name}")

        try:
            # Fetch raw data
            raw_data = adapter.fetch_data(query)

            # Validate incoming schema
            if not adapter.validate_schema(raw_data):
                raise ValueError(f"Schema validation failed for {source_name}")

            # Normalize data
            normalized_data = [NormalizationContract.normalize_record(record)
                             for record in raw_data]

            # Create result metadata
            result = {
                "data": normalized_data,
                "metadata": {
                    "source": source_name,
                    "record_count": len(normalized_data),
                    "ingestion_timestamp": datetime.utcnow().isoformat() + "Z",
                    "service_version": SERVICE_VERSION,
                    "python_version": PYTHON_VERSION,
                    "data_quality_summary": self._calculate_quality_summary(normalized_data)
                }
            }

            self.logger.info(f"Successfully ingested {len(normalized_data)} records from {source_name}")
            return result

        finally:
            adapter.disconnect()

    def _calculate_quality_summary(self, data: List[Dict]) -> Dict:
        """Calculate quality metrics for ingested data"""
        if not data:
            return {"average_quality_score": 0.0, "quality_distribution": {}}

        quality_scores = [record["_metadata"]["data_quality_score"] for record in data]

        return {
            "average_quality_score": sum(quality_scores) / len(quality_scores),
            "quality_distribution": {
                "high": sum(1 for s in quality_scores if s >= 0.8),
                "medium": sum(1 for s in quality_scores if 0.5 <= s < 0.8),
                "low": sum(1 for s in quality_scores if s < 0.5)
            },
            "total_records": len(data)
        }


# Service interface documentation
SERVICE_INTERFACE = {
    "service": SERVICE_NAME,
    "version": SERVICE_VERSION,
    "description": "Data ingestion and normalization service for external market data sources",
    "endpoints": {
        "ingest": {
            "method": "POST",
            "path": "/api/v1/ingestion/ingest",
            "input": {
                "source_name": "string (registered adapter name)",
                "query": "object (data retrieval parameters)"
            },
            "output": {
                "data": "array (normalized records)",
                "metadata": "object (ingestion metadata)"
            },
            "token_budget": 1000,
            "timeout_seconds": 300
        },
        "validate": {
            "method": "POST",
            "path": "/api/v1/ingestion/validate",
            "input": {
                "data": "array (raw data records)"
            },
            "output": {
                "valid": "boolean",
                "errors": "array (validation error messages)",
                "quality_score": "number"
            },
            "token_budget": 500,
            "timeout_seconds": 60
        }
    },
    "failure_modes": {
        "connection_failed": "Cannot connect to data source",
        "schema_validation_failed": "Incoming data doesn't match expected schema",
        "normalization_error": "Data normalization failed",
        "quality_threshold_not_met": "Data quality below acceptable threshold",
        "rate_limit_exceeded": "Data source rate limit exceeded"
    },
    "grounding_sources": [
        "External API documentation",
        "Data source schema specifications",
        "Industry data standards (ISO 20022, FIX protocol)",
        "Internal data quality benchmarks"
    ],
    "redaction_points": [
        "API keys and credentials in logs",
        "PII data in error messages",
        "Sensitive business data in debug output"
    ],
    "observability": {
        "spans": ["data_fetch", "schema_validation", "normalization", "quality_check"],
        "metrics": ["records_processed", "quality_score_avg", "error_rate"],
        "logs": ["source_connection", "data_validation", "normalization_progress"]
    }
}
