import { motion, useReducedMotion } from "framer-motion";
import { useState } from "react";
import { Link } from "react-router-dom";
import { lifecycleStages, siteCopy, type LifecycleStageId } from "../content/siteContent";
import { LifecycleTabs } from "./LifecycleTabs";

export function CapabilityExplorer() {
  const [selectedId, setSelectedId] = useState<LifecycleStageId>("understand");
  const reducedMotion = Boolean(useReducedMotion());
  const copy = siteCopy.fullLifecycle.explorer;

  return (
    <section className="capability-explorer" aria-labelledby="explorer-title">
      <div className="capability-explorer-inner">
        <div className="section-heading">
          <p className="eyebrow">{copy.eyebrow}</p>
          <h2 id="explorer-title">{copy.title}</h2>
        </div>
        <LifecycleTabs
          idPrefix="capability"
          ariaLabel="Engineering lifecycle capabilities"
          tabs={lifecycleStages}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
        {lifecycleStages.map((stage) => {
          const active = selectedId === stage.id;

          return (
            <section
              key={stage.id}
              className="capability-panel"
              role="tabpanel"
              id={`capability-panel-${stage.id}`}
              aria-labelledby={`capability-tab-${stage.id}`}
              hidden={!active}
            >
              <motion.div
                className="capability-panel-layout"
                initial={false}
                animate={{ y: active || reducedMotion ? 0 : 8 }}
                transition={{ duration: reducedMotion ? 0 : 0.24, ease: [0.22, 1, 0.36, 1] }}
              >
                <div>
                  <p className="panel-kicker">Engineering question</p>
                  <h3>{stage.question}</h3>
                  <p>{stage.outcome}</p>
                </div>
                <div className="capability-panel-detail">
                  <ul>
                    {stage.capabilities.map((capability) => (
                      <li key={capability.name}>{capability.name}</li>
                    ))}
                  </ul>
                  <div className="panel-evidence">
                    <p><strong>Example output</strong>{stage.exampleOutput}</p>
                    <p><strong>Evidence required</strong>{stage.evidenceInput}</p>
                  </div>
                  <Link className="text-link" to="/demo-report">Explore the four-scenario demo</Link>
                </div>
              </motion.div>
            </section>
          );
        })}
      </div>
    </section>
  );
}
