import { useQuery } from "@tanstack/react-query";
import { Card, List, Tag, Typography, Button, Spin } from "antd";
import { SwapOutlined, ReadOutlined } from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { getTextRelations } from "../api/client";

const RELATION_LABELS: Record<string, { label: string; color: string }> = {
  parallel: { label: "平行", color: "blue" },
  alt_translation: { label: "异译", color: "orange" },
  commentary: { label: "注疏", color: "green" },
};

export default function RelatedTexts({ textId }: { textId: number }) {
  const navigate = useNavigate();

  const { data, isLoading } = useQuery({
    queryKey: ["relations", textId],
    queryFn: () => getTextRelations(textId),
    enabled: !!textId,
  });

  if (isLoading) {
    return <Spin />;
  }

  if (!data?.relations.length) {
    return null;
  }

  return (
    <Card
      title={
        <span>
          <SwapOutlined /> 关联文本
        </span>
      }
      size="small"
    >
      <List
        dataSource={data.relations}
        renderItem={(item) => {
          const meta = RELATION_LABELS[item.relation_type] || {
            label: item.relation_type,
            color: "default",
          };
          return (
            <List.Item
              actions={[
                <Button
                  type="link"
                  size="small"
                  icon={<ReadOutlined />}
                  onClick={() =>
                    navigate(`/parallel/${textId}?compare=${item.text_id}`)
                  }
                >
                  对照
                </Button>,
              ]}
            >
              <List.Item.Meta
                title={
                  <span
                    style={{ cursor: "pointer" }}
                    onClick={() => navigate(`/texts/${item.text_id}`)}
                  >
                    {item.title_zh}
                    <Tag color={meta.color} style={{ marginLeft: 8 }}>
                      {meta.label}
                    </Tag>
                  </span>
                }
                description={
                  <Typography.Text type="secondary">
                    {item.dynasty && `${item.dynasty} · `}
                    {item.translator || "佚名"}
                    {item.lang !== "lzh" && ` · ${item.lang}`}
                  </Typography.Text>
                }
              />
            </List.Item>
          );
        }}
      />
    </Card>
  );
}
