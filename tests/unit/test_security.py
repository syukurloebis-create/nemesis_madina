"""
Unit tests for security module
"""

import pytest
from backend.security.auth import auth_handler
from backend.security.models import User, Role, Permission


class TestAuthHandler:
    """Test authentication handler"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "test123"
        hashed = auth_handler.hash_password(password)
        assert hashed != password
        assert len(hashed) == 64  # SHA-256 produces 64 hex chars
    
    def test_verify_password(self):
        """Test password verification"""
        password = "test123"
        hashed = auth_handler.hash_password(password)
        assert auth_handler.verify_password(password, hashed) is True
        assert auth_handler.verify_password("wrong", hashed) is False
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        token = auth_handler.create_access_token("user1", "testuser", "admin")
        assert token is not None
        assert len(token) > 0
    
    def test_decode_token(self):
        """Test JWT token decoding"""
        token = auth_handler.create_access_token("user1", "testuser", "admin")
        payload = auth_handler.decode_token(token)
        assert payload["sub"] == "user1"
        assert payload["username"] == "testuser"
        assert payload["role"] == "admin"
    
    def test_authenticate_user(self):
        """Test user authentication"""
        user = auth_handler.authenticate_user("admin", "admin")
        assert user is not None
        assert user.username == "admin"
        
        # Wrong password
        user = auth_handler.authenticate_user("admin", "wrong")
        assert user is None


class TestRBAC:
    """Test role-based access control"""
    
    def test_admin_has_all_permissions(self):
        """Admin should have all permissions"""
        admin = auth_handler.get_user_by_username("admin")
        
        # Admin should have evidence read permission
        assert admin.has_permission(Permission.EVIDENCE_READ) is True
        # Admin should have admin system permission
        assert admin.has_permission(Permission.ADMIN_SYSTEM) is True
    
    def test_viewer_has_limited_permissions(self):
        """Viewer should have limited permissions"""
        viewer = auth_handler.get_user_by_username("viewer")
        
        assert viewer.has_permission(Permission.EVIDENCE_READ) is True
        assert viewer.has_permission(Permission.GRAPH_VIEW) is True
        assert viewer.has_permission(Permission.ADMIN_SYSTEM) is False
    
    def test_analyst_permissions(self):
        """Analyst should have appropriate permissions"""
        analyst = auth_handler.get_user_by_username("analyst")
        
        assert analyst.has_permission(Permission.EVIDENCE_READ) is True
        assert analyst.has_permission(Permission.EVIDENCE_WRITE) is True
        assert analyst.has_permission(Permission.ML_PREDICT) is True
        assert analyst.has_permission(Permission.ADMIN_SYSTEM) is False


class TestAPIKeys:
    """Test API key functionality"""
    
    def test_create_api_key(self):
        """Test API key creation"""
        user = auth_handler.get_user_by_username("admin")
        api_key = auth_handler.create_api_key(user.id, "Test Key")
        
        assert api_key is not None
        assert api_key.startswith("nemesis_")
    
    def test_verify_api_key(self):
        """Test API key verification"""
        user = auth_handler.get_user_by_username("admin")
        api_key = auth_handler.create_api_key(user.id, "Test Key")
        
        user_id = auth_handler.verify_api_key(api_key)
        assert user_id == user.id
    
    def test_revoke_api_key(self):
        """Test API key revocation"""
        user = auth_handler.get_user_by_username("admin")
        api_key = auth_handler.create_api_key(user.id, "Test Key")
        
        # Verify it works
        assert auth_handler.verify_api_key(api_key) is not None
        
        # Revoke it
        assert auth_handler.revoke_api_key(api_key) is True
        
        # Verify it no longer works
        assert auth_handler.verify_api_key(api_key) is None
