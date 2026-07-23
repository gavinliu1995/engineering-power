import { fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";
import App from "./App";

test("leads with full-lifecycle engineering intelligence", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);

  const hero = screen.getByRole("region", {
    name: "Engineering intelligence across the software lifecycle.",
  });

  expect(
    within(hero).getByRole("heading", {
      name: "Engineering intelligence across the software lifecycle.",
    }),
  ).toBeInTheDocument();
  expect(within(hero).getByText(/understand unfamiliar repositories/i)).toBeInTheDocument();
  expect(within(hero).queryByText(/pull request|diff|review-ready report/i)).not.toBeInTheDocument();
});

test("connects hero actions to onboarding and capabilities", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const hero = screen.getByRole("region", {
    name: "Engineering intelligence across the software lifecycle.",
  });

  expect(within(hero).getByRole("link", { name: "Choose your assistant" })).toHaveAttribute("href", "/start");
  expect(within(hero).getByRole("link", { name: "Explore capabilities" })).toHaveAttribute("href", "#capabilities");
});

test("uses the selected citation-frame brand asset", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);

  const brandLink = screen.getByRole("link", { name: "Engineering Power home" });
  const mark = brandLink.querySelector("img.brand-mark");

  expect(mark).toHaveAttribute(
    "src",
    "/images/engineering-power-citation-frame-header.png",
  );
  expect(mark).toHaveAttribute("alt", "");
});

test("lets users choose every supported coding assistant from the quick-start route", () => {
  render(<MemoryRouter initialEntries={["/start"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /use engineering power with your coding assistant/i })).toBeInTheDocument();
  const hostNav = screen.getByRole("navigation", { name: "Supported coding assistants" });
  expect(within(hostNav).getAllByRole("link")).toHaveLength(4);
  expect(within(hostNav).getByRole("link", { name: "Use Engineering Power with Codex" })).toHaveAttribute("href", "/start/codex");
  expect(within(hostNav).getByRole("link", { name: "Use Engineering Power with GitHub Copilot" })).toHaveAttribute("href", "/start/copilot");
  expect(within(hostNav).getByRole("link", { name: "Use Engineering Power with Claude Code" })).toHaveAttribute("href", "/start/claude");
  expect(within(hostNav).getByRole("link", { name: "Use Engineering Power with Cursor" })).toHaveAttribute("href", "/start/cursor");
  expect(screen.getByText(/read-only by default/i)).toBeInTheDocument();
  expect(screen.queryByText("$repo-intelligence /path/to/repository")).not.toBeInTheDocument();
});

test.each(["/start", "/start/codex"])(
  "offers a visible route back to the home page from %s",
  (route) => {
    render(<MemoryRouter initialEntries={[route]}><App /></MemoryRouter>);

    expect(
      screen.getByRole("link", { name: "Engineering Power home" }),
    ).toHaveAttribute("href", "/");
  },
);

test("uses product-facing Codex guidance instead of an internal workflow name", () => {
  render(<MemoryRouter initialEntries={["/start/codex"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /use engineering power in codex/i })).toBeInTheDocument();
  expect(screen.getByText(/local developer preview/i)).toBeInTheDocument();
  expect(screen.getByText(/not a public codex install/i)).toBeInTheDocument();
  expect(screen.getByText('PLUGIN_ROOT="$HOME/Documents/engineering-power"')).toBeInTheDocument();
  expect(screen.getByText('python3 "$HOME/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py" "$PLUGIN_ROOT"')).toBeInTheDocument();
  expect(screen.getByText(/start a new task and describe the repository or pull request/i)).toBeInTheDocument();
  expect(screen.getByText("codex plugin add engineering-power@personal")).toBeInTheDocument();
  expect(screen.getByText(/configured personal codex plugin source/i)).toBeInTheDocument();
  expect(screen.queryByText(/from your codex plugin marketplace/i)).not.toBeInTheDocument();
});

