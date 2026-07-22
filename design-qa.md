# Design QA — Citation Frame and product-clarity pass

## Visual truth

- Selected reference: `/Users/gavin.liu/.codex/generated_images/019f83a8-22f2-73c2-b19b-abbdf9d2cd43/exec-cb7ac925-83d5-4d8c-9b7d-479ec7e26781.png`
- Reference state: Citation Frame lockup at the reference's labelled 32px navigation usage.
- Implementation: `/Users/gavin.liu/Documents/engineering-power-vercel-app/public/images/engineering-power-citation-frame-header.png`
- Final homepage capture: `/tmp/engineering-power-final-qa/home-final.png`
- Focused reference/implementation comparison: `/tmp/engineering-power-final-qa/brand-comparison.png`

## Capture conditions

- URL: `http://127.0.0.1:5173/`
- Viewport: 482 × 899 CSS px
- Device pixel ratio: 2
- Browser state: home route, scroll position 0, motion enabled
- Rendered mark slot: 33.6 × 23.5 CSS px with natural aspect ratio and no stretching

## Comparison

The target crop and implemented header were placed in one comparison image. The implementation preserves the selected mark's two chartreuse opposing brackets, warm-white evidence rule, black field, and compact wordmark relationship. The image remains legible at navigation size, uses a transparent raster asset, and is not reconstructed with CSS, text glyphs, or inline SVG.

### Surface review

- Typography: the wordmark uses the site's established sans-serif system and maintains the target's heavy, compact lockup. Hero type is balanced at the tested narrow viewport without horizontal overflow.
- Spacing: the mark/wordmark gap, header vertical alignment, hero actions, and mobile section rhythm are consistent. Document scroll width remained below the viewport width.
- Color: graphite, chartreuse, and warm white match the selected reference and the existing landing-page palette.
- Image quality: the transparent PNG is rendered below its native size with `object-fit: contain`; no visible stretching or clipping was observed.
- Copy: the hero now names repository/change analysis, cited findings, explicit unknowns, and review-ready reports. The page no longer claims to be a generic AI-native developer platform.
- Content density: trust boundaries were reduced from seven overlapping statements to six distinct statements, avoiding a desktop grid orphan.

## Interaction and motion checks

- Primary hero CTA opens `/start`.
- Secondary hero CTA opens `/demo-report` at scroll position 0.
- The assistant chooser exposes exactly four working routes: Codex, GitHub Copilot, Claude Code, and Cursor.
- Entering a host guide resets the route to scroll position 0 and moves keyboard focus to the new page heading; both behaviors were verified from a deliberately scrolled chooser state.
- Codex is clearly identified as a local developer preview rather than a public install. The three portable guides begin with the canonical clone and checkout prerequisites before their host-specific installer commands.
- Homepage background motion was captured 900 ms apart. Frame hashes differed and the full-frame average luminance delta was 0.621, confirming subtle live movement rather than a static background.
- Reduced-motion behavior remains covered by the existing component test.
- No new browser-console warnings or errors appeared after the correct dev server was restarted. The retained browser log buffer only contained stale Vite HMR errors from the earlier offline 5173 session.

## QA history

1. P0 — the browser was showing a cached old build because the 5173 dev server had exited. Restarted the correct `engineering-power-vercel-app` server on `vercel-demo` and reloaded with a fresh URL state.
2. P1 — host-guide navigation inherited the chooser's scroll position, hiding the guide heading. Added pathname-based scroll reset plus an integration test.
3. P2 — seven trust statements repeated the citation concept and would leave a desktop grid orphan. Removed the duplicate reasoning statement and asserted six trust items.
4. P1 — onboarding commands assumed the Engineering Power source checkout, while Codex also assumed a maintainer-only marketplace. Added clone prerequisites to the portable hosts and explicitly bounded Codex as a local developer preview.
5. P2 — route transitions reset scroll but initially left keyboard focus behind. The destination `h1` now receives focus after client-side navigation.
6. Final comparison and independent code re-review — no remaining P0, P1, or P2 visual, content, or interaction defects at the captured state.

final result: passed
