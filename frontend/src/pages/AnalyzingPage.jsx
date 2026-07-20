import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { AlertTriangle, FileSearch } from "lucide-react";
import { getFriendlyErrorMessage, matchResumeToJob, uploadResume } from "../api/client.js";

const STEPS = [
  "Parsing your resume...",
  "Extracting skills, experience & projects...",
  "Comparing against the job description...",
  "Running semantic similarity analysis...",
  "Generating AI recommendations...",
];

export default function AnalyzingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [stepIndex, setStepIndex] = useState(0);
  const [error, setError] = useState(null);

  const { file, jobDescription } = location.state || {};

  useEffect(() => {
    if (!file || !jobDescription) {
      navigate("/upload", {
        replace: true,
        state: { notice: "Please upload your resume and job description to get started." },
      });
      return;
    }

    // React StrictMode intentionally mounts effects twice in development.
    // Rather than fight that by aborting the in-flight request (which would
    // leave a real navigation's request half-cancelled), we let it run to
    // completion and simply ignore its result if this effect instance was
    // superseded before it finished.
    let ignoreResult = false;

    const stepTimer = setInterval(() => {
      setStepIndex((current) => Math.min(current + 1, STEPS.length - 1));
    }, 1600);

    (async () => {
      try {
        const uploadResult = await uploadResume(file);
        const matchResult = await matchResumeToJob({
          resumeId: uploadResult.resume_id,
          description: jobDescription,
        });

        if (ignoreResult) return;

        clearInterval(stepTimer);
        setStepIndex(STEPS.length - 1);

        setTimeout(() => {
          if (ignoreResult) return;
          navigate("/results", {
            replace: true,
            state: { resume: uploadResult, match: matchResult },
          });
        }, 500);
      } catch (err) {
        if (ignoreResult) return;
        clearInterval(stepTimer);
        setError(getFriendlyErrorMessage(err));
      }
    })();

    return () => {
      ignoreResult = true;
      clearInterval(stepTimer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  if (error) {
    return (
      <div className="mx-auto flex max-w-lg flex-col items-center px-6 py-24 text-center">
        <span className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-red-50 text-red-600">
          <AlertTriangle size={28} />
        </span>
        <h1 className="text-2xl font-bold text-slate-900">Something went wrong</h1>
        <p className="mt-2 text-slate-600">{error}</p>
        <button
          onClick={() => navigate("/upload")}
          className="mt-8 rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white shadow-sm transition hover:bg-slate-800"
        >
          Try again
        </button>
      </div>
    );
  }

  const progressPercent = ((stepIndex + 1) / STEPS.length) * 100;

  return (
    <div className="mx-auto flex max-w-lg flex-col items-center px-6 py-24 text-center">
      <span className="relative mb-8 flex h-20 w-20 items-center justify-center rounded-full bg-brand-100 text-brand-600">
        <span className="absolute inset-0 animate-ping rounded-full bg-brand-200 opacity-75" />
        <FileSearch size={32} className="relative" />
      </span>

      <h1 className="text-2xl font-bold text-slate-900">Analyzing your resume</h1>
      <p className="mt-2 min-h-[1.5rem] text-slate-600">{STEPS[stepIndex]}</p>

      <div className="mt-8 h-2 w-full overflow-hidden rounded-full bg-slate-100">
        <div
          className="h-full rounded-full bg-gradient-to-r from-brand-500 to-accent-400 transition-all duration-700 ease-out"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <ul className="mt-8 w-full space-y-2 text-left">
        {STEPS.map((step, index) => (
          <li
            key={step}
            className={`flex items-center gap-2.5 text-sm transition ${
              index <= stepIndex ? "text-slate-700" : "text-slate-300"
            }`}
          >
            <span
              className={`h-1.5 w-1.5 shrink-0 rounded-full ${
                index <= stepIndex ? "bg-brand-500" : "bg-slate-200"
              }`}
            />
            {step}
          </li>
        ))}
      </ul>
    </div>
  );
}
