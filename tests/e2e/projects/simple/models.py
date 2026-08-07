# scripts/tests/e2e/projects/simple/models.py
"""
Simple SQLAlchemy project for E2E testing.
"""

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


# Create engine for testing
engine = create_engine("sqlite:///:memory:")


def create_schema():
    """Create schema for testing."""
    Base.metadata.create_all(engine)


def create_sample_data():
    """Create sample data for testing."""
    with Session(engine) as session:
        user = User(name="Test User", email="test@example.com")
        session.add(user)
        session.commit()
        
        order = Order(user_id=user.id, amount=100)
        session.add(order)
        session.commit()