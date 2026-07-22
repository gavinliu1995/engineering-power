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

function QuickStartPage() {
  return (
    <main className="quick-start-page">
      <p className="eyebrow">Quick start</p>
      <h1>Choose where you use Engineering Power.</h1>
      <p className="quick-start-intro">Select your assistant to see the right installation path. Engineering Power stays focused on cited, decision-ready engineering work.</p>
      <div className="assistant-choice-grid">
        <Link className="assistant-choice assistant-choice-codex" to="/start/codex" aria-label="Use Engineering Power with Codex">
          <span className="guide-step">Option 01</span>
          <h2>Codex</h2>
          <p>Use the Engineering Power plugin inside a Codex task.</p>
          <span className="choice-action">Use Engineering Power with Codex <span aria-hidden="true">→</span></span>
        </Link>
        <Link className="assistant-choice assistant-choice-copilot" to="/start/copilot" aria-label="Use Engineering Power with GitHub Copilot">
          <span className="guide-step">Option 02</span>
          <h2>GitHub Copilot</h2>
          <p>Install the portable Engineering Power skill in your project.</p>
          <span className="choice-action">Use Engineering Power with GitHub Copilot <span aria-hidden="true">→</span></span>
        </Link>
      </div>
    </main>
  );
}

function HostGuidePage({ host }: { host: "codex" | "copilot" }) {
  const isCodex = host === "codex";
  const heading = isCodex ? "Use Engineering Power in Codex." : "Use Engineering Power in GitHub Copilot.";

  return (
    <main className="quick-start-page host-guide-page">
      <Link className="back-link" to="/start">← Choose another assistant</Link>
      <p className="eyebrow">{isCodex ? "Codex plugin" : "Portable agent skill"}</p>
      <h1>{heading}</h1>
      <p className="quick-start-intro">
        {isCodex
          ? "Install the Engineering Power plugin, then describe the repository or pull request you want to understand."
          : "Install Engineering Power into the project where GitHub Copilot works, then reload and verify the skill."}
      </p>
      <ol className="host-guide-steps">
        {isCodex ? (
          <>
            <li><span>01</span><div><h2>Install the plugin</h2><p>Install Engineering Power from your Codex plugin marketplace.</p></div></li>
            <li><span>02</span><div><h2>Start a task</h2><p>Start a new task and describe the repository or pull request you want Engineering Power to analyze.</p></div></li>
            <li><span>03</span><div><h2>Ask for the decision you need</h2><p>Request an evidence-backed answer with facts, inferences, unknowns, and file citations.</p><code>Analyze this pull request with Engineering Power. Separate facts, inferences, and unknowns, with citations.</code></div></li>
          </>
        ) : (
          <>
            <li><span>01</span><div><h2>Install into your project</h2><p>Run the installer from the Engineering Power repository with your project as the target.</p><code>python3 scripts/install_agent_skill.py --host copilot --target-root /path/to/project</code></div></li>
            <li><span>02</span><div><h2>Reload and verify</h2><p>In GitHub Copilot, reload skills and confirm Engineering Power is available.</p><code>/skills reload</code><code>/skills info engineering-power</code></div></li>
            <li><span>03</span><div><h2>Invoke Engineering Power</h2><p>Use <code>/engineering-power</code> when slash invocation is available, then provide a repository, pull request, or local comparison.</p></div></li>
          </>
        )}
      </ol>
      <a className="button button-primary" href="https://github.com/gavinliu1995/engineering-power" target="_blank" rel="noreferrer">View installation files on GitHub</a>
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
      <Route path="/start" element={<QuickStartPage />} />
      <Route path="/start/codex" element={<HostGuidePage host="codex" />} />
      <Route path="/start/copilot" element={<HostGuidePage host="copilot" />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
