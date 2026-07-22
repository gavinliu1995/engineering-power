import { siteCopy } from "../content/siteContent";

export function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label={`${siteCopy.brand} home`}>
        <span className="brand-mark" aria-hidden="true">E</span>
        {siteCopy.brand}
      </a>
      <a
        className="header-link"
        href="https://github.com/gavinliu1995/engineering-power"
        target="_blank"
        rel="noreferrer"
      >
        GitHub
      </a>
    </header>
  );
}
