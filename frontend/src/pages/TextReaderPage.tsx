import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Helmet } from "react-helmet-async";
import { useQuery } from "@tanstack/react-query";
import { Typography, Spin, Button, Select, Breadcrumb, Space } from "antd";
import { HomeOutlined, LeftOutlined, RightOutlined } from "@ant-design/icons";
import { getJuanList, getJuanContent } from "../api/client";

export default function TextReaderPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const textId = Number(id);
  const [juanNum, setJuanNum] = useState(1);

  const { data: juanList } = useQuery({
    queryKey: ["juanList", textId],
    queryFn: () => getJuanList(textId),
    enabled: !!textId,
  });

  const { data: content, isLoading } = useQuery({
    queryKey: ["juanContent", textId, juanNum],
    queryFn: () => getJuanContent(textId, juanNum),
    enabled: !!textId,
  });

  return (
    <div style={{ maxWidth: 800, margin: "24px auto", padding: "0 16px" }}>
      <Helmet>
        <title>{content?.title_zh ? `${content.title_zh} 第${juanNum}卷` : "在线阅读"} — 佛津</title>
      </Helmet>

      <Breadcrumb
        style={{ marginBottom: 16 }}
        items={[
          { title: <span style={{ cursor: "pointer" }} onClick={() => navigate("/")}><HomeOutlined /> 首页</span> },
          { title: <span style={{ cursor: "pointer" }} onClick={() => navigate(`/texts/${textId}`)}>经典详情</span> },
          { title: "在线阅读" },
        ]}
      />

      {/* Header */}
      <div style={{ marginBottom: 24 }}>
        <Typography.Title level={3} style={{ marginBottom: 8 }}>
          {content?.title_zh || juanList?.title_zh || "加载中..."}
        </Typography.Title>
        <Space>
          <Select
            value={juanNum}
            onChange={setJuanNum}
            style={{ width: 140 }}
            options={
              juanList?.juans.map((j) => ({
                value: j.juan_num,
                label: `第 ${j.juan_num} 卷 (${j.char_count.toLocaleString()}字)`,
              })) || [{ value: 1, label: "第 1 卷" }]
            }
          />
          <Button
            icon={<LeftOutlined />}
            disabled={!content?.prev_juan}
            onClick={() => content?.prev_juan && setJuanNum(content.prev_juan)}
          >
            上一卷
          </Button>
          <Button
            disabled={!content?.next_juan}
            onClick={() => content?.next_juan && setJuanNum(content.next_juan)}
          >
            下一卷 <RightOutlined />
          </Button>
        </Space>
      </div>

      {/* Content */}
      {isLoading ? (
        <div style={{ textAlign: "center", padding: 80 }}>
          <Spin size="large" />
        </div>
      ) : content ? (
        <div
          style={{
            fontFamily: '"Noto Serif SC", "Source Han Serif SC", serif',
            fontSize: 18,
            lineHeight: 2.2,
            color: "var(--fj-ink)",
            whiteSpace: "pre-wrap",
            background: "var(--fj-card-bg)",
            padding: "32px 24px",
            borderRadius: 8,
            border: "1px solid var(--fj-border)",
          }}
        >
          {content.content}
        </div>
      ) : (
        <Typography.Text type="secondary">暂无内容</Typography.Text>
      )}

      {/* Bottom navigation */}
      {content && (
        <div style={{ display: "flex", justifyContent: "space-between", marginTop: 24, marginBottom: 48 }}>
          <Button
            disabled={!content.prev_juan}
            onClick={() => content.prev_juan && setJuanNum(content.prev_juan)}
          >
            <LeftOutlined /> 上一卷
          </Button>
          <Button
            disabled={!content.next_juan}
            onClick={() => content.next_juan && setJuanNum(content.next_juan)}
          >
            下一卷 <RightOutlined />
          </Button>
        </div>
      )}
    </div>
  );
}
