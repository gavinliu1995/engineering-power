---
name: api-contract-generator
description: Generate an evidence-backed API surface or compatibility delta from a GitHub repository, pull request, local Git comparison, working tree, or downloaded patch. Use for endpoint inventories, request and response schemas, authentication evidence, API review, and breaking-change analysis.
---

# API Contract Generator

Generate a cited description of the API that the available source evidence can
support. Keep the source repository read-only.

## Workflow

1. Resolve the plugin root from this skill directory.
2. Collect or reuse one exact-state snapshot through the shared engine under
   `$PLUGIN_ROOT/scripts/repo_evidence/`.
3. Run `prepare_analysis_context.py`, then run
   `prepare_workflow_context.py SNAPSHOT --workflow api-contract --profile
   quick`. Use `deep` only when explicitly requested.
4. Discover API evidence in routes, controllers, handlers, OpenAPI or Swagger
   documents, GraphQL schemas, protobuf definitions, DTOs, serializers,
   validators, authentication middleware, and relevant tests.
5. For a repository, describe the discovered surface. For a change, compare the
   exact base and head and classify each operation as `added`, `removed`,
   `compatible`, `potentially breaking`, or `breaking`.
6. Record operation, path or message name, inputs, outputs, status/error behavior,
   authentication and authorization evidence, versioning, compatibility, and
   citations. Mark absent evidence as **Unknown**.
7. Format the result with `../../references/api-contract-schema.md`.
8. Write the draft with the required runtime placeholders, then run
   `finalize_report.py DRAFT --snapshot SNAPSHOT --profile PROFILE
   --started-at-epoch START --report-type api-contract --output FINAL`.
   Return the finalized report only; if validation fails, correct the report
   contract rather than bypassing the validator.

## Guardrails

- **Do not invent** endpoints, fields, requiredness, status codes,
  authentication, authorization, or compatibility guarantees.
- Treat framework conventions as **Inference** unless repository evidence
  confirms the concrete behavior.
- Distinguish declared specifications from implementation and test evidence.
- Do not call a change compatible when a consumer-facing field, type, enum,
  requiredness rule, path, method, authorization rule, or error shape is unknown.
- Do not expose secret values from configuration or examples.
- Disclose collection deadlines, missing layers, and unsupported API mechanisms.
