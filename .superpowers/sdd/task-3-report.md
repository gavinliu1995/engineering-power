# Task 3 — Static evidence-report demonstration

## Scope delivered

Implemented the static `/demo-report` route for the fictional
`checkout-tax-rounding` pull request. The report is deliberately a presentation
of illustrative data only: it has no form inputs, submit actions, API calls, or
claims of live repository analysis.

The page contains:

- Typed `reportData` metadata, evidence findings, validation states, risks, and
  release conditions.
- A `Proceed with conditions` release recommendation.
- Separate Facts, Inferences, and Unknowns sections, each rendered through the
  shared `EvidenceSection` component.
- Explicit illustrative-citation labels beside every code-style source path.
- An API compatibility summary and an Executed / Discovered / Recommended
  validation matrix.
- Focused report styles, including narrow-screen stacking required for legible
  report content.

## RED

Added `renders distinct evidence and validation states on the demo report` to
`src/App.test.tsx` before writing the report components.

Command:

```sh
npm test -- --run src/App.test.tsx --reporter=verbose
```

Result: failed as intended. The only existing report heading was `Demo report`,
so Testing Library could not find the required `Release decision` heading. This
confirmed the test was exercising the missing report behavior rather than a
test setup issue.

## GREEN

Created `ReportHeader`, `EvidenceSection`, `ValidationMatrix`, and
`ReleaseDecision`; added the typed static data; composed the route; and added
the report-specific styles. A pre-existing test then identified that the route
heading no longer included `Demo report`; the header was adjusted to `Demo
report: checkout-tax-rounding` so the established route contract remains true.

Command:

```sh
npm test -- --run src/App.test.tsx --reporter=verbose && npm run build
```

Result: 7 tests passed and the TypeScript/Vite production build completed.

## Constraints checked

- No live analysis or online-analysis controls were added.
- Citation text clearly says it is illustrative, and the header explicitly says
  the demo is not live repository analysis.
- Facts, inferences, and unknowns are visually and semantically separated.
- Validation states distinguish executed checks from discovered gaps and
  recommendations.
