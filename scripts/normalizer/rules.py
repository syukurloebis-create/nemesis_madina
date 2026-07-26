# scripts/normalizer/rules.py
from typing import List, Optional
from scripts.architecture.models.module import Module, ModuleType

class NormalizationRules:
    """Rules for data validation during normalization"""
    
    @staticmethod
    def validate_module(module: Module) -> List[str]:
        """Validate module data"""
        errors = []
        
        # Check ID format
        if not module.id or not isinstance(module.id, str):
            errors.append("Invalid ID")
        
        # Check name
        if not module.name or len(module.name) < 1:
            errors.append("Invalid name")
        
        # Check path
        if not module.path:
            errors.append("Missing path")
        
        # Check type
        if not isinstance(module.type, ModuleType):
            errors.append("Invalid module type")
        
        # Check language
        if not module.language:
            errors.append("Missing language")
        
        # Check lines
        if module.lines < 0:
            errors.append("Invalid lines count")
        
        # Check complexity
        if module.complexity < 0:
            errors.append("Invalid complexity")
        
        return errors
    
    @staticmethod
    def is_pure_domain(module: Module) -> bool:
        """Check if domain module is pure (no framework imports)"""
        if module.type != ModuleType.DOMAIN:
            return True
        
        forbidden_imports = ['fastapi', 'sqlalchemy', 'django', 'flask', 'requests']
        for import_name in module.imports:
            for forbidden in forbidden_imports:
                if forbidden in import_name:
                    return False
        return True
    
    @staticmethod
    def is_testable(module: Module) -> bool:
        """Check if module has tests"""
        # Check if test file exists
        test_path = module.path.replace('backend/', 'tests/').replace('.py', '_test.py')
        # This is a placeholder - actual check will use inventory
        return True