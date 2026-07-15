---
name: pr-impact-analysis
description: Analyze GitHub pull requests, local commit ranges, working-tree changes, or downloaded patches. Return evidence-backed change propagation, test impact, regression risk, and architecture review.
---

# PR Impact Analysis

Use the shared evidence engine in pull-request mode. Accept a GitHub PR URL, a
local repository with `compare BASE HEAD`, `working-tree`, or a downloaded patch
with its base ref. Collect once, prepare one citation context, and report the
exact base/head state, user-visible change, affected callers and data paths,
tests to run or add, regression risk, and evidence index. Never apply a patch or
modify the target repository.

Use `finalize_report.py` before returning the inline result. Distinguish direct
diff evidence from inferred impact and from runtime behavior not verified here.
