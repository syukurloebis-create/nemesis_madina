# backend/crypto/signer.py
from abc import ABC, abstractmethod
import base64
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


class Signer(ABC):
    @abstractmethod
    async def sign(self, message: str) -> str:
        pass
    
    @abstractmethod
    async def verify(self, message: str, signature: str) -> bool:
        pass
    
    @abstractmethod
    async def get_key_id(self) -> str:
        pass


class DevFileSigner(Signer):
    def __init__(self):
        self.key_path = "/keys/dev_signing_key.pem"
        self._ensure_key_exists()
    
    def _ensure_key_exists(self):
        if not os.path.exists(self.key_path):
            os.makedirs(os.path.dirname(self.key_path), exist_ok=True)
            from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
            private_key = Ed25519PrivateKey.generate()
            with open(self.key_path, 'wb') as f:
                f.write(private_key.private_bytes_raw())
    
    async def sign(self, message: str) -> str:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        with open(self.key_path, 'rb') as f:
            private_key = Ed25519PrivateKey.from_private_bytes(f.read())
        signature = private_key.sign(message.encode())
        return base64.b64encode(signature).decode()
    
    async def verify(self, message: str, signature: str) -> bool:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        with open(self.key_path, 'rb') as f:
            private_bytes = f.read()
            public_key = Ed25519PrivateKey.from_private_bytes(private_bytes).public_key()
        try:
            public_key.verify(base64.b64decode(signature), message.encode())
            return True
        except:
            return False
    
    async def get_key_id(self) -> str:
        return "dev-key-001"


class VaultTransitSigner(Signer):
    def __init__(self, key_name: str = "nemesis-signing"):
        self.key_name = key_name
        self._init_vault()
    
    def _init_vault(self):
        import hvac
        self.client = hvac.Client(
            url=settings.VAULT_ADDR,
            token=settings.VAULT_TOKEN
        )
        try:
            self.client.secrets.transit.read_key(self.key_name)
        except:
            self.client.secrets.transit.create_key(self.key_name, key_type='ed25519')
    
    async def sign(self, message: str) -> str:
        import base64
        result = self.client.secrets.transit.sign_data(
            name=self.key_name,
            input=base64.b64encode(message.encode()).decode(),
            key_version=None
        )
        signature = result['data']['signature'].split(':')[2]
        return signature
    
    async def verify(self, message: str, signature: str) -> bool:
        import base64
        try:
            self.client.secrets.transit.verify_data(
                name=self.key_name,
                input=base64.b64encode(message.encode()).decode(),
                signature=f"vault:v1:{signature}"
            )
            return True
        except:
            return False
    
    async def get_key_id(self) -> str:
        key_info = self.client.secrets.transit.read_key(self.key_name)
        return f"vault://{self.key_name}/{key_info['data']['latest_version']}"


class HSMSigner(Signer):
    def __init__(self):
        self.key_handle = "hsm-key-001"
    
    async def sign(self, message: str) -> str:
        raise NotImplementedError("HSM integration requires vendor-specific implementation")
    
    async def verify(self, message: str, signature: str) -> bool:
        raise NotImplementedError("HSM integration requires vendor-specific implementation")
    
    async def get_key_id(self) -> str:
        return self.key_handle


def get_signer(environment: str) -> Signer:
    if environment == "development":
        return DevFileSigner()
    elif environment == "staging":
        return VaultTransitSigner()
    elif environment == "production":
        return HSMSigner()
    else:
        raise ValueError(f"Unknown environment: {environment}")