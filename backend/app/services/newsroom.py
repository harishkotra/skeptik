from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any, TypeVar

from app.config import Settings
from app.schemas import ClaimCheck, EditorPacket, FactCheckBundle, KnowledgePack, ReporterDraft, SkepticReview, TopicPitch, VirloSignal
from app.services.agents import AgentFactory
from app.services.errors import ProviderAPIError
from app.services.ingestion import IngestionService
from app.services.integrations import IntegrationMonitor
from app.services.tavily import TavilyClient
from app.services.utils import compact_json

ModelT = TypeVar("ModelT")


@dataclass
class PipelineDecision:
    status: str
    reason: str | None
    topic: TopicPitch | None = None
    knowledge_pack: KnowledgePack | None = None
    reporter: ReporterDraft | None = None
    skeptic: SkepticReview | None = None
    fact_checks: list[ClaimCheck] | None = None
    editor: EditorPacket | None = None
    confidence_score: float = 0.0
    disagreement_score: float = 0.0


class NewsroomPipeline:
    def __init__(
        self,
        settings: Settings,
        agents: AgentFactory,
        ingestion: IngestionService,
        tavily: TavilyClient,
        monitor: IntegrationMonitor,
    ):
        self.settings = settings
        self.agents = agents
        self.ingestion = ingestion
        self.tavily = tavily
        self.monitor = monitor

    def _coerce_model(self, model_cls: type[ModelT], response: Any) -> ModelT:
        if isinstance(response, model_cls):
            return response

        content = getattr(response, "content", response)
        if isinstance(content, model_cls):
            return content
        if isinstance(content, dict):
            return model_cls.model_validate(content)
        if isinstance(content, str):
            return model_cls.model_validate_json(content)
        raise TypeError(f"Could not coerce response into {model_cls.__name__}")

    async def create_story(self, signal: VirloSignal) -> PipelineDecision:
        topic = await self._pitch_topic(signal)
        knowledge_pack = await self.ingestion.build_knowledge_pack(topic)
        if len(knowledge_pack.sources) < self.settings.newsroom_min_sources:
            return PipelineDecision(status="rejected", reason="insufficient_sources", topic=topic, knowledge_pack=knowledge_pack)

        reporter = await self._report(topic, knowledge_pack)
        skeptic = await self._skepticize(reporter, knowledge_pack)
        fact_checks = await self._fact_check(reporter.claims)
        false_claims = sum(1 for check in fact_checks if check.status == "false")
        uncertain_claims = sum(1 for check in fact_checks if check.status == "uncertain")
        uncertain_ratio = uncertain_claims / max(len(fact_checks), 1)
        disagreement_score = round(min(1.0, skeptic.skepticism_score * 0.7 + uncertain_ratio * 0.3), 3)

        if false_claims > self.settings.newsroom_max_false_claims:
            return PipelineDecision(
                status="rejected",
                reason="false_claims_detected",
                topic=topic,
                knowledge_pack=knowledge_pack,
                reporter=reporter,
                skeptic=skeptic,
                fact_checks=fact_checks,
                disagreement_score=disagreement_score,
            )

        if skeptic.skepticism_score > self.settings.newsroom_max_skeptic_score:
            revised = await self._report(topic, knowledge_pack, skeptic=skeptic, prior_draft=reporter)
            revised_skeptic = await self._skepticize(revised, knowledge_pack)
            revised_checks = await self._fact_check(revised.claims)
            revised_false = sum(1 for check in revised_checks if check.status == "false")
            revised_uncertain = sum(1 for check in revised_checks if check.status == "uncertain")
            revised_uncertain_ratio = revised_uncertain / max(len(revised_checks), 1)
            disagreement_score = round(min(1.0, revised_skeptic.skepticism_score * 0.7 + revised_uncertain_ratio * 0.3), 3)

            if revised_false > self.settings.newsroom_max_false_claims:
                return PipelineDecision(
                    status="rejected",
                    reason="false_claims_after_revision",
                    topic=topic,
                    knowledge_pack=knowledge_pack,
                    reporter=revised,
                    skeptic=revised_skeptic,
                    fact_checks=revised_checks,
                    disagreement_score=disagreement_score,
                )

            if revised_skeptic.skepticism_score > self.settings.newsroom_max_skeptic_score:
                return PipelineDecision(
                    status="rejected",
                    reason="skeptic_score_too_high",
                    topic=topic,
                    knowledge_pack=knowledge_pack,
                    reporter=revised,
                    skeptic=revised_skeptic,
                    fact_checks=revised_checks,
                    disagreement_score=disagreement_score,
                )
            reporter, skeptic, fact_checks = revised, revised_skeptic, revised_checks

        if uncertain_ratio > self.settings.newsroom_max_uncertain_ratio:
            return PipelineDecision(
                status="rejected",
                reason="too_many_uncertain_claims",
                topic=topic,
                knowledge_pack=knowledge_pack,
                reporter=reporter,
                skeptic=skeptic,
                fact_checks=fact_checks,
                disagreement_score=disagreement_score,
            )

        editor = await self._edit(reporter, skeptic, fact_checks, knowledge_pack)
        confidence_score = self._confidence_score(fact_checks, skeptic)
        return PipelineDecision(
            status="published",
            reason=None,
            topic=topic,
            knowledge_pack=knowledge_pack,
            reporter=reporter,
            skeptic=skeptic,
            fact_checks=fact_checks,
            editor=editor,
            confidence_score=confidence_score,
            disagreement_score=disagreement_score,
        )

    async def _pitch_topic(self, signal: VirloSignal) -> TopicPitch:
        if not self.settings.featherless_api_key:
            error = ProviderAPIError("featherless", "Missing FEATHERLESS_API_KEY")
            self.monitor.set_error("featherless", error.message)
            raise error
        try:
            prompt = f"Virlo signal:\n{compact_json(signal.model_dump())}"
            response = self.agents.topic_agent().run(prompt)
            result = self._coerce_model(TopicPitch, response)
            self.monitor.set_ok("featherless", details="Topic agent completed", status_code=200)
            return result
        except Exception as exc:
            error = ProviderAPIError("featherless", f"Topic agent failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("featherless", error.message, details=str(exc))
            raise error

    async def _report(
        self,
        topic: TopicPitch,
        knowledge_pack: KnowledgePack,
        skeptic: SkepticReview | None = None,
        prior_draft: ReporterDraft | None = None,
    ) -> ReporterDraft:
        try:
            prompt_parts = [
                "Topic pitch:",
                compact_json(topic.model_dump()),
                "Knowledge pack:",
                compact_json(knowledge_pack.model_dump(mode="json")),
            ]
            if skeptic:
                prompt_parts.extend(["Skeptic revision brief:", compact_json(skeptic.model_dump())])
            if prior_draft:
                prompt_parts.extend(["Previous draft:", compact_json(prior_draft.model_dump())])
            response = self.agents.reporter_agent().run("\n\n".join(prompt_parts))
            result = self._coerce_model(ReporterDraft, response)
            self.monitor.set_ok("featherless", details="Reporter agent completed", status_code=200)
            return result
        except Exception as exc:
            error = ProviderAPIError("featherless", f"Reporter agent failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("featherless", error.message, details=str(exc))
            raise error

    async def _skepticize(self, reporter: ReporterDraft, knowledge_pack: KnowledgePack) -> SkepticReview:
        try:
            prompt = "\n\n".join(
                [
                    "Draft:",
                    compact_json(reporter.model_dump()),
                    "Knowledge pack:",
                    compact_json(knowledge_pack.model_dump(mode="json")),
                ]
            )
            response = self.agents.skeptic_agent().run(prompt)
            result = self._coerce_model(SkepticReview, response)
            self.monitor.set_ok("featherless", details="Skeptic agent completed", status_code=200)
            return result
        except Exception as exc:
            error = ProviderAPIError("featherless", f"Skeptic agent failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("featherless", error.message, details=str(exc))
            raise error

    async def _fact_check(self, claims: list[str]) -> list[ClaimCheck]:
        evidence_checks: list[ClaimCheck] = []
        for claim in claims:
            evidence = await self.tavily.verify_claim(claim)
            evidence_checks.append(
                ClaimCheck(
                    claim=claim,
                    status="verified" if evidence else "uncertain",
                    explanation="Verification is based on overlap across the retrieved source set.",
                    evidence=evidence[:2],
                )
            )

        try:
            assembled = [
                {"claim": check.claim, "evidence": [item.model_dump(mode="json") for item in check.evidence]}
                for check in evidence_checks
            ]
            response = self.agents.fact_checker_agent().run(compact_json(assembled))
            result = self._coerce_model(FactCheckBundle, response).checks
            self.monitor.set_ok("featherless", details="Fact-check agent completed", status_code=200)
            return result
        except Exception as exc:
            error = ProviderAPIError("featherless", f"Fact-check agent failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("featherless", error.message, details=str(exc))
            raise error

    async def _edit(
        self,
        reporter: ReporterDraft,
        skeptic: SkepticReview,
        fact_checks: list[ClaimCheck],
        knowledge_pack: KnowledgePack,
    ) -> EditorPacket:
        try:
            prompt = "\n\n".join(
                [
                    "Reporter draft:",
                    compact_json(reporter.model_dump()),
                    "Skeptic review:",
                    compact_json(skeptic.model_dump()),
                    "Fact checks:",
                    compact_json([item.model_dump(mode="json") for item in fact_checks]),
                    "Knowledge pack:",
                    compact_json(knowledge_pack.model_dump(mode="json")),
                ]
            )
            response = self.agents.editor_agent().run(prompt)
            result = self._coerce_model(EditorPacket, response)
            self.monitor.set_ok("featherless", details="Editor agent completed", status_code=200)
            return result
        except Exception as exc:
            error = ProviderAPIError("featherless", f"Editor agent failed: {type(exc).__name__}", details=str(exc))
            self.monitor.set_error("featherless", error.message, details=str(exc))
            raise error

    def _confidence_score(self, fact_checks: list[ClaimCheck], skeptic: SkepticReview) -> float:
        claim_scores = []
        for check in fact_checks:
            if check.status == "verified":
                claim_scores.append(1.0)
            elif check.status == "uncertain":
                claim_scores.append(0.5)
            else:
                claim_scores.append(0.0)
        base = mean(claim_scores) if claim_scores else 0.0
        confidence = (base * 0.75) + ((1 - skeptic.skepticism_score) * 0.25)
        return round(confidence, 3)
