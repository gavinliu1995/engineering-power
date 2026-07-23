import type { ValidationRow } from "../content/siteContent";

export function ValidationMatrix({ rows }: { rows: readonly ValidationRow[] }) {
  return (
    <section className="validation-section" aria-labelledby="validation-title">
      <p className="eyebrow">Validation status</p>
      <h2 id="validation-title">Validation matrix</h2>
      <div className="validation-table-wrapper">
        <table className="validation-table" aria-label="Validation matrix">
          <thead>
            <tr>
              <th scope="col">State</th>
              <th scope="col">Check</th>
              <th scope="col">Evidence</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((validation) => (
              <tr key={validation.check}>
                <td>
                  <strong className={`validation-state state-${validation.state.toLowerCase()}`}>
                    {validation.state}
                  </strong>
                </td>
                <td>{validation.check}</td>
                <td>{validation.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
