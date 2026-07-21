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
import { homepageEvidenceStates, reportData, siteCopy } from "./content/siteContent";

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
          <div className="evidence-state-grid">
            {homepageEvidenceStates.map((state) => (
              <article key={state.label} className={`evidence-state evidence-state-${state.label.toLowerCase()}`}>
                <h3>{state.label}</h3>
                <p>{state.description}</p>
              </article>
            ))}
          </div>
        </section>
        <EvidenceFlow />
        <OutputCards />
        <section className="demo-section" aria-labelledby="demo-title">
          <div>
            <p className="eyebrow">Demo preview</p>
            <h2 id="demo-title">{siteCopy.demo.title}</h2>
            <p>{siteCopy.demo.description}</p>
            <article className="demo-excerpt" aria-label="Compact report excerpt">
              <p className="demo-excerpt-label">{siteCopy.demo.excerpt.label}</p>
              <p className="demo-excerpt-decision">{siteCopy.demo.excerpt.recommendation}</p>
              <p>{siteCopy.demo.excerpt.fact}</p>
              <code>{siteCopy.demo.excerpt.citation}</code>
            </article>
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
    <main className="not-found-page">
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
      <Link className="button button-primary" to="/">
        Back to home
      </Link>
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
