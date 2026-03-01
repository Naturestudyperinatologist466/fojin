import { Input } from "antd";
import { SearchOutlined } from "@ant-design/icons";

const { Search } = Input;

// Ant Design icons — we use a simple inline SVG to avoid extra deps
function SearchIcon() {
  return <SearchOutlined />;
}

interface SearchBarProps {
  value?: string;
  onSearch: (value: string) => void;
  size?: "large" | "middle" | "small";
  placeholder?: string;
}

export default function SearchBar({
  value,
  onSearch,
  size = "large",
  placeholder = "搜索经名、编号、译者...",
}: SearchBarProps) {
  return (
    <Search
      defaultValue={value}
      placeholder={placeholder}
      allowClear
      enterButton={
        <>
          <SearchIcon /> 搜索
        </>
      }
      size={size}
      onSearch={onSearch}
      style={{ maxWidth: 640 }}
    />
  );
}
