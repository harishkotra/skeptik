export function FooterRail() {
  return (
    <>
      <aside className="fixed bottom-6 left-6 z-20 hidden w-64 xl:block">
        <div className="rounded-3xl border border-black/10 bg-white/80 p-5 shadow-editorial backdrop-blur-sm">
          <div className="text-[11px] uppercase tracking-[0.22em] text-steel">Built By</div>
          <a
            href="https://harishkotra.me"
            target="_blank"
            rel="noreferrer"
            className="mt-2 block font-display text-2xl text-ink transition-opacity hover:opacity-70"
          >
            Harish Kotra
          </a>
          <a
            href="https://dailybuild.xyz"
            target="_blank"
            rel="noreferrer"
            className="mt-4 block text-sm leading-7 text-steel transition-opacity hover:opacity-70"
          >
            Checkout my other builds
          </a>
        </div>
      </aside>

      <footer className="border-t border-black/10 px-6 py-8 xl:hidden">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 text-sm text-steel">
          <a href="https://harishkotra.me" target="_blank" rel="noreferrer" className="font-medium text-ink">
            Built By Harish Kotra
          </a>
          <a href="https://dailybuild.xyz" target="_blank" rel="noreferrer">
            Checkout my other builds
          </a>
        </div>
      </footer>
    </>
  );
}
