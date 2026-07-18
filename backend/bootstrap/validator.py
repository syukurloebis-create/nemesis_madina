"""
Container Validator — Memverifikasi container setelah startup.
"""

import logging
from typing import List, Tuple, Any
from backend.core.container import ApplicationContainer

logger = logging.getLogger(__name__)


class ContainerValidator:
    """Validate ApplicationContainer after construction."""
    
    @staticmethod
    def validate(container: ApplicationContainer) -> None:
        """Validate all critical dependencies exist."""
        errors: List[str] = []
        
        required: List[Tuple[str, Any]] = [
            ("Infrastructure container", container.infrastructure),
            ("UnitOfWorkFactory", container.infrastructure.uow_factory),
            ("Calculator container", container.calculators),
            ("Fraud calculator", container.calculators.fraud),
            ("Mapper container", container.mappers),
            ("Domain services container", container.domain_services),
            ("Collector container", container.collectors),
            ("Collector registry", container.collectors.registry),
            ("Service container", container.services),
            ("Dashboard service", container.services.dashboard),
            ("Health container", container.health),
        ]
        
        for name, value in required:
            if value is None:
                errors.append(f"{name} is None")
        
        if errors:
            logger.error("Container validation failed: %s", errors)
            raise RuntimeError(f"Container validation failed: {errors}")
        
        logger.info("Container validation passed: %d collectors registered", len(container.collectors.registry))