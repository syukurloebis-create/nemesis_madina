"""
Startup Validator - Validate environment and dependencies before starting
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Tuple
from datetime import datetime


class StartupValidator:
    """Validate system before starting"""
    
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def validate_environment(self) -> bool:
        """Validate environment variables"""
        print("\n[1/5] Validating environment...")
        
        required_vars = [
            "SECRET_KEY"
        ]
        
        optional_vars = [
            "DATABASE_URL",
            "REDIS_URL",
            "NATS_URL",
            "LOG_LEVEL",
            "METRICS_ENABLED"
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                # Set default for development
                if var == "SECRET_KEY":
                    os.environ[var] = "dev-secret-key-change-in-production"
                    print(f"  ⚠️ {var} not set, using default for development")
                else:
                    self.errors.append(f"Missing required environment variable: {var}")
            else:
                print(f"  ✅ {var} = {os.getenv(var)[:20]}...")
        
        for var in optional_vars:
            if not os.getenv(var):
                self.warnings.append(f"Missing optional environment variable: {var}")
                print(f"  ⚠️ {var} not set (using default)")
            else:
                print(f"  ✅ {var} = {os.getenv(var)}")
        
        return len(self.errors) == 0
    
    async def validate_database_async(self) -> bool:
        """Validate database connection asynchronously"""
        print("\n[2/5] Validating database...")
        
        if not os.getenv("DATABASE_URL"):
            self.warnings.append("DATABASE_URL not set, skipping database validation")
            print("  ⚠️ DATABASE_URL not set, skipping database validation")
            return True
        
        try:
            import asyncpg
            
            async def check_db():
                try:
                    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))
                    await conn.execute("SELECT 1")
                    await conn.close()
                    return True, None
                except Exception as e:
                    return False, str(e)
            
            success, error = await check_db()
            if success:
                print("  ✅ Database connection successful")
                return True
            else:
                self.warnings.append(f"Database connection failed: {error}")
                print(f"  ⚠️ Database connection failed: {error[:50]}")
                return True  # Non-critical for development
        except ImportError:
            self.warnings.append("asyncpg not installed, skipping database validation")
            print("  ⚠️ asyncpg not installed")
            return True
    
    async def validate_redis_async(self) -> bool:
        """Validate Redis connection asynchronously"""
        print("\n[3/5] Validating Redis...")
        
        if not os.getenv("REDIS_URL"):
            print("  ⚠️ REDIS_URL not set, skipping Redis validation")
            return True
        
        try:
            import redis
            import asyncio
            
            # Use threads for redis (sync library)
            loop = asyncio.get_event_loop()
            r = redis.from_url(os.getenv("REDIS_URL"))
            
            def ping_redis():
                return r.ping()
            
            try:
                result = await loop.run_in_executor(None, ping_redis)
                if result:
                    print("  ✅ Redis connection successful")
                    return True
                else:
                    self.warnings.append("Redis connection failed")
                    return True
            except Exception as e:
                self.warnings.append(f"Redis connection failed: {e}")
                return True
        except ImportError:
            print("  ⚠️ redis not installed")
            return True
    
    def validate_disk_space(self) -> bool:
        """Validate available disk space"""
        print("\n[4/5] Validating disk space...")
        
        try:
            import shutil
            usage = shutil.disk_usage("/")
            free_gb = usage.free / (1024**3)
            
            if free_gb < 1:
                self.errors.append(f"Low disk space: {free_gb:.1f}GB free (min 1GB)")
                return False
            elif free_gb < 5:
                self.warnings.append(f"Low disk space: {free_gb:.1f}GB free")
                print(f"  ⚠️ {free_gb:.1f}GB free")
            else:
                print(f"  ✅ {free_gb:.1f}GB free")
            return True
        except Exception as e:
            self.warnings.append(f"Disk space check failed: {e}")
            return True
    
    def validate_modules(self) -> bool:
        """Validate critical modules can be imported"""
        print("\n[5/5] Validating modules...")
        
        critical_modules = [
            ("fastapi", "FastAPI"),
            ("evidence", "EvidenceRegistry"),
            ("core.events", "EventBus"),
            ("websocket", "ConnectionManager"),
            ("graph", "GraphBuilder")
        ]
        
        for module_name, class_name in critical_modules:
            try:
                if "." in module_name:
                    module = __import__(module_name, fromlist=[class_name])
                    getattr(module, class_name)
                else:
                    __import__(module_name)
                print(f"  ✅ {module_name}")
            except ImportError as e:
                self.errors.append(f"Failed to import {module_name}: {e}")
                print(f"  ❌ {module_name}: {e}")
        
        return len(self.errors) == 0
    
    async def run_all_async(self) -> Tuple[bool, List[str], List[str]]:
        """Run all validations asynchronously"""
        print("\n" + "="*60)
        print("STARTUP VALIDATION")
        print("="*60)
        
        env_ok = self.validate_environment()
        db_ok = await self.validate_database_async()
        redis_ok = await self.validate_redis_async()
        disk_ok = self.validate_disk_space()
        modules_ok = self.validate_modules()
        
        all_ok = env_ok and modules_ok
        
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        if all_ok:
            print("✅ All critical checks passed")
        else:
            print("❌ Critical checks failed")
        
        if self.warnings:
            print(f"\n⚠️ Warnings ({len(self.warnings)}):")
            for w in self.warnings[:5]:
                print(f"  - {w}")
        
        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  - {e}")
        
        return all_ok, self.errors, self.warnings
    
    def run_all(self) -> Tuple[bool, List[str], List[str]]:
        """Legacy sync method - use run_all_async instead"""
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            # Already in async context
            return asyncio.create_task(self.run_all_async())
        except RuntimeError:
            # No running loop, create one
            return asyncio.run(self.run_all_async())


# Global validator
startup_validator = StartupValidator()


async def validate_startup() -> bool:
    """Validate system before startup"""
    result, _, _ = await startup_validator.run_all_async()
    return result
