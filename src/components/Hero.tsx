import { Link } from "react-router-dom";
import { siteCopy } from "../content/siteContent";
import { EvidenceSignalField } from "./EvidenceSignalField";

export function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-layout">
        <div className="hero-content">
          <p className="eyebrow">Evidence-backed engineering intelligence</p>
          <h1 id="hero-title">{siteCopy.hero.title}</h1>
          <p className="hero-copy">{siteCopy.hero.description}</p>
          <Link className="button button-primary" to="/start">
            Get started
          </Link>
        </div>
        <EvidenceSignalField />
      </div>
    </section>
  );
}
