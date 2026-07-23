import { Link } from "react-router-dom";
import { siteCopy, supportedHosts } from "../content/siteContent";

export function HostOverview() {
  const copy = siteCopy.fullLifecycle.hosts;

  return (
    <section id="hosts" className="host-overview" aria-labelledby="hosts-title">
      <div className="section-heading">
        <p className="eyebrow">{copy.eyebrow}</p>
        <h2 id="hosts-title">{copy.title}</h2>
        <p>{copy.description}</p>
      </div>
      <ul className="host-list">
        {supportedHosts.map((host) => (
          <li key={host.id}>
            <h3>{host.name}</h3>
            <p>{host.description}</p>
          </li>
        ))}
      </ul>
      <Link className="button button-primary" to="/start">Choose your assistant</Link>
    </section>
  );
}
