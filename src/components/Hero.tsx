import { Link } from "react-router-dom";
import { motion, useReducedMotion } from "framer-motion";
import { siteCopy } from "../content/siteContent";
import { IntelligenceFlowField } from "./IntelligenceFlowField";

export function Hero() {
  const reducedMotion = Boolean(useReducedMotion());
  const copy = siteCopy.fullLifecycle.hero;

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-layout">
        <motion.div
          className="hero-content"
          initial={reducedMotion ? undefined : { opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: reducedMotion ? 0 : 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="eyebrow">{copy.eyebrow}</p>
          <h1 id="hero-title">{copy.title}</h1>
          <p className="hero-copy">{copy.description}</p>
          <div className="hero-actions">
            <Link className="button button-primary hero-cta" to="/start">
              {copy.primaryCta}
            </Link>
            <a className="hero-secondary-link" href="#capabilities">{copy.secondaryCta}</a>
          </div>
        </motion.div>
        <IntelligenceFlowField reducedMotion={reducedMotion} />
      </div>
    </section>
  );
}