test("shows the verified GitHub Copilot setup steps", () => {
  render(<MemoryRouter initialEntries={["/start/copilot"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /use engineering power in github copilot/i })).toBeInTheDocument();
  expect(screen.getByText("git clone https://github.com/gavinliu1995/engineering-power.git")).toBeInTheDocument();
  expect(screen.getByText("cd engineering-power")).toBeInTheDocument();
  expect(screen.getByText("python3 scripts/install_agent_skill.py --host copilot --target-root /path/to/project")).toBeInTheDocument();
  expect(screen.getByText("/skills reload")).toBeInTheDocument();
  expect(screen.getByText("/skills info engineering-power")).toBeInTheDocument();
});

test("shows the documented Claude Code installation path", () => {
  render(<MemoryRouter initialEntries={["/start/claude"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /use engineering power in claude code/i })).toBeInTheDocument();
  expect(screen.getByText("git clone https://github.com/gavinliu1995/engineering-power.git")).toBeInTheDocument();
  expect(screen.getByText("cd engineering-power")).toBeInTheDocument();
  expect(screen.getByText("python3 scripts/install_agent_skill.py --host claude --target-root /path/to/project")).toBeInTheDocument();
  expect(screen.getByText("/path/to/project/.claude/skills/engineering-power")).toBeInTheDocument();
});

test("shows the documented Cursor installation path", () => {
  render(<MemoryRouter initialEntries={["/start/cursor"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /use engineering power in cursor/i })).toBeInTheDocument();
  expect(screen.getByText("git clone https://github.com/gavinliu1995/engineering-power.git")).toBeInTheDocument();
  expect(screen.getByText("cd engineering-power")).toBeInTheDocument();
  expect(screen.getByText("python3 scripts/install_agent_skill.py --host cursor --target-root /path/to/project")).toBeInTheDocument();
  expect(screen.getByText("/path/to/project/.cursor/skills/engineering-power")).toBeInTheDocument();
});

test("returns to the top when moving from an assistant choice to its guide", async () => {
  const scrollTo = vi.spyOn(window, "scrollTo").mockImplementation(() => {});

  render(<MemoryRouter initialEntries={["/start"]}><App /></MemoryRouter>);
  await waitFor(() => expect(scrollTo).toHaveBeenCalledTimes(1));

  fireEvent.click(
    screen.getByRole("link", { name: "Use Engineering Power with Claude Code" }),
  );

  await waitFor(() => {
    const guideHeading = screen.getByRole("heading", { name: /use engineering power in claude code/i });
    expect(guideHeading).toBeInTheDocument();
    expect(guideHeading).toHaveFocus();
    expect(scrollTo).toHaveBeenLastCalledWith(0, 0);
    expect(scrollTo).toHaveBeenCalledTimes(2);
  });

  scrollTo.mockRestore();
});

test("exposes every assigned capability in the static lifecycle overview", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const overview = screen.getByRole("region", { name: "From first read to production reality." });

  for (const capability of [
    "Repository-specific onboarding",
    "Architecture review support",
    "Repository refactoring assistance",
    "Dependency impact analysis",
    "Test impact analysis",
    "Regression risk detection",
    "API contract generation",
    "Release note generation",
    "Migration planning",
    "Runtime incident triage",
  ]) {
    expect(within(overview).getByText(capability)).toBeInTheDocument();
  }

  expect(within(overview).getAllByRole("article")).toHaveLength(4);
  expect(screen.queryByRole("heading", { name: /a diff shows changes/i })).not.toBeInTheDocument();
});

