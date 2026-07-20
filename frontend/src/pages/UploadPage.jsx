import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ArrowRight, ClipboardPaste, Info } from "lucide-react";
import FileDropzone from "../components/FileDropzone.jsx";

const MIN_JOB_DESCRIPTION_LENGTH = 20;

export default function UploadPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [file, setFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [formError, setFormError] = useState(null);
  const notice = location.state?.notice;

  const handleFileSelected = (selectedFile, error) => {
    setFile(selectedFile);
    setFileError(error);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    setFormError(null);

    if (!file) {
      setFormError("Please upload your resume as a PDF.");
      return;
    }

    if (jobDescription.trim().length < MIN_JOB_DESCRIPTION_LENGTH) {
      setFormError(`Job description must be at least ${MIN_JOB_DESCRIPTION_LENGTH} characters.`);
      return;
    }

    navigate("/analyzing", { state: { file, jobDescription } });
  };

  return (
    <div className="mx-auto max-w-3xl px-6 py-14">
      <div className="mb-10 text-center">
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          Let's analyze your fit
        </h1>
        <p className="mt-3 text-slate-600">
          Upload your resume and paste the job description you're targeting.
        </p>
      </div>

      {notice && (
        <div className="mb-6 flex items-start gap-2.5 rounded-lg bg-brand-50 px-4 py-3 text-sm font-medium text-brand-700 ring-1 ring-brand-100">
          <Info size={16} className="mt-0.5 shrink-0" />
          {notice}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-8 rounded-2xl bg-white p-8 shadow-sm ring-1 ring-slate-200">
        <div>
          <label className="mb-2 block text-sm font-semibold text-slate-800">1. Your resume</label>
          <FileDropzone file={file} onFileSelected={handleFileSelected} error={fileError} />
        </div>

        <div>
          <label htmlFor="job-description" className="mb-2 block text-sm font-semibold text-slate-800">
            2. Job description
          </label>
          <div className="relative">
            <textarea
              id="job-description"
              value={jobDescription}
              onChange={(event) => setJobDescription(event.target.value)}
              rows={10}
              placeholder="Paste the full job description here, including requirements and responsibilities..."
              className="w-full resize-y rounded-xl border border-slate-300 bg-slate-50 p-4 text-sm text-slate-800 placeholder:text-slate-400 focus:border-brand-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-brand-100"
            />
            {jobDescription.trim().length === 0 && (
              <span className="pointer-events-none absolute right-4 top-4 flex items-center gap-1 text-xs text-slate-400">
                <ClipboardPaste size={14} />
                Paste here
              </span>
            )}
          </div>
          <p className="mt-1.5 text-right text-xs text-slate-400">
            {jobDescription.trim().length} characters
          </p>
        </div>

        {formError && (
          <div className="rounded-lg bg-red-50 px-4 py-3 text-sm font-medium text-red-700 ring-1 ring-red-100">
            {formError}
          </div>
        )}

        <button
          type="submit"
          className="flex w-full items-center justify-center gap-2 rounded-xl bg-slate-900 px-6 py-3.5 text-base font-semibold text-white shadow-md transition hover:bg-slate-800"
        >
          Analyze match
          <ArrowRight size={18} />
        </button>
      </form>
    </div>
  );
}
