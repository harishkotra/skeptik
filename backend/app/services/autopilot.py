from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.config import Settings
from app.schemas import ArticlePublic
from app.services.errors import ProviderAPIError
from app.services.integrations import IntegrationMonitor
from app.services.newsroom import NewsroomPipeline
from app.services.storage import ArticleRepository
from app.services.virlo import VirloClient


logger = logging.getLogger(__name__)


class AutopilotService:
    def __init__(
        self,
        settings: Settings,
        virlo: VirloClient,
        pipeline: NewsroomPipeline,
        repository: ArticleRepository,
        db_factory,
        monitor: IntegrationMonitor,
    ):
        self.settings = settings
        self.virlo = virlo
        self.pipeline = pipeline
        self.repository = repository
        self.db_factory = db_factory
        self.monitor = monitor
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if not self.settings.newsroom_autopilot_enabled:
            return
        if self._task and not self._task.done():
            return
        self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def seed_if_needed(self) -> None:
        db: Session = self.db_factory()
        try:
            if self.repository.count(db) >= self.settings.newsroom_target_article_count:
                return
        finally:
            db.close()

        try:
            signals = await self.virlo.fetch_signals()
            for signal in signals:
                await self.run_once(signal)
        except ProviderAPIError as exc:
            logger.error("autopilot seed failed: %s", exc.message)

    async def run_once(self, signal=None) -> ArticlePublic | None:
        try:
            signals = [signal] if signal else await self.virlo.fetch_signals()
        except ProviderAPIError as exc:
            logger.error("signal fetch failed: %s", exc.message)
            return None
        for item in signals:
            try:
                decision = await self.pipeline.create_story(item)
            except ProviderAPIError as exc:
                logger.error("pipeline failed: %s", exc.message)
                return None
            if decision.status != "published" or not decision.editor or not decision.reporter or not decision.skeptic or not decision.fact_checks or not decision.knowledge_pack or not decision.topic:
                logger.info("story skipped: %s", decision.reason)
                continue

            article_dict = {
                "slug": self.repository.make_slug(decision.editor.title),
                "status": "published",
                "title": decision.editor.title,
                "summary": decision.editor.summary,
                "content": decision.editor.content,
                "topic": decision.topic.model_dump(mode="json"),
                "sources": [source.model_dump(mode="json") for source in decision.knowledge_pack.sources],
                "claims": decision.reporter.claims,
                "fact_checks": [check.model_dump(mode="json") for check in decision.fact_checks],
                "agent_traces": {
                    "reporter": decision.reporter.model_dump(mode="json"),
                    "skeptic": decision.skeptic.model_dump(mode="json"),
                    "fact_checker": [check.model_dump(mode="json") for check in decision.fact_checks],
                    "editor": decision.editor.model_dump(mode="json"),
                },
                "why_this_matters": decision.editor.why_this_matters,
                "virlo_score": decision.topic.virlo_score,
                "confidence_score": decision.confidence_score,
                "disagreement_score": decision.disagreement_score,
                "number_of_sources": len(decision.knowledge_pack.sources),
                "unique_domains_count": decision.knowledge_pack.unique_domains_count,
            }
            db: Session = self.db_factory()
            try:
                record = self.repository.save_article(db, article_dict)
                return self.repository.to_public(record)
            finally:
                db.close()
        return None

    async def _loop(self) -> None:
        while True:
            try:
                await self.seed_if_needed()
                await asyncio.sleep(self.settings.newsroom_autopilot_seconds)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("autopilot iteration failed")
                self.monitor.set_error("backend", "Autopilot iteration failed")
                await asyncio.sleep(30)
