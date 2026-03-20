import { test, expect } from "@playwright/test";

test.describe("首页", () => {
  test("页面加载并显示搜索栏", async ({ page }) => {
    await page.goto("/");

    // 搜索输入框应可见
    const searchInput = page.locator(".search-combo-input");
    await expect(searchInput).toBeVisible();

    // 搜索按钮应可见
    const searchBtn = page.locator(".search-combo-btn");
    await expect(searchBtn).toBeVisible();
  });

  test("页面包含功能卡片", async ({ page }) => {
    await page.goto("/");

    // 应有 4 个功能卡片（数据源、知识图谱、AI 问答、收藏集）
    const featureCards = page.locator(".home-feature-card");
    await expect(featureCards).toHaveCount(4);
  });

  test("页面包含统计数据区域", async ({ page }) => {
    await page.goto("/");

    const statsGroup = page.locator('[role="group"]');
    await expect(statsGroup).toBeVisible();
  });

  test("导航栏显示站点标题", async ({ page }) => {
    await page.goto("/");

    // "佛津" 标题应可见
    await expect(page.getByText("佛津")).toBeVisible();
  });

  test("点击功能卡片可导航", async ({ page }) => {
    await page.goto("/");

    // 点击第一个功能卡片（数据源）应导航到 /sources
    const firstCard = page.locator(".home-feature-card").first();
    await firstCard.click();

    await expect(page).toHaveURL(/\/sources/);
  });
});
