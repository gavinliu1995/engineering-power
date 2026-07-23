import { useEffect, useRef } from "react";
import { Link, Route, Routes, useLocation } from "react-router-dom";
import { Footer } from "./components/Footer";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { LifecycleOverview } from "./components/LifecycleOverview";
import { CapabilityExplorer } from "./components/CapabilityExplorer";
import { TrustBoundary } from "./components/TrustBoundary";
import { EvidenceSection } from "./components/EvidenceSection";
import { ReleaseDecision } from "./components/ReleaseDecision";
import { ReportHeader } from "./components/ReportHeader";
import { ValidationMatrix } from "./components/ValidationMatrix";
import { reportData } from "./content/siteContent";

function ScrollToTop() {
  const { pathname } = useLocation();
  const previousPath = useRef(pathname);

  useEffect(() => {
    const pathChanged = previousPath.current !== pathname;
    window.scrollTo(0, 0);

    if (pathChanged) {
      const heading = document.querySelector<HTMLElement>("main h1");
      heading?.setAttribute("tabindex", "-1");
      heading?.focus({ preventScroll: true });
    }

    previousPath.current = pathname;
  }, [pathname]);

  return null;
}

function HomePage() {
  return (
    <div className="page-shell" id="top">
      <div className="home-header-shell">
        <Header />
      </div>
      <main>
        <Hero />
        <LifecycleOverview />
        <CapabilityExplorer />
        <TrustBoundary />
      </main>
      <Footer />
    </div>
  );
}

function DemoReportPage() {
  return (
    <main className="report-page">
      <ReportHeader />
      <ReleaseDecision />
      <section className="api-summary" aria-labelledby="api-summary-title">
        <p className="eyebrow">API contract delta</p>
        <h2 id="api-summary-title">Compatibility summary</h2>
        <p>{reportData.apiCompatibility}</p>
      </section>
      <EvidenceSection label="Facts" tone="fact" items={reportData.facts} />
      <EvidenceSection label="Inferences" tone="inference" items={reportData.inferences} />
      <EvidenceSection label="Unknowns" tone="unknown" items={reportData.unknowns} />
      <ValidationMatrix />
    </main>
  );
}

function OnboardingHeader() {
  return (
    <div className="onboarding-header-shell">
      <Header homeHref="/" anchorPrefix="/" />
    </div>
  );
}

function QuickStartPage() {
  const hosts = [
    {
      id: "codex",
      name: "Codex",
      description: "Local developer preview for a configured personal marketplace.",
    },
    {
      id: "copilot",
      name: "GitHub Copilot",
      description: "Install the portable project skill for Copilot CLI or VS Code.",
    },
    {
      id: "claude",
      name: "Claude Code",
      description: "Install Engineering Power as a Claude Code project skill.",
    },
    {
      id: "cursor",
      name: "Cursor",
      description: "Install Engineering Power as a Cursor project skill.",
    },
  ] as const;

  return (
    <div className="onboarding-page-shell" id="top">
      <OnboardingHeader />
      <main className="quick-start-page">
        <p className="eyebrow">Choose a host</p>
        <h1>Use Engineering Power with your coding assistant.</h1>
        <p className="quick-start-intro">Pick your assistant for installation and a first evidence-backed analysis. Engineering Power is read-only by default and does not merge, deploy, or change the target repository.</p>
        <nav className="assistant-choice-grid" aria-label="Supported coding assistants">
          {hosts.map((host, index) => (
            <Link
              key={host.id}
              className={`assistant-choice assistant-choice-${host.id}`}
              to={`/start/${host.id}`}
              aria-label={`Use Engineering Power with ${host.name}`}
            >
              <span className="guide-step">Option {String(index + 1).padStart(2, "0")}</span>
              <h2>{host.name}</h2>
              <p>{host.description}</p>
              <span className="choice-action">Open {host.name} guide</span>
            </Link>
          ))}
        </nav>
      </main>
    </div>
  );
}

type HostId = "codex" | "copilot" | "claude" | "cursor";

type GuideStep = {
  title: string;
  description: string;
  code?: readonly string[];
};

const portableSourceStep: GuideStep = {
  title: "Get Engineering Power",
  description: "Clone the canonical repository, then run the installer from that checkout.",
  code: [
    "git clone https://github.com/gavinliu1995/engineering-power.git",
    "cd engineering-power",
  ],
};

