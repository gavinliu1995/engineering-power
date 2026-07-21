import { Link, Route, Routes } from "react-router-dom";
import { EvidenceFlow } from "./components/EvidenceFlow";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { OutputCards } from "./components/OutputCards";
import { TrustBoundary } from "./components/TrustBoundary";
import { siteCopy } from "./content/siteContent";

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
    <main>
      <h1>Demo report</h1>
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
