"""
Password Validation Service

SEC-6 canonical password policy.

Responsibilities:
- Enforce AuthSettings password length policy.
- Enforce configured character-class requirements.
- Reject known common passwords.
- Reject common weak-password patterns.
- Provide password-strength classification.

This validator is used by authentication schemas and therefore sits
at the security contract boundary.
"""

import re
from typing import Optional, Tuple

from backend.config.auth import auth_settings


class PasswordValidator:
    """Password validation with security best practices."""

    COMMON_PASSWORDS = {
        "password",
        "123456",
        "12345678",
        "qwerty",
        "abc123",
        "monkey",
        "1234567",
        "letmein",
        "trustno1",
        "dragon",
        "baseball",
        "111111",
        "iloveyou",
        "master",
        "sunshine",
        "ashley",
        "bailey",
        "passw0rd",
        "shadow",
        "123123",
        "654321",
        "superman",
        "qazwsx",
        "michael",
        "football",
    }

    COMMON_PASSWORD_PREFIXES = {
        "password",
        "admin",
        "administrator",
        "welcome",
        "qwerty",
        "letmein",
        "login",
        "user",
        "changeme",
        "secret",
        "default",
    }

    COMMON_PASSWORD_SUFFIXES = {
        "123",
        "1234",
        "12345",
        "123456",
        "1",
        "12",
        "!",
        "@",
        "#",
        "2020",
        "2021",
        "2022",
        "2023",
        "2024",
        "2025",
        "2026",
    }

    SPECIAL_CHAR_PATTERN = r"[!@#$%^&*()_+\-=\[\]{};:,.<>?]"

    @classmethod
    def validate(cls, password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against the SEC-6 security policy.

        Returns:
            (True, None) when the password is valid.
            (False, error_message) when the password violates policy.
        """

        if len(password) < auth_settings.password_min_length:
            return (
                False,
                (
                    "Password must be at least "
                    f"{auth_settings.password_min_length} characters"
                ),
            )

        if len(password) > auth_settings.password_max_length:
            return (
                False,
                (
                    "Password must be less than "
                    f"{auth_settings.password_max_length + 1} characters"
                ),
            )

        if (
            auth_settings.password_require_uppercase
            and not re.search(r"[A-Z]", password)
        ):
            return False, "Password must contain at least one uppercase letter"

        if (
            auth_settings.password_require_lowercase
            and not re.search(r"[a-z]", password)
        ):
            return False, "Password must contain at least one lowercase letter"

        if (
            auth_settings.password_require_digit
            and not re.search(r"\d", password)
        ):
            return False, "Password must contain at least one number"

        if (
            auth_settings.password_require_special
            and not re.search(cls.SPECIAL_CHAR_PATTERN, password)
        ):
            return False, (
                "Password must contain at least one special character "
                "(!@#$%^&*()_+-=[]{};:,.<>?)"
            )

        if cls._is_common_password(password):
            return False, (
                "Password is too common. "
                "Please choose a stronger password"
            )

        return True, None

    @classmethod
    def _is_common_password(cls, password: str) -> bool:
        """
        Detect both exact common passwords and common weak patterns.

        Examples rejected:
            password
            password123
            Password123!
            admin123
            Admin123!
            qwerty123
            welcome2026!
        """

        normalized = password.strip().lower()

        if normalized in cls.COMMON_PASSWORDS:
            return True

        # Remove non-alphanumeric characters so that common passwords
        # such as "Password123!" and "Admin123!" can be detected.
        compact = re.sub(r"[^a-z0-9]", "", normalized)

        if compact in cls.COMMON_PASSWORDS:
            return True

        for prefix in cls.COMMON_PASSWORD_PREFIXES:
            if not compact.startswith(prefix):
                continue

            suffix = compact[len(prefix):]

            if not suffix:
                return True

            if suffix in cls.COMMON_PASSWORD_SUFFIXES:
                return True

            # Common numeric suffixes such as:
            # password2026
            # admin123456
            # welcome2025
            if suffix.isdigit() and len(suffix) <= 6:
                return True

        return False

    @classmethod
    def get_password_strength(cls, password: str) -> str:
        """Return a simple password-strength classification."""

        score = 0

        if len(password) >= 8:
            score += 1

        if len(password) >= 12:
            score += 1

        if re.search(r"[A-Z]", password):
            score += 1

        if re.search(r"[a-z]", password):
            score += 1

        if re.search(r"\d", password):
            score += 1

        if re.search(cls.SPECIAL_CHAR_PATTERN, password):
            score += 1

        if cls._is_common_password(password):
            return "weak"

        if score <= 2:
            return "weak"

        if score <= 4:
            return "medium"

        return "strong"