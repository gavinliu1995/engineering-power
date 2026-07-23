import { lifecycleStarterPrompts } from "../content/siteContent";

export function StarterPrompts({ hostName }: { hostName: string }) {
  return (
    <section className="starter-prompts" aria-labelledby="starter-prompts-title">
      <p className="eyebrow">First things to try</p>
      <h2 id="starter-prompts-title">First things to try in {hostName}</h2>
      <div className="starter-prompt-grid">
        {lifecycleStarterPrompts.map((item, index) => (
          <article key={item.stage}>
            <span>{String(index + 1).padStart(2, "0")}</span>
            <h3>{item.title}</h3>
            <code>{item.prompt}</code>
          </article>
        ))}
      </div>
    </section>
  );
}
