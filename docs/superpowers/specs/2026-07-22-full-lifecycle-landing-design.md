# Engineering Power Full-Lifecycle Landing Design

## Status

Approved direction. This specification replaces the PR-review-led narrative in
the current Vercel demo with a full software-engineering lifecycle narrative.

## Goal

Present Engineering Power as an evidence-backed engineering intelligence layer
for Codex, GitHub Copilot, Claude Code, and Cursor. A visitor should understand
within the first screen that the product helps engineers understand, change,
ship, evolve, and operate codebases. Pull-request review remains supported, but
it is one workflow inside the broader product rather than the product identity.

## Source of truth

The user confirmed that all ten assigned capabilities are currently integrated.
The website must therefore present every capability as available, not planned:

1. Repository refactoring assistance
2. API contract generation
3. Release note generation
4. Dependency impact analysis
5. Runtime incident triage
6. Architecture review support
7. Test impact analysis
8. Regression risk detection
9. Migration planning
10. Repository-specific onboarding

This confirmed product state supersedes older demo copy that describes
refactoring assistance or runtime incident triage as future work.

These ten capabilities are the minimum product story, not a replacement for
the broader workflows already present in Engineering Power. Repository
Intelligence, PR Impact Analysis, Release Readiness, and Systematic Debugging
remain available and are placed within the lifecycle rather than promoted as
separate product identities.

## Selected narrative

### Primary promise

**Engineering intelligence across the software lifecycle.**

Suggested hero copy:

> Install Engineering Power in Codex, GitHub Copilot, Claude Code, or Cursor.
> Understand unfamiliar repositories, change them safely, prepare releases,
> plan migrations, and investigate incidents with cited code evidence.

The primary CTA remains **Choose your assistant**. A secondary
**Explore capabilities** anchor moves visitors to the lifecycle section rather
than making a PR report the second-most-important action.

### Considered approaches

1. **Lifecycle narrative — selected.** Group the ten capabilities by the job an
   engineer is trying to complete. This gives the broad product a memorable
   story without creating a wall of feature cards.
2. **Flat capability catalog — rejected.** Ten equal cards would be complete
   but would feel like a plugin marketplace and provide no sense of how the
   capabilities work together.
3. **PR-led story with additional capability sections — rejected.** This would
   preserve the current misconception because the hero, first problem, and
   demo would still teach visitors that PR review is the main product.

## Capability model

The home page groups the complete product into four user-facing stages:

| Stage | User outcome | Included capabilities |
| --- | --- | --- |
| **Understand** | Build a reliable mental model of an unfamiliar repository | Repository Intelligence; Repository-specific onboarding; Architecture review support |
| **Change safely** | Plan and review code changes without losing downstream effects | Repository refactoring assistance; Dependency impact analysis; Test impact analysis; Regression risk detection; PR Impact Analysis as a supporting workflow |
| **Ship clearly** | Make interfaces, release communication, and go/no-go criteria explicit | API contract generation; Release note generation; Release Readiness as a supporting workflow |
| **Evolve & operate** | Modernize systems and investigate runtime failures | Migration planning; Runtime incident triage, supported by Systematic Debugging |

Every assigned capability appears by name in the home-page content. The broader
existing workflows can appear as supporting labels, but they must not obscure
those ten capabilities. PR review appears only inside **Change safely**.

## Information architecture

### Header

Keep the Citation Frame mark and current color system. Expand the desktop
navigation to:

- Capabilities
- How it works
- Hosts
- GitHub

On narrow screens, keep the brand and a compact in-page navigation treatment;
do not introduce an app-style drawer for this static site.

### 1. Hero

- Eyebrow: `Evidence-backed AI engineering workflows`
- Headline: `Engineering intelligence across the software lifecycle.`
- Supporting copy uses the full-lifecycle promise above.
- Primary CTA: `Choose your assistant` → `/start`
- Secondary CTA: `Explore capabilities` → `#capabilities`
- Keep the existing abstract Intelligence Flow Field and calm mouse response.
- Remove hero-level emphasis on reports, PRs, diffs, reviewers, base/head, or
  release decisions.

### 2. Lifecycle overview

Introduce the four stages in one editorial sequence: **Understand → Change
safely → Ship clearly → Evolve & operate**. Avoid ten equal cards. Each stage
gets a concise outcome statement and a plain-language list of its capabilities.

This section replaces the current `A diff shows changes` section and the
Facts/Inferences/Unknowns cards. Evidence discipline moves to the later
`How it works` section, where it supports the product rather than defines it.

