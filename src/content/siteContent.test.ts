import { describe, expect, test } from "vitest";
import {
  assignedCapabilityNames,
  demoScenarios,
  lifecycleStageIds,
  lifecycleStages,
  lifecycleStarterPrompts,
} from "./siteContent";

describe("full-lifecycle site content", () => {
  test("maps every assigned capability exactly once", () => {
    const renderedNames = lifecycleStages.flatMap((stage) =>
      stage.capabilities
        .filter((capability) => capability.role === "assigned")
        .map((capability) => capability.name),
    );

    expect(assignedCapabilityNames).toHaveLength(10);
    expect(new Set(assignedCapabilityNames)).toHaveProperty("size", 10);
    expect([...renderedNames].sort()).toEqual([...assignedCapabilityNames].sort());
  });

  test("defaults the ordered lifecycle to repository understanding", () => {
    expect(lifecycleStages.map((stage) => stage.id)).toEqual(lifecycleStageIds);
    expect(lifecycleStages[0].id).toBe("understand");
  });

  test("defines one complete illustrative scenario per lifecycle stage", () => {
    expect(demoScenarios.map((scenario) => scenario.id)).toEqual(lifecycleStageIds);

    for (const scenario of demoScenarios) {
      expect(scenario.disclosure).toBe("Illustrative static example");
      expect(scenario.outputs).toHaveLength(3);
      expect(scenario.evidence.length).toBeGreaterThanOrEqual(2);
      expect(scenario.target).not.toBe("");
      expect(scenario.gitState).not.toBe("");
      expect(scenario.unknown.statement).not.toBe("");
      expect(scenario.nextDecision.owner).not.toBe("");
      expect(scenario.nextDecision.action).not.toBe("");
    }

    expect(demoScenarios[1].target).toBe(
      "Pull request #482 · checkout-tax-rounding",
    );
  });

  test("provides one starter prompt for every stage", () => {
    expect(lifecycleStarterPrompts.map((prompt) => prompt.stage)).toEqual(
      lifecycleStageIds,
    );
  });
});
