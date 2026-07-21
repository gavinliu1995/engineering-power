import { evidenceFlow, siteCopy } from "../content/siteContent";

export function EvidenceFlow() {
  return (
    <section className="flow-section" aria-labelledby="flow-title">
      <div className="section-heading">
        <p className="eyebrow">{siteCopy.flow.eyebrow}</p>
        <h2 id="flow-title">{siteCopy.flow.title}</h2>
      </div>
      <ol className="evidence-flow">
        {evidenceFlow.map((step, index) => (
          <li key={step}>
            <span className="step-number">0{index + 1}</span>
            <span>{step}</span>
          </li>
        ))}
      </ol>
    </section>
  );
}
