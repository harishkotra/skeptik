from __future__ import annotations

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.models import ArticleRecord
from app.schemas import ArticlePublic
from app.services.utils import slugify


class ArticleRepository:
    def list_articles(self, db: Session) -> list[ArticleRecord]:
        stmt = select(ArticleRecord).order_by(desc(ArticleRecord.created_at))
        return list(db.scalars(stmt).all())

    def get_by_slug(self, db: Session, slug: str) -> ArticleRecord | None:
        stmt = select(ArticleRecord).where(ArticleRecord.slug == slug)
        return db.scalar(stmt)

    def count(self, db: Session) -> int:
        return len(self.list_articles(db))

    def save_article(self, db: Session, article: dict) -> ArticleRecord:
        slug = article["slug"]
        existing = self.get_by_slug(db, slug)
        if existing:
            for key, value in article.items():
                setattr(existing, key, value)
            db.add(existing)
            db.commit()
            db.refresh(existing)
            return existing
        record = ArticleRecord(**article)
        db.add(record)
        db.commit()
        db.refresh(record)
        return record

    @staticmethod
    def to_public(record: ArticleRecord) -> ArticlePublic:
        return ArticlePublic.model_validate(
            {
                "id": record.id,
                "slug": record.slug,
                "status": record.status,
                "title": record.title,
                "summary": record.summary,
                "content": record.content,
                "topic": record.topic,
                "sources": record.sources,
                "claims": record.claims,
                "fact_checks": record.fact_checks,
                "agent_traces": record.agent_traces,
                "why_this_matters": record.why_this_matters,
                "virlo_score": record.virlo_score,
                "confidence_score": record.confidence_score,
                "disagreement_score": record.disagreement_score,
                "number_of_sources": record.number_of_sources,
                "unique_domains_count": record.unique_domains_count,
                "created_at": record.created_at,
            }
        )

    @staticmethod
    def make_slug(title: str) -> str:
        return slugify(title)
