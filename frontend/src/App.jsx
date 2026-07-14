import { Route, Routes } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Footer from "./components/Footer.jsx";
import LandingPage from "./pages/LandingPage.jsx";
import UploadPage from "./pages/UploadPage.jsx";
import AnalyzingPage from "./pages/AnalyzingPage.jsx";
import ResultsPage from "./pages/ResultsPage.jsx";

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<UploadPage />} />
          <Route path="/analyzing" element={<AnalyzingPage />} />
          <Route path="/results" element={<ResultsPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
