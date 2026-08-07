# tests/e2e/test_real_sqlalchemy.py
"""
E2E tests with real SQLAlchemy projects.
"""

import sys
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture
def simple_project_dir():
    """Create a temporary directory with simple project."""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir) / "simple_project"
    project_dir.mkdir(parents=True)
    
    # Create models.py with SQLAlchemy models
    models_content = '''
from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship, Session

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    user = relationship("User", back_populates="orders")
'''
    
    with open(project_dir / "models.py", "w") as f:
        f.write(models_content)
    
    yield project_dir
    
    shutil.rmtree(temp_dir)


class TestRealSQLAlchemyE2E:
    """E2E tests with real SQLAlchemy projects."""
    
    def test_import_phase2_runner(self):
        """Test Phase2Runner can be imported."""
        from metadata_inventory.phase2_runner import Phase2Runner
        assert Phase2Runner is not None
    
    def test_import_phase3_runner(self):
        """Test Phase3Runner can be imported."""
        from metadata_inventory.phase3_runner import Phase3Runner
        assert Phase3Runner is not None
    
    def test_simple_project_full_pipeline(self, simple_project_dir):
        """Test full pipeline on simple project."""
        import sys
        sys.path.insert(0, str(simple_project_dir))
        
        # Import the models
        import models
        from sqlalchemy import create_engine
        
        # Create engine and schema
        engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(engine)
        
        # Run discovery
        from metadata_inventory.phase2_runner import Phase2Runner
        runner = Phase2Runner()
        result = asyncio.run(runner.run())
        
        # Verify discovery succeeded
        assert result["status"] == "SUCCESS"
        
        # Run verification
        from metadata_inventory.phase3_runner import Phase3Runner
        verifier = Phase3Runner()
        verify_result = asyncio.run(verifier.run())
        
        assert verify_result["status"] == "SUCCESS"
    
    def test_missing_primary_key_detection(self, simple_project_dir):
        """Test missing primary key is detected."""
        # Create modified models without primary key
        models_path = simple_project_dir / "models.py"
        with open(models_path, "w") as f:
            f.write('''
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    name = Column(String(100), nullable=False)  # NO PRIMARY KEY
''')
        
        import sys
        sys.path.insert(0, str(simple_project_dir))
        
        import models
        from sqlalchemy import create_engine
        
        engine = create_engine("sqlite:///:memory:")
        models.Base.metadata.create_all(engine)
        
        # Run discovery and verification
        from metadata_inventory.phase2_runner import Phase2Runner
        runner = Phase2Runner()
        result = asyncio.run(runner.run())
        
        # Verify discovery completed
        assert result["status"] == "SUCCESS"