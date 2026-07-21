import { Link } from "react-router-dom";
import { siteCopy } from "../content/siteContent";

export function Hero() {
  return (
    <section className="hero" aria-labelledby="hero-title">
      <p className="eyebrow">{siteCopy.hero.eyebrow}</p>
      <h1 id="hero-title">{siteCopy.hero.title}</h1>
      <p className="hero-copy">{siteCopy.hero.description}</p>
      <Link className="button button-primary" to="/demo-report">
        {siteCopy.hero.cta}
      </Link>
    </section>
  );
}
