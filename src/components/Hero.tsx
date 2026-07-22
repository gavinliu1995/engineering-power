import { Link } from "react-router-dom";
import { motion, useReducedMotion } from "framer-motion";
import { siteCopy } from "../content/siteContent";
import { IntelligenceFlowField } from "./IntelligenceFlowField";

export function Hero() {
  const reducedMotion = Boolean(useReducedMotion());

  return (
    <section className="hero" aria-labelledby="hero-title">
      <div className="hero-layout">
        <motion.div
          className="hero-content"
          initial={reducedMotion ? undefined : { opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.22, 1, 0.36, 1] }}
        >
          <p className="eyebrow">{siteCopy.hero.eyebrow}</p>
          <h1 id="hero-title">{siteCopy.hero.title}</h1>
          <p className="hero-copy">{siteCopy.hero.description}</p>
          <div className="hero-actions">
            <Link className="button button-primary hero-cta" to="/start">
              {siteCopy.hero.cta}
            </Link>
            <Link className="hero-secondary-link" to="/demo-report">
              View sample report
            </Link>
          </div>
        </motion.div>
        <IntelligenceFlowField reducedMotion={reducedMotion} />
      </div>
    </section>
  );
}
