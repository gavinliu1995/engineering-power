import { siteCopy } from "../content/siteContent";

export function Footer() {
  return (
    <footer className="site-footer">
      <div>
        <p>{siteCopy.brand}</p>
        <p className="footer-note">{siteCopy.footer.demoNote}</p>
      </div>
      <a href={siteCopy.footer.githubUrl}>{siteCopy.footer.githubLabel}</a>
    </footer>
  );
}
