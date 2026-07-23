import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";
import { demoScenarios, type LifecycleStageId } from "../content/siteContent";
import { EvidenceSection } from "./EvidenceSection";
import { LifecycleTabs } from "./LifecycleTabs";
import { ReleaseDecision } from "./ReleaseDecision";
import { ValidationMatrix } from "./ValidationMatrix";

export function ScenarioDemo() {
  const [selectedId, setSelectedId] = useState<LifecycleStageId>("understand");
  const reducedMotion = Boolean(useReducedMotion());

  return (
    <section className="scenario-demo" aria-labelledby="scenario-demo-title">
      <div className="scenario-demo-inner">
        <p className="eyebrow">Four lifecycle scenarios</p>
        <h1 id="scenario-demo-title">Engineering Power demo</h1>
        <p className="scenario-demo-intro">
          Follow one fictional repository from first orientation through change,
          release, migration, and incident response.
        </p>
        <LifecycleTabs
          idPrefix="scenario"
          ariaLabel="Engineering Power demo scenarios"
          tabs={demoScenarios}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
        {demoScenarios.map((scenario) => {
          const active = selectedId === scenario.id;

          return (
            <section
              key={scenario.id}
              className="scenario-panel"
              role="tabpanel"
              id={`scenario-panel-${scenario.id}`}
              aria-labelledby={`scenario-tab-${scenario.id}`}
              hidden={!active}
            >
              <motion.div
                className="scenario-panel-content"
                initial={false}
                animate={{ y: active || reducedMotion ? 0 : 8 }}
                transition={{ duration: reducedMotion ? 0 : 0.24, ease: [0.22, 1, 0.36, 1] }}
              >
                <p className="illustrative-note">{scenario.disclosure}</p>
                <h2>{scenario.heading}</h2>
                <p className="scenario-summary">{scenario.summary}</p>
                <dl className="scenario-metadata">
                  <div><dt>Target</dt><dd>{scenario.target}</dd></div>
                  <div><dt>Git state</dt><dd>{scenario.gitState}</dd></div>
                  <div><dt>Engineering question</dt><dd>{scenario.question}</dd></div>
                </dl>
                <div className="scenario-output-list">
                  {scenario.outputs.map((output) => (
                    <article className="scenario-output" key={output.title}>
                      <h3>{output.title}</h3>
                      <p>{output.summary}</p>
                      <ul>{output.items.map((item) => <li key={item}>{item}</li>)}</ul>
                    </article>
                  ))}
                </div>
                <section className="scenario-evidence" aria-label={`${scenario.title} illustrative evidence`}>
                  <h3>Illustrative evidence</h3>
                  <ul>
                    {scenario.evidence.map((item) => (
                      <li key={item.statement}><p>{item.statement}</p><code>{item.citation}</code></li>
                    ))}
                  </ul>
                </section>
                <div className="scenario-closeout">
                  <article><p className="panel-kicker">Explicit unknown</p><h3>{scenario.unknown.statement}</h3><p>{scenario.unknown.neededEvidence}</p></article>
                  <article><p className="panel-kicker">Human-owned next decision</p><h3>{scenario.nextDecision.owner}</h3><p>{scenario.nextDecision.action}</p></article>
                </div>
                {scenario.detailReport ? (
                  <div className="change-report-detail">
                    <ReleaseDecision report={scenario.detailReport} />
                    <EvidenceSection label="Facts" tone="fact" items={scenario.detailReport.facts} />
                    <EvidenceSection label="Inferences" tone="inference" items={scenario.detailReport.inferences} />
                    <EvidenceSection label="Unknowns" tone="unknown" items={scenario.detailReport.unknowns} />
                    <ValidationMatrix rows={scenario.detailReport.validations} />
                  </div>
                ) : null}
              </motion.div>
            </section>
          );
        })}
      </div>
    </section>
  );
}
