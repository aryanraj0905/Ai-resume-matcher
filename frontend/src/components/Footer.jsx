export default function Footer() {
  return (
    <footer className="border-t border-slate-200 bg-white">
      <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-3 px-6 py-8 text-sm text-slate-500 sm:flex-row">
        <p>© {new Date().getFullYear()} ResumeMatch AI. Built for demonstration purposes.</p>
        <p className="text-slate-400">Powered by FastAPI, Sentence Transformers &amp; React</p>
      </div>
    </footer>
  );
}
