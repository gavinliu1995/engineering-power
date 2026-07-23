import { lifecycleStages, siteCopy } from "../content/siteContent";

export function LifecycleOverview() {
  const copy = siteCopy.fullLifecycle.lifecycle;

  return (
    <section id="capabilities" className="lifecycle-section" aria-labelledby="lifecycle-title">
      <div className="section-heading lifecycle-heading">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h2 id="lifecycle-title">{copy.title}</h2>
        <p>{copy.description}</p>
      </div>
      <ol className="lifecycle-list">
        {lifecycleStages.map((stage) => (
          <li key={stage.id}>
            <article className="lifecycle-stage">
              <span className="stage-number">{stage.number}</span>
              <div>
                <h3>{stage.title}</h3>
                <p>{stage.outcome}</p>
              </div>
              <ul className="lifecycle-capabilities">
                {stage.capabilities.map((capability) => (
                  <li key={capability.name}>
                    <strong>{capability.name}</strong>
                    <span>{capability.description}</span>
                    {capability.role === "supporting" ? <em>Supporting workflow</em> : null}
                  </li>
                ))}
              </ul>
            </article>
          </li>
        ))}
      </ol>
    </section>
  );
}
