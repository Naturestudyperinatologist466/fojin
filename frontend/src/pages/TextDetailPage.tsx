import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import {
  Typography,
  Descriptions,
  Spin,
  Button,
  Space,
  Card,
  Tag,
} from "antd";
import { ArrowLeftOutlined } from "@ant-design/icons";
import { getTextDetail } from "../api/client";
import ResourceList from "../components/ResourceList";

const { Title } = Typography;

export default function TextDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: text, isLoading } = useQuery({
    queryKey: ["text", id],
    queryFn: () => getTextDetail(Number(id)),
    enabled: !!id,
  });

  if (isLoading) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!text) {
    return (
      <div style={{ textAlign: "center", padding: 80 }}>
        <Typography.Text type="secondary">经典未找到</Typography.Text>
      </div>
    );
  }

  const resources = [];
  if (text.cbeta_url) {
    resources.push({ label: "CBETA 在线阅读", url: text.cbeta_url });
  }

  return (
    <div style={{ maxWidth: 800, margin: "24px auto" }}>
      <Space direction="vertical" size="large" style={{ width: "100%" }}>
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(-1)}
        >
          返回
        </Button>

        <Card>
          <Title level={3} style={{ marginBottom: 4 }}>
            {text.title_zh}
          </Title>
          <Space style={{ marginBottom: 16 }}>
            <Tag color="blue">{text.cbeta_id}</Tag>
            {text.taisho_id && text.taisho_id !== text.cbeta_id && (
              <Tag>{text.taisho_id}</Tag>
            )}
            {text.category && <Tag color="geekblue">{text.category}</Tag>}
          </Space>

          <Descriptions column={1} bordered size="small">
            {text.translator && (
              <Descriptions.Item label="译者">
                {text.dynasty ? `${text.dynasty} ` : ""}
                {text.translator}
              </Descriptions.Item>
            )}
            {text.dynasty && (
              <Descriptions.Item label="朝代">
                {text.dynasty}
              </Descriptions.Item>
            )}
            {text.fascicle_count && (
              <Descriptions.Item label="卷数">
                {text.fascicle_count} 卷
              </Descriptions.Item>
            )}
            {text.subcategory && (
              <Descriptions.Item label="典藏">
                {text.subcategory}
              </Descriptions.Item>
            )}
            {text.title_sa && (
              <Descriptions.Item label="梵文名">
                {text.title_sa}
              </Descriptions.Item>
            )}
            {text.title_pi && (
              <Descriptions.Item label="巴利文名">
                {text.title_pi}
              </Descriptions.Item>
            )}
            {text.title_bo && (
              <Descriptions.Item label="藏文名">
                {text.title_bo}
              </Descriptions.Item>
            )}
            <Descriptions.Item label="CBETA 编号">
              {text.cbeta_id}
            </Descriptions.Item>
          </Descriptions>
        </Card>

        <ResourceList resources={resources} />
      </Space>
    </div>
  );
}