test("renders the demo report route", () => {
  render(
    <MemoryRouter initialEntries={["/demo-report"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", { name: /demo report/i }),
  ).toBeInTheDocument();
});

test("renders distinct evidence and validation states on the demo report", () => {
  render(
    <MemoryRouter initialEntries={["/demo-report"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", { name: /release decision/i }),
  ).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Facts" })).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "Inferences" }),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "Unknowns" }),
  ).toBeInTheDocument();
  expect(screen.getByText(/illustrative demo citations/i)).toBeInTheDocument();
});

test("renders the demo report evidence snapshot metadata", () => {
  render(
    <MemoryRouter initialEntries={["/demo-report"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByText("Target")).toBeInTheDocument();
  expect(
    screen.getByText("Pull request #482 · checkout-tax-rounding"),
  ).toBeInTheDocument();
  expect(screen.getByText("Base")).toBeInTheDocument();
  expect(screen.getByText("main @ 8f31c2a")).toBeInTheDocument();
  expect(screen.getByText("Head")).toBeInTheDocument();
  expect(
    screen.getByText("feature/checkout-tax-rounding @ c7e194d"),
  ).toBeInTheDocument();
  expect(screen.getByText("Profile")).toBeInTheDocument();
  expect(screen.getByText("Release readiness review")).toBeInTheDocument();
  expect(screen.getByText("Evidence snapshot")).toBeInTheDocument();
  expect(screen.getByText("8f31c2a..c7e194d")).toBeInTheDocument();
});

test("renders confidence and affected components on the demo report", () => {
  render(
    <MemoryRouter initialEntries={["/demo-report"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole("heading", { name: "Confidence" })).toBeInTheDocument();
  expect(
    screen.getByText(
      "Moderate — core checkout behavior is evidenced; provider reconciliation remains unverified.",
    ),
  ).toBeInTheDocument();
  expect(
    screen.getByRole("heading", { name: "Affected components" }),
  ).toBeInTheDocument();
  expect(screen.getByText("Tax calculation")).toBeInTheDocument();
  expect(screen.getByText("Checkout API response")).toBeInTheDocument();
  expect(screen.getByText("Payment provider reconciliation")).toBeInTheDocument();
});

test("uses semantic table headers for the validation matrix", () => {
  render(
    <MemoryRouter initialEntries={["/demo-report"]}>
      <App />
    </MemoryRouter>,
  );

  const table = screen.getByRole("table", { name: "Validation matrix" });
  expect(table.tagName).toBe("TABLE");

  const headers = within(table).getAllByRole("columnheader");
  expect(headers).toHaveLength(3);
  expect(headers.map((header) => header.textContent)).toEqual([
    "State",
    "Check",
    "Evidence",
  ]);
  headers.forEach((header) => expect(header).toHaveAttribute("scope", "col"));
});

test("uses the canonical GitHub repository URL", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("link", { name: "View Engineering Power on GitHub" }),
  ).toHaveAttribute(
    "href",
    "https://github.com/gavinliu1995/engineering-power",
  );
});

test("uses direct lifecycle anchors and the canonical GitHub destination", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const nav = screen.getByRole("navigation", { name: "Primary" });

  expect(within(nav).getByRole("link", { name: "Capabilities" })).toHaveAttribute("href", "#capabilities");
  expect(within(nav).getByRole("link", { name: "How it works" })).toHaveAttribute("href", "#how-it-works");
  expect(within(nav).getByRole("link", { name: "Hosts" })).toHaveAttribute("href", "#hosts");
  expect(within(nav).getByRole("link", { name: "GitHub" })).toHaveAttribute("href", "https://github.com/gavinliu1995/engineering-power");
});

test("keeps the intelligence flow field decorative", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  const field = screen.getByTestId("intelligence-flow-field");
  expect(field).toHaveAttribute("aria-hidden", "true");
  expect(field).not.toHaveTextContent("PROCEED WITH CONDITIONS");
  expect(screen.getByTestId("intelligence-flow-fallback")).toBeInTheDocument();
});

test("renders the not-found page for an unmatched route", () => {
  render(
    <MemoryRouter initialEntries={["/missing"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", { name: /page not found/i }),
  ).toBeInTheDocument();
});

test("offers a route back home when a page is not found", () => {
  render(
    <MemoryRouter initialEntries={["/missing"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("link", { name: /back to home/i }),
  ).toHaveAttribute("href", "/");
});
