export function EvidenceSignalField() {
  return (
    <div aria-hidden="true" className="evidence-signal-field" data-testid="evidence-signal-field">
      <div className="signal-orbit signal-orbit-one" />
      <div className="signal-orbit signal-orbit-two" />
      <span className="signal-line signal-line-one" />
      <span className="signal-line signal-line-two" />
      <span className="signal-node signal-node-one" />
      <span className="signal-node signal-node-two" />
      <span className="signal-node signal-node-three" />
      <span className="signal-code signal-code-one">src/checkout/TaxCalculator.ts</span>
      <span className="signal-code signal-code-two">evidence snapshot · exact state</span>
      <div className="signal-decision">
        <span>RELEASE DECISION</span>
        <strong>PROCEED WITH CONDITIONS</strong>
      </div>
    </div>
  );
}
