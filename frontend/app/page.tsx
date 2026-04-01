import Link from "next/link";
import { Activity, ArrowRight, Globe2, ShieldCheck } from "lucide-react";

import { ArticleCard } from "@/components/article-card";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getArticles, getStatus } from "@/lib/api";

export default async function HomePage() {
  const [statusResult, articlesResult] = await Promise.allSettled([getStatus(), getArticles()]);
  const status = statusResult.status === "fulfilled" ? statusResult.value : null;
  const articles = articlesResult.status === "fulfilled" ? articlesResult.value : [];
  const pageError = statusResult.status === "rejected" ? String(statusResult.reason) : articlesResult.status === "rejected" ? String(articlesResult.reason) : null;
  const lead = articles[0];
  const rest = articles.slice(1, 7);

  return (
    <main className="mx-auto max-w-6xl px-6 py-8 md:py-10">
      <section className="mb-6 flex items-center justify-between gap-4 border-b border-black/10 pb-4">
        <div className="text-[11px] uppercase tracking-[0.26em] text-steel">Live Autonomous Coverage</div>
        <div className="text-[11px] uppercase tracking-[0.2em] text-steel">
          {status?.autopilot_enabled ? "Desk Active" : "Desk Paused"}
        </div>
      </section>

      {pageError ? (
        <section className="mb-8 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm leading-7 text-red-900">
          <div className="text-[11px] uppercase tracking-[0.22em] text-red-700">Backend Error</div>
          <div className="mt-2">{pageError}</div>
        </section>
      ) : null}

      {status ? (
        <section className="mb-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {Object.values(status.integrations ?? {}).map((integration) => (
            <Card key={integration.name} className={integration.status === "error" ? "border-red-200 bg-red-50" : "bg-white/80"}>
              <CardContent className="space-y-2 p-5">
                <div className="text-[11px] uppercase tracking-[0.2em] text-steel">{integration.name}</div>
                <div className={integration.status === "error" ? "font-semibold text-red-800" : "font-semibold text-ink"}>
                  {integration.status}
                </div>
                {integration.last_error ? <p className="text-sm leading-6 text-steel">{integration.last_error}</p> : null}
                {integration.details ? <p className="text-xs leading-6 text-steel">{integration.details}</p> : null}
              </CardContent>
            </Card>
          ))}
        </section>
      ) : null}

      <section className="grid gap-8 lg:grid-cols-[minmax(0,1.55fr)_360px]">
        <div className="space-y-6">
          <div className="max-w-3xl">
            <h1 className="font-display text-5xl leading-[0.95] text-ink md:text-7xl">
              Serious reporting from an autonomous newsroom.
            </h1>
            <p className="mt-5 max-w-2xl text-lg leading-8 text-steel">
              Skeptik ranks stories with Virlo, builds knowledge packs with Tavily and Bright Data, then routes drafts through reporter, skeptic, fact-checker, and editor agents before publication.
            </p>
          </div>

          {lead ? (
            <Card className="overflow-hidden bg-ink text-paper">
              <CardContent className="space-y-7 p-8 md:p-10">
                <div className="flex flex-wrap items-center gap-3">
                  <Badge className="border-white/15 bg-white/10 text-paper">Lead Story</Badge>
                  <div className="text-[11px] uppercase tracking-[0.24em] text-paper/65">
                    Signal Strength {Math.round(lead.virlo_score * 100)}
                  </div>
                </div>
                <div className="grid gap-8 md:grid-cols-[minmax(0,1fr)_220px] md:items-end">
                  <div>
                    <h2 className="max-w-3xl font-display text-4xl leading-tight md:text-6xl">{lead.title}</h2>
                    <p className="mt-5 max-w-2xl text-lg leading-8 text-paper/82">{lead.summary}</p>
                  </div>
                  <div className="grid grid-cols-3 gap-3 md:grid-cols-1">
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <div className="text-[11px] uppercase tracking-[0.2em] text-paper/60">Confidence</div>
                      <div className="mt-1 text-3xl font-semibold">{Math.round(lead.confidence_score * 100)}</div>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <div className="text-[11px] uppercase tracking-[0.2em] text-paper/60">Disagreement</div>
                      <div className="mt-1 text-3xl font-semibold">{Math.round(lead.disagreement_score * 100)}</div>
                    </div>
                    <div className="rounded-2xl border border-white/10 bg-white/5 p-4">
                      <div className="text-[11px] uppercase tracking-[0.2em] text-paper/60">Sources</div>
                      <div className="mt-1 text-3xl font-semibold">{lead.number_of_sources}</div>
                    </div>
                  </div>
                </div>
                <div className="grid gap-6 border-t border-white/10 pt-6 md:grid-cols-[minmax(0,1fr)_auto] md:items-end">
                  <p className="max-w-3xl text-sm leading-7 text-paper/85">{lead.why_this_matters}</p>
                  <Link
                    href={`/articles/${lead.slug}`}
                    className="inline-flex items-center gap-2 text-sm uppercase tracking-[0.18em] text-paper/90 transition-opacity hover:opacity-70"
                  >
                    Open Story
                    <ArrowRight className="h-4 w-4" />
                  </Link>
                </div>
              </CardContent>
            </Card>
          ) : null}
        </div>

        <div className="space-y-4">
          <Card className="bg-white/88">
            <CardContent className="grid gap-5">
              <div className="flex items-center gap-3">
                <Activity className="h-5 w-5 text-accent" />
                <div>
                  <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Autonomous Loop</div>
                  <div className="text-xl font-semibold text-ink">{status?.autopilot_enabled ? "Running" : "Paused"}</div>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 border-t border-black/10 pt-4">
                <div>
                  <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Published</div>
                  <div className="mt-1 text-3xl font-semibold text-ink">{status?.published_count ?? 0}</div>
                </div>
                <div>
                  <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Tracked</div>
                  <div className="mt-1 text-3xl font-semibold text-ink">{status?.article_count ?? 0}</div>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card className="bg-white/88">
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <Globe2 className="h-5 w-5 text-accent" />
                <div className="font-semibold text-ink">Trending via Virlo</div>
              </div>
              <p className="text-sm leading-7 text-steel">
                Topic selection is driven by signal strength, cross-beat convergence, and urgency. Readers are seeing stories because the momentum profile is rising now.
              </p>
            </CardContent>
          </Card>
          <Card className="bg-white/88">
            <CardContent className="space-y-4">
              <div className="flex items-center gap-3">
                <ShieldCheck className="h-5 w-5 text-accent" />
                <div className="font-semibold text-ink">Editorial Gate</div>
              </div>
              <p className="text-sm leading-7 text-steel">
                Articles are rejected for false claims, routed back when skeptic pressure is too high, and published only after confidence clears the deterministic threshold.
              </p>
            </CardContent>
          </Card>
        </div>
      </section>

      {rest.length > 0 ? (
        <section className="mt-14">
          <div className="mb-6 flex items-end justify-between gap-4 border-b border-black/10 pb-4">
            <div>
              <div className="text-[11px] uppercase tracking-[0.24em] text-steel">Published Desk</div>
              <h3 className="mt-2 font-display text-3xl text-ink">More from the autonomous file</h3>
            </div>
          </div>
          <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
            {rest.map((article) => (
              <ArticleCard key={article.slug} article={article} />
            ))}
          </div>
        </section>
      ) : null}

      <section className="mt-14 grid gap-6 lg:grid-cols-3">
        <Card className="bg-white/80">
          <CardContent className="space-y-3">
            <div className="text-[11px] uppercase tracking-[0.22em] text-steel">Why It Feels Credible</div>
            <p className="text-sm leading-7 text-steel">
              The story is the reporting process itself: source discovery, extraction, challenge, verification, and publication policy are exposed rather than hidden.
            </p>
          </CardContent>
        </Card>
        <Card className="bg-white/80">
          <CardContent className="space-y-3">
            <div className="text-[11px] uppercase tracking-[0.22em] text-steel">What To Test</div>
            <p className="text-sm leading-7 text-steel">
              Focus on pipeline outputs, reject paths, source quality, and whether the article page makes the reporting chain understandable in under thirty seconds.
            </p>
          </CardContent>
        </Card>
        <Card className="bg-white/80">
          <CardContent className="space-y-3">
            <div className="text-[11px] uppercase tracking-[0.22em] text-steel">Reader Signal</div>
            <p className="text-sm leading-7 text-steel">
              Virlo is not just decoration here. It decides what rises, informs why-now messaging, and surfaces signal strength directly in the UI.
            </p>
          </CardContent>
        </Card>
      </section>

      {!lead ? (
        <section className="mt-16 rounded-3xl border border-black/10 bg-white/70 p-8 text-center text-steel">
          The newsroom is waiting for its first publishable cycle.
        </section>
      ) : null}
    </main>
  );
}
