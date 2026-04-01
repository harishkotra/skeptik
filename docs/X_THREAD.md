# X Thread

1. Built `Skeptik`: a zero-editorial AI newsroom that produces serious stories through a fully autonomous reporting pipeline.

2. The goal was explicit: not an AI summarizer, not a chatbot with headlines, but a product that feels like a credible newsroom.

3. Stack:
   Agno + Featherless.ai (`moonshotai/Kimi-K2.5`) + Tavily + Bright Data + Virlo + FastAPI + Next.js + Tailwind.

4. Virlo is deeply integrated, not decorative.
   It drives:
   - topic selection
   - signal strength
   - urgency
   - “why you’re seeing this”

5. The backend runs a multi-agent desk:
   - Topic Agent
   - Reporter Agent
   - Skeptic Agent
   - Fact-check Agent
   - Editor Agent

6. The important part is the controller logic.
   Stories get:
   - rejected on false claims
   - revised when skeptic pressure is high
   - published only when confidence clears the gate

7. Ingestion is two-stage:
   Tavily finds the reporting surface.
   Bright Data extracts fuller page content.
   That becomes a structured knowledge pack for the agents.

8. I also exposed the editorial chain in the UI:
   readers can inspect
   - reporter draft summary
   - skeptic critique
   - fact-check results
   - sources and domain counts

9. One of the hard parts wasn’t writing prompts.
   It was making the app honest when providers fail.

10. The app now runs in live-only mode:
   - no fake Virlo trends
   - no seeded article fallbacks
   - no silent provider substitution
   If an API breaks, the UI shows it.

11. Frontend goal: make it feel like a newsroom, not a dashboard.
   So the homepage now has:
   - a true lead story
   - ranked story cards
   - an editorial rail with live desk state

12. Tech choices worked well because each tool had a real role:
   - Agno = stage orchestration
   - Featherless = model inference
   - Tavily = retrieval + verification
   - Bright Data = extraction
   - Virlo = ranking brain

13. The best part of the build:
   the product explains itself in under 30 seconds.
   You land, see the lead story, and understand how it was made.

14. Virlo + Tavily are live, and Bright Data is wired as a real dependency with visible extraction failures instead of fake success.

15. If I keep pushing it, next adds are:
   - Postgres + migrations
   - Playwright smoke tests
   - stronger source scoring
   - richer claim evidence rendering

16. This was a good reminder that AI products get better when you put rigor in the system, not just eloquence in the model.

17. Built by Harish Kotra
   https://harishkotra.me

18. Other builds:
   https://dailybuild.xyz
