# Robinhood-Inspired Visual Refresh Design

## Goal

Refresh the Engineering Power static demo so it feels sharper, more modern,
and more technologically confident without reproducing Robinhood branding,
assets, copy, or page structure. The site remains a static English product
demo with the same routes, content claims, and truth boundaries.

## Visual direction

Use a **dark signal hero, light evidence canvas** composition:

- The hero and primary navigation use an almost-black ink background, white
  typography, and a single chartreuse signal color for the main action and
  active evidence points.
- The remaining home-page sections use a warm off-white background, deep
  navy-black type, fine graphite rules, and restrained pale-lilac/steel-blue
  surface tints.
- Cards alternate between white analysis surfaces and black feature panels;
  chartreuse appears only as a status, CTA, hover, or visual-path accent.
- Typography becomes more editorial: large compact headlines, clear
  mono-styled evidence labels, and deliberate whitespace.

This borrows Robinhood's high-contrast product confidence, not its trade dress.
Engineering Power retains its own name, messages, information hierarchy, and
abstract evidence-specific visuals.

## Hero composition

The hero becomes a two-column layout on desktop:

- Left: existing product statement, short supporting copy, and the exact
  `View Demo Report` CTA.
- Right: an abstract **evidence signal field** made from local CSS and SVG-like
  primitives: connected points, fine lines, code fragments, and a floating
  release-decision capsule. It represents a traceable code-change path, not a
  financial chart or Robinhood asset.
- On narrow screens the signal field moves below the copy and remains purely
  decorative so it does not interfere with reading or controls.

## Motion

Motion supports orientation and responsiveness rather than functioning as
ambient spectacle:

- Evidence points drift gently on staggered 7–12 second loops; connecting
  strokes receive a low-contrast traveling highlight.
- The decision capsule has a subtle entrance settle when the page loads.
- Sections and cards use a small fade-and-rise reveal when they enter the
  viewport; hover states use 150–220ms lift, border, and shadow transitions.
- Respect `prefers-reduced-motion: reduce`: all loops, reveals, and transforms
  become static or near-instant.
- No scroll-jacking, flashing, animated text replacement, or automatically
  moving essential content.

## Components and scope

- Add a focused `EvidenceSignalField` presentational component used only by
  the home hero.
- Update home-page structural classes and CSS tokens; retain all existing
  report facts, static-demo disclosures, CTA destinations, and route behavior.
- Restyle the report page for the same light evidence canvas with ink report
  panels; keep semantic table markup and status text intact.
- Do not add dependencies, network calls, images copied from external sites,
  animation libraries, or a live data experience.

## Accessibility and validation

- The decorative signal field is hidden from assistive technology.
- All interactive controls retain visible focus treatments and sufficient
  contrast.
- Tests continue to verify the hero CTA, truth-boundary language, report
  metadata, validation states, footer note, and route behavior.
- Add a focused test that the decorative signal field exists but is marked
  `aria-hidden`.
- Validate with the frontend test suite, production build, existing Python
  suite, and `git diff --check`.
