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

test("defaults the capability explorer to Understand and keeps every panel mounted", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const tabs = screen.getByRole("tablist", { name: "Engineering lifecycle capabilities" });

  expect(within(tabs).getAllByRole("tab")).toHaveLength(4);
  expect(within(tabs).getByRole("tab", { name: "Understand" })).toHaveAttribute("aria-selected", "true");

  for (const id of ["understand", "change-safely", "ship-clearly", "evolve-operate"]) {
    expect(document.getElementById(`capability-panel-${id}`)).toBeInTheDocument();
  }

  expect(document.getElementById("capability-panel-understand")).not.toHaveAttribute("hidden");
  expect(document.getElementById("capability-panel-change-safely")).toHaveAttribute("hidden");
});

test("changes the visible capability question with the keyboard", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const understand = screen.getByRole("tab", { name: "Understand" });

  fireEvent.keyDown(understand, { key: "ArrowRight" });

  expect(screen.getByRole("tab", { name: "Change safely" })).toHaveFocus();
  expect(document.getElementById("capability-panel-change-safely")).not.toHaveAttribute("hidden");
  expect(screen.getByText(/what should change, what depends on it/i)).toBeVisible();
});

test("explains the evidence workflow and installed-skill boundary", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const workflow = screen.getByRole("region", { name: "Evidence in. Engineering judgment out." });
  expect(within(workflow).getAllByRole("listitem")).toHaveLength(4);
  expect(within(workflow).getByText(/records the Git state/i)).toBeInTheDocument();

  const boundary = within(workflow).getByRole("complementary", { name: "Where analysis runs" });
  expect(boundary).toHaveTextContent(/website is a static demo/i);
  expect(boundary).toHaveTextContent(/runs inside your chosen coding assistant/i);
});

test("shows all supported hosts and a complete conversion path", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const hosts = screen.getByRole("region", { name: "Bring the same engineering discipline to your assistant." });
  for (const host of ["Codex", "GitHub Copilot", "Claude Code", "Cursor"]) {
    expect(within(hosts).getByRole("heading", { name: host })).toBeInTheDocument();
  }
  expect(within(hosts).getByRole("link", { name: "Choose your assistant" })).toHaveAttribute("href", "/start");
  expect(screen.getByRole("link", { name: /Bring Engineering Power to your coding assistant/i })).toHaveAttribute("href", "/start");
});

test("condenses the trust boundary to four principles and a static-demo disclosure", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  const trust = screen.getByRole("region", { name: "Evidence has clear limits." });
  expect(within(trust).getAllByRole("article")).toHaveLength(4);
  expect(within(trust).getByText(/exact Git state/i)).toBeInTheDocument();
  expect(within(trust).getByText(/facts, inferences, and unknowns/i)).toBeInTheDocument();
  expect(within(trust).getByText(/executed, discovered, and recommended/i)).toBeInTheDocument();
  expect(within(trust).getByText(/read-only by default/i)).toBeInTheDocument();
  expect(within(trust).getByText(/does not analyze your repository/i)).toBeInTheDocument();
});

test("defaults the Engineering Power demo to repository understanding", () => {
  render(<MemoryRouter initialEntries={["/demo-report"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: "Engineering Power demo" })).toBeInTheDocument();
  expect(screen.getByRole("tab", { name: "Understand" })).toHaveAttribute("aria-selected", "true");
  expect(screen.getByRole("heading", { name: "Map northstar-commerce before touching checkout." })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Repository overview" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Checkout business flow" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Start here" })).toBeVisible();
});

test("keeps the existing PR report inside Change safely", () => {
  render(<MemoryRouter initialEntries={["/demo-report"]}><App /></MemoryRouter>);
  fireEvent.click(screen.getByRole("tab", { name: "Change safely" }));
  expect(screen.getByText("Pull request #482 · checkout-tax-rounding")).toBeVisible();
  expect(screen.getByText("Proceed with conditions")).toBeVisible();
  expect(screen.getByRole("heading", { name: "Facts" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Inferences" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Unknowns" })).toBeVisible();
  expect(screen.getByRole("table", { name: "Validation matrix" })).toBeVisible();
});

test("shows release artifacts and evolve-operate outputs in their own demo panels", () => {
  render(<MemoryRouter initialEntries={["/demo-report"]}><App /></MemoryRouter>);
  fireEvent.click(screen.getByRole("tab", { name: "Ship clearly" }));
  expect(screen.getByRole("heading", { name: "API compatibility" })).toBeVisible();
  expect(screen.getByText(/Technical: tax rounding/i)).toBeVisible();
  expect(screen.getByText(/User-facing: checkout tax totals/i)).toBeVisible();

  fireEvent.click(screen.getByRole("tab", { name: "Evolve & operate" }));
  expect(screen.getByRole("heading", { name: "Migration waves" })).toBeVisible();
  expect(screen.getByRole("heading", { name: "Ranked incident hypotheses" })).toBeVisible();
  expect(screen.getByText(/one sandbox run contradicts/i)).toBeVisible();
});

test("labels every mounted scenario as illustrative", () => {
  render(<MemoryRouter initialEntries={["/demo-report"]}><App /></MemoryRouter>);
  expect(screen.getAllByText("Illustrative static example")).toHaveLength(4);
  for (const id of ["understand", "change-safely", "ship-clearly", "evolve-operate"]) {
    expect(document.getElementById(`scenario-panel-${id}`)).toBeInTheDocument();
  }
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
