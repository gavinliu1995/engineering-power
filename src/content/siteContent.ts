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
  "Repository, PR, local comparison, working tree, or patch",
  "One bounded evidence snapshot",
  "Cited engineering analysis",
  "Human review and decision",
];

export const outputs: Output[] = [
  {
    title: "Change Impact",
    description: "Trace evidenced code, configuration, and test relationships.",
    detail: "Keep inferred runtime impact clearly labeled for reviewers.",
  },
  {
    title: "API Contract Delta",
    description: "Describe discovered API surface changes and compatibility risks.",
    detail: "Keep missing evidence visible instead of implying a guarantee.",
  },
  {
    title: "Release Readiness",
    description: "Summarize evidence, validation status, risks, and release conditions.",
    detail: "Give people a cited brief for the final release decision.",
  },
];

export const homepageEvidenceStates: readonly EvidenceState[] = [
  {
    label: "Facts",
    description: "Observed code, configuration, and test evidence tied to the analyzed snapshot.",
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
      "Material technical claims cite the analyzed snapshot, while limitations remain explicit.",
  },
  {
    title: "Validation states stay distinct",
    description:
      "Executed checks have observed results. Discovered and recommended checks are labeled separately, not presented as completed validation.",
  },
  {
    title: "Missing evidence stays visible",
    description:
      "Missing or incomplete evidence stays visible instead of being converted into certainty.",
  },
  {
    title: "Read-only by default",
    description:
      "Target repositories stay read-only unless you separately authorize an implementation workflow.",
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
    eyebrow: "Evidence-backed repository and change analysis",
    title: "Turn code evidence into cited engineering reports.",
    description:
      "Engineering Power analyzes a repository, pull request, or local change and returns cited findings, explicit unknowns, and review-ready engineering reports.",
    cta: "Choose your assistant",
  },
  whyItMatters: {
    title: "A diff shows changes. Reviewers still need the impact.",
    description:
      "Engineering Power separates observed facts, reasoned inferences, and unanswered questions. It also distinguishes checks that ran from tests it found or recommends.",
  },
  flow: {
    eyebrow: "One evidence snapshot",
    title: "Analyze once. Reuse the evidence.",
  },
  outputs: {
    eyebrow: "Cited review inputs",
    title: "Useful reports without false certainty.",
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
    title: "Evidence has clear limits.",
  },
  footer: {
    githubLabel: "View Engineering Power on GitHub",
    githubUrl: "https://github.com/gavinliu1995/engineering-power",
    demoNote: "Static demo only — it does not analyze your repository.",
  },
} as const;
