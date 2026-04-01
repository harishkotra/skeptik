from __future__ import annotations

from datetime import datetime


class IntegrationMonitor:
    def __init__(self):
        self._state = {
            "virlo": self._blank("virlo"),
            "tavily": self._blank("tavily"),
            "brightdata": self._blank("brightdata"),
            "featherless": self._blank("featherless"),
            "backend": self._blank("backend"),
        }

    @staticmethod
    def _blank(name: str) -> dict:
        return {
            "name": name,
            "status": "unknown",
            "last_checked_at": None,
            "last_error": None,
            "last_http_status": None,
            "details": None,
        }

    def set_ok(self, name: str, details: str | None = None, status_code: int | None = None) -> None:
        self._state[name] = {
            "name": name,
            "status": "ok",
            "last_checked_at": datetime.utcnow(),
            "last_error": None,
            "last_http_status": status_code,
            "details": details,
        }

    def set_error(self, name: str, error: str, details: str | None = None, status_code: int | None = None) -> None:
        self._state[name] = {
            "name": name,
            "status": "error",
            "last_checked_at": datetime.utcnow(),
            "last_error": error,
            "last_http_status": status_code,
            "details": details,
        }

    def snapshot(self) -> dict[str, dict]:
        return self._state.copy()
