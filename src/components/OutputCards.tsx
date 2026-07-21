import { outputs, siteCopy } from "../content/siteContent";

export function OutputCards() {
  return (
    <section className="outputs-section" id="outputs" aria-labelledby="outputs-title">
      <div className="section-heading">
        <p className="eyebrow">{siteCopy.outputs.eyebrow}</p>
        <h2 id="outputs-title">{siteCopy.outputs.title}</h2>
      </div>
      <div className="output-grid">
        {outputs.map((output) => (
          <article className="output-card" key={output.title}>
            <h3>{output.title}</h3>
            <p>{output.description}</p>
            <p className="detail">{output.detail}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
