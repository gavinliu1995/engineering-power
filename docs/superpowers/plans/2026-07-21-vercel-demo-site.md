# Engineering Power Vercel Demo Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use engineering-power:subagent-driven-development (recommended) or engineering-power:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static, responsive English product site and illustrative demo-report route for Engineering Power that can deploy to Vercel without backend services.

**Architecture:** Use Vite, React, TypeScript, and React Router for a static single-page application. Keep reusable product content in a typed local module, map it into small presentational components, and use a route-aware app shell to render the home page, demo report, and not-found state.

**Tech Stack:** Vite, React 18, TypeScript, React Router, Vitest, Testing Library, CSS.

## Global Constraints

- No server routes, database, authentication, analytics dependency, environment variables, or API calls.
- All public UI copy is English.
- Do not claim live repository analysis, GitHub App access, or automated release approval.
- The primary CTA text is exactly `View Demo Report` and navigates to `/demo-report`.
- Demo citations are visibly labeled illustrative; facts, inferences, unknowns, and validation states remain distinct.
- The site must build with `npm run build`, remain responsive, and preserve the existing Python plugin tests.

---

### Task 1: Bootstrap the static application and verify its routes

**Files:**
- Create: `package.json`
- Create: `vite.config.ts`
- Create: `tsconfig.json`
- Create: `index.html`
- Create: `src/main.tsx`
- Create: `src/App.tsx`
- Create: `src/styles.css`
- Create: `src/test/setup.ts`
- Create: `src/App.test.tsx`

**Interfaces:**
- Consumes: browser pathname and static React assets.
- Produces: `App`, rendering `/`, `/demo-report`, and an accessible not-found route.

- [ ] **Step 1: Write the failing route test**

```tsx
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

test("renders the product headline on the home route", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /evidence-backed engineering decisions/i })).toBeInTheDocument();
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because the Vite/React application and `App` do not exist.

- [ ] **Step 3: Create the minimal application**

Create a Vite React TypeScript configuration with `dev`, `build`, `preview`, and
`test` scripts. Mount `App` in `src/main.tsx`; add React Router routes for
`/`, `/demo-report`, and `*`; render the required home headline and a minimal
not-found message. Configure Vitest with jsdom and Testing Library matchers.

```tsx
<Routes>
  <Route path="/" element={<HomePage />} />
  <Route path="/demo-report" element={<DemoReportPage />} />
  <Route path="*" element={<NotFoundPage />} />
</Routes>
```

- [ ] **Step 4: Verify GREEN and production build**

Run: `npm test -- --run src/App.test.tsx && npm run build`

Expected: route test passes and Vite emits a production `dist/` directory.

- [ ] **Step 5: Commit**

```bash
git add package.json package-lock.json vite.config.ts tsconfig.json index.html src
git commit -m "feat: scaffold static demo site"
```

### Task 2: Build the product narrative home page

**Files:**
- Create: `src/content/siteContent.ts`
- Create: `src/components/Header.tsx`
- Create: `src/components/Hero.tsx`
- Create: `src/components/EvidenceFlow.tsx`
- Create: `src/components/OutputCards.tsx`
- Create: `src/components/TrustBoundary.tsx`
- Create: `src/components/Footer.tsx`
- Modify: `src/App.tsx`
- Modify: `src/styles.css`
- Modify: `src/App.test.tsx`

**Interfaces:**
- `siteContent.ts` exports typed `outputs` and `trustBoundaries` arrays.
- `HomePage` consumes the content arrays and renders one semantic section per
  product-story stage.
- `Hero` renders a link to `/demo-report` with accessible name `View Demo Report`.

- [ ] **Step 1: Write failing content and CTA tests**

```tsx
test("connects the hero CTA to the static demo report", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByRole("link", { name: "View Demo Report" })).toHaveAttribute("href", "/demo-report");
});

test("describes the three decision-ready outputs", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByText("Change Impact")).toBeInTheDocument();
  expect(screen.getByText("API Contract Delta")).toBeInTheDocument();
  expect(screen.getByText("Release Readiness")).toBeInTheDocument();
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because the CTA and product-output content are absent.

- [ ] **Step 3: Implement the home page sections**

Use compact, evidence-accurate copy and the following flow nodes:

```ts
export const evidenceFlow = [
  "Pull request or local comparison",
  "One exact evidence snapshot",
  "Cited engineering outputs",
  "Decision-ready summary",
];
```

