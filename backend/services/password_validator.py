"""
Password Validation Service
"""
import re
from typing import Tuple, Optional, List
from backend.config.auth import auth_settings

class PasswordValidator:
    """Password validation with security best practices"""
    
    COMMON_PASSWORDS = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "111111", "iloveyou", "master", "sunshine",
        "ashley", "bailey", "passw0rd", "shadow", "123123",
        "654321", "superman", "qazwsx", "michael", "football"
    ]
    
    @classmethod
    def validate(cls, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against security policy
        Returns: (is_valid, error_message)
        """
        # Check minimum length
        if len(password) < auth_settings.PASSWORD_MIN_LENGTH:
            return False, f"Password must be at least {auth_settings.PASSWORD_MIN_LENGTH} characters"
        
        # Check maximum length (bcrypt limit)
        if len(password) > 72:
            return False, "Password must be less than 72 characters"
        
        # Check for uppercase
        if auth_settings.PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for lowercase
        if auth_settings.PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for digit
        if auth_settings.PASSWORD_REQUIRE_DIGIT and not re.search(r'\d', password):
            return False, "Password must contain at least one number"
        
        # Check for special character
        if auth_settings.PASSWORD_REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', password):
            return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{};:,.<>?)"
        
        # Check against common passwords
        if password.lower() in cls.COMMON_PASSWORDS:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, None
    
    @classmethod
    def get_password_strength(cls, password: str) -> str:
        """Get password strength indicator"""
        score = 0
        
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[!@#$%^&*()_+\-=\[\]{};:,.<>?]', password):
            score += 1
        
        if score <= 2:
            return "weak"
        elif score <= 4:
            return "medium"
        else:
            return "strong"