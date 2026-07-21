export type Output = {
  title: string;
  description: string;
  detail: string;
};

export type TrustBoundary = {
  title: string;
  description: string;
};

export const evidenceFlow = [
  "Pull request or local comparison",
  "One exact evidence snapshot",
  "Cited engineering outputs",
  "Decision-ready summary",
];

export const outputs: Output[] = [
  {
    title: "Change Impact",
    description: "See the modules, callers, and behavior a change can touch.",
    detail: "Turn a diff into an evidence-backed blast-radius assessment.",
  },
  {
    title: "API Contract Delta",
    description: "Surface compatibility changes before they surprise consumers.",
    detail: "Translate implementation differences into a clear contract delta.",
  },
  {
    title: "Release Readiness",
    description: "Review release risk with traceable evidence, not instinct.",
    detail: "Collect the checks, caveats, and decisions needed to ship confidently.",
  },
];

export const trustBoundaries: TrustBoundary[] = [
  {
    title: "Evidence stays specific",
    description:
      "Every conclusion is grounded in the exact repository snapshot being analyzed.",
  },
  {
    title: "Reasoning stays traceable",
    description:
      "Citations keep reviewers connected to the code, tests, and configuration behind each recommendation.",
  },
  {
    title: "Decisions stay yours",
    description:
      "Engineering Power frames the evidence; your team owns the final call.",
  },
];

export const siteCopy = {
  brand: "Engineering Power",
  hero: {
    eyebrow: "Evidence-backed engineering intelligence",
    title: "Evidence-backed engineering decisions.",
    description:
      "Engineering Power turns a pull request or local comparison into cited, decision-ready engineering outputs.",
    cta: "Open Demo Report",
  },
  whyItMatters: {
    title: "A diff shows what changed. Decisions need what it means.",
    description:
      "Give reviewers a compact narrative of impact, compatibility, and release risk while the evidence is still close at hand.",
  },
  flow: {
    eyebrow: "Connected decision flow",
    title: "One evidence trail, from comparison to decision.",
  },
  outputs: {
    eyebrow: "Decision-ready outputs",
    title: "The questions a release review needs answered.",
  },
  demo: {
    title: "See the evidence in report form.",
    description:
      "Explore a static example of a concise, cited engineering narrative.",
    cta: "View Demo Report",
  },
  trust: {
    eyebrow: "Trust boundary",
    title: "Useful analysis without pretending certainty.",
  },
  footer: {
    githubLabel: "View Engineering Power on GitHub",
    githubUrl: "https://github.com",
  },
} as const;