### 3. Capability explorer

Add one interactive, static capability explorer with the four lifecycle stages
as an accessible tab set. The default selection is **Understand**, not PR review.

Each stage panel contains:

- the engineering question being answered;
- the included capabilities;
- one concise example output;
- the evidence or human input required;
- a link to the multi-scenario demo route.

The four example outcomes are:

1. **Understand:** architecture map, business flow, reading order, setup path.
2. **Change safely:** refactor sequence, dependency/test impact, regression
   risks, with PR analysis shown only as one possible input.
3. **Ship clearly:** API compatibility delta and technical/user-facing release
   notes.
4. **Evolve & operate:** migration waves or ranked incident hypotheses with
   supporting and contradicting evidence.

The explorer is local state only. It does not upload code or imply live
analysis.

### 4. How it works

Replace internal phrasing such as `One bounded evidence snapshot` with a clear
four-step explanation:

1. Choose a repository, PR, local comparison, working tree, patch, or incident
   evidence.
2. Engineering Power records the exact Git state and collects limited,
   traceable evidence.
3. The selected workflow produces a cited engineering result and keeps facts,
   inferences, unknowns, and validation states distinct.
4. The engineer reviews the result and owns the decision.

State prominently that this website is a static demo. Repository analysis runs
inside the chosen coding assistant, subject to that host's access and data
policy.

### 5. Multi-scenario demo

Retain the existing `/demo-report` route to avoid unnecessary route expansion,
but redesign the page as **Engineering Power demo** with the same four lifecycle
tabs. Each tab renders static illustrative content.

The current checkout-tax-rounding PR report becomes the **Change safely**
scenario. It is no longer the default or the only demo. The default demo is
**Understand**, showing a repository overview, architecture boundary, business
flow, and recommended reading order.

Use one coherent fictional codebase, `northstar-commerce`, across all four
panels so the demo feels like a connected engineering lifecycle rather than
four unrelated marketing samples:

- **Understand:** repository overview, checkout business flow, architecture
  boundary, setup path, and recommended reading order at `main @ 8f31c2a`.
- **Change safely:** retain pull request `#482 · checkout-tax-rounding` and its
  existing base/head comparison, then add the refactor sequence, dependency
  impact, test impact, and regression risks around it.
- **Ship clearly:** use the same change to show an API compatibility conclusion,
  technical release notes, user-facing release notes, and release conditions.
- **Evolve & operate:** show a compact integer-money migration plan alongside
  ranked hypotheses for an illustrative provider-reconciliation incident.

Every panel includes the target and Git state, the engineering question, two
or three representative outputs, at least two illustrative file-and-line
citations, one explicit unknown, and a human-owned next decision. Each panel
must visibly say `Illustrative static example`; the fictional repository and
citations must never be presented as a live analysis result.

No mock analyze form, repository upload, authentication, or backend is added.

### 6. Host integration

Show the four supported hosts on the home page:

- Codex
- GitHub Copilot
- Claude Code
- Cursor

The existing `/start` route remains the conversion destination. Its intro
briefly states that every host can run the four lifecycle stages, then lets the
visitor choose a host. Each downstream host guide adds a `First things to try`
section with four prompts spanning the lifecycle:

- understand this repository;
- plan a safe refactor or assess a change;
- generate an API/release artifact;
- plan a migration or investigate an incident.

Do not default every host guide to a pull-request prompt.

### 7. Trust boundary

Retain the strongest trust claims, condensed into four readable principles:

- cited evidence tied to an exact Git state;
- facts, inferences, and unknowns remain separate;
- executed, discovered, and recommended checks remain separate;
- read-only by default, with humans owning the decision.

The static-demo disclosure remains visible before the footer.

### 8. Final CTA and footer

End with `Bring Engineering Power to your coding assistant`, linking to
`/start`, followed by the existing GitHub destination and static-demo note.

## Visual and motion direction

- Preserve the current black/graphite, warm off-white, white, and chartreuse
  system; this is an information-architecture correction, not another brand
  reset.
- Preserve the Citation Frame identity and the abstract flowing intelligence
  field.
- Use large editorial headlines, restrained monospace labels, open whitespace,
  and thin rules.
- Use one active chartreuse underline or indicator in the lifecycle explorer;
  do not turn it into a dashboard, node graph, architecture diagram, or grid of
  ten boxes.
