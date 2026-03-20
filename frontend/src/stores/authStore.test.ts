import { describe, it, expect, beforeEach } from "vitest";
import { useAuthStore, type UserProfile } from "./authStore";

const mockUser: UserProfile = {
  id: 1,
  username: "testuser",
  email: "test@example.com",
  display_name: "测试用户",
  role: "user",
  is_active: true,
  created_at: "2024-01-01T00:00:00Z",
};

describe("authStore", () => {
  beforeEach(() => {
    // 每次测试前重置 store 状态
    useAuthStore.setState({ token: null, user: null });
    localStorage.clear();
  });

  it("初始状态为未登录", () => {
    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
  });

  it("setAuth 设置 token 和用户信息", () => {
    useAuthStore.getState().setAuth("test-token-123", mockUser);

    const state = useAuthStore.getState();
    expect(state.token).toBe("test-token-123");
    expect(state.user).toEqual(mockUser);
  });

  it("logout 清除认证信息", () => {
    useAuthStore.getState().setAuth("test-token-123", mockUser);
    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.token).toBeNull();
    expect(state.user).toBeNull();
  });

  it("persist 中间件将状态写入 localStorage", () => {
    useAuthStore.getState().setAuth("persist-token", mockUser);

    const raw = localStorage.getItem("fojin-auth");
    expect(raw).toBeTruthy();

    const parsed = JSON.parse(raw!);
    expect(parsed.state.token).toBe("persist-token");
    expect(parsed.state.user.username).toBe("testuser");
  });

  it("logout 后 localStorage 中 token 被清除", () => {
    useAuthStore.getState().setAuth("some-token", mockUser);
    useAuthStore.getState().logout();

    const raw = localStorage.getItem("fojin-auth");
    expect(raw).toBeTruthy();

    const parsed = JSON.parse(raw!);
    expect(parsed.state.token).toBeNull();
    expect(parsed.state.user).toBeNull();
  });

  it("可以区分不同角色", () => {
    const adminUser: UserProfile = { ...mockUser, role: "admin" };
    useAuthStore.getState().setAuth("admin-token", adminUser);

    expect(useAuthStore.getState().user?.role).toBe("admin");
  });
});
