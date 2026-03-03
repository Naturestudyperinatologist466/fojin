import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Typography, Card, Tabs, List, Tag, Empty, Spin, Descriptions, Button, Space } from "antd";
import { BookOutlined, HistoryOutlined, UserOutlined, ReadOutlined } from "@ant-design/icons";
import { useAuthStore } from "../stores/authStore";
import { getBookmarks, getHistory } from "../api/client";

const { Title } = Typography;

export default function ProfilePage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const { data: bookmarks, isLoading: bmLoading } = useQuery({
    queryKey: ["bookmarks"],
    queryFn: getBookmarks,
    enabled: !!user,
  });

  const { data: history, isLoading: histLoading } = useQuery({
    queryKey: ["history"],
    queryFn: getHistory,
    enabled: !!user,
  });

  if (!user) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Typography.Text type="secondary">请先登录</Typography.Text>
        <br />
        <Button type="primary" style={{ marginTop: 16 }} onClick={() => navigate("/login")}>
          去登录
        </Button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 800, margin: "24px auto" }}>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Title level={3}>个人中心</Title>

        <Tabs
          items={[
            {
              key: "profile",
              label: (
                <span>
                  <UserOutlined /> 个人资料
                </span>
              ),
              children: (
                <Card>
                  <Descriptions column={1} bordered size="small">
                    <Descriptions.Item label="用户名">{user.username}</Descriptions.Item>
                    <Descriptions.Item label="显示名称">{user.display_name || "-"}</Descriptions.Item>
                    <Descriptions.Item label="邮箱">{user.email}</Descriptions.Item>
                    <Descriptions.Item label="注册时间">
                      {new Date(user.created_at).toLocaleDateString("zh-CN")}
                    </Descriptions.Item>
                  </Descriptions>
                </Card>
              ),
            },
            {
              key: "bookmarks",
              label: (
                <span>
                  <BookOutlined /> 我的收藏 {bookmarks ? `(${bookmarks.length})` : ""}
                </span>
              ),
              children: bmLoading ? (
                <div style={{ textAlign: "center", padding: 40 }}>
                  <Spin />
                </div>
              ) : !bookmarks?.length ? (
                <Empty description="暂无收藏" />
              ) : (
                <List
                  dataSource={bookmarks}
                  renderItem={(item) => (
                    <List.Item
                      style={{ cursor: "pointer" }}
                      onClick={() => navigate(`/texts/${item.text_id}`)}
                      actions={[
                        <Tag color="blue">{item.cbeta_id}</Tag>,
                      ]}
                    >
                      <List.Item.Meta
                        title={item.title_zh}
                        description={
                          item.note ||
                          `收藏于 ${new Date(item.created_at).toLocaleDateString("zh-CN")}`
                        }
                      />
                    </List.Item>
                  )}
                />
              ),
            },
            {
              key: "history",
              label: (
                <span>
                  <HistoryOutlined /> 阅读历史 {history ? `(${history.length})` : ""}
                </span>
              ),
              children: histLoading ? (
                <div style={{ textAlign: "center", padding: 40 }}>
                  <Spin />
                </div>
              ) : !history?.length ? (
                <Empty description="暂无阅读记录" />
              ) : (
                <List
                  dataSource={history}
                  renderItem={(item) => (
                    <List.Item
                      style={{ cursor: "pointer" }}
                      onClick={() => navigate(`/read/${item.text_id}?juan=${item.juan_num}`)}
                      actions={[
                        <Button type="link" icon={<ReadOutlined />}>
                          继续阅读
                        </Button>,
                      ]}
                    >
                      <List.Item.Meta
                        title={item.title_zh}
                        description={`${item.cbeta_id} · 第${item.juan_num}卷 · ${new Date(item.last_read_at).toLocaleDateString("zh-CN")}`}
                      />
                    </List.Item>
                  )}
                />
              ),
            },
          ]}
        />
      </Space>
    </div>
  );
}
