import { reportData } from "../content/siteContent";

export function ReleaseDecision() {
  return (
    <section className="release-decision" aria-labelledby="release-decision-title">
      <p className="eyebrow">Recommendation</p>
      <h2 id="release-decision-title">Release decision</h2>
      <p className="decision-value">{reportData.recommendation}</p>
      <div className="confidence-statement">
        <h3>Confidence</h3>
        <p>{reportData.confidence}</p>
      </div>
      <div className="report-columns">
        <div>
          <h3>Risks</h3>
          <ul>{reportData.risks.map((risk) => <li key={risk}>{risk}</li>)}</ul>
        </div>
        <div>
          <h3>Release conditions</h3>
          <ul>{reportData.releaseConditions.map((condition) => <li key={condition}>{condition}</li>)}</ul>
        </div>
      </div>
    </section>
  );
}
