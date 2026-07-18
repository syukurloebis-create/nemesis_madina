"""
Model Registry
Mengelola versi model AI dan metadata
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
import json
import logging

logger = logging.getLogger(__name__)


class ModelStatus(str, Enum):
    """Status model"""
    DRAFT = "draft"
    TRAINING = "training"
    VALIDATING = "validating"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ModelType(str, Enum):
    """Tipe model"""
    FRAUD_DETECTION = "fraud_detection"
    RISK_PREDICTION = "risk_prediction"
    ANOMALY_DETECTION = "anomaly_detection"
    COLLUSION_DETECTION = "collusion_detection"
    RECOMMENDATION = "recommendation"


@dataclass
class ModelVersion:
    """Model version metadata"""
    id: UUID = field(default_factory=uuid4)
    model_name: str = ""
    model_type: ModelType = ModelType.FRAUD_DETECTION
    version: str = "1.0.0"
    status: ModelStatus = ModelStatus.DRAFT
    description: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    trained_at: Optional[datetime] = None
    validated_at: Optional[datetime] = None
    deployed_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    
    # Performance metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    test_accuracy: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    roc_auc: float = 0.0
    
    # Metadata
    dataset_version: str = ""
    feature_names: List[str] = field(default_factory=list)
    hyperparameters: Dict[str, Any] = field(default_factory=dict)
    training_size: int = 0
    validation_size: int = 0
    
    # Governance
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    validation_report: Optional[str] = None
    drift_monitoring_enabled: bool = True
    last_drift_check: Optional[datetime] = None
    drift_threshold: float = 0.1
    
    # File path
    model_path: str = ""
    metadata_path: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": str(self.id),
            "model_name": self.model_name,
            "model_type": self.model_type.value,
            "version": self.version,
            "status": self.status.value,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "trained_at": self.trained_at.isoformat() if self.trained_at else None,
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
            "deployed_at": self.deployed_at.isoformat() if self.deployed_at else None,
            "deprecated_at": self.deprecated_at.isoformat() if self.deprecated_at else None,
            "metrics": self.metrics,
            "test_accuracy": self.test_accuracy,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1_score,
            "roc_auc": self.roc_auc,
            "dataset_version": self.dataset_version,
            "feature_names": self.feature_names,
            "hyperparameters": self.hyperparameters,
            "training_size": self.training_size,
            "validation_size": self.validation_size,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "validation_report": self.validation_report,
            "drift_monitoring_enabled": self.drift_monitoring_enabled,
            "last_drift_check": self.last_drift_check.isoformat() if self.last_drift_check else None,
            "drift_threshold": self.drift_threshold,
            "model_path": self.model_path,
            "metadata_path": self.metadata_path
        }

    def approve(self, approver: str, validation_report: str) -> None:
        """Approve model for deployment"""
        self.status = ModelStatus.APPROVED
        self.approved_by = approver
        self.approved_at = datetime.now()
        self.validation_report = validation_report
        logger.info(f"Model {self.model_name} v{self.version} approved by {approver}")

    def deploy(self) -> None:
        """Deploy model to production"""
        self.status = ModelStatus.DEPLOYED
        self.deployed_at = datetime.now()
        logger.info(f"Model {self.model_name} v{self.version} deployed")

    def deprecate(self) -> None:
        """Deprecate model"""
        self.status = ModelStatus.DEPRECATED
        self.deprecated_at = datetime.now()
        logger.info(f"Model {self.model_name} v{self.version} deprecated")

    def archive(self) -> None:
        """Archive model"""
        self.status = ModelStatus.ARCHIVED
        logger.info(f"Model {self.model_name} v{self.version} archived")


class ModelRegistry:
    """
    Model Registry
    Central registry for all AI models
    """

    def __init__(self):
        self.models: Dict[str, ModelVersion] = {}
        self.current_models: Dict[ModelType, str] = {}

    def register_model(self, model: ModelVersion) -> str:
        """Register new model version"""
        model_id = str(model.id)
        self.models[model_id] = model
        logger.info(f"Model registered: {model.model_name} v{model.version} ({model_id})")
        return model_id

    def get_model(self, model_id: str) -> Optional[ModelVersion]:
        """Get model by ID"""
        return self.models.get(model_id)

    def get_model_by_name_and_version(self, name: str, version: str) -> Optional[ModelVersion]:
        """Get model by name and version"""
        for model in self.models.values():
            if model.model_name == name and model.version == version:
                return model
        return None

    def get_models_by_type(self, model_type: ModelType) -> List[ModelVersion]:
        """Get all models by type"""
        return [m for m in self.models.values() if m.model_type == model_type]

    def get_models_by_status(self, status: ModelStatus) -> List[ModelVersion]:
        """Get models by status"""
        return [m for m in self.models.values() if m.status == status]

    def get_deployed_models(self) -> List[ModelVersion]:
        """Get all deployed models"""
        return self.get_models_by_status(ModelStatus.DEPLOYED)

    def get_current_model(self, model_type: ModelType) -> Optional[ModelVersion]:
        """Get current deployed model for a type"""
        model_id = self.current_models.get(model_type)
        if model_id:
            return self.models.get(model_id)
        return None

    def set_current_model(self, model_type: ModelType, model_id: str) -> bool:
        """Set current model for a type"""
        if model_id not in self.models:
            return False
        model = self.models[model_id]
        if model.status != ModelStatus.DEPLOYED:
            return False
        self.current_models[model_type] = model_id
        logger.info(f"Current model set: {model_type.value} -> {model.model_name} v{model.version}")
        return True

    def get_version_history(self, model_name: str) -> List[ModelVersion]:
        """Get version history for a model"""
        versions = [m for m in self.models.values() if m.model_name == model_name]
        return sorted(versions, key=lambda x: x.created_at, reverse=True)

    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        total = len(self.models)
        by_type = {}
        by_status = {}
        deployed = len(self.get_deployed_models())

        for model in self.models.values():
            by_type[model.model_type.value] = by_type.get(model.model_type.value, 0) + 1
            by_status[model.status.value] = by_status.get(model.status.value, 0) + 1

        return {
            "total_models": total,
            "deployed_models": deployed,
            "by_type": by_type,
            "by_status": by_status,
            "current_models": {k.value: v for k, v in self.current_models.items()}
        }

    def generate_registry_report(self) -> str:
        """Generate registry report"""
        stats = self.get_model_stats()
        report = f"""
MODEL REGISTRY REPORT
=====================
Generated: {datetime.now().isoformat()}

SUMMARY:
- Total Models: {stats['total_models']}
- Deployed: {stats['deployed_models']}

CURRENT MODELS:
"""
        for model_type, model_id in self.current_models.items():
            model = self.models.get(model_id)
            if model:
                report += f"""
  {model_type.value}:
    - Model: {model.model_name}
    - Version: {model.version}
    - Accuracy: {model.test_accuracy:.2%}
    - F1: {model.f1_score:.2%}
"""

        return report


# Singleton instance
model_registry = ModelRegistry()