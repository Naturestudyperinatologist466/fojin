import { List, Typography } from "antd";
import { LinkOutlined } from "@ant-design/icons";

interface Resource {
  label: string;
  url: string;
}

interface ResourceListProps {
  resources: Resource[];
}

export default function ResourceList({ resources }: ResourceListProps) {
  if (resources.length === 0) return null;

  return (
    <List
      header={
        <Typography.Text strong>
          <LinkOutlined /> 数字资源
        </Typography.Text>
      }
      bordered
      dataSource={resources}
      renderItem={(item) => (
        <List.Item>
          <a href={item.url} target="_blank" rel="noopener noreferrer">
            {item.label}
          </a>
        </List.Item>
      )}
    />
  );
}
