# LinkedIn Post

I built `Skeptik`, an AI-native autonomous newsroom designed around one constraint:

Don’t build another AI news summarizer.

The goal was to create a product that feels like a credible newsroom, where serious articles are produced through a fully autonomous pipeline with no human in the editorial path.

### What it does

Skeptik selects topics using Virlo signals, builds source packs with Tavily and Bright Data, then routes each story through a multi-agent editorial chain:

- Topic Agent
- Reporter Agent
- Skeptic Agent
- Fact-check Agent
- Editor Agent

Each article is scored, challenged, verified, and only published if it passes deterministic quality gates.

### Tech stack

- Agno for orchestration
- Featherless.ai for inference using `moonshotai/Kimi-K2.5`
- Tavily for search and verification
- Bright Data for content extraction
- Virlo for trend ranking and urgency
- FastAPI for the backend
- Next.js + Tailwind for the frontend

### What I focused on

I wanted the system to feel rigorous, not performative.

So instead of exposing raw prompts, the UI shows:

- why a story is rising now
- confidence and disagreement scores
- number of sources and unique domains
- skeptic critique
- fact-check outcomes

I also moved the app into strict live-integration mode:

- no fake trend signals
- no seeded fallback articles
- no hidden provider substitution

If Virlo, Tavily, Bright Data, or Featherless fail, the app surfaces that directly in the interface.

### A key engineering lesson

The hardest part was not “getting the model to write.”

The harder part was building system behavior around it:

- deterministic publish/reject logic
- explicit provider health and failure visibility
- structured article outputs
- a frontend that looks like a publication instead of a dashboard

### What’s next

There’s still room to push this further with:

- Postgres + migrations
- better source freshness scoring
- richer evidence rendering for fact checks
- end-to-end Playwright testing
- deeper ranking explanations from Virlo

This project reinforced a belief I keep coming back to:

The best AI products are not just model wrappers. They are systems with judgment, structure, and clear user trust signals.

Built by Harish Kotra: https://harishkotra.me  
More builds: https://dailybuild.xyz
