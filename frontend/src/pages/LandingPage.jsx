import { Link } from "react-router-dom";
import { BrainCircuit, FileSearch, Gauge, Sparkles, Target, Zap } from "lucide-react";

const FEATURES = [
  {
    icon: BrainCircuit,
    title: "Real Semantic Matching",
    description:
      "Powered by Sentence Transformers, not just keyword overlap — your resume is understood in context.",
  },
  {
    icon: Gauge,
    title: "Category-by-Category Scoring",
    description:
      "See exactly how you score on Skills, Experience, Education, Projects, and overall Semantic Fit.",
  },
  {
    icon: Target,
    title: "Missing Skills, Pinpointed",
    description:
      "Instantly see which required and preferred skills from the job are missing from your resume.",
  },
  {
    icon: Sparkles,
    title: "Explained AI Recommendations",
    description:
      "Every suggestion tells you why it matters — not generic advice, but reasoning tied to your score.",
  },
];

const STEPS = [
  {
    step: "01",
    title: "Upload your resume",
    description: "Drop in your PDF resume — we parse skills, experience, education, and projects automatically.",
  },
  {
    step: "02",
    title: "Paste a job description",
    description: "Add the job posting you're targeting so the AI knows what to match against.",
  },
  {
    step: "03",
    title: "Get your match report",
    description: "Receive a full compatibility breakdown with actionable, explained recommendations.",
  },
];

export default function LandingPage() {
  return (
    <div>
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-brand-50 via-white to-white" />
        <div className="mx-auto flex max-w-6xl flex-col items-center px-6 pb-20 pt-16 text-center sm:pt-24">
          <span className="mb-6 inline-flex items-center gap-2 rounded-full border border-brand-200 bg-white px-4 py-1.5 text-xs font-medium text-brand-700 shadow-sm">
            <Zap size={14} className="text-brand-500" />
            AI-powered resume intelligence
          </span>
          <h1 className="max-w-3xl text-4xl font-bold tracking-tight text-slate-900 sm:text-6xl">
            Know exactly how well your resume matches{" "}
            <span className="bg-gradient-to-r from-brand-600 to-accent-500 bg-clip-text text-transparent">
              any job
            </span>
          </h1>
          <p className="mt-6 max-w-2xl text-lg text-slate-600">
            Upload your resume and a job description to get an instant, AI-driven compatibility
            score — backed by real semantic similarity, not just keyword counting.
          </p>
          <div className="mt-10 flex flex-col items-center gap-3 sm:flex-row">
            <Link
              to="/upload"
              className="rounded-xl bg-slate-900 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-slate-900/10 transition hover:bg-slate-800"
            >
              Analyze my resume — it's free
            </Link>
            <a
              href="#how-it-works"
              className="rounded-xl px-7 py-3.5 text-base font-semibold text-slate-600 transition hover:text-slate-900"
            >
              See how it works
            </a>
          </div>
        </div>
      </section>

      <section className="border-y border-slate-200 bg-white py-16">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">
              More than a keyword checker
            </h2>
            <p className="mt-3 text-slate-600">
              A real matching engine that reasons about your resume the way a recruiter does.
            </p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {FEATURES.map(({ icon: Icon, title, description }) => (
              <div
                key={title}
                className="rounded-2xl border border-slate-200 bg-slate-50/60 p-6 transition hover:border-brand-200 hover:bg-white hover:shadow-md"
              >
                <span className="mb-4 flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-accent-400 text-white shadow-sm">
                  <Icon size={20} />
                </span>
                <h3 className="font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section id="how-it-works" className="py-20">
        <div className="mx-auto max-w-6xl px-6">
          <div className="mx-auto max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight text-slate-900">How it works</h2>
            <p className="mt-3 text-slate-600">Three steps to a full match report.</p>
          </div>
          <div className="mt-12 grid grid-cols-1 gap-8 sm:grid-cols-3">
            {STEPS.map(({ step, title, description }) => (
              <div key={step} className="relative rounded-2xl bg-white p-6 text-left shadow-sm ring-1 ring-slate-200">
                <span className="text-3xl font-bold text-brand-100">{step}</span>
                <h3 className="mt-2 font-semibold text-slate-900">{title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-600">{description}</p>
              </div>
            ))}
          </div>
          <div className="mt-14 flex justify-center">
            <Link
              to="/upload"
              className="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-brand-600 to-accent-500 px-7 py-3.5 text-base font-semibold text-white shadow-lg shadow-brand-600/20 transition hover:opacity-90"
            >
              <FileSearch size={18} />
              Try it with your resume
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
