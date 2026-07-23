import { siteCopy } from "../content/siteContent";

type HeaderProps = {
  homeHref?: string;
  anchorPrefix?: "" | "/";
};

export function Header({ homeHref = "#top", anchorPrefix = "" }: HeaderProps) {
  return (
    <header className="site-header">
      <a className="brand" href={homeHref} aria-label={`${siteCopy.brand} home`}>
        <img
          className="brand-mark"
          src="/images/engineering-power-citation-frame-header.png"
          alt=""
          aria-hidden="true"
          width="930"
          height="650"
        />
        {siteCopy.brand}
      </a>
      <nav className="site-nav" aria-label="Primary">
        <a href={`${anchorPrefix}#capabilities`}>Capabilities</a>
        <a href={`${anchorPrefix}#how-it-works`}>How it works</a>
        <a href={`${anchorPrefix}#hosts`}>Hosts</a>
        <a href={siteCopy.footer.githubUrl} target="_blank" rel="noreferrer">GitHub</a>
      </nav>
    </header>
  );
}
