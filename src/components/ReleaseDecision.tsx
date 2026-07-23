import type { DemoReport } from "../content/siteContent";

export function ReleaseDecision({ report }: { report: DemoReport }) {
  return (
    <section className="release-decision" aria-labelledby="release-decision-title">
      <p className="eyebrow">Recommendation</p>
      <h2 id="release-decision-title">Release decision</h2>
      <p className="decision-value">{report.recommendation}</p>
      <div className="confidence-statement">
        <h3>Confidence</h3>
        <p>{report.confidence}</p>
      </div>
      <div className="report-columns">
        <div>
          <h3>Risks</h3>
          <ul>{report.risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
        </div>
        <div>
          <h3>Release conditions</h3>
          <ul>{report.releaseConditions.map((condition) => <li key={condition}>{condition}</li>)}</ul>
        </div>
      </div>
    </section>
  );
}
