import type { EvidenceItem } from "../content/siteContent";

type EvidenceSectionProps = {
  label: string;
  tone: "fact" | "inference" | "unknown";
  items: readonly EvidenceItem[];
};

export function EvidenceSection({ label, tone, items }: EvidenceSectionProps) {
  return (
    <section className={`evidence-section evidence-${tone}`} aria-labelledby={`${tone}-title`}>
      <h2 id={`${tone}-title`}>{label}</h2>
      <ul className="evidence-list">
        {items.map((item) => (
          <li key={item.statement}>
            <p>{item.statement}</p>
            <code>Illustrative citation: {item.citation}</code>
          </li>
        ))}
      </ul>
    </section>
  );
}
