import { Layout as AntLayout, Typography } from "antd";
import { Outlet, useNavigate } from "react-router-dom";

const { Header, Content, Footer } = AntLayout;

export default function Layout() {
  const navigate = useNavigate();

  return (
    <AntLayout style={{ minHeight: "100vh" }}>
      <Header
        style={{
          display: "flex",
          alignItems: "center",
          background: "#1a1a2e",
          padding: "0 24px",
          cursor: "pointer",
        }}
        onClick={() => navigate("/")}
      >
        <Typography.Title
          level={4}
          style={{ color: "#d4a843", margin: 0, letterSpacing: 4 }}
        >
          佛津 FoJin
        </Typography.Title>
      </Header>
      <Content style={{ padding: "0 24px", flex: 1 }}>
        <Outlet />
      </Content>
      <Footer style={{ textAlign: "center", color: "#999" }}>
        佛津 FoJin &copy; 2026 — 全球佛教古籍数字资源聚合平台
      </Footer>
    </AntLayout>
  );
}
