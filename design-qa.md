# Design QA

## Evidence

- Source visual truth: `/Users/gavin.liu/.codex/generated_images/019f83a8-22f2-73c2-b19b-abbdf9d2cd43/exec-3d015f7c-0772-4d61-9700-6995e2628f3a.png`
- Browser-rendered implementation: `/tmp/engineering-power-hero-final.png`
- Final combined comparison: `/tmp/engineering-power-design-qa-final.png`
- Route and state: `http://127.0.0.1:5173/`, dark desktop hero, entry motion settled for 1.1 seconds, no pointer input
- CSS viewport: `1672 x 941`
- Source pixels: `1672 x 941`
- Implementation screenshot pixels: `1657 x 933` (the in-app browser capture excludes its scrollbar gutter)
- Density: `deviceScaleFactor 1`; source and implementation were each proportionally normalized into `836 x 471` panes and placed in one `1672 x 471` comparison canvas without cropping
- Responsive evidence: `390 x 844` CSS viewport; document scroll width remained within the viewport, the heading stayed inside its container, and the primary CTA remained visible

## Findings

- No actionable P0, P1, or P2 differences remain.
- [P3] The live flow field is slightly more filament-like than the source's softer ribbon volume. This is an acceptable consequence of implementing the requested real-time React Three Fiber scene instead of shipping the static concept image. The broad translucent layer, converging flow, lime highlight, and restrained motion preserve the selected art direction.
- [P3] The header intentionally keeps the existing product's direct GitHub navigation instead of reproducing the concept mock's generic enterprise navigation. This preserves the user-approved product journey and does not affect the hero hierarchy.

## Required Fidelity Surfaces

- Fonts and typography: the implementation uses the existing Inter/system sans stack with a restrained medium display weight, tight negative tracking, and the same three-line headline structure as the source. Eyebrow, body copy, and CTA retain clear optical hierarchy at desktop and mobile sizes.
- Spacing and layout rhythm: the brand aligns near the outer edge while hero content uses the source's slightly deeper inset. The hero fills the first viewport, the copy/CTA rhythm matches the source, and no desktop or mobile overflow was observed.
- Colors and visual tokens: graphite-black background, warm white type, muted gray body copy, and a single lime accent match the source. The flow field keeps low saturation and controlled luminance rather than drifting into a generic blue or cyberpunk palette.
- Image quality and asset fidelity: the central visual is a live WebGL shader field rendered through React Three Fiber, as explicitly requested. It contains smooth antialiased ribbons and filaments, no raster scaling artifacts, random particles, nodes, boxes, chips, or dashboard imagery.
- Copy and content: the headline matches the selected concept. Supporting copy was adapted to the actual Engineering Power product—agents, reusable skills, repository context, and evidence-backed delivery—rather than introducing unsupported platform claims.

## Full-view Comparison Evidence

The final side-by-side comparison shows matching first-view hierarchy: minimal dark navigation, left-aligned lime eyebrow, large white three-line headline, concise two-line support copy, lime CTA, and a luminous flow system occupying the right and lower visual field. The implementation is deliberately calmer and slightly more structured than the static source while preserving its premium enterprise developer-tool character.

No focused crop was required because this is a single, uncluttered hero and the headline, body copy, CTA, navigation, and flow treatment remain legible in the normalized full-view comparison.

## Comparison History

### Iteration 1 — blocked

- Evidence: `/tmp/engineering-power-hero-iteration-1.png` and `/tmp/engineering-power-design-qa-iteration-1.png`
- [P2] The headline wrapped as `Engineering moves at / the speed of / intelligence`, which changed the source hierarchy.
- [P2] Supporting copy was centered inside its column instead of sharing the headline's left edge.
- [P2] The first hero stopped before the viewport bottom, revealing the following light section.
- [P2] Flow strands were too horizontal and thin, making the composition read more like lines than an intelligent fluid system.

Fixes made:

- Narrowed the display measure and removed balanced wrapping to reproduce the source's `Engineering moves / at the speed of / intelligence` structure.
- Removed inherited auto inline margins from the support copy and aligned the complete text stack.
- Made hero height equal to the viewport minus header height.
- Reworked the shader paths around a convergence focus, introduced diagonal starts, broader translucent layers, internal filaments, and stronger depth separation.

### Iteration 2 — passed

- Evidence: `/tmp/engineering-power-hero-final.png` and `/tmp/engineering-power-design-qa-final.png`
- The earlier P2 hierarchy, alignment, viewport, and flow-composition findings are resolved in the revised browser capture.
- After code review, the same view was recaptured after enabling the R3F event layer and adding WebGL context probing/fallback; no visual regression was observed in the refreshed combined comparison.

## Functional and Runtime Checks

- Primary CTA tested in the browser: `Get started` navigates to `/start`.
- `/start` exposes exactly one Codex option and one GitHub Copilot option.
- Two motion frames captured 700 ms apart were different, confirming that the background is actively animating.
- Pointer-reactive motion is implemented with damped, low-amplitude group rotation and translation.
- The live R3F event layer and canvas both resolve to `pointer-events: auto`, while the event layer keeps `touch-action: pan-y` so background response does not remove mobile page scrolling.
- Reduced-motion users receive a demand-rendered static scene.
- WebGL support is verified with real context creation; unsupported or failed contexts keep the text-first hero usable through a quiet fallback.
- Browser console errors checked: none from the application.

## Implementation Checklist

- [x] Match selected desktop composition and hierarchy
- [x] Implement the flow field with React Three Fiber / Three.js
- [x] Use Framer Motion for restrained content entry
- [x] Preserve the Codex and GitHub Copilot onboarding paths
- [x] Verify pointer-event wiring, reduced motion, and no-WebGL fallback
- [x] Validate desktop and mobile layouts
- [x] Verify motion, CTA navigation, build, and tests

final result: passed
