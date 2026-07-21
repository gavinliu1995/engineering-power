import { Link, Route, Routes } from "react-router-dom";

function HomePage() {
  return (
    <main>
      <h1>Evidence-backed engineering decisions</h1>
      <Link to="/demo-report">View Demo Report</Link>
    </main>
  );
}

function DemoReportPage() {
  return (
    <main>
      <h1>Demo report</h1>
    </main>
  );
}

function NotFoundPage() {
  return (
    <main>
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
    </main>
  );
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/demo-report" element={<DemoReportPage />} />
      <Route path="*" element={<NotFoundPage />} />
    </Routes>
  );
}
