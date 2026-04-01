from __future__ import annotations

from agno.agent import Agent
from agno.models.openai.like import OpenAILike

from app.config import Settings
from app.schemas import EditorPacket, FactCheckBundle, ReporterDraft, SkepticReview, TopicPitch


class AgentFactory:
    def __init__(self, settings: Settings):
        self.settings = settings

    def _model(self) -> OpenAILike:
        return OpenAILike(
            id=self.settings.featherless_model,
            api_key=self.settings.featherless_api_key,
            base_url=self.settings.featherless_base_url,
            temperature=0.2,
            max_tokens=1600,
            timeout=60,
            retries=1,
            strict_output=False,
        )

    def topic_agent(self) -> Agent:
        return Agent(
            model=self._model(),
            output_schema=TopicPitch,
            structured_outputs=True,
            instructions=[
                "You are the Topic Agent for a serious autonomous newsroom.",
                "Convert Virlo signals into a concrete reporting pitch.",
                "Pick an angle that can support original synthesis across multiple sources.",
                "Return newsroom-safe, non-hype framing.",
            ],
        )

    def reporter_agent(self) -> Agent:
        return Agent(
            model=self._model(),
            output_schema=ReporterDraft,
            structured_outputs=True,
            instructions=[
                "You are the Reporter Agent for a serious publication.",
                "Write with restraint, specificity, and multiple perspectives.",
                "Do not summarize a single article. Synthesize across sources.",
                "Avoid hype and unsupported certainty.",
                "Include explicit claims that can be fact-checked.",
            ],
        )

    def skeptic_agent(self) -> Agent:
        return Agent(
            model=self._model(),
            output_schema=SkepticReview,
            structured_outputs=True,
            instructions=[
                "You are the Skeptic Agent in an autonomous newsroom.",
                "Challenge weak reasoning, missing context, imbalance, and overstatement.",
                "Assign a skepticism_score from 0 to 1 where higher means more serious issues.",
                "Be exact and editorially demanding.",
            ],
        )

    def fact_checker_agent(self) -> Agent:
        return Agent(
            model=self._model(),
            output_schema=FactCheckBundle,
            structured_outputs=True,
            instructions=[
                "You are the Fact-checker Agent.",
                "For each claim, classify it as verified, uncertain, or false.",
                "Ground every judgment in the evidence provided.",
                "If evidence is mixed or incomplete, mark uncertain rather than verified.",
            ],
        )

    def editor_agent(self) -> Agent:
        return Agent(
            model=self._model(),
            output_schema=EditorPacket,
            structured_outputs=True,
            instructions=[
                "You are the final Editor Agent.",
                "Produce a polished publication-ready story only if the draft has enough support.",
                "Preserve nuance, uncertainty, and material caveats.",
                "Make the story feel like a credible newsroom article.",
            ],
        )
