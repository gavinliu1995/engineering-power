# Business-logic focus

Load this reference when the user asks how the product works, requests business
logic, user journeys, state machines, decision rules, or workflow diagrams.

## Select meaningful flows

Choose up to three flows:

1. Primary value journey
2. State/progress lifecycle
3. Failure, fallback, or integration journey

Do not draw import graphs as business logic.

## Trace each flow

Record:

- User/system goal and trigger
- Preconditions and eligibility
- Entry point
- Ordered decision rules
- State read/write or external side effect
- Success output and feedback
- Rejection, retry, fallback, timeout, and recovery

When useful, add a compact decision table covering condition, branch, state
change, and output. Use sequence diagrams for order and flowcharts for branches
or state transitions.

Explicitly distinguish rule-driven, human-reviewed, AI-generated, and external
service behavior. Cite every stage and label inference confidence.
