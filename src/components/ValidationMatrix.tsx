import { reportData } from "../content/siteContent";

export function ValidationMatrix() {
  return (
    <section className="validation-section" aria-labelledby="validation-title">
      <p className="eyebrow">Validation status</p>
      <h2 id="validation-title">Validation matrix</h2>
      <div className="validation-table" role="table" aria-label="Validation matrix">
        {reportData.validations.map((validation) => (
          <div className="validation-row" role="row" key={validation.check}>
            <strong role="cell" className={`validation-state state-${validation.state.toLowerCase()}`}>
              {validation.state}
            </strong>
            <span role="cell">{validation.check}</span>
            <span role="cell">{validation.detail}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
