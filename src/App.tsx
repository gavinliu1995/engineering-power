import { Link, Route, Routes } from "react-router-dom";
import { EvidenceFlow } from "./components/EvidenceFlow";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { OutputCards } from "./components/OutputCards";
import { TrustBoundary } from "./components/TrustBoundary";
import { EvidenceSection } from "./components/EvidenceSection";
import { ReleaseDecision } from "./components/ReleaseDecision";
import { ReportHeader } from "./components/ReportHeader";
import { ValidationMatrix } from "./components/ValidationMatrix";
import { reportData, siteCopy } from "./content/siteContent";

function HomePage() {
  return (
    <div className="page-shell" id="top">
      <Header />
      <main>
        <Hero />
        <section className="why-section" aria-labelledby="why-title">
          <p className="eyebrow">Why it matters</p>
          <h2 id="why-title">{siteCopy.whyItMatters.title}</h2>
          <p>{siteCopy.whyItMatters.description}</p>
        </section>
        <EvidenceFlow />
        <OutputCards />
        <section className="demo-section" aria-labelledby="demo-title">
          <div>
            <p className="eyebrow">Demo preview</p>
            <h2 id="demo-title">{siteCopy.demo.title}</h2>
            <p>{siteCopy.demo.description}</p>
          </div>
          <Link className="button button-secondary" to="/demo-report">
            {siteCopy.demo.cta}
          </Link>
        </section>
        <TrustBoundary />
      </main>
      <Footer />
    </div>
  );
}

function DemoReportPage() {
  return (
    <main className="report-page">
      <ReportHeader />
      <ReleaseDecision />
      <section className="api-summary" aria-labelledby="api-summary-title">
        <p className="eyebrow">API contract delta</p>
        <h2 id="api-summary-title">Compatibility summary</h2>
        <p>{reportData.apiCompatibility}</p>
      </section>
      <EvidenceSection label="Facts" tone="fact" items={reportData.facts} />
      <EvidenceSection label="Inferences" tone="inference" items={reportData.inferences} />
      <EvidenceSection label="Unknowns" tone="unknown" items={reportData.unknowns} />
      <ValidationMatrix />
    </main>
  );
}

function NotFoundPage() {
  return (
    <main>
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/demo-report" element={<DemoReportPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
