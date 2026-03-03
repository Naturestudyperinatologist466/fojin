import { Layout as AntLayout, Typography, Button, Dropdown, Space } from "antd";
import { Outlet, useNavigate, useLocation } from "react-router-dom";
import {
  UserOutlined,
  LogoutOutlined,
  HeartOutlined,
  LoginOutlined,
  ApartmentOutlined,
  DatabaseOutlined,
  CloudOutlined,
} from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";

const { Header, Content, Footer } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();
  const isHome = location.pathname === "/";

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  /* 古典配色 */
  const ink = "#2b2318";
  const inkMuted = "#9a8e7a";
  const accent = "#8b2500";
  const pageBg = "#f8f5ef";
  const headerBg = isHome ? "rgba(248,245,239,0.85)" : pageBg;

  const navItems = [
    { icon: <DatabaseOutlined />, label: "数据源", path: "/sources" },
    { icon: <CloudOutlined />, label: "典津联检", path: "/dianjin" },
    { icon: <ApartmentOutlined />, label: "知识图谱", path: "/kg" },
  ];

  return (
    <AntLayout style={{ minHeight: "100vh", background: pageBg }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: headerBg,
          backdropFilter: isHome ? "blur(12px)" : undefined,
          padding: "0 32px",
          height: 52,
          lineHeight: "52px",
          borderBottom: `1px solid rgba(217,208,193,0.5)`,
          position: isHome ? "sticky" : undefined,
          top: 0,
          zIndex: 10,
        }}
      >
        <Space size="large">
          <Typography.Title
            level={5}
            style={{
              color: ink,
              margin: 0,
              letterSpacing: 4,
              cursor: "pointer",
              fontWeight: 600,
              fontSize: 16,
              fontFamily: '"Noto Serif SC", serif',
            }}
            onClick={() => navigate("/")}
          >
            佛津
          </Typography.Title>
          {navItems.map((item) => (
            <Button
              key={item.path}
              type="text"
              icon={item.icon}
              style={{
                color: inkMuted,
                fontSize: 13,
                fontWeight: 400,
                fontFamily: '"Noto Serif SC", serif',
              }}
              onClick={() => navigate(item.path)}
            >
              {item.label}
            </Button>
          ))}
        </Space>
        <Space>
          {user ? (
            <Dropdown
              menu={{
                items: [
                  {
                    key: "profile",
                    icon: <UserOutlined />,
                    label: "个人中心",
                    onClick: () => navigate("/profile"),
                  },
                  {
                    key: "bookmarks",
                    icon: <HeartOutlined />,
                    label: "我的收藏",
                    onClick: () => navigate("/profile"),
                  },
                  { type: "divider" },
                  {
                    key: "logout",
                    icon: <LogoutOutlined />,
                    label: "退出登录",
                    onClick: handleLogout,
                  },
                ],
              }}
            >
              <Button
                type="text"
                icon={<UserOutlined />}
                style={{ color: inkMuted, fontSize: 13 }}
              >
                {user.display_name || user.username}
              </Button>
            </Dropdown>
          ) : (
            <Button
              type="text"
              icon={<LoginOutlined />}
              style={{
                color: "#fff",
                background: accent,
                borderRadius: 4,
                fontSize: 12,
                fontWeight: 400,
                height: 30,
                padding: "0 16px",
                fontFamily: '"Noto Serif SC", serif',
              }}
              onClick={() => navigate("/login")}
            >
              登录
            </Button>
          )}
        </Space>
      </Header>
      <Content style={{ padding: isHome ? 0 : "24px 32px", flex: 1 }}>
        <Outlet />
      </Content>
      <Footer
        style={{
          textAlign: "center",
          fontSize: 12,
          fontFamily: '"Noto Serif SC", serif',
          color: inkMuted,
          background: pageBg,
          borderTop: "1px solid rgba(217,208,193,0.5)",
          padding: "16px 32px",
        }}
      >
        佛津 FoJin &copy; 2026 — 全球佛教古籍数字资源聚合平台
      </Footer>
    </AntLayout>
  );
}
