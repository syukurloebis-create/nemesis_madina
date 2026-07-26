"""
Database Configuration
Centralized database connection and session management
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION
# ============================================================

# Get database URL from environment or use default SQLite
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./nemesis.db"
)

# Database options
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create base class for models
Base = declarative_base()

# ============================================================
# CORE FUNCTIONS
# ============================================================

def get_db() -> Session:
    """
    Get database session.
    Use as dependency in FastAPI routes.
    
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database error: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """
    Get a database session directly (for non-FastAPI usage).
    Example: background tasks, scripts
    """
    return SessionLocal()

def init_db():
    """
    Initialize database - create all tables.
    Should be called at application startup.
    """
    try:
        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            logger.info("Creating database tables...")
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Database tables created successfully")
        else:
            logger.info(f"✅ Database already initialized. Tables found: {len(existing_tables)}")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

def drop_db():
    """Drop all tables (for testing only)"""
    if os.getenv("ENV") in ["test", "testing"]:
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ Database tables dropped")

def check_db_connection() -> bool:
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

# ============================================================
# TENANT SUPPORT (OPTIONAL)
# ============================================================

class TenantContext:
    """Context manager for tenant isolation"""
    _tenant_id = None
    
    @classmethod
    def set_tenant(cls, tenant_id: str):
        cls._tenant_id = tenant_id
    
    @classmethod
    def get_tenant(cls):
        return cls._tenant_id
    
    @classmethod
    def clear_tenant(cls):
        cls._tenant_id = None

def get_tenant_id():
    """Get current tenant ID from context"""
    return TenantContext.get_tenant()

# ============================================================
# MIGRATION HELPER (OPTIONAL)
# ============================================================

def run_migrations():
    """
    Run database migrations.
    Can use Alembic or custom migration logic.
    """
    try:
        # Check if Alembic is available
        import alembic.config
        alembic.config.main(argv=['upgrade', 'head'])
        logger.info("✅ Migrations applied successfully")
    except ImportError:
        logger.warning("⚠️ Alembic not installed, skipping migrations")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")

# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    'engine',
    'SessionLocal',
    'Base',
    'get_db',
    'get_db_session',
    'init_db',
    'drop_db',
    'check_db_connection',
    'TenantContext',
    'get_tenant_id',
    'run_migrations'
]

# Log initialization
logger.info(f"✅ Database configured: {DATABASE_URL}")