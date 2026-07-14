import {
  Bar,
  BarChart,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const SCORE_COLOR = (score) => {
  if (score >= 80) return "#16a34a";
  if (score >= 60) return "#6366f1";
  if (score >= 40) return "#d97706";
  return "#dc2626";
};

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null;
  const { label, score } = payload[0].payload;

  return (
    <div className="rounded-lg bg-slate-900 px-3 py-2 text-xs font-medium text-white shadow-lg">
      {label}: {Math.round(score)}%
    </div>
  );
}

export default function CategoryScoreChart({ data }) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 4, right: 28, bottom: 4, left: 4 }}
          barCategoryGap={18}
        >
          <XAxis type="number" domain={[0, 100]} hide />
          <YAxis
            type="category"
            dataKey="label"
            width={110}
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#475569", fontSize: 13 }}
          />
          <Tooltip content={<ChartTooltip />} cursor={{ fill: "#f1f5f9" }} />
          <Bar dataKey="score" radius={[6, 6, 6, 6]} maxBarSize={22}>
            {data.map((entry) => (
              <Cell key={entry.label} fill={SCORE_COLOR(entry.score)} />
            ))}
            <LabelList
              dataKey="score"
              position="right"
              formatter={(value) => `${Math.round(value)}%`}
              style={{ fill: "#334155", fontSize: 12, fontWeight: 600 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
