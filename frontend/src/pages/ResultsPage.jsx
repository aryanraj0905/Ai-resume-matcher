import { useMemo } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import {
  Briefcase,
  GraduationCap,
  Layers,
  Mail,
  Phone,
  RefreshCw,
} from "lucide-react";
import { GithubIcon, LinkedinIcon } from "../components/BrandIcons.jsx";
import ScoreRing from "../components/ScoreRing.jsx";
import CategoryScoreBar from "../components/CategoryScoreBar.jsx";
import CategoryScoreChart from "../components/CategoryScoreChart.jsx";
import SkillBadge from "../components/SkillBadge.jsx";
import InsightCard from "../components/InsightCard.jsx";

const CATEGORY_LABELS = {
  skills: "Skills",
  experience: "Experience",
  education: "Education",
  projects: "Projects",
  semantic_similarity: "Semantic Similarity",
};

function StatPill({ icon: Icon, label, value }) {
  return (
    <div className="flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 ring-1 ring-slate-200">
      <Icon size={15} className="shrink-0 text-slate-400" />
      <span className="truncate text-sm text-slate-600">{value ?? <em className="text-slate-400">{label} not found</em>}</span>
    </div>
  );
}

export default function ResultsPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { resume, match } = location.state || {};

  const chartData = useMemo(() => {
    if (!match) return [];
    return Object.entries(match.category_scores)
      .filter(([, score]) => typeof score === "number")
      .map(([key, score]) => ({ label: CATEGORY_LABELS[key] || key, score }));
  }, [match]);

  if (!resume || !match) {
    return (
      <Navigate
        to="/upload"
        replace
        state={{ notice: "Your results have expired. Please run a new analysis." }}
      />
    );
  }

  const { recommendations } = match;

  return (
    <div className="mx-auto max-w-6xl px-6 py-12">
      <div className="mb-8 flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
            Match Report
          </h1>
          <p className="mt-1 text-slate-500">{resume.filename}</p>
        </div>
        <button
          onClick={() => navigate("/upload")}
          className="inline-flex items-center gap-2 self-start rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
        >
          <RefreshCw size={15} />
          Analyze another
        </button>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Overall score card */}
        <div className="flex flex-col items-center justify-center rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200 lg:col-span-1">
          <ScoreRing score={match.overall_score} />
          <p className="mt-6 text-center text-sm leading-relaxed text-slate-600">
            {recommendations.summary}
          </p>
        </div>

        {/* Category scores */}
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 lg:col-span-2">
          <h2 className="mb-5 font-semibold text-slate-900">Category Breakdown</h2>
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
            <div className="space-y-5">
              {Object.entries(match.category_scores).map(([key, score]) => (
                <CategoryScoreBar
                  key={key}
                  label={CATEGORY_LABELS[key] || key}
                  score={score}
                  weight={Math.round((match.category_weights?.[key] ?? 0) * 100)}
                />
              ))}
            </div>
            <CategoryScoreChart data={chartData} />
          </div>
        </div>
      </div>

      {/* Contact & quick stats */}
      <div className="mt-6 grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
        <StatPill icon={Mail} label="Email" value={resume.email} />
        <StatPill icon={Phone} label="Phone" value={resume.phone} />
        <StatPill icon={GithubIcon} label="GitHub" value={resume.github} />
        <StatPill icon={LinkedinIcon} label="LinkedIn" value={resume.linkedin} />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Skills breakdown */}
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200 lg:col-span-2">
          <h2 className="mb-4 font-semibold text-slate-900">Skills Breakdown</h2>

          <div className="space-y-4">
            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Matched ({match.matched_skills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {match.matched_skills.length ? (
                  match.matched_skills.map((skill) => (
                    <SkillBadge key={skill} label={skill} variant="matched" />
                  ))
                ) : (
                  <p className="text-sm text-slate-400">No matched skills found.</p>
                )}
              </div>
            </div>

            <div>
              <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                Missing &ndash; Required ({match.missing_required_skills.length})
              </p>
              <div className="flex flex-wrap gap-2">
                {match.missing_required_skills.length ? (
                  match.missing_required_skills.map((skill) => (
                    <SkillBadge key={skill} label={skill} variant="missing" />
                  ))
                ) : (
                  <p className="text-sm text-slate-400">None — great coverage!</p>
                )}
              </div>
            </div>

            {match.missing_preferred_skills.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Missing &ndash; Preferred ({match.missing_preferred_skills.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {match.missing_preferred_skills.map((skill) => (
                    <SkillBadge key={skill} label={skill} variant="missing" />
                  ))}
                </div>
              </div>
            )}

            {match.extra_skills.length > 0 && (
              <div>
                <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Additional skills on your resume ({match.extra_skills.length})
                </p>
                <div className="flex flex-wrap gap-2">
                  {match.extra_skills.map((skill) => (
                    <SkillBadge key={skill} label={skill} variant="extra" />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Resume summary */}
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
          <h2 className="mb-4 font-semibold text-slate-900">Resume Summary</h2>
          <ul className="space-y-3 text-sm text-slate-600">
            <li className="flex items-center gap-2.5">
              <Briefcase size={16} className="text-slate-400" />
              {resume.experience.length} experience {resume.experience.length === 1 ? "entry" : "entries"}
            </li>
            <li className="flex items-center gap-2.5">
              <Layers size={16} className="text-slate-400" />
              {resume.projects.length} {resume.projects.length === 1 ? "project" : "projects"}
            </li>
            <li className="flex items-center gap-2.5">
              <GraduationCap size={16} className="text-slate-400" />
              {resume.education.length} education {resume.education.length === 1 ? "entry" : "entries"}
            </li>
            <li className="flex items-center gap-2.5">
              <Layers size={16} className="text-slate-400" />
              {resume.certifications.length} {resume.certifications.length === 1 ? "certification" : "certifications"}
            </li>
          </ul>
        </div>
      </div>

      {/* AI Recommendations */}
      <div className="mt-6 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-slate-200">
        <h2 className="mb-4 font-semibold text-slate-900">AI Recommendations</h2>
        <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
          {recommendations.insights.map((insight, index) => (
            <InsightCard key={index} insight={insight} />
          ))}
        </div>

        {recommendations.suggested_resume_bullets.length > 0 && (
          <div className="mt-6 rounded-xl bg-brand-50/60 p-5 ring-1 ring-brand-100">
            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-brand-700">
              Suggested bullets to add
            </p>
            <ul className="list-inside list-disc space-y-1.5 text-sm text-slate-700">
              {recommendations.suggested_resume_bullets.map((bullet, index) => (
                <li key={index}>{bullet}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
