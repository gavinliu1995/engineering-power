import { siteCopy, trustBoundaries } from "../content/siteContent";

export function TrustBoundary() {
  return (
    <section className="trust-section" aria-labelledby="trust-title">
      <div className="section-heading">
        <p className="eyebrow">{siteCopy.trust.eyebrow}</p>
        <h2 id="trust-title">{siteCopy.trust.title}</h2>
      </div>
      <div className="trust-list">
        {trustBoundaries.map((boundary) => (
          <article key={boundary.title}>
            <h3>{boundary.title}</h3>
            <p>{boundary.description}</p>
          </article>
        ))}
      </div>
      <p className="static-demo-disclosure">{siteCopy.trust.disclosure}</p>
    </section>
  );
}
