import { siteCopy } from "../content/siteContent";

export function Footer() {
  return (
    <footer className="site-footer">
      <p>{siteCopy.brand}</p>
      <a href={siteCopy.footer.githubUrl}>{siteCopy.footer.githubLabel}</a>
    </footer>
  );
}
