from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, HttpUrl


class SourceDocument(BaseModel):
    title: str
    url: HttpUrl
    domain: str
    snippet: str = ""
    content: str = ""
    published_at: str | None = None
    relevance_score: float = 0.0


class VirloSignal(BaseModel):
    topic: str
    angle: str
    urgency: Literal["watch", "active", "urgent"] = "active"
    signal_strength: float = Field(default=0.5, ge=0, le=1)
    explanation: str
    keywords: list[str] = Field(default_factory=list)
    region: str = "global"


class TopicPitch(BaseModel):
    topic: str
    angle: str
    urgency: Literal["watch", "active", "urgent"]
    virlo_score: float = Field(ge=0, le=1)
    why_now: str
    search_queries: list[str]
    keywords: list[str] = Field(default_factory=list)


class KnowledgePack(BaseModel):
    topic: TopicPitch
    sources: list[SourceDocument]
    source_summary: str
    unique_domains_count: int
    generated_at: datetime


class ClaimCheck(BaseModel):
    claim: str
    status: Literal["verified", "uncertain", "false"]
    explanation: str
    evidence: list[SourceDocument] = Field(default_factory=list)


class FactCheckBundle(BaseModel):
    checks: list[ClaimCheck]


class ReporterDraft(BaseModel):
    headline: str
    dek: str
    summary: str
    article_markdown: str
    why_this_matters: str
    claims: list[str]
    key_points: list[str]
    perspectives_considered: list[str]


class SkepticReview(BaseModel):
    skepticism_score: float = Field(ge=0, le=1)
    bias_risks: list[str]
    missing_context: list[str]
    logical_flaws: list[str]
    revision_notes: list[str]
    disagreement_summary: str


class EditorPacket(BaseModel):
    title: str
    summary: str
    content: str
    why_this_matters: str
    publication_notes: list[str]


class ArticleTrace(BaseModel):
    reporter: dict[str, Any]
    skeptic: dict[str, Any]
    fact_checker: dict[str, Any]
    editor: dict[str, Any]


class ArticlePublic(BaseModel):
    id: int
    slug: str
    status: str
    title: str
    summary: str
    content: str
    topic: dict[str, Any]
    sources: list[dict[str, Any]]
    claims: list[str]
    fact_checks: list[dict[str, Any]]
    agent_traces: dict[str, Any]
    why_this_matters: str
    virlo_score: float
    confidence_score: float
    disagreement_score: float
    number_of_sources: int
    unique_domains_count: int
    created_at: datetime


class StatusResponse(BaseModel):
    app: str
    autopilot_enabled: bool
    article_count: int
    published_count: int
    last_article_at: datetime | None
    integrations: dict[str, dict[str, Any]]


class PipelineRunResponse(BaseModel):
    status: str
    article: ArticlePublic | None = None
    reason: str | None = None
    errors: list[dict[str, Any]] = Field(default_factory=list)