- Transitions between lifecycle stages use a short fade/translate animation.
  Essential text never animates continuously.
- Respect `prefers-reduced-motion` and keep the existing background static when
  reduced motion is requested.
- Fix the current dark-card heading contrast defect so every capability title
  is legible.

## Component and content boundaries

Keep route composition in `App.tsx`, but move lifecycle and scenario content
into typed data in `siteContent.ts`.

Add focused presentational components:

- `LifecycleOverview` — static four-stage narrative and complete capability list.
- `CapabilityExplorer` — accessible local-state tab interaction.
- `HowItWorks` — static four-step explanation and website/skill boundary.
- `HostOverview` — four supported hosts and link to `/start`.
- `ScenarioDemo` — shared rendering for the four static demo scenarios.

Retire or repurpose the current PR-led `EvidenceFlow` and `OutputCards` rather
than layering the new narrative beneath them. Keep the existing evidence report
components only where they support the **Change safely** demo.

## Repository documentation

Update the website repository `README.md` in the same implementation. Replace
the Demo-MVP and planned-work wording with the confirmed full-lifecycle scope,
while keeping installation and local-development instructions accurate. This
prevents the deployed site and its own repository documentation from making
contradictory capability claims.

## Data flow and failure behavior

The site remains a static Vite SPA:

```text
Local typed content
  → React presentation components
  → local lifecycle/demo selection
  → /start installation guides
```

There is no fetch, server action, API route, repository credential, analytics
dependency, or persistence. Unknown routes continue to use the custom 404.

The lifecycle overview exposes all ten assigned capabilities without requiring
tab interaction. In the explorer and demo, every tab panel remains mounted in
the document and inactive panels use the native `hidden` attribute; the
**Understand** panel is visible by default before the visitor makes a selection.

## Accessibility and responsive behavior

- Use semantic sections with unique headings and stable anchor targets.
- Implement the explorer as a keyboard-operable tab set with `aria-selected`,
  linked tab/panel IDs, Left/Right Arrow behavior, and visible focus.
- Do not rely on chartreuse alone to communicate the selected stage.
- Maintain readable text/background contrast, including dark feature panels.
- At narrow widths, stack each lifecycle stage and keep capability names fully
  visible without horizontal scrolling.
- The hero headline must reflow without clipping from 320px upward.
- Decorative 3D motion remains hidden from assistive technology.

## Testing strategy

Add or update frontend tests to prove:

- the hero communicates full-lifecycle engineering intelligence;
- all ten assigned capabilities appear on the home page;
- PR review is not the home-page headline or default demo;
- lifecycle tabs expose four named stages and support keyboard selection;
- the default demo is repository understanding;
- the Change safely demo retains the illustrative PR report;
- every host guide includes lifecycle-spanning starter prompts;
- the website/installed-skill boundary remains explicit;
- the `/start` chooser states lifecycle breadth and every downstream host guide
  includes four lifecycle-spanning prompts;
- home, demo, start, host guide, and not-found routes remain navigable;
- reduced-motion and decorative-canvas accessibility contracts remain intact.

Run the complete frontend test suite, TypeScript/Vite production build,
`git diff --check`, and a visual browser pass at narrow and desktop widths.

## Acceptance criteria

1. A first-time visitor can describe Engineering Power without using the phrase
   `PR review tool` after reading the hero and lifecycle overview.
2. Every assigned capability is visible by name on the home page.
3. PR review appears only inside the **Change safely** stage.
4. Repository understanding is the default interactive example.
5. The demo covers all four lifecycle stages, `/start` states that breadth, and
   every downstream host guide offers one starter prompt per stage.
6. The site remains honest about being static and never presents an upload or
   live-analysis control.
7. Existing visual identity, motion quality, routes, GitHub link, and return-home
   navigation remain intact.
8. The production build and all automated checks pass.
9. Existing Repository Intelligence, PR Impact Analysis, Release Readiness, and
   Systematic Debugging workflows remain discoverable in their lifecycle
   context without displacing the ten assigned capabilities.
10. The website repository README no longer describes repository refactoring
    assistance or runtime incident triage as planned work. Its overview and
    capability table match the full-lifecycle product story.

## Non-goals

- A hosted repository-analysis backend or additional API spend.
- GitHub authentication, repository upload, billing, analytics, or persistence.
- A new visual brand, new illustration metaphor, or additional 3D scene.
- Ten independent feature pages.
- Removing PR analysis; it remains an important **Change safely** workflow.
