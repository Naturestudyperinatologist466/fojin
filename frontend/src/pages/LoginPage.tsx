import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Form, Input, Button, Typography, Tabs, message } from "antd";
import { UserOutlined, LockOutlined, MailOutlined } from "@ant-design/icons";
import { useTranslation } from "react-i18next";
import { useAuthStore } from "../stores/authStore";
import api from "../api/client";

const { Title } = Typography;

export default function LoginPage() {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const setAuth = useAuthStore((s) => s.setAuth);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState("login");

  const handleLogin = async (values: { username: string; password: string }) => {
    setLoading(true);
    try {
      const { data: tokenData } = await api.post("/auth/login", values);
      const { data: user } = await api.get("/auth/me", {
        headers: { Authorization: `Bearer ${tokenData.access_token}` },
      });
      setAuth(tokenData.access_token, user);
      message.success(t("auth.login_success"));
      navigate("/");
    } catch (err: any) {
      message.error(err.response?.data?.detail || t("auth.login_fail"));
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values: {
    username: string;
    email: string;
    password: string;
    display_name?: string;
  }) => {
    setLoading(true);
    try {
      await api.post("/auth/register", values);
      message.success(t("auth.register_success"));
      setActiveTab("login");
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      const msg = Array.isArray(detail) ? detail.map((d: any) => d.msg).join("; ") : detail || t("auth.register_fail");
      message.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "calc(100vh - 200px)",
        padding: 24,
      }}
    >
      <Card style={{ width: 400 }}>
        <Title level={3} style={{ textAlign: "center", marginBottom: 24 }}>
          {t("app.name")}
        </Title>
        <Tabs
          activeKey={activeTab}
          onChange={setActiveTab}
          centered
          items={[
            {
              key: "login",
              label: t("auth.login"),
              children: (
                <Form onFinish={handleLogin} layout="vertical">
                  <Form.Item name="username" rules={[{ required: true, message: t("auth.username_required") }]}>
                    <Input prefix={<UserOutlined />} placeholder={t("auth.username")} size="large" />
                  </Form.Item>
                  <Form.Item name="password" rules={[{ required: true, message: t("auth.password_required") }]}>
                    <Input.Password prefix={<LockOutlined />} placeholder={t("auth.password")} size="large" />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading} block size="large">
                      {t("auth.login")}
                    </Button>
                  </Form.Item>
                </Form>
              ),
            },
            {
              key: "register",
              label: t("auth.register"),
              children: (
                <Form onFinish={handleRegister} layout="vertical">
                  <Form.Item name="username" rules={[{ required: true, message: t("auth.username_required") }]}>
                    <Input prefix={<UserOutlined />} placeholder={t("auth.username")} size="large" />
                  </Form.Item>
                  <Form.Item
                    name="email"
                    rules={[
                      { required: true, message: t("auth.email_required") },
                      { type: "email", message: t("auth.email_invalid") },
                    ]}
                  >
                    <Input prefix={<MailOutlined />} placeholder={t("auth.email")} size="large" />
                  </Form.Item>
                  <Form.Item
                    name="password"
                    rules={[
                      { required: true, message: t("auth.password_required") },
                      { min: 8, message: t("auth.password_min") },
                      { pattern: /[a-zA-Z]/, message: t("auth.password_letter") },
                      { pattern: /\d/, message: t("auth.password_digit") },
                    ]}
                  >
                    <Input.Password prefix={<LockOutlined />} placeholder={t("auth.password_hint")} size="large" />
                  </Form.Item>
                  <Form.Item name="display_name">
                    <Input prefix={<UserOutlined />} placeholder={t("auth.display_name")} size="large" />
                  </Form.Item>
                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading} block size="large">
                      {t("auth.register")}
                    </Button>
                  </Form.Item>
                </Form>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
}
