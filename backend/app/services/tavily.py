from __future__ import annotations

from typing import Any

import httpx

from app.config import Settings
from app.schemas import SourceDocument
from app.services.errors import ProviderAPIError
from app.services.integrations import IntegrationMonitor
from app.services.utils import extract_domain


class TavilyClient:
    def __init__(self, settings: Settings, monitor: IntegrationMonitor):
        self.settings = settings
        self.monitor = monitor

    async def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        if not self.settings.tavily_api_key:
            error = ProviderAPIError("tavily", "Missing TAVILY_API_KEY")
            self.monitor.set_error("tavily", error.message)
            raise error

        payload = {
            "api_key": self.settings.tavily_api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "advanced",
            "include_answer": True,
            "include_raw_content": True,
        }

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(f"{self.settings.tavily_api_url}/search", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            body = exc.response.text[:500]
            error = ProviderAPIError("tavily", f"Tavily request failed with {exc.response.status_code}", exc.response.status_code, body)
            self.monitor.set_error("tavily", error.message, details=body, status_code=exc.response.status_code)
            raise error
        except Exception as exc:
            error = ProviderAPIError("tavily", f"Tavily request failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("tavily", error.message, details=str(exc))
            raise error

        results = data.get("results", []) if isinstance(data, dict) else []
        documents: list[SourceDocument] = []
        for item in results:
            url = item.get("url")
            if not url:
                continue
            documents.append(
                SourceDocument(
                    title=item.get("title") or url,
                    url=url,
                    domain=extract_domain(url),
                    snippet=item.get("content") or "",
                    content=item.get("raw_content") or item.get("content") or "",
                    published_at=item.get("published_date"),
                    relevance_score=float(item.get("score") or 0.0),
                )
            )
        if not documents:
            error = ProviderAPIError("tavily", f"Tavily returned no results for query: {query}")
            self.monitor.set_error("tavily", error.message)
            raise error
        self.monitor.set_ok("tavily", details=f"{len(documents)} results for query", status_code=200)
        return documents

    async def verify_claim(self, claim: str) -> list[SourceDocument]:
        return await self.search(claim, max_results=3)
