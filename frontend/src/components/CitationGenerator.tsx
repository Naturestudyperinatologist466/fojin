import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Select, Typography, Button, Space, message, Modal } from "antd";
import { CopyOutlined, BookOutlined } from "@ant-design/icons";
import api from "../api/client";

const { Paragraph, Text } = Typography;

interface CitationResponse {
  text_id: number;
  title: string;
  style: string;
  citation: string;
}

interface CitationGeneratorProps {
  textId: number;
  open: boolean;
  onClose: () => void;
}

const styleOptions = [
  { value: "chicago", label: "Chicago" },
  { value: "apa", label: "APA" },
  { value: "mla", label: "MLA" },
  { value: "harvard", label: "Harvard" },
];

export default function CitationGenerator({ textId, open, onClose }: CitationGeneratorProps) {
  const [style, setStyle] = useState("chicago");

  const { data: citation } = useQuery<CitationResponse>({
    queryKey: ["citation", textId, style],
    queryFn: async () =>
      (await api.get(`/citations/text/${textId}`, { params: { style } })).data,
    enabled: open && !!textId,
  });

  const handleCopy = () => {
    if (citation) {
      navigator.clipboard.writeText(citation.citation);
      message.success("引用已复制到剪贴板");
    }
  };

  return (
    <Modal
      title={
        <Space>
          <BookOutlined /> 生成引用格式
        </Space>
      }
      open={open}
      onCancel={onClose}
      footer={null}
      width={500}
    >
      <Space direction="vertical" style={{ width: "100%" }}>
        <Space>
          <Text>引用风格:</Text>
          <Select
            value={style}
            onChange={setStyle}
            options={styleOptions}
            style={{ width: 150 }}
          />
        </Space>
        {citation && (
          <div
            style={{
              background: "#fafafa",
              padding: 16,
              borderRadius: 8,
              border: "1px solid #f0f0f0",
            }}
          >
            <Paragraph style={{ margin: 0, whiteSpace: "pre-wrap" }}>
              {citation.citation}
            </Paragraph>
          </div>
        )}
        <Button icon={<CopyOutlined />} onClick={handleCopy} disabled={!citation}>
          复制引用
        </Button>
      </Space>
    </Modal>
  );
}
