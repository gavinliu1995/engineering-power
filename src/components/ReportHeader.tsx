import { reportData } from "../content/siteContent";

export function ReportHeader() {
  return (
    <header className="report-header">
      <p className="eyebrow">Static evidence report</p>
      <h1>Demo report: {reportData.pullRequest}</h1>
      <p className="report-summary">{reportData.summary}</p>
      <dl className="report-metadata">
        <div>
          <dt>Target</dt>
          <dd>{reportData.metadata.target}</dd>
        </div>
        <div>
          <dt>Base</dt>
          <dd>{reportData.metadata.base}</dd>
        </div>
        <div>
          <dt>Head</dt>
          <dd>{reportData.metadata.head}</dd>
        </div>
        <div>
          <dt>Profile</dt>
          <dd>{reportData.metadata.profile}</dd>
        </div>
        <div>
          <dt>Evidence snapshot</dt>
          <dd>{reportData.metadata.evidenceSnapshot}</dd>
        </div>
      </dl>
      <section className="affected-components" aria-labelledby="affected-components-title">
        <h2 id="affected-components-title">Affected components</h2>
        <ul>
          {reportData.affectedComponents.map((component) => (
            <li key={component}>{component}</li>
          ))}
        </ul>
      </section>
      <p className="illustrative-note">
        Illustrative demo citations only — this is not live repository analysis.
      </p>
    </header>
  );
}
