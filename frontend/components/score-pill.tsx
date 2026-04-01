type ScorePillProps = {
  label: string;
  value: number;
};

export function ScorePill({ label, value }: ScorePillProps) {
  return (
    <div className="rounded-2xl border border-black/10 bg-white px-4 py-3">
      <div className="text-[11px] uppercase tracking-[0.2em] text-steel">{label}</div>
      <div className="mt-1 text-xl font-semibold text-ink">{Math.round(value * 100)}</div>
    </div>
  );
}
