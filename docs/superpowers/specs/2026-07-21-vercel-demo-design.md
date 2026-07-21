# Engineering Power Vercel Demo Site Design

## Goal

Create a static, English-language product demonstration site for Engineering
Power that deploys on Vercel without a backend, repository access, or new API
budget. The site must help engineering leaders understand the decision-making
value while giving engineers a concrete view of the evidence-backed workflow.

## Product boundary

This is a product narrative and report-demo site, not an online repository
analysis product. It must not imply that visitors can submit a repository, PR,
or credentials for live analysis. The site presents the plugin's documented
capabilities and a clearly labeled, static example report.

## Audience and conversion

The primary audience is both engineering leaders and individual engineers:

- Leaders should quickly see that Engineering Power makes release and change
  decisions traceable, bounded, and easier to review.
- Engineers should see the concrete outputs: impact analysis, API deltas,
  validation status, and release decision support.

The primary call to action is **View Demo Report**. It opens an in-site static
report page rather than an integration or purchase flow.

## Information architecture

### Home page

1. **Hero** — `Evidence-backed engineering decisions.` A concise explanation
   that the product turns one exact code-change snapshot into cited engineering
   outputs.
2. **Why it matters** — Contrast ungrounded summaries with facts, inferences,
   and unknowns that remain traceable to code evidence.
3. **One snapshot, connected decisions** — A visual workflow from PR or local
   comparison to shared evidence and then to impact, API, release, and decision
   outputs.
4. **Decision-ready outputs** — Three feature cards: Change Impact, API
   Contract Delta, and Release Readiness. The copy must reflect existing plugin
   capabilities only.
5. **Demo report preview** — A compact, credible report excerpt and the main
   **View Demo Report** button.
6. **Built for trustworthy boundaries** — Explain exact Git state, citations,
   test-status distinctions, deadlines, and explicit limitations.
7. **Footer** — GitHub repository link and an honest static-demo note.

### Demo report page

The page portrays a fictional but plausible pull-request analysis. It contains:

- target, base/head, profile, and evidence snapshot metadata;
- a release recommendation and confidence statement;
- facts, inferences, and unknowns as visually distinct sections;
- affected components and an API compatibility delta;
- executed, discovered, and recommended validation separated explicitly;
- risks and release conditions;
- repository-relative citations presented as illustrative links/text, labeled as
  demo evidence rather than real source references.

## Visual direction

Use a polished technical-editorial look: a deep ink/navy foundation, quiet
off-white content panels, electric blue for active evidence paths, and restrained
green/amber/red semantic status colors. Favor large, confident typography,
generous whitespace, thin rules, and compact monospace metadata. The report
should feel like a high-quality engineering review artifact, not a generic SaaS
dashboard.

## Technical approach

Implement a small static site with a Vercel-compatible React framework and no
server routes, database, authentication, analytics dependency, or environment
variables. Keep all copy and demo-report data local in the repository. The
deployment should work using Vercel's standard build detection and provide an
explicit local development command.

## Error handling and limitations

Because the first version has no runtime data fetching or user input, the main
failure mode is a missing route or build error. The implementation should use
simple static routes, accessible links, semantic headings, and a custom 404
experience if supported by the selected framework. Product copy must never
promise live analysis, GitHub App access, or automated release approvals.

## Testing and acceptance criteria

- The site builds successfully with the production build command.
- Both the home and demo-report routes render locally.
- The primary CTA reaches the demo report.
- The static content accurately reflects documented plugin capabilities and
  boundaries.
- The layout is responsive and usable on narrow screens.
- Existing Python plugin tests continue to pass.

## Non-goals

- Live GitHub, Git, PR, or patch ingestion.
- API routes, credentials, authentication, billing, or persistence.
- A fake submit/analyze control that suggests the product is already an online
  service.
