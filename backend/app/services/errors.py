from __future__ import annotations


class ProviderAPIError(Exception):
    def __init__(self, provider: str, message: str, status_code: int | None = None, details: str | None = None):
        super().__init__(message)
        self.provider = provider
        self.message = message
        self.status_code = status_code
        self.details = details

    def to_dict(self) -> dict:
        return {
            "provider": self.provider,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }
