import Link from "next/link";
import { ArrowUpRight } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Article } from "@/lib/types";

export function ArticleCard({ article }: { article: Article }) {
  return (
    <Link href={`/articles/${article.slug}`}>
      <Card className="h-full transition-all duration-300 hover:-translate-y-1 hover:shadow-[0_24px_70px_rgba(15,23,32,0.12)]">
        <CardContent className="flex h-full flex-col space-y-5 p-7">
          <div className="flex items-start justify-between gap-4">
            <Badge>Virlo {Math.round(article.virlo_score * 100)}</Badge>
            <ArrowUpRight className="h-4 w-4 text-steel" />
          </div>
          <div>
            <div className="text-[11px] uppercase tracking-[0.22em] text-steel">{article.topic.topic}</div>
            <h2 className="mt-3 font-display text-[2rem] leading-tight text-ink">{article.title}</h2>
            <p className="mt-4 text-sm leading-7 text-steel">{article.summary}</p>
          </div>
          <div className="grid grid-cols-3 gap-3 border-y border-black/10 py-4 text-sm text-ink">
            <div>
              <div className="text-[11px] uppercase tracking-[0.18em] text-steel">Confidence</div>
              <div className="mt-1 text-lg font-semibold">{Math.round(article.confidence_score * 100)}</div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.18em] text-steel">Disagreement</div>
              <div className="mt-1 text-lg font-semibold">{Math.round(article.disagreement_score * 100)}</div>
            </div>
            <div>
              <div className="text-[11px] uppercase tracking-[0.18em] text-steel">Sources</div>
              <div className="mt-1 text-lg font-semibold">{article.number_of_sources}</div>
            </div>
          </div>
          <p className="mt-auto text-sm leading-7 text-ink">{article.why_this_matters}</p>
        </CardContent>
      </Card>
    </Link>
  );
}
