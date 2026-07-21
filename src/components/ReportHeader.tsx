import { reportData } from "../content/siteContent";

export function ReportHeader() {
  return (
    <header className="report-header">
      <p className="eyebrow">Static evidence report</p>
      <h1>Demo report: {reportData.pullRequest}</h1>
      <p className="report-summary">{reportData.summary}</p>
      <p className="illustrative-note">
        Illustrative demo citations only — this is not live repository analysis.
      </p>
    </header>
  );
}
