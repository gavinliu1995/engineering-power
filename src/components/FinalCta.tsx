import { Link } from "react-router-dom";
import { siteCopy } from "../content/siteContent";

export function FinalCta() {
  const copy = siteCopy.fullLifecycle.finalCta;

  return (
    <section className="final-cta" aria-label={copy.title}>
      <div className="final-cta-inner">
        <h2>{copy.title}</h2>
        <Link className="button button-primary" to="/start" aria-label={copy.title}>{copy.cta}</Link>
      </div>
    </section>
  );
}
