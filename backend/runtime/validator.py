"""
Runtime Validator
Validates modules and classes at startup
"""
import sys
import importlib
from typing import Dict, Any, List, Tuple
from datetime import datetime

class StartupValidator:
    """Validate modules and classes at startup"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.results = {}
    
    def validate_module(self, module_name: str, class_names: List[str] = None) -> Tuple[bool, str]:
        """
        Validate that a module exists and optionally has certain classes
        """
        try:
            # ✅ FIX: Jika module_name adalah 'database', gunakan 'backend.database'
            actual_module_name = module_name
            if module_name == "database":
                actual_module_name = "backend.database"
            
            module = __import__(actual_module_name, fromlist=class_names or [])
            
            if class_names:
                for class_name in class_names:
                    if not hasattr(module, class_name):
                        return False, f"Class {class_name} not found in {module_name}"
            
            return True, "OK"
        except ImportError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    def validate_class(self, module_name: str, class_name: str) -> Tuple[bool, str]:
        """
        Validate that a class exists in a module
        """
        try:
            # ✅ FIX: Jika module_name adalah 'database', gunakan 'backend.database'
            actual_module_name = module_name
            if module_name == "database":
                actual_module_name = "backend.database"
            
            module = __import__(actual_module_name, fromlist=[class_name])
            if not hasattr(module, class_name):
                return False, f"Class {class_name} not found in {module_name}"
            return True, "OK"
        except ImportError as e:
            return False, str(e)
        except Exception as e:
            return False, str(e)
    
    async def run_all_async(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations asynchronously"""
        errors = []
        warnings = []
        
        # Validate critical modules
        critical_modules = [
            ("backend.database", ["get_db", "async_session_maker"]),
            ("backend.config", ["settings"]),
            ("backend.cases.models", ["Case"]),
            ("backend.services.replay_service", ["ReplayService"]),
        ]
        
        for module_name, class_names in critical_modules:
            try:
                module = importlib.import_module(module_name)
                for class_name in class_names:
                    if not hasattr(module, class_name):
                        errors.append(f"Class {class_name} not found in {module_name}")
            except ImportError as e:
                errors.append(f"Module {module_name} not found: {e}")
        
        # Check database connection
        try:
            from backend.database import check_db_health
            if await check_db_health():
                warnings.append("Database connected")
            else:
                warnings.append("Database not reachable")
        except Exception as e:
            warnings.append(f"Database health check failed: {e}")
        
        self.errors = errors
        self.warnings = warnings
        
        return len(errors) == 0, errors, warnings
    
    def get_summary(self) -> Dict[str, Any]:
        """Get validation summary"""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "timestamp": datetime.now().isoformat(),
            "status": "OK" if len(self.errors) == 0 else "ERROR"
        }

startup_validator = StartupValidator()
