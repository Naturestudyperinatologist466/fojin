import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Typography, Card, Button, Space, Select, Tag, Spin } from "antd";
import {
  DownloadOutlined,
  FileTextOutlined,
  ApartmentOutlined,
  ShareAltOutlined,
} from "@ant-design/icons";
import api from "../api/client";

const { Title, Paragraph, Text } = Typography;

interface ExportStats {
  texts: number;
  kg_entities: number;
  kg_relations: number;
}

const ENTITY_TYPE_OPTIONS = [
  { value: "", label: "全部类型" },
  { value: "person", label: "人物" },
  { value: "text", label: "典籍" },
  { value: "monastery", label: "寺院" },
  { value: "school", label: "宗派" },
  { value: "place", label: "地点" },
  { value: "concept", label: "概念" },
  { value: "dynasty", label: "朝代" },
];

function buildUrl(base: string, params: Record<string, string>) {
  const qs = Object.entries(params)
    .filter(([, v]) => v)
    .map(([k, v]) => `${k}=${encodeURIComponent(v)}`)
    .join("&");
  return qs ? `${base}?${qs}` : base;
}

export default function ExportsPage() {
  const [dynasty, setDynasty] = useState("");
  const [category, setCategory] = useState("");
  const [entityType, setEntityType] = useState("");

  const { data: stats, isLoading } = useQuery<ExportStats>({
    queryKey: ["exportStats"],
    queryFn: async () => (await api.get("/exports/stats")).data,
  });

  const csvUrl = buildUrl("/api/exports/metadata.csv", { dynasty, category });
  const kgJsonUrl = buildUrl("/api/exports/kg.json", { entity_type: entityType });
  const kgJsonLdUrl = buildUrl("/api/exports/kg.jsonld", { entity_type: entityType });

  return (
    <div style={{ maxWidth: 800, margin: "24px auto" }}>
      <Title level={3}>
        <DownloadOutlined /> 开放数据下载
      </Title>
      <Paragraph type="secondary">
        佛津平台数据以开放协议提供，欢迎学术研究和开发者使用。
        数据采用分批流式导出，适合大规模数据集。
      </Paragraph>

      {isLoading ? (
        <Spin style={{ display: "block", margin: "24px auto" }} />
      ) : stats ? (
        <Card size="small" style={{ marginBottom: 24 }}>
          <Space size="large">
            <span>
              经典元数据 <Tag color="blue">{stats.texts.toLocaleString()} 条</Tag>
            </span>
            <span>
              知识图谱实体 <Tag color="green">{stats.kg_entities.toLocaleString()} 个</Tag>
            </span>
            <span>
              知识图谱关系 <Tag color="orange">{stats.kg_relations.toLocaleString()} 条</Tag>
            </span>
          </Space>
        </Card>
      ) : null}

      {/* CSV Export */}
      <Card style={{ marginBottom: 16 }}>
        <Space align="start" size="large">
          <div style={{ color: "#1a1a2e" }}>
            <FileTextOutlined style={{ fontSize: 24 }} />
          </div>
          <div style={{ flex: 1 }}>
            <Text strong style={{ fontSize: 16 }}>
              佛典元数据 (CSV)
            </Text>
            <Paragraph type="secondary" style={{ margin: "4px 0 8px" }}>
              包含所有经典的编号、标题、译者、朝代、分类等元数据。可选按朝代/分类筛选。
            </Paragraph>
            <Space wrap style={{ marginBottom: 8 }}>
              <Select
                style={{ width: 120 }}
                placeholder="朝代"
                allowClear
                value={dynasty || undefined}
                onChange={(v) => setDynasty(v || "")}
                options={[
                  { value: "东汉", label: "东汉" },
                  { value: "三国", label: "三国" },
                  { value: "西晋", label: "西晋" },
                  { value: "东晋", label: "东晋" },
                  { value: "南北朝", label: "南北朝" },
                  { value: "隋", label: "隋" },
                  { value: "唐", label: "唐" },
                  { value: "宋", label: "宋" },
                  { value: "元", label: "元" },
                  { value: "明", label: "明" },
                  { value: "清", label: "清" },
                ]}
              />
              <Select
                style={{ width: 120 }}
                placeholder="分类"
                allowClear
                value={category || undefined}
                onChange={(v) => setCategory(v || "")}
                options={[
                  { value: "阿含部", label: "阿含部" },
                  { value: "般若部", label: "般若部" },
                  { value: "华严部", label: "华严部" },
                  { value: "法华部", label: "法华部" },
                  { value: "密教部", label: "密教部" },
                  { value: "律部", label: "律部" },
                  { value: "论集部", label: "论集部" },
                ]}
              />
            </Space>
            <br />
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              href={csvUrl}
              download="fojin_metadata.csv"
            >
              下载 CSV
            </Button>
          </div>
        </Space>
      </Card>

      {/* KG JSON Export */}
      <Card style={{ marginBottom: 16 }}>
        <Space align="start" size="large">
          <div style={{ color: "#1a1a2e" }}>
            <ApartmentOutlined style={{ fontSize: 24 }} />
          </div>
          <div style={{ flex: 1 }}>
            <Text strong style={{ fontSize: 16 }}>
              知识图谱 (JSON)
            </Text>
            <Paragraph type="secondary" style={{ margin: "4px 0 8px" }}>
              包含实体（人物、地点、概念等）和关系的完整知识图谱数据，含属性和外部标识符。
            </Paragraph>
            <Space style={{ marginBottom: 8 }}>
              <Select
                style={{ width: 140 }}
                placeholder="实体类型"
                allowClear
                value={entityType || undefined}
                onChange={(v) => setEntityType(v || "")}
                options={ENTITY_TYPE_OPTIONS.filter((o) => o.value)}
              />
            </Space>
            <br />
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              href={kgJsonUrl}
              download="fojin_kg.json"
            >
              下载 JSON
            </Button>
          </div>
        </Space>
      </Card>

      {/* KG JSON-LD Export */}
      <Card style={{ marginBottom: 16 }}>
        <Space align="start" size="large">
          <div style={{ color: "#1a1a2e" }}>
            <ShareAltOutlined style={{ fontSize: 24 }} />
          </div>
          <div style={{ flex: 1 }}>
            <Text strong style={{ fontSize: 16 }}>
              知识图谱 (JSON-LD)
            </Text>
            <Paragraph type="secondary" style={{ margin: "4px 0 8px" }}>
              语义化链接数据格式，使用 SKOS/Dublin Core/Schema.org 标准词汇，
              支持多语言标签（@language 标注）。可用于与其他 LOD 数据集互操作。
            </Paragraph>
            <Button
              type="primary"
              icon={<DownloadOutlined />}
              href={kgJsonLdUrl}
              download="fojin_kg.jsonld"
            >
              下载 JSON-LD
            </Button>
          </div>
        </Space>
      </Card>
    </div>
  );
}
