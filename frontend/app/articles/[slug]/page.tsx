import Link from "next/link";
import { marked } from "marked";
import { ArrowLeft, CircleAlert, ShieldCheck, Sparkles } from "lucide-react";

import { ScorePill } from "@/components/score-pill";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { getArticle, getStatus } from "@/lib/api";

export default async function ArticlePage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const [statusResult, articleResult] = await Promise.allSettled([getStatus(), getArticle(slug)]);
  const status = statusResult.status === "fulfilled" ? statusResult.value : null;
  if (articleResult.status === "rejected") {
    return (
      <main className="mx-auto max-w-4xl px-6 py-10">
        <Card className="border-red-200 bg-red-50">
          <CardContent className="space-y-4 p-8">
            <div className="text-[11px] uppercase tracking-[0.2em] text-red-700">Article Error</div>
            <div className="text-lg font-semibold text-red-900">The article could not be loaded.</div>
            <p className="text-sm leading-7 text-red-900/80">{String(articleResult.reason)}</p>
            {status ? (
              <div className="grid gap-3 md:grid-cols-2">
                {Object.values(status.integrations ?? {}).map((integration) => (
                  <div key={integration.name} className="rounded-2xl border border-red-200 bg-white/80 p-4">
                    <div className="text-[11px] uppercase tracking-[0.2em] text-steel">{integration.name}</div>
                    <div className="mt-1 font-semibold text-ink">{integration.status}</div>
                    {integration.last_error ? <p className="mt-2 text-sm leading-6 text-steel">{integration.last_error}</p> : null}
                  </div>
                ))}
              </div>
            ) : null}
          </CardContent>
        </Card>
      </main>
    );
  }

  const article = articleResult.value;
  const html = await marked.parse(article.content);

  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <Link href="/" className="inline-flex items-center gap-2 text-sm uppercase tracking-[0.16em] text-steel">
        <ArrowLeft className="h-4 w-4" />
        Back to front page
      </Link>

      <section className="mt-8 grid gap-8 lg:grid-cols-[1.4fr_0.8fr]">
        <article className="space-y-8">
          <div>
            <Badge>Trending via Virlo</Badge>
            <h1 className="mt-5 max-w-4xl font-display text-5xl leading-tight text-ink">{article.title}</h1>
            <p className="mt-5 max-w-3xl text-xl leading-8 text-steel">{article.summary}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <ScorePill label="Signal Strength" value={article.virlo_score} />
            <ScorePill label="Confidence" value={article.confidence_score} />
            <ScorePill label="Disagreement" value={article.disagreement_score} />
          </div>

          <Card>
            <CardContent className="p-8">
              <div className="mb-5 flex items-center gap-3">
                <Sparkles className="h-5 w-5 text-accent" />
                <div>
                  <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Why You’re Seeing This</div>
                  <div className="font-semibold text-ink">Virlo explanation</div>
                </div>
              </div>
              <p className="text-base leading-8 text-ink">{article.why_this_matters}</p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-8">
              <div className="mb-6 text-[11px] uppercase tracking-[0.2em] text-steel">Article Content</div>
              <div className="prose-story max-w-none text-lg text-ink" dangerouslySetInnerHTML={{ __html: html }} />
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-8 p-8">
              <div className="text-[11px] uppercase tracking-[0.2em] text-steel">How This Was Created</div>

              <section>
                <div className="font-semibold text-ink">Reporter Draft</div>
                <p className="mt-2 text-sm leading-7 text-steel">
                  {String(article.agent_traces.reporter.summary ?? article.summary)}
                </p>
              </section>

              <section>
                <div className="flex items-center gap-2 font-semibold text-ink">
                  <CircleAlert className="h-4 w-4 text-accent" />
                  Skeptic Critique
                </div>
                <p className="mt-2 text-sm leading-7 text-steel">
                  {String(article.agent_traces.skeptic.disagreement_summary ?? "No critique stored.")}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  {Array.isArray(article.agent_traces.skeptic.revision_notes)
                    ? article.agent_traces.skeptic.revision_notes.map((note) => (
                        <span key={String(note)} className="rounded-full border border-black/10 bg-paper px-3 py-1 text-xs text-ink">
                          {String(note)}
                        </span>
                      ))
                    : null}
                </div>
              </section>

              <section>
                <div className="flex items-center gap-2 font-semibold text-ink">
                  <ShieldCheck className="h-4 w-4 text-accent" />
                  Fact-check Results
                </div>
                <div className="mt-4 space-y-4">
                  {article.fact_checks.map((check) => (
                    <div key={check.claim} className="rounded-2xl border border-black/10 bg-paper/60 p-4">
                      <div className="flex items-center justify-between gap-4">
                        <div className="font-medium text-ink">{check.claim}</div>
                        <Badge className="bg-white">{check.status}</Badge>
                      </div>
                      <p className="mt-2 text-sm leading-7 text-steel">{check.explanation}</p>
                    </div>
                  ))}
                </div>
              </section>
            </CardContent>
          </Card>
        </article>

        <aside className="space-y-6">
          <Card>
            <CardContent className="space-y-4">
              <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Metadata</div>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-steel">Sources</div>
                  <div className="text-2xl font-semibold text-ink">{article.number_of_sources}</div>
                </div>
                <div>
                  <div className="text-steel">Domains</div>
                  <div className="text-2xl font-semibold text-ink">{article.unique_domains_count}</div>
                </div>
              </div>
              <p className="text-sm leading-7 text-steel">
                Signal strength, confidence, and disagreement are calculated at publish time and exposed for readers.
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-4">
              <div className="text-[11px] uppercase tracking-[0.2em] text-steel">Sources</div>
              <div className="space-y-4">
                {article.sources.map((source) => (
                  <a
                    key={source.url}
                    href={source.url}
                    target="_blank"
                    rel="noreferrer"
                    className="block rounded-2xl border border-black/10 bg-paper/60 p-4"
                  >
                    <div className="font-medium text-ink">{source.title}</div>
                    <div className="mt-1 text-xs uppercase tracking-[0.18em] text-steel">{source.domain}</div>
                    <p className="mt-2 text-sm leading-7 text-steel">{source.snippet}</p>
                  </a>
                ))}
              </div>
            </CardContent>
          </Card>
        </aside>
      </section>
    </main>
  );
}
