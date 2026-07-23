import { fireEvent, render, screen } from "@testing-library/react";
import { useState } from "react";
import { describe, expect, test } from "vitest";
import type { LifecycleStageId } from "../content/siteContent";
import { LifecycleTabs } from "./LifecycleTabs";

const tabs = [
  { id: "understand", title: "Understand" },
  { id: "change-safely", title: "Change safely" },
  { id: "ship-clearly", title: "Ship clearly" },
  { id: "evolve-operate", title: "Evolve & operate" },
] as const;

function Harness() {
  const [selectedId, setSelectedId] = useState<LifecycleStageId>("understand");

  return <LifecycleTabs idPrefix="test" ariaLabel="Test stages" tabs={tabs} selectedId={selectedId} onSelect={setSelectedId} />;
}

describe("LifecycleTabs", () => {
  test("links tabs to panels and starts with Understand selected", () => {
    render(<Harness />);
    const understand = screen.getByRole("tab", { name: "Understand" });

    expect(understand).toHaveAttribute("aria-selected", "true");
    expect(understand).toHaveAttribute("aria-controls", "test-panel-understand");
    expect(understand).toHaveAttribute("tabindex", "0");
  });

  test("moves selection and focus with arrow, Home, and End keys", () => {
    render(<Harness />);
    const understand = screen.getByRole("tab", { name: "Understand" });
    const change = screen.getByRole("tab", { name: "Change safely" });
    const operate = screen.getByRole("tab", { name: "Evolve & operate" });

    understand.focus();
    fireEvent.keyDown(understand, { key: "ArrowRight" });
    expect(change).toHaveFocus();
    expect(change).toHaveAttribute("aria-selected", "true");

    fireEvent.keyDown(change, { key: "End" });
    expect(operate).toHaveFocus();
    expect(operate).toHaveAttribute("aria-selected", "true");

    fireEvent.keyDown(operate, { key: "Home" });
    expect(understand).toHaveFocus();

    fireEvent.keyDown(understand, { key: "ArrowLeft" });
    expect(operate).toHaveFocus();
  });
});
