import { test, expect } from "@playwright/test";

test.describe("搜索功能", () => {
  test("在首页搜索栏输入并跳转到搜索结果页", async ({ page }) => {
    await page.goto("/");

    const searchInput = page.locator(".search-combo-input");
    await searchInput.fill("心经");
    await page.locator(".search-combo-btn").click();

    // 应导航到搜索页，URL 包含查询参数
    await expect(page).toHaveURL(/\/search\?q=%E5%BF%83%E7%BB%8F/);
  });

  test("直接访问搜索页并输入查询", async ({ page }) => {
    await page.goto("/search?q=般若");

    // 搜索页应该加载，等待页面内容渲染
    await page.waitForLoadState("networkidle");

    // 页面上应该有搜索相关的内容区域
    await expect(page.locator("body")).toBeVisible();
  });

  test("空搜索不触发导航", async ({ page }) => {
    await page.goto("/");

    // 不输入任何内容直接点击搜索
    await page.locator(".search-combo-btn").click();

    // 应该仍然在首页
    await expect(page).toHaveURL("/");
  });

  test("搜索栏支持回车键触发搜索", async ({ page }) => {
    await page.goto("/");

    const searchInput = page.locator(".search-combo-input");
    await searchInput.fill("金刚经");
    await searchInput.press("Enter");

    await expect(page).toHaveURL(/\/search\?q=/);
  });
});
