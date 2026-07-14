import { Check, Plus, X } from "lucide-react";

const VARIANTS = {
  matched: "bg-emerald-50 text-emerald-700 ring-emerald-600/20",
  missing: "bg-red-50 text-red-700 ring-red-600/10",
  extra: "bg-slate-100 text-slate-600 ring-slate-500/10",
};

const ICONS = {
  matched: Check,
  missing: X,
  extra: Plus,
};

export default function SkillBadge({ label, variant = "extra" }) {
  const Icon = ICONS[variant];

  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-medium ring-1 ring-inset ${VARIANTS[variant]}`}
    >
      <Icon size={12} strokeWidth={3} />
      {label}
    </span>
  );
}
