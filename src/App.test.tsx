import { render, screen, within } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import App from "./App";

test("renders the product headline on the home route", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("heading", {
      name: /evidence-backed engineering decisions/i,
    }),
  ).toBeInTheDocument();

});

test("connects the hero CTA to the quick-start guide", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  const hero = screen.getByRole("region", {
    name: "Evidence-backed engineering decisions.",
  });

  expect(
    within(hero).getByRole("link", { name: "Get started" }),
  ).toHaveAttribute("href", "/start");
});

test("guides Codex and GitHub Copilot users from the quick-start route", () => {
  render(<MemoryRouter initialEntries={["/start"]}><App /></MemoryRouter>);
  expect(screen.getByRole("heading", { name: /bring evidence into your coding workflow/i })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "Codex" })).toBeInTheDocument();
  expect(screen.getByRole("heading", { name: "GitHub Copilot" })).toBeInTheDocument();
});

test("describes the three decision-ready outputs", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByText("Change Impact")).toBeInTheDocument();
  expect(screen.getByText("API Contract Delta")).toBeInTheDocument();
  expect(screen.getByText("Release Readiness")).toBeInTheDocument();
});

test("labels demo evidence and citations as illustrative rather than live analysis", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByText(/static demo uses illustrative evidence and citations/i),
  ).toBeInTheDocument();
  expect(screen.getByText(/not live repository analysis/i)).toBeInTheDocument();
});

test("makes the homepage evidence states, report excerpt, and trust limits explicit", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  const whyItMatters = screen.getByRole("region", {
    name: /a diff shows what changed/i,
  });
  expect(within(whyItMatters).getByRole("heading", { name: "Facts" })).toBeInTheDocument();
  expect(within(whyItMatters).getByRole("heading", { name: "Inferences" })).toBeInTheDocument();
  expect(within(whyItMatters).getByRole("heading", { name: "Unknowns" })).toBeInTheDocument();

  const demoPreview = screen.getByRole("region", { name: /see the evidence in report form/i });
  expect(within(demoPreview).getByText(/proceed with conditions/i)).toBeInTheDocument();
  expect(within(demoPreview).getByText(/taxcalculator rounds each tax line/i)).toBeInTheDocument();

  expect(screen.getByText(/executed checks are run in the captured snapshot/i)).toBeInTheDocument();
  expect(screen.getByText(/discovered checks are evidence found, not tests run/i)).toBeInTheDocument();
  expect(screen.getByText(/recommended checks are next steps, not completed validation/i)).toBeInTheDocument();
  expect(screen.getByText(/deadline or incomplete coverage can limit a report/i)).toBeInTheDocument();
  expect(screen.getByText(/static demo only — it does not analyze your repository/i)).toBeInTheDocument();
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

test("uses GitHub as the direct top navigation destination", () => {
  render(<MemoryRouter initialEntries={["/"]}><App /></MemoryRouter>);
  expect(screen.getByRole("link", { name: "GitHub" })).toHaveAttribute(
    "href",
    "https://github.com/gavinliu1995/engineering-power",
  );
});

test("keeps the demo preview call to action available from the home page", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(screen.getByRole("link", { name: "View Demo Report" })).toHaveAttribute("href", "/demo-report");
});

test("keeps the animated evidence signal decorative and exposes its release state", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  const signal = screen.getByTestId("evidence-signal-field");
  expect(signal).toHaveAttribute("aria-hidden", "true");
  expect(signal).toHaveTextContent("PROCEED WITH CONDITIONS");
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
