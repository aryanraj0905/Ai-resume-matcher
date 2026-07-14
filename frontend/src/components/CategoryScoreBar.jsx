const BAR_COLOR_BY_SCORE = (score) => {
  if (score >= 80) return "bg-emerald-500";
  if (score >= 60) return "bg-brand-500";
  if (score >= 40) return "bg-amber-500";
  return "bg-red-500";
};

export default function CategoryScoreBar({ label, score, weight }) {
  const hasScore = typeof score === "number";
  const displayScore = hasScore ? Math.round(score) : null;

  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-sm font-medium text-slate-700">{label}</span>
        <span className="text-sm font-semibold text-slate-900">
          {hasScore ? `${displayScore}%` : "N/A"}
          {weight ? <span className="ml-1 text-xs font-normal text-slate-400">({weight}%)</span> : null}
        </span>
      </div>
      <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className={`h-full rounded-full transition-all duration-700 ease-out ${
            hasScore ? BAR_COLOR_BY_SCORE(displayScore) : "bg-slate-200"
          }`}
          style={{ width: `${hasScore ? displayScore : 0}%` }}
        />
      </div>
    </div>
  );
}
