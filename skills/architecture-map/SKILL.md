---
name: architecture-map
description: Produce an evidence-backed architecture map for a GitHub repository or local Git repository, including concrete module boundaries, trust boundaries, data ownership, integrations, and business flows.
---

# Architecture Map

Collect one repository snapshot through the shared engine, then focus the report
on actual modules, entry points, pages/routes, orchestration, persistence, and
external clients. Draw Mermaid diagrams using concrete symbols from evidence,
not generic UI/service/DAO boxes. Label cross-file deductions as Inference and
state unknown ownership or runtime behavior explicitly.

Return an inline architecture map with a compact system diagram, one to three
business flows when evidence supports them, boundary risks, and an evidence
index. Keep source targets read-only and validate citations before delivery.