Render a header, hero, why-it-matters section, connected-decision flow, three
output cards, demo-preview CTA, trust-boundary section, and footer GitHub link.
Keep UI sections composed from focused components and all repeated copy in
`siteContent.ts`.

- [ ] **Step 4: Verify GREEN**

Run: `npm test -- --run src/App.test.tsx && npm run build`

Expected: all home-page assertions pass and the site builds.

- [ ] **Step 5: Commit**

```bash
git add src
git commit -m "feat: add engineering power product narrative"
```

### Task 3: Implement the evidence-report demonstration

**Files:**
- Create: `src/components/ReportHeader.tsx`
- Create: `src/components/EvidenceSection.tsx`
- Create: `src/components/ValidationMatrix.tsx`
- Create: `src/components/ReleaseDecision.tsx`
- Modify: `src/content/siteContent.ts`
- Modify: `src/App.tsx`
- Modify: `src/styles.css`
- Modify: `src/App.test.tsx`

**Interfaces:**
- `reportData` provides typed metadata, findings, validation rows, risks, and
  release conditions to the report components.
- `EvidenceSection` receives `{ label, tone, items }` and labels demo citations
  as illustrative.
- `DemoReportPage` presents a static report only; it contains no submit controls
  or live-analysis promise.

- [ ] **Step 1: Write the failing report-route test**

```tsx
test("renders distinct evidence and validation states on the demo report", () => {
  render(<MemoryRouter initialEntries={["/demo-report"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /release decision/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Facts" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Inferences" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Unknowns" })).toBeInTheDocument();
  expect(screen.getByText(/illustrative demo citations/i)).toBeInTheDocument();
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because the report sections and demo-citation note are absent.

- [ ] **Step 3: Implement the static report**

Populate a fictional `checkout-tax-rounding` pull request with a recommendation
of `Proceed with conditions`. Use code-style source paths such as
`src/checkout/TaxCalculator.ts:L42-L61`, while visibly marking all citations as
illustrative. Render metadata, a decision block, separate Facts/Inferences/
Unknowns, an API compatibility summary, executed/discovered/recommended
validation rows, risks, and release conditions.

```tsx
<EvidenceSection label="Facts" tone="fact" items={reportData.facts} />
<EvidenceSection label="Inferences" tone="inference" items={reportData.inferences} />
<EvidenceSection label="Unknowns" tone="unknown" items={reportData.unknowns} />
```

- [ ] **Step 4: Verify GREEN**

Run: `npm test -- --run src/App.test.tsx && npm run build`

Expected: report assertions pass and static production build succeeds.

- [ ] **Step 5: Commit**

```bash
git add src
git commit -m "feat: add static evidence report demo"
```

### Task 4: Finish responsive visual design and deployment readiness

**Files:**
- Modify: `src/styles.css`
- Create: `public/vercel.svg`
- Create: `README.md` (deployment section only)
- Create: `vercel.json`
- Modify: `src/App.test.tsx`

**Interfaces:**
- CSS exposes responsive layouts for the hero, flow, cards, report grid, and
  data tables without JavaScript viewport logic.
- `vercel.json` rewrites non-asset routes to `/index.html` so the demo-report
  route works on a direct Vercel visit.

- [ ] **Step 1: Write the failing navigation resilience test**

```tsx
test("offers a route back home when a page is not found", () => {
  render(<MemoryRouter initialEntries={["/missing"]}><App /></MemoryRouter>);
  expect(screen.getByRole("link", { name: /back to home/i })).toHaveAttribute("href", "/");
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because the fallback link is absent or has an incorrect target.

- [ ] **Step 3: Add responsive and deployment details**

Add the not-found recovery link. Complete the deep-ink, quiet-panel visual
system with semantic status colors and a mobile breakpoint that stacks grids and
keeps report tables horizontally scrollable. Add the following Vercel rewrite:

```json
{
  "rewrites": [{ "source": "/(.*)", "destination": "/index.html" }]
}
```

Document `npm install`, `npm run dev`, `npm run build`, and Vercel import
instructions in the README without altering the existing plugin documentation.

- [ ] **Step 4: Verify GREEN and regressions**

Run: `npm test -- --run && npm run build && python3 -m unittest discover -s tests -v && git diff --check`

Expected: frontend tests, production build, all existing Python tests, and
whitespace checks pass.

- [ ] **Step 5: Commit**

```bash
git add README.md vercel.json public src
git commit -m "feat: prepare vercel demo deployment"
```
