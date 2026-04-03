from cryptography.fernet import Fernet

from app.core.config import settings


class SessionCrypto:
    def __init__(self, key: str) -> None:
        self.fernet = Fernet(key)

    def encrypt(self, payload: str) -> str:
        return self.fernet.encrypt(payload.encode()).decode()

    def decrypt(self, payload: str) -> str:
        return self.fernet.decrypt(payload.encode()).decode()


crypto = SessionCrypto(settings.session_encryption_key)
