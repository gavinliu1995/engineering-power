import { siteCopy } from "../content/siteContent";

export function Header() {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label={`${siteCopy.brand} home`}>
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
