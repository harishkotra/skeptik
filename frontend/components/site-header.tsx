import Link from "next/link";

export function SiteHeader() {
  return (
    <header className="border-b border-black/10 bg-white/45 backdrop-blur-sm">
      <div className="mx-auto flex max-w-6xl items-end justify-between gap-6 px-6 py-5">
        <div>
          <div className="text-[11px] uppercase tracking-[0.26em] text-steel">Autonomous News Desk</div>
          <Link href="/" className="mt-1 block font-display text-3xl text-ink">
            Skeptik
          </Link>
        </div>
        <div className="text-right text-xs uppercase tracking-[0.22em] text-steel">
          <div>Zero-Editorial AI Newsroom</div>
          <div className="mt-1 text-[11px] text-steel/80">Trending via Virlo</div>
        </div>
      </div>
    </header>
  );
}
