# scripts/architecture/logging/logger.py
import json
import logging
from datetime import datetime
from typing import Any, Dict, Optional

class NemesisLogger:
    """Unified logger for all architecture components"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        self.logger = logging.getLogger('nemesis')
        self.logger.setLevel(logging.INFO)
        
        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter('%(message)s'))
        self.logger.addHandler(handler)
    
    def _log(self, level: str, message: str, **kwargs):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message,
            **kwargs
        }
        getattr(self.logger, level.lower())(json.dumps(log_entry))
    
    def debug(self, message: str, **kwargs):
        self._log('DEBUG', message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log('INFO', message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log('WARNING', message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log('ERROR', message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log('CRITICAL', message, **kwargs)
