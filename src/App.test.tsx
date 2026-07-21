import { render, screen } from "@testing-library/react";
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

  expect(
    screen.getByRole("link", { name: "View Demo Report" }),
  ).toHaveAttribute("href", "/demo-report");
});

test("connects the hero CTA to the static demo report", () => {
  render(
    <MemoryRouter initialEntries={["/"]}>
      <App />
    </MemoryRouter>,
  );

  expect(
    screen.getByRole("link", { name: "View Demo Report" }),
  ).toHaveAttribute("href", "/demo-report");
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
