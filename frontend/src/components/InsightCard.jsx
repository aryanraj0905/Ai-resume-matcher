import { AlertTriangle, Info, Lightbulb } from "lucide-react";

const SEVERITY_STYLES = {
  high: {
    icon: AlertTriangle,
    ring: "ring-red-200",
    iconWrap: "bg-red-50 text-red-600",
    badge: "bg-red-50 text-red-700",
  },
  medium: {
    icon: Lightbulb,
    ring: "ring-amber-200",
    iconWrap: "bg-amber-50 text-amber-600",
    badge: "bg-amber-50 text-amber-700",
  },
  low: {
    icon: Info,
    ring: "ring-slate-200",
    iconWrap: "bg-slate-100 text-slate-500",
    badge: "bg-slate-100 text-slate-600",
  },
};

export default function InsightCard({ insight }) {
  const style = SEVERITY_STYLES[insight.severity] ?? SEVERITY_STYLES.low;
  const Icon = style.icon;

  return (
    <div className={`rounded-xl bg-white p-4 ring-1 ${style.ring} shadow-sm`}>
      <div className="flex items-start gap-3">
        <span className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-lg ${style.iconWrap}`}>
          <Icon size={16} />
        </span>
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex flex-wrap items-center gap-2">
            <span className={`rounded-full px-2 py-0.5 text-[11px] font-semibold uppercase tracking-wide ${style.badge}`}>
              {insight.category}
            </span>
          </div>
          <p className="text-sm font-medium text-slate-800">{insight.message}</p>
          <p className="mt-1 text-sm text-slate-500">{insight.why}</p>
        </div>
      </div>
    </div>
  );
}
