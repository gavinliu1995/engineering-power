import { howItWorksSteps, siteCopy } from "../content/siteContent";

export function HowItWorks() {
  const copy = siteCopy.fullLifecycle.howItWorks;

  return (
    <section id="how-it-works" className="how-it-works" aria-labelledby="how-it-works-title">
      <div className="section-heading">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h2 id="how-it-works-title">{copy.title}</h2>
      </div>
      <ol className="workflow-list">
        {howItWorksSteps.map((step) => (
          <li className="workflow-step" key={step.number}>
            <span>{step.number}</span>
            <h3>{step.title}</h3>
            <p>{step.description}</p>
          </li>
        ))}
      </ol>
      <aside className="analysis-boundary" aria-label="Where analysis runs">
        <strong>Where analysis runs</strong>
        <p>{copy.boundary}</p>
      </aside>
    </section>
  );
}
