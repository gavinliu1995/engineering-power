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

export const lifecycleStageIds = [
  "understand",
  "change-safely",
  "ship-clearly",
  "evolve-operate",
] as const;

export type LifecycleStageId = (typeof lifecycleStageIds)[number];

export const assignedCapabilityNames = [
  "Repository-specific onboarding",
  "Architecture review support",
  "Repository refactoring assistance",
  "Dependency impact analysis",
  "Test impact analysis",
  "Regression risk detection",
  "API contract generation",
  "Release note generation",
  "Migration planning",
  "Runtime incident triage",
] as const;

export type AssignedCapabilityName = (typeof assignedCapabilityNames)[number];

export type SupportingCapabilityName =
  | "Repository Intelligence"
  | "PR Impact Analysis"
  | "Release Readiness"
  | "Systematic Debugging";

export type LifecycleCapability =
  | { role: "assigned"; name: AssignedCapabilityName; description: string }
  | { role: "supporting"; name: SupportingCapabilityName; description: string };

export type LifecycleStage = {
  id: LifecycleStageId;
  number: "01" | "02" | "03" | "04";
  title: "Understand" | "Change safely" | "Ship clearly" | "Evolve & operate";
  outcome: string;
  question: string;
  capabilities: readonly LifecycleCapability[];
  exampleOutput: string;
  evidenceInput: string;
};

export type ScenarioOutput = {
  title: string;
  summary: string;
  items: readonly string[];
};

export type DemoScenario = {
  id: LifecycleStageId;
  title: LifecycleStage["title"];
  disclosure: "Illustrative static example";
  heading: string;
  target: string;
  gitState: string;
  question: string;
  summary: string;
  outputs: readonly [ScenarioOutput, ScenarioOutput, ScenarioOutput];
  evidence: readonly [EvidenceItem, EvidenceItem, ...EvidenceItem[]];
  unknown: { statement: string; neededEvidence: string };
  nextDecision: { owner: string; action: string };
  detailReport?: DemoReport;
};

