from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.schemas import VirloSignal
from app.services.errors import ProviderAPIError
from app.services.integrations import IntegrationMonitor


class VirloClient:
    def __init__(self, settings: Settings, monitor: IntegrationMonitor):
        self.settings = settings
        self.monitor = monitor

    async def fetch_signals(self) -> list[VirloSignal]:
        if not self.settings.virlo_api_key:
            error = ProviderAPIError("virlo", "Missing VIRLO_API_KEY")
            self.monitor.set_error("virlo", error.message)
            raise error

        headers = {"Authorization": f"Bearer {self.settings.virlo_api_key}"}

        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get(self.settings.virlo_api_url, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            error = ProviderAPIError("virlo", f"Virlo request failed with {exc.response.status_code}", exc.response.status_code, body)
            self.monitor.set_error("virlo", error.message, details=body, status_code=exc.response.status_code)
            raise error
        except Exception as exc:
            error = ProviderAPIError("virlo", f"Virlo request failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("virlo", error.message, details=str(exc))
            raise error

        signals = self._coerce_digest(data)
        if not signals:
            error = ProviderAPIError("virlo", "Virlo returned no trends", details=str(data)[:500])
            self.monitor.set_error("virlo", error.message, details=error.details)
            raise error
        self.monitor.set_ok("virlo", details=f"{len(signals)} trends loaded", status_code=200)
        return signals

    @staticmethod
    def _coerce_digest(payload: Any) -> list[VirloSignal]:
        if not isinstance(payload, dict):
            return []
        groups = payload.get("data", [])
        if not isinstance(groups, list):
            return []

        signals: list[VirloSignal] = []
        for group in groups:
            trends = group.get("trends", []) if isinstance(group, dict) else []
            if not isinstance(trends, list):
                continue
            for entry in trends:
                trend = entry.get("trend", {}) if isinstance(entry, dict) else {}
                if not isinstance(trend, dict):
                    continue
                ranking = int(entry.get("ranking") or 10)
                strength = max(0.1, min(1.0, 1 - ((ranking - 1) * 0.08)))
                name = trend.get("name") or trend.get("title")
                description = trend.get("description") or trend.get("summary") or ""
                if not name:
                    continue
                signals.append(
                    VirloSignal(
                        topic=name,
                        angle=description[:180] or name,
                        urgency="urgent" if ranking <= 3 else "active",
                        signal_strength=strength,
                        explanation=description or f"Virlo trend rank #{ranking}",
                        keywords=[name],
                        region="global",
                    )
                )
        return signals
