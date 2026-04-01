export type FactCheck = {
  claim: string;
  status: "verified" | "uncertain" | "false";
  explanation: string;
  evidence: SourceDocument[];
};

export type SourceDocument = {
  title: string;
  url: string;
  domain: string;
  snippet: string;
  content: string;
  published_at?: string | null;
  relevance_score: number;
};

export type Article = {
  id: number;
  slug: string;
  status: string;
  title: string;
  summary: string;
  content: string;
  topic: {
    topic: string;
    angle: string;
    urgency: string;
    virlo_score: number;
    why_now: string;
    search_queries: string[];
    keywords: string[];
  };
  sources: SourceDocument[];
  claims: string[];
  fact_checks: FactCheck[];
  agent_traces: {
    reporter: Record<string, unknown>;
    skeptic: Record<string, unknown>;
    fact_checker: Record<string, unknown>[];
    editor: Record<string, unknown>;
  };
  why_this_matters: string;
  virlo_score: number;
  confidence_score: number;
  disagreement_score: number;
  number_of_sources: number;
  unique_domains_count: number;
  created_at: string;
};

export type Status = {
  app: string;
  autopilot_enabled: boolean;
  article_count: number;
  published_count: number;
  last_article_at?: string | null;
  integrations: Record<
    string,
    {
      name: string;
      status: "ok" | "error" | "unknown";
      last_checked_at?: string | null;
      last_error?: string | null;
      last_http_status?: number | null;
      details?: string | null;
    }
  >;
};
