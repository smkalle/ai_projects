import { expect, test, type Page } from "@playwright/test";

async function expectShell(page: Page) {
  await page.goto("/");

  await expect(page.getByText("EvalOps Console")).toBeVisible();
  await expect(page.getByRole("heading", { name: /operate model quality/i })).toBeVisible();
  await expect(page.getByTestId("batch-control-panel")).toBeVisible();
  await expect(page.getByTestId("model-analytics-panel")).toBeVisible();
  await expect(page.getByTestId("scenario-analytics-panel")).toBeVisible();
  await expect(page.getByTestId("observability-panel")).toBeVisible();
  await expect(page.getByTestId("audit-panel")).toBeVisible();
  await expect(page.getByTestId("support-panel")).toBeVisible();
}

test("renders SaaS admin shell and analytics surfaces", async ({ page }) => {
  await expectShell(page);
  await expect(page.locator(".metrics-grid .metric span", { hasText: /^Runs$/ })).toBeVisible();
  await expect(page.locator(".metrics-grid .metric span", { hasText: /^Cases$/ })).toBeVisible();
  await expect(page.locator(".metrics-grid .metric span", { hasText: /^Pass Rate$/ })).toBeVisible();
  await expect(page.locator(".metrics-grid .metric span", { hasText: /^Latency$/ })).toBeVisible();
});

test("runs all scenarios and validates batch observability evidence", async ({ page }) => {
  await expectShell(page);
  const matrix = page.getByTestId("observability-panel");

  await page.getByLabel("Matrix models").selectOption(["rule-based-v1", "rule-based-v2"]);
  await page.getByLabel("Matrix scenarios").selectOption(["tutorial_basics_v1", "tutorial_regression_v1"]);
  await page.getByRole("button", { name: "Run Batch Matrix" }).click();

  await expect(page.getByText("Operational")).toBeVisible({ timeout: 20_000 });
  await expect(page.getByText("100.0%").first()).toBeVisible();
  await expect(matrix.getByRole("cell", { name: "Tutorial basics" }).first()).toBeVisible();
  await expect(matrix.getByRole("cell", { name: "Tutorial regression" }).first()).toBeVisible();
  await expect(matrix.getByRole("cell", { name: "rule-based-v1" }).first()).toBeVisible();
  await expect(matrix.getByRole("cell", { name: "rule-based-v2" }).first()).toBeVisible();

  await expect(matrix.getByText("finished")).toHaveCount(4);

  const evidence = page.getByTestId("case-evidence-panel");
  await expect(evidence.getByText("calc_01").or(evidence.getByText("calc_02"))).toBeVisible();
  await expect(evidence.getByText("passed").first()).toBeVisible();

  const audit = page.getByTestId("audit-panel");
  await expect(audit.getByText("run_finished").first()).toBeVisible();
});

test("answers interactive support request with tool evidence", async ({ page }) => {
  await expectShell(page);
  await page.getByTestId("support-panel").getByRole("button", { name: "Ask Agent" }).click();
  await expect(page.getByTestId("support-answer").getByText("streamlit")).toBeVisible();
  await expect(page.getByTestId("support-panel").getByText("lookup").first()).toBeVisible();
});