export type StarterPrompt = {
  stage: LifecycleStageId;
  title: LifecycleStage["title"];
  prompt: string;
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

export const lifecycleStages = [
  { id: "understand", number: "01", title: "Understand", outcome: "Get oriented before you make a change.", question: "How does this repository work, where should I start, and which boundaries matter?", capabilities: [
    { role: "assigned", name: "Repository-specific onboarding", description: "A practical reading order, setup path, and common change locations." },
    { role: "assigned", name: "Architecture review support", description: "Module boundaries, ownership, business flows, and design risks." },
    { role: "supporting", name: "Repository Intelligence", description: "A cited overview of structure, build paths, and risk areas." },
  ], exampleOutput: "Architecture map, checkout flow, setup path, and recommended reading order.", evidenceInput: "One repository revision plus available documentation, build files, source, and tests." },
  { id: "change-safely", number: "02", title: "Change safely", outcome: "Plan and review changes with downstream effects visible.", question: "What should change, what depends on it, and how could the change regress?", capabilities: [
    { role: "assigned", name: "Repository refactoring assistance", description: "A sequenced refactor plan with safe checkpoints and rollback boundaries." },
    { role: "assigned", name: "Dependency impact analysis", description: "Direct and transitive consumers across code, configuration, build, and runtime." },
    { role: "assigned", name: "Test impact analysis", description: "Executed, discovered, and recommended checks kept distinct." },
    { role: "assigned", name: "Regression risk detection", description: "Evidence-backed failure modes, affected behavior, and unresolved risk." },
    { role: "supporting", name: "PR Impact Analysis", description: "A pull request is one possible input, not the product boundary." },
  ], exampleOutput: "Refactor sequence, dependency and test impact, regression risks, and review conditions.", evidenceInput: "A repository, pull request, local comparison, working tree, or patch at an exact Git state." },
  { id: "ship-clearly", number: "03", title: "Ship clearly", outcome: "Make compatibility, communication, and release conditions explicit.", question: "What changed at the interface, what should people know, and what must be true before release?", capabilities: [
    { role: "assigned", name: "API contract generation", description: "Endpoint, schema, and compatibility changes tied to repository evidence." },
    { role: "assigned", name: "Release note generation", description: "Technical and user-facing notes grounded in the same change snapshot." },
    { role: "supporting", name: "Release Readiness", description: "Validation status, risks, rollback signals, and a human-owned release decision." },
  ], exampleOutput: "API compatibility delta, technical and user-facing release notes, and release conditions.", evidenceInput: "An exact comparison plus API definitions, tests, deployment configuration, and release documentation." },
  { id: "evolve-operate", number: "04", title: "Evolve & operate", outcome: "Modernize systems and investigate failures without losing evidence.", question: "How should this system evolve, and what evidence best explains the current failure?", capabilities: [
    { role: "assigned", name: "Migration planning", description: "Migration waves, validation gates, dependency order, and rollback points." },
    { role: "assigned", name: "Runtime incident triage", description: "Ranked hypotheses with supporting, contradicting, and missing evidence." },
    { role: "supporting", name: "Systematic Debugging", description: "Evidence-first diagnosis before corrective implementation." },
  ], exampleOutput: "Migration waves or ranked incident hypotheses with validation and rollback gates.", evidenceInput: "The repository state plus a target platform or bounded incident evidence such as symptoms, logs, and runbooks." },
] as const satisfies readonly LifecycleStage[];

export const howItWorksSteps = [
  { number: "01", title: "Choose the evidence", description: "Point Engineering Power at a repository, pull request, local comparison, working tree, patch, or bounded incident evidence." },
  { number: "02", title: "Capture the exact state", description: "It records the Git state and collects a limited, traceable evidence snapshot before drawing conclusions." },
  { number: "03", title: "Run the right workflow", description: "The selected workflow returns cited findings while keeping facts, inferences, unknowns, and validation states distinct." },
  { number: "04", title: "Keep the decision human", description: "An engineer reviews the evidence, resolves the remaining unknowns, and owns the implementation or release decision." },
] as const;

export const supportedHosts = [
  { id: "codex", name: "Codex", description: "Local developer preview for a configured personal marketplace." },
  { id: "copilot", name: "GitHub Copilot", description: "Portable project skill for Copilot CLI or VS Code." },
  { id: "claude", name: "Claude Code", description: "Portable project skill for repository-local Claude workflows." },
  { id: "cursor", name: "Cursor", description: "Portable project skill for Cursor-assisted engineering work." },
] as const;

export const lifecycleStarterPrompts = [
  { stage: "understand", title: "Understand", prompt: "Use Engineering Power to onboard me to this repository. Map its architecture and main business flows, then give me a cited reading order and setup path." },
  { stage: "change-safely", title: "Change safely", prompt: "Use Engineering Power to plan a safe refactor of the checkout totals module. Trace dependency and test impact, surface regression risks, and cite the relevant files." },
  { stage: "ship-clearly", title: "Ship clearly", prompt: "Use Engineering Power to generate the API compatibility delta and technical and user-facing release notes for this change, including release conditions and citations." },
  { stage: "evolve-operate", title: "Evolve & operate", prompt: "Use Engineering Power to investigate this provider-reconciliation incident. Rank hypotheses with supporting and contradicting evidence, then recommend whether an integer-money migration should be planned." },
] as const satisfies readonly StarterPrompt[];

export const demoScenarios: readonly DemoScenario[] = [
  {
    id: "understand", title: "Understand", disclosure: "Illustrative static example", heading: "Map northstar-commerce before touching checkout.", target: "northstar-commerce repository", gitState: "main @ 8f31c2a",
    question: "How does checkout work, which boundary owns totals, and where should a new engineer start?", summary: "The storefront calls a checkout service that owns totals, tax orchestration, and payment-provider boundaries.",
    outputs: [
      { title: "Repository overview", summary: "The storefront owns cart interaction; the checkout service owns quote calculation and provider coordination.", items: ["Primary domain: checkout", "Public entry point: POST /checkout/quote", "External boundary: PaymentProviderAdapter"] },
      { title: "Checkout business flow", summary: "CartPage → checkout route → CheckoutService → TaxCalculator → PaymentProviderAdapter.", items: ["Tax lines are calculated before provider authorization.", "Integer cents cross the public API boundary."] },
      { title: "Start here", summary: "Read the route, orchestration service, and provider adapter before changing totals.", items: ["src/api/routes/checkout.ts", "src/checkout/CheckoutService.ts", "src/payments/PaymentProviderAdapter.ts", "Run the documented local checkout bootstrap."] },
    ],
    evidence: [
      { statement: "The checkout route delegates quote creation to CheckoutService.", citation: "src/api/routes/checkout.ts:L12-L38" },
      { statement: "CheckoutService composes tax calculation and provider reconciliation.", citation: "src/checkout/CheckoutService.ts:L24-L78" },
      { statement: "The repository documents a local checkout bootstrap path.", citation: "README.md:L18-L42" },
    ],
    unknown: { statement: "Whether payment-provider sandbox credentials are available to every new contributor.", neededEvidence: "Maintainer confirmation or a verified sandbox onboarding run." },
    nextDecision: { owner: "Repository maintainer", action: "Confirm ownership of the provider adapter, then use checkout as the first onboarding change slice." },
  },
  {
    id: "change-safely", title: "Change safely", disclosure: "Illustrative static example", heading: "Refactor checkout tax rounding with bounded risk.", target: "Pull request #482 · checkout-tax-rounding", gitState: "main @ 8f31c2a → feature/checkout-tax-rounding @ c7e194d",
    question: "How can the rounding refactor land without breaking totals or provider reconciliation?", summary: "Move tax rounding to the checkout boundary while keeping the integer-cents API contract unchanged.",
    outputs: [
      { title: "Refactor sequence", summary: "Introduce the boundary conversion first, update consumers second, and remove duplicate rounding last.", items: ["Add boundary conversion in TaxCalculator.", "Update CheckoutService consumers.", "Remove provider-specific duplicate rounding after validation."] },
      { title: "Dependency impact", summary: "Checkout totals affect the API response, persisted orders, and payment-provider reconciliation.", items: ["Checkout API response", "Order persistence", "Payment-provider adapters"] },
      { title: "Test and regression impact", summary: "Unit coverage exists; provider reconciliation and historical-cart behavior remain release risks.", items: ["Execute high-precision TaxCalculator cases.", "Add checkout response contract coverage.", "Replay provider reconciliation in staging."] },
    ],
    evidence: [
      { statement: "TaxCalculator rounds each tax line before adding it to the order total.", citation: "src/checkout/TaxCalculator.ts:L42-L61" },
      { statement: "The checkout response exposes totals as integer cents.", citation: "src/api/CheckoutResponse.ts:L18-L31" },
      { statement: "Historical carts can be recalculated from stored order data.", citation: "src/checkout/OrderRepository.ts:L88-L104" },
    ],
    unknown: { statement: "Whether every payment provider reconciles fractional adjustments identically.", neededEvidence: "Provider-specific reconciliation results for the supported adapter matrix." },
    nextDecision: { owner: "PR owner and reviewer", action: "Run the provider reconciliation matrix, then decide whether PR #482 can merge with staged rollout conditions." }, detailReport: reportData,
  },
  {
    id: "ship-clearly", title: "Ship clearly", disclosure: "Illustrative static example", heading: "Turn the same change into release-ready artifacts.", target: "Pull request #482 · checkout-tax-rounding", gitState: "main @ 8f31c2a → feature/checkout-tax-rounding @ c7e194d",
    question: "Is the public contract compatible, what should the release say, and what blocks rollout?", summary: "The response shape remains compatible, but rollout depends on provider and historical-cart validation.",
    outputs: [
      { title: "API compatibility", summary: "Compatible — no endpoint, field, or type shape changes are illustrated.", items: ["POST /checkout/quote is unchanged.", "Total fields remain integer cents."] },
      { title: "Release notes", summary: "Generate distinct technical and user-facing explanations from the same evidence.", items: ["Technical: tax rounding now occurs at the checkout boundary.", "User-facing: checkout tax totals remain consistent across line items and order totals."] },
      { title: "Release conditions", summary: "Roll out only after reconciliation and staged high-precision comparisons.", items: ["Confirm every supported provider.", "Compare staged high-precision carts.", "Record rollback owner and threshold."] },
    ],
    evidence: [
      { statement: "The checkout response retains its existing integer-cent fields.", citation: "src/api/CheckoutResponse.ts:L18-L31" },
      { statement: "The rounding behavior changes inside TaxCalculator.", citation: "src/checkout/TaxCalculator.ts:L42-L61" },
      { statement: "The provider runbook defines reconciliation checks before rollout.", citation: "docs/payments/provider-reconciliation.md:L1-L24" },
    ],
    unknown: { statement: "Whether historical carts need correction after the release.", neededEvidence: "A replay of representative stored carts against the new calculation." },
    nextDecision: { owner: "Release owner", action: "Approve rollout only after provider reconciliation and historical-cart replay satisfy the documented thresholds." },
  },
  {
    id: "evolve-operate", title: "Evolve & operate", disclosure: "Illustrative static example", heading: "Plan the money migration and triage reconciliation drift.", target: "northstar-commerce · checkout payments", gitState: "main @ 8f31c2a · incident INC-204 evidence snapshot",
    question: "What is causing provider reconciliation drift, and how should integer money be migrated safely?", summary: "Provider-boundary conversion is the leading incident hypothesis and the natural first migration seam.",
    outputs: [
      { title: "Migration waves", summary: "Move from scattered decimal handling to one Money value object through reversible boundaries.", items: ["Wave 1: introduce Money at checkout boundaries.", "Wave 2: migrate tax and order persistence.", "Wave 3: adapt providers and backfill historical data."] },
      { title: "Ranked incident hypotheses", summary: "Provider conversion leads; historical-cart recalculation remains plausible.", items: ["#1 Provider adapter compares decimal and integer totals; one sandbox run contradicts a universal provider failure.", "#2 Historical carts recalculate under new rounding; clean new-cart totals contradict a global checkout defect."] },
      { title: "Validation and rollback", summary: "Capture the failing payload, replay it, and gate the migration on parity.", items: ["Capture raw provider request and response.", "Replay affected and unaffected carts.", "Rollback boundary conversion if reconciliation exceeds the threshold."] },
    ],
    evidence: [
      { statement: "The provider adapter converts checkout totals before reconciliation.", citation: "src/payments/PaymentProviderAdapter.ts:L44-L77" },
      { statement: "Stored carts can be recalculated when an order is reopened.", citation: "src/checkout/OrderRepository.ts:L88-L104" },
      { statement: "The runbook defines payload replay and containment steps.", citation: "docs/runbooks/reconciliation.md:L32-L68" },
    ],
    unknown: { statement: "The failing provider payload is not present in this illustrative snapshot.", neededEvidence: "The raw provider exchange and correlated application logs for INC-204." },
    nextDecision: { owner: "Incident commander and migration owner", action: "Choose containment after payload replay, then authorize migration wave 1 only after parity checks pass." },
  },
];

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
  fullLifecycle: {
    hero: {
      eyebrow: "Evidence-backed AI engineering workflows",
      title: "Engineering intelligence across the software lifecycle.",
      description:
        "Install Engineering Power in Codex, GitHub Copilot, Claude Code, or Cursor. Understand unfamiliar repositories, change them safely, prepare releases, plan migrations, and investigate incidents with cited code evidence.",
      primaryCta: "Choose your assistant",
      secondaryCta: "Explore capabilities",
    },
    lifecycle: {
      eyebrow: "The complete engineering loop",
      title: "From first read to production reality.",
      description:
        "Use one evidence discipline across the work that happens before, during, and after a code change.",
    },
    explorer: {
      eyebrow: "Explore the workflows",
      title: "Start with the engineering question.",
    },
    howItWorks: {
      eyebrow: "How it works",
      title: "Evidence in. Engineering judgment out.",
      boundary:
        "This website is a static demo. Repository analysis runs inside your chosen coding assistant and follows that host's access and data policy.",
    },
    hosts: {
      eyebrow: "Works where you code",
      title: "Bring the same engineering discipline to your assistant.",
      description:
        "Every supported host can run workflows across understanding, safe change, clear shipping, migration, and incident investigation.",
    },
    finalCta: {
      title: "Bring Engineering Power to your coding assistant.",
      cta: "Choose your assistant",
    },
  },
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
