from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import Base, SessionLocal, engine, get_db
from app.services.agents import AgentFactory
from app.services.autopilot import AutopilotService
from app.services.brightdata import BrightDataClient
from app.services.ingestion import IngestionService
from app.services.integrations import IntegrationMonitor
from app.services.newsroom import NewsroomPipeline
from app.services.storage import ArticleRepository
from app.services.tavily import TavilyClient
from app.services.virlo import VirloClient
from app.schemas import ArticlePublic, PipelineRunResponse, StatusResponse


settings = get_settings()
repository = ArticleRepository()
monitor = IntegrationMonitor()
virlo_client = VirloClient(settings, monitor)
tavily_client = TavilyClient(settings, monitor)
brightdata_client = BrightDataClient(settings, monitor)
agent_factory = AgentFactory(settings)
ingestion_service = IngestionService(tavily_client, brightdata_client)
pipeline = NewsroomPipeline(settings, agent_factory, ingestion_service, tavily_client, monitor)
autopilot = AutopilotService(settings, virlo_client, pipeline, repository, SessionLocal, monitor)
manual_pipeline_task: asyncio.Task | None = None


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    autopilot.start()
    try:
        yield
    finally:
        await autopilot.stop()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/status", response_model=StatusResponse)
def status(db: Session = Depends(get_db)):
    articles = repository.list_articles(db)
    published = [article for article in articles if article.status == "published"]
    return StatusResponse(
        app=settings.app_name,
        autopilot_enabled=settings.newsroom_autopilot_enabled,
        article_count=len(articles),
        published_count=len(published),
        last_article_at=articles[0].created_at if articles else None,
        integrations=monitor.snapshot(),
    )


@app.get("/api/articles", response_model=list[ArticlePublic])
def list_articles(db: Session = Depends(get_db)):
    return [repository.to_public(record) for record in repository.list_articles(db)]


@app.get("/api/articles/{slug}", response_model=ArticlePublic)
def get_article(slug: str, db: Session = Depends(get_db)):
    record = repository.get_by_slug(db, slug)
    if not record:
        raise HTTPException(status_code=404, detail="Article not found")
    return repository.to_public(record)


@app.post("/api/pipeline/run", response_model=PipelineRunResponse)
async def run_pipeline():
    global manual_pipeline_task

    if manual_pipeline_task and not manual_pipeline_task.done():
        return PipelineRunResponse(
            status="running",
            reason="A pipeline run is already in progress.",
            errors=[],
        )

    async def _run() -> None:
        try:
            await autopilot.run_once()
        except Exception as exc:
            monitor.set_error("backend", f"Manual pipeline run failed: {type(exc).__name__}", details=str(exc))

    manual_pipeline_task = asyncio.create_task(_run())
    return PipelineRunResponse(
        status="accepted",
        reason="Pipeline run started. Refresh /api/status or the homepage shortly.",
        errors=[],
    )
