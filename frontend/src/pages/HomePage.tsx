import { Typography, Space, Statistic, Row, Col, Card } from "antd";
import { BookOutlined, DatabaseOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import SearchBar from "../components/SearchBar";
import { getStats } from "../api/client";

const { Title, Paragraph } = Typography;

export default function HomePage() {
  const navigate = useNavigate();
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: getStats,
  });

  const handleSearch = (value: string) => {
    if (value.trim()) {
      navigate(`/search?q=${encodeURIComponent(value.trim())}`);
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        minHeight: "calc(100vh - 200px)",
        padding: "40px 20px",
      }}
    >
      <Space direction="vertical" align="center" size="large">
        <Title
          style={{
            fontSize: 56,
            color: "#1a1a2e",
            letterSpacing: 12,
            marginBottom: 0,
          }}
        >
          佛津
        </Title>
        <Title
          level={3}
          style={{ color: "#8b7355", fontWeight: 400, marginTop: 0 }}
        >
          FoJin — 全球佛教古籍数字资源聚合平台
        </Title>
        <Paragraph
          type="secondary"
          style={{ fontSize: 16, textAlign: "center", maxWidth: 500 }}
        >
          聚合 CBETA 等多家数字化佛教典藏，提供统一检索与浏览
        </Paragraph>
        <SearchBar onSearch={handleSearch} />
        {stats && (
          <Row gutter={24} style={{ marginTop: 40 }}>
            <Col>
              <Card size="small">
                <Statistic
                  title="收录典籍"
                  value={stats.total_texts}
                  prefix={<BookOutlined />}
                />
              </Card>
            </Col>
            <Col>
              <Card size="small">
                <Statistic
                  title="数据来源"
                  value="CBETA"
                  prefix={<DatabaseOutlined />}
                />
              </Card>
            </Col>
          </Row>
        )}
      </Space>
    </div>
  );
}
