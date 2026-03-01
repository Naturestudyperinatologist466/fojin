import { Card, Tag, Typography, Space } from "antd";
import { useNavigate } from "react-router-dom";
import type { SearchHit } from "../api/client";

const { Text } = Typography;

interface TextCardProps {
  hit: SearchHit;
}

export default function TextCard({ hit }: TextCardProps) {
  const navigate = useNavigate();

  const titleHtml = hit.highlight?.title_zh?.[0] ?? hit.title_zh;

  return (
    <Card
      hoverable
      size="small"
      style={{ marginBottom: 12 }}
      onClick={() => navigate(`/texts/${hit.id}`)}
    >
      <Space direction="vertical" size={4} style={{ width: "100%" }}>
        <Space align="center" wrap>
          <Text
            strong
            style={{ fontSize: 16 }}
            // eslint-disable-next-line react/no-danger
            dangerouslySetInnerHTML={{ __html: titleHtml }}
          />
          <Text type="secondary" style={{ fontSize: 13 }}>
            {hit.cbeta_id}
          </Text>
        </Space>
        <Space wrap>
          {hit.translator && (
            <Text type="secondary">
              {hit.dynasty ? `${hit.dynasty} ` : ""}
              <span
                // eslint-disable-next-line react/no-danger
                dangerouslySetInnerHTML={{
                  __html: hit.highlight?.translator?.[0] ?? hit.translator,
                }}
              />
              译
            </Text>
          )}
          {hit.category && <Tag color="geekblue">{hit.category}</Tag>}
        </Space>
      </Space>
    </Card>
  );
}
