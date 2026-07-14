import { useCallback, useRef, useState } from "react";
import { FileText, UploadCloud, X } from "lucide-react";

const MAX_FILE_BYTES = 10 * 1024 * 1024;

function formatBytes(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function FileDropzone({ file, onFileSelected, error }) {
  const [isDragActive, setIsDragActive] = useState(false);
  const inputRef = useRef(null);

  const validateAndSet = useCallback(
    (candidate) => {
      if (!candidate) return;

      if (candidate.type !== "application/pdf" && !candidate.name.toLowerCase().endsWith(".pdf")) {
        onFileSelected(null, "Only PDF files are supported.");
        return;
      }

      if (candidate.size > MAX_FILE_BYTES) {
        onFileSelected(null, "File is too large. Maximum size is 10 MB.");
        return;
      }

      onFileSelected(candidate, null);
    },
    [onFileSelected]
  );

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      setIsDragActive(false);
      validateAndSet(event.dataTransfer.files?.[0]);
    },
    [validateAndSet]
  );

  return (
    <div>
      <div
        onDragOver={(event) => {
          event.preventDefault();
          setIsDragActive(true);
        }}
        onDragLeave={() => setIsDragActive(false)}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(event) => {
          if (event.key === "Enter" || event.key === " ") inputRef.current?.click();
        }}
        className={`flex cursor-pointer flex-col items-center justify-center rounded-2xl border-2 border-dashed px-6 py-10 text-center transition ${
          isDragActive
            ? "border-brand-400 bg-brand-50"
            : error
            ? "border-red-300 bg-red-50"
            : "border-slate-300 bg-slate-50 hover:border-brand-300 hover:bg-brand-50/50"
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf,.pdf"
          className="hidden"
          onChange={(event) => validateAndSet(event.target.files?.[0])}
        />

        {file ? (
          <div className="flex items-center gap-3">
            <span className="flex h-11 w-11 items-center justify-center rounded-lg bg-brand-100 text-brand-600">
              <FileText size={22} />
            </span>
            <div className="text-left">
              <p className="max-w-[220px] truncate text-sm font-medium text-slate-800">{file.name}</p>
              <p className="text-xs text-slate-500">{formatBytes(file.size)}</p>
            </div>
            <button
              type="button"
              onClick={(event) => {
                event.stopPropagation();
                onFileSelected(null, null);
                if (inputRef.current) inputRef.current.value = "";
              }}
              className="ml-2 rounded-full p-1.5 text-slate-400 hover:bg-slate-200 hover:text-slate-700"
              aria-label="Remove file"
            >
              <X size={16} />
            </button>
          </div>
        ) : (
          <>
            <span className="mb-3 flex h-12 w-12 items-center justify-center rounded-full bg-brand-100 text-brand-600">
              <UploadCloud size={24} />
            </span>
            <p className="text-sm font-medium text-slate-700">
              Drag &amp; drop your resume PDF here, or click to browse
            </p>
            <p className="mt-1 text-xs text-slate-400">PDF only, up to 10 MB</p>
          </>
        )}
      </div>
      {error && <p className="mt-2 text-sm font-medium text-red-600">{error}</p>}
    </div>
  );
}
