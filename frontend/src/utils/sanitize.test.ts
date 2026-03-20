import { describe, it, expect } from "vitest";
import { sanitizeHighlight, escapeHtml } from "./sanitize";

describe("sanitizeHighlight", () => {
  it("保留 em/b/strong/mark 标签", () => {
    const input = '<em>搜索</em> <b>结果</b> <strong>高亮</strong> <mark>标记</mark>';
    const result = sanitizeHighlight(input);
    expect(result).toContain("<em>搜索</em>");
    expect(result).toContain("<b>结果</b>");
    expect(result).toContain("<strong>高亮</strong>");
    expect(result).toContain("<mark>标记</mark>");
  });

  it("移除不允许的标签（如 script、img、a）", () => {
    const input = '<script>alert("xss")</script><em>safe</em>';
    const result = sanitizeHighlight(input);
    expect(result).not.toContain("<script>");
    expect(result).toContain("<em>safe</em>");
  });

  it("移除 img 标签（含 onerror 注入）", () => {
    const input = '<img src=x onerror="alert(1)"><em>ok</em>';
    const result = sanitizeHighlight(input);
    expect(result).not.toContain("<img");
    expect(result).not.toContain("onerror");
    expect(result).toContain("<em>ok</em>");
  });

  it("移除标签上的所有属性", () => {
    const input = '<em style="color:red" onclick="alert(1)">text</em>';
    const result = sanitizeHighlight(input);
    expect(result).toBe("<em>text</em>");
  });

  it("移除 a 标签但保留文本内容", () => {
    const input = '<a href="http://evil.com">链接</a>';
    const result = sanitizeHighlight(input);
    expect(result).not.toContain("<a");
    expect(result).toContain("链接");
  });

  it("处理空字符串", () => {
    expect(sanitizeHighlight("")).toBe("");
  });

  it("纯文本直接返回", () => {
    expect(sanitizeHighlight("普通文本")).toBe("普通文本");
  });

  it("移除嵌套的危险标签", () => {
    const input = "<em><script>alert(1)</script>文本</em>";
    const result = sanitizeHighlight(input);
    expect(result).not.toContain("<script>");
    expect(result).toContain("<em>");
    expect(result).toContain("文本");
  });
});

describe("escapeHtml", () => {
  it("转义 HTML 特殊字符", () => {
    expect(escapeHtml('<script>alert("xss")</script>')).toBe(
      "&lt;script&gt;alert(\"xss\")&lt;/script&gt;",
    );
  });

  it("转义 & 符号", () => {
    expect(escapeHtml("a & b")).toBe("a &amp; b");
  });

  it("转义尖括号", () => {
    expect(escapeHtml("<div>")).toBe("&lt;div&gt;");
  });

  it("处理空字符串", () => {
    expect(escapeHtml("")).toBe("");
  });

  it("纯文本不变", () => {
    expect(escapeHtml("普通文本")).toBe("普通文本");
  });
});
