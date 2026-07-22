export type Output = {
  title: string;
  description: string;
  detail: string;
};

export type TrustBoundary = {
  title: string;
  description: string;
};

export type EvidenceState = {
  label: "Facts" | "Inferences" | "Unknowns";
  description: string;
};

export type EvidenceItem = {
  statement: string;
  citation: string;
};

export type ValidationRow = {
  state: "Executed" | "Discovered" | "Recommended";
  check: string;
  detail: string;
};

export type ReportMetadata = {
  target: string;
  base: string;
  head: string;
  profile: string;
  evidenceSnapshot: string;
};

export type DemoReport = {
  metadata: ReportMetadata;
  pullRequest: string;
  summary: string;
  recommendation: string;
  confidence: string;
  affectedComponents: readonly string[];
  facts: readonly EvidenceItem[];
  inferences: readonly EvidenceItem[];
  unknowns: readonly EvidenceItem[];
  apiCompatibility: string;
  validations: readonly ValidationRow[];
  risks: readonly string[];
  releaseConditions: readonly string[];
};

export const reportData = {
  metadata: {
    target: "Pull request #482 · checkout-tax-rounding",
    base: "main @ 8f31c2a",
    head: "feature/checkout-tax-rounding @ c7e194d",
    profile: "Release readiness review",
    evidenceSnapshot: "8f31c2a..c7e194d",
  },
  pullRequest: "checkout-tax-rounding",
  summary: "Normalize tax rounding at the checkout boundary before totals are persisted.",
  recommendation: "Proceed with conditions",
  confidence:
    "Moderate — core checkout behavior is evidenced; provider reconciliation remains unverified.",
  affectedComponents: [
    "Tax calculation",
    "Checkout API response",
    "Payment provider reconciliation",
  ],
  facts: [
    {
      statement: "TaxCalculator rounds each tax line before adding it to the order total.",
      citation: "src/checkout/TaxCalculator.ts:L42-L61",
    },
    {
      statement: "The checkout response exposes totals as integer cents.",
      citation: "src/api/CheckoutResponse.ts:L18-L31",
    },
  ],
  inferences: [
    {
      statement: "Moving rounding to the boundary should make line-item and order-total calculations consistent.",
      citation: "src/checkout/TaxCalculator.ts:L42-L61",
    },
    {
      statement: "Existing consumers should remain compatible because the response shape is unchanged.",
      citation: "src/api/CheckoutResponse.ts:L18-L31",
    },
  ],
  unknowns: [
    {
      statement: "Whether every payment provider reconciles fractional tax adjustments in the same way.",
      citation: "docs/payments/provider-reconciliation.md:L1-L24",
    },
    {
      statement: "Whether historical carts require a data correction after release.",
      citation: "src/checkout/OrderRepository.ts:L88-L104",
    },
  ],
  apiCompatibility: "Compatible: no endpoint, field, or type changes are illustrated in this example.",
  validations: [
    {
      state: "Executed",
      check: "Unit suite",
      detail: "TaxCalculator rounding scenarios passed in this illustrative snapshot.",
    },
    {
      state: "Discovered",
      check: "Provider reconciliation",
      detail: "No evidence is included for provider-specific fractional-cent handling.",
    },
    {
      state: "Recommended",
      check: "Staged checkout",
      detail: "Compare tax totals for high-precision carts before broad rollout.",
    },
  ],
  risks: [
    "A provider may reject or adjust a fractional-cent reconciliation differently from checkout.",
    "Historical carts may display a different tax total if recalculated after release.",
  ],
  releaseConditions: [
    "Confirm reconciliation behavior with each supported payment provider.",
    "Run a staged checkout comparison for high-precision tax scenarios.",
    "Document the rollback owner and decision threshold before release.",
  ],
} as const satisfies DemoReport;

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

export const homepageEvidenceStates: readonly EvidenceState[] = [
  {
    label: "Facts",
    description: "Observed code, configuration, and test evidence tied to the exact snapshot.",
  },
  {
    label: "Inferences",
    description: "Reasoned implications that stay separate from the evidence supporting them.",
  },
  {
    label: "Unknowns",
    description: "Questions the available evidence cannot establish, kept visible for reviewers.",
  },
];

export const trustBoundaries: TrustBoundary[] = [
  {
    title: "Static demo, clear boundary",
    description:
      "This static demo uses illustrative evidence and citations. It is not live repository analysis.",
  },
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
    title: "Validation states stay distinct",
    description:
      "Executed checks are run in the captured snapshot. Discovered checks are evidence found, not tests run. Recommended checks are next steps, not completed validation.",
  },
  {
    title: "Coverage has limits",
    description:
      "A deadline or incomplete coverage can limit a report; those limits remain explicit instead of becoming certainty.",
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
    eyebrow: "AI-native developer platform",
    title: "Engineering moves at the speed of intelligence.",
    description:
      "Unify agents, reusable skills, repository context, and delivery in one evidence-backed engineering workflow.",
    cta: "Get started",
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
    excerpt: {
      label: "Report excerpt · checkout-tax-rounding",
      recommendation: "Proceed with conditions",
      fact: "TaxCalculator rounds each tax line before adding it to the order total.",
      citation: "src/checkout/TaxCalculator.ts:L42-L61",
    },
    cta: "View Demo Report",
  },
  trust: {
    eyebrow: "Trust boundary",
    title: "Useful analysis without pretending certainty.",
  },
  footer: {
    githubLabel: "View Engineering Power on GitHub",
    githubUrl: "https://github.com/gavinliu1995/engineering-power",
    demoNote: "Static demo only — it does not analyze your repository.",
  },
} as const;
