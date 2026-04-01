from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.services.errors import ProviderAPIError
from app.services.integrations import IntegrationMonitor


class BrightDataClient:
    def __init__(self, settings: Settings, monitor: IntegrationMonitor):
        self.settings = settings
        self.monitor = monitor
        self._zone: str | None = settings.brightdata_zone or None

    async def _resolve_zone(self) -> str:
        if self._zone:
            return self._zone
        headers = {"Authorization": f"Bearer {self.settings.brightdata_api_key}"}
        try:
            async with httpx.AsyncClient(timeout=20) as client:
                response = await client.get("https://api.brightdata.com/zone/get_active_zones", headers=headers)
                response.raise_for_status()
                data = response.json()
        except Exception as exc:
            raise ProviderAPIError("brightdata", "Failed to resolve active Bright Data zones", details=str(exc)) from exc
        if not isinstance(data, list) or not data:
            raise ProviderAPIError("brightdata", "No active Bright Data zones found")
        zone = data[0].get("name")
        if not zone:
            raise ProviderAPIError("brightdata", "Bright Data active zone payload missing name", details=str(data)[:500])
        self._zone = zone
        return zone

    async def extract(self, url: str) -> str:
        if not self.settings.brightdata_api_key:
            error = ProviderAPIError("brightdata", "Missing BRIGHTDATA_API_KEY")
            self.monitor.set_error("brightdata", error.message)
            raise error

        zone = await self._resolve_zone()

        headers = {
            "Authorization": f"Bearer {self.settings.brightdata_api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "zone": zone,
            "url": url,
            "format": "raw",
            "browser": {"render": True},
        }

        try:
            async with httpx.AsyncClient(timeout=45) as client:
                response = await client.post(self.settings.brightdata_api_url, headers=headers, json=payload)
                response.raise_for_status()
                if "application/json" in response.headers.get("content-type", ""):
                    data = response.json()
                    content = str(data.get("body") or data.get("content") or data.get("html") or "")
                else:
                    content = response.text
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            error = ProviderAPIError("brightdata", f"Bright Data request failed with {exc.response.status_code}", exc.response.status_code, body)
            self.monitor.set_error("brightdata", error.message, details=body, status_code=exc.response.status_code)
            raise error
        except Exception as exc:
            error = ProviderAPIError("brightdata", f"Bright Data request failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("brightdata", error.message, details=str(exc))
            raise error

        if not content:
            error = ProviderAPIError("brightdata", f"Bright Data returned empty content for {url}")
            self.monitor.set_error("brightdata", error.message)
            raise error
        self.monitor.set_ok("brightdata", details=f"Zone {zone}", status_code=200)
        return content
