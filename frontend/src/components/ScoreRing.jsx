const SCORE_COLORS = [
  { min: 80, stroke: "#16a34a", text: "text-emerald-600", label: "Strong Match" },
  { min: 60, stroke: "#6366f1", text: "text-brand-600", label: "Good Match" },
  { min: 40, stroke: "#d97706", text: "text-amber-600", label: "Moderate Match" },
  { min: 0, stroke: "#dc2626", text: "text-red-600", label: "Needs Work" },
];

function getScoreStyle(score) {
  return SCORE_COLORS.find((tier) => score >= tier.min) ?? SCORE_COLORS.at(-1);
}

export default function ScoreRing({ score, size = 180, strokeWidth = 14 }) {
  const clamped = Math.max(0, Math.min(100, score ?? 0));
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (clamped / 100) * circumference;
  const style = getScoreStyle(clamped);

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            fill="none"
            stroke={style.stroke}
            strokeWidth={strokeWidth}
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            className="transition-[stroke-dashoffset] duration-1000 ease-out"
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-4xl font-bold text-slate-900">{Math.round(clamped)}%</span>
          <span className="text-xs font-medium text-slate-400">Overall Match</span>
        </div>
      </div>
      <span className={`text-sm font-semibold ${style.text}`}>{style.label}</span>
    </div>
  );
}
