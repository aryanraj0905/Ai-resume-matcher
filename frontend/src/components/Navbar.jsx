import { Link, useLocation } from "react-router-dom";
import { Sparkles } from "lucide-react";

export default function Navbar() {
  const location = useLocation();
  const isLanding = location.pathname === "/";

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/70 bg-white/80 backdrop-blur-md">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <Link to="/" className="flex items-center gap-2 font-semibold text-slate-900">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-brand-500 to-accent-400 text-white shadow-sm">
            <Sparkles size={18} />
          </span>
          <span className="text-lg tracking-tight">ResumeMatch AI</span>
        </Link>

        <div className="flex items-center gap-3">
          {isLanding && (
            <a
              href="#how-it-works"
              className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 sm:block"
            >
              How it works
            </a>
          )}
          <Link
            to="/upload"
            className="rounded-lg bg-slate-900 px-4 py-2 text-sm font-medium text-white shadow-sm transition hover:bg-slate-800"
          >
            Analyze my resume
          </Link>
        </div>
      </nav>
    </header>
  );
}