const hostGuides: Record<HostId, {
  eyebrow: string;
  heading: string;
  intro: string;
  steps: readonly GuideStep[];
}> = {
  codex: {
    eyebrow: "Local developer preview",
    heading: "Use Engineering Power in Codex.",
    intro: "This is not a public Codex install. The documented path is for developers whose personal marketplace already points to a local Engineering Power checkout; everyone else can use one of the portable project-skill hosts.",
    steps: [
      {
        title: "Refresh the local plugin snapshot",
        description: "The maintainer setup expects the canonical checkout at this path and a configured personal Codex plugin source.",
        code: [
          'PLUGIN_ROOT="$HOME/Documents/engineering-power"',
          'python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py" "$PLUGIN_ROOT"',
        ],
      },
      {
        title: "Add the configured plugin",
        description: "Continue only when the personal marketplace entry already points to that checkout.",
        code: ["codex plugin add engineering-power@personal"],
      },
      {
        title: "Start a new task",
        description: "Start a new task and describe the repository or pull request you want Engineering Power to analyze.",
      },
      {
        title: "Ask a concrete question",
        description: "Request an evidence-backed answer with facts, inferences, unknowns, and file citations.",
        code: ["Analyze this pull request with Engineering Power. Separate facts, inferences, and unknowns, with citations."],
      },
    ],
  },
  copilot: {
    eyebrow: "Portable project skill",
    heading: "Use Engineering Power in GitHub Copilot.",
    intro: "Add Engineering Power as a project skill for GitHub Copilot CLI or the VS Code coding agent.",
    steps: [
      portableSourceStep,
      {
        title: "Install into your project",
        description: "Run the installer from the Engineering Power repository with your project as the target.",
        code: ["python3 scripts/install_agent_skill.py --host copilot --target-root /path/to/project"],
      },
      {
        title: "Reload and verify",
        description: "Reload Copilot skills and confirm Engineering Power is available.",
        code: ["/skills reload", "/skills info engineering-power"],
      },
      {
        title: "Start an analysis",
        description: "Invoke Engineering Power, then provide a repository, pull request, local comparison, working tree, or patch.",
        code: ["/engineering-power"],
      },
    ],
  },
  claude: {
    eyebrow: "Portable project skill",
    heading: "Use Engineering Power in Claude Code.",
    intro: "Install Engineering Power into your project, then ask Claude Code to analyze a repository or code change with cited evidence.",
    steps: [
      portableSourceStep,
      {
        title: "Install into your project",
        description: "Run the installer from the Engineering Power repository.",
        code: ["python3 scripts/install_agent_skill.py --host claude --target-root /path/to/project"],
      },
      {
        title: "Confirm the skill file",
        description: "The installed skill should exist at this documented project path.",
        code: ["/path/to/project/.claude/skills/engineering-power"],
      },
      {
        title: "Start an analysis",
        description: "Ask Claude Code to use Engineering Power with a repository, comparison, working tree, or patch.",
        code: ["Use the engineering-power skill to analyze this repository."],
      },
    ],
  },
  cursor: {
    eyebrow: "Portable project skill",
    heading: "Use Engineering Power in Cursor.",
    intro: "Install Engineering Power as a Cursor project skill, then give it a repository or change target to analyze.",
    steps: [
      portableSourceStep,
      {
        title: "Install into your project",
        description: "Run the installer from the Engineering Power repository.",
        code: ["python3 scripts/install_agent_skill.py --host cursor --target-root /path/to/project"],
      },
      {
        title: "Confirm the skill file",
        description: "The installed skill should exist at this documented project path.",
        code: ["/path/to/project/.cursor/skills/engineering-power"],
      },
      {
        title: "Start an analysis",
        description: "Ask Cursor to use Engineering Power with a repository or change target.",
        code: ["Use the engineering-power skill to analyze this repository."],
      },
    ],
  },
};

function HostGuidePage({ host }: { host: HostId }) {
  const guide = hostGuides[host];

  return (
    <div className="onboarding-page-shell" id="top">
      <OnboardingHeader />
      <main className="quick-start-page host-guide-page">
        <Link className="back-link" to="/start">Choose another assistant</Link>
        <p className="eyebrow">{guide.eyebrow}</p>
        <h1>{guide.heading}</h1>
        <p className="quick-start-intro">{guide.intro}</p>
        <ol className="host-guide-steps">
          {guide.steps.map((step, index) => (
            <li key={step.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <div>
                <h2>{step.title}</h2>
                <p>{step.description}</p>
                {step.code?.map((line) => <code key={line}>{line}</code>)}
              </div>
            </li>
          ))}
        </ol>
        <a className="button button-primary" href="https://github.com/gavinliu1995/engineering-power" target="_blank" rel="noreferrer">Open the canonical repository</a>
      </main>
    </div>
  );
}

function NotFoundPage() {
  return (
    <main className="not-found-page">
      <h1>Page not found</h1>
      <p>The page you requested does not exist.</p>
      <Link className="button button-primary" to="/">
        Back to home
      </Link>
    </main>
  );
}

export default function App() {
  return (
    <>
      <ScrollToTop />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/demo-report" element={<DemoReportPage />} />
        <Route path="/start" element={<QuickStartPage />} />
        <Route path="/start/codex" element={<HostGuidePage host="codex" />} />
        <Route path="/start/copilot" element={<HostGuidePage host="copilot" />} />
        <Route path="/start/claude" element={<HostGuidePage host="claude" />} />
        <Route path="/start/cursor" element={<HostGuidePage host="cursor" />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </>
  );
}
