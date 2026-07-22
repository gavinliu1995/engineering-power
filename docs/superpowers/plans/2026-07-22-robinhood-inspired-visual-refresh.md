# Robinhood-Inspired Visual Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use engineering-power:subagent-driven-development (recommended) or engineering-power:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restyle the static Engineering Power demo as a dark-signal, light-canvas product site with accessible, reduced-motion-safe evidence animation.

**Architecture:** Add one decorative `EvidenceSignalField` component to the existing home hero, then replace CSS tokens and responsive layout rules while leaving routes, content, and report semantics intact. CSS keyframes implement all motion without new runtime dependencies.

**Tech Stack:** React, TypeScript, CSS keyframes, Vitest, Testing Library.

## Global Constraints

- Do not copy Robinhood branding, assets, copy, or page structure.
- Keep the hero CTA text and destination exactly `View Demo Report` → `/demo-report`.
- No dependencies, network calls, animation libraries, server routes, or live data.
- The decorative signal field must be `aria-hidden="true"` and respect `prefers-reduced-motion`.
- Preserve every static-demo disclosure, report fact, validation state, and semantic table.

---

### Task 1: Add the decorative evidence-signal hero component

**Files:**
- Create: `src/components/EvidenceSignalField.tsx`
- Modify: `src/App.tsx`
- Modify: `src/App.test.tsx`

**Interfaces:**
- `EvidenceSignalField(): JSX.Element` renders only decorative nodes, paths,
  code labels, and a release-decision capsule.
- `Hero` consumes the component beside its existing copy without changing the
  CTA contract.

- [ ] **Step 1: Write a failing accessibility test**

```tsx
test("keeps the animated evidence signal decorative", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByTestId("evidence-signal-field")).toHaveAttribute("aria-hidden", "true");
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because `evidence-signal-field` does not exist.

- [ ] **Step 3: Implement the minimal component and composition**

```tsx
export function EvidenceSignalField() {
  return <div aria-hidden="true" className="evidence-signal-field" data-testid="evidence-signal-field">...</div>;
}
```

Wrap the existing Hero copy and this component in a `.hero-layout` container.
Use only local text fragments and presentational spans.

- [ ] **Step 4: Verify GREEN**

Run: `npm test -- --run src/App.test.tsx`

Expected: all assertions pass.

### Task 2: Apply dark-signal/light-canvas styling and accessible motion

**Files:**
- Modify: `src/styles.css`
- Modify: `src/App.test.tsx`

**Interfaces:**
- CSS tokenizes ink, warm canvas, chartreuse signal, lilac tint, and motion
  values.
- The hero is two columns at desktop width and one column below 720px.

- [ ] **Step 1: Write a failing visual-contract test**

```tsx
test("renders the release-decision signal inside the decorative field", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByTestId("evidence-signal-field")).toHaveTextContent("PROCEED WITH CONDITIONS");
});
```

- [ ] **Step 2: Verify RED**

Run: `npm test -- --run src/App.test.tsx`

Expected: FAIL because the signal component has no decision capsule.

- [ ] **Step 3: Implement visual tokens and motion**

Create CSS keyframes for point drift, path glow, and capsule settle. Use a
`@media (prefers-reduced-motion: reduce)` block to remove animation and
transforms. Restyle page canvases, cards, report panels, controls, focus rings,
and mobile layout to the approved dark-signal/light-canvas system.

- [ ] **Step 4: Verify GREEN and build**

Run: `npm test -- --run src/App.test.tsx && npm run build`

Expected: test suite passes and production build completes.

### Task 3: Verify full regressions and commit

**Files:**
- Modify: `src/components/EvidenceSignalField.tsx`
- Modify: `src/App.tsx`
- Modify: `src/App.test.tsx`
- Modify: `src/styles.css`

- [ ] **Step 1: Run complete checks**

Run: `npm test -- --run && npm run build && python3 -m unittest discover -s tests -v && git diff --check`

Expected: frontend tests, production build, 54 Python tests, and whitespace
check all pass.

- [ ] **Step 2: Commit**

```bash
git add src
git commit -m "feat: refresh demo visual system"
```
