from __future__ import annotations

from datetime import datetime

from app.schemas import KnowledgePack, SourceDocument, TopicPitch
from app.services.brightdata import BrightDataClient
from app.services.errors import ProviderAPIError
from app.services.tavily import TavilyClient


class IngestionService:
    def __init__(self, tavily: TavilyClient, brightdata: BrightDataClient):
        self.tavily = tavily
        self.brightdata = brightdata

    async def build_knowledge_pack(self, topic: TopicPitch) -> KnowledgePack:
        all_sources: list[SourceDocument] = []
        for query in topic.search_queries:
            all_sources.extend(await self.tavily.search(query))

        deduped: dict[str, SourceDocument] = {}
        for source in all_sources:
            deduped[str(source.url)] = source

        sources = list(deduped.values())[:8]
        if not sources:
            raise ProviderAPIError("tavily", f"No sources found for topic: {topic.topic}")
        enriched: list[SourceDocument] = []
        for source in sources:
            content = await self.brightdata.extract(str(source.url))
            source = source.model_copy(update={"content": content[:8000]})
            enriched.append(source)

        unique_domains_count = len({source.domain for source in enriched})
        summary = "\n\n".join(
            f"- {source.title} ({source.domain}): {source.snippet or source.content[:240]}"
            for source in enriched
        )

        return KnowledgePack(
            topic=topic,
            sources=enriched,
            source_summary=summary,
            unique_domains_count=unique_domains_count,
            generated_at=datetime.utcnow(),
        )
