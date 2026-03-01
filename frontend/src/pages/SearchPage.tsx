import { useEffect } from "react";
import {
  Typography,
  Pagination,
  Spin,
  Empty,
  Select,
  Space,
  Row,
  Col,
  Card,
} from "antd";
import { useSearchParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import SearchBar from "../components/SearchBar";
import TextCard from "../components/TextCard";
import { searchTexts, getFilters } from "../api/client";
import { useSearchStore } from "../stores/searchStore";

export default function SearchPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const { query, page, dynasty, category, setQuery, setPage, setDynasty, setCategory } =
    useSearchStore();

  // Sync URL params to store on mount
  useEffect(() => {
    const q = searchParams.get("q") ?? "";
    const p = parseInt(searchParams.get("page") ?? "1", 10);
    const d = searchParams.get("dynasty") ?? null;
    const c = searchParams.get("category") ?? null;
    if (q !== query) setQuery(q);
    if (p !== page) setPage(p);
    if (d !== dynasty) setDynasty(d);
    if (c !== category) setCategory(c);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Sync store to URL
  useEffect(() => {
    const params: Record<string, string> = {};
    if (query) params.q = query;
    if (page > 1) params.page = String(page);
    if (dynasty) params.dynasty = dynasty;
    if (category) params.category = category;
    setSearchParams(params, { replace: true });
  }, [query, page, dynasty, category, setSearchParams]);

  const { data, isLoading } = useQuery({
    queryKey: ["search", query, page, dynasty, category],
    queryFn: () =>
      searchTexts({ q: query, page, size: 20, dynasty: dynasty ?? undefined, category: category ?? undefined }),
    enabled: query.length > 0,
  });

  const { data: filters } = useQuery({
    queryKey: ["filters"],
    queryFn: getFilters,
  });

  const handleSearch = (value: string) => {
    setQuery(value);
  };

  return (
    <div style={{ maxWidth: 960, margin: "24px auto" }}>
      <Space direction="vertical" size="middle" style={{ width: "100%" }}>
        <SearchBar value={query} onSearch={handleSearch} />

        <Row gutter={16}>
          <Col flex="auto">
            {isLoading && (
              <div style={{ textAlign: "center", padding: 60 }}>
                <Spin size="large" />
              </div>
            )}

            {!isLoading && data && data.results.length === 0 && (
              <Empty description="未找到相关典籍" />
            )}

            {!isLoading && data && data.results.length > 0 && (
              <>
                <Typography.Text type="secondary" style={{ display: "block", marginBottom: 12 }}>
                  共找到 {data.total} 部典籍
                </Typography.Text>
                {data.results.map((hit) => (
                  <TextCard key={hit.id} hit={hit} />
                ))}
                <div style={{ textAlign: "center", marginTop: 16 }}>
                  <Pagination
                    current={page}
                    total={data.total}
                    pageSize={20}
                    showSizeChanger={false}
                    onChange={(p) => setPage(p)}
                  />
                </div>
              </>
            )}
          </Col>

          <Col flex="220px">
            <Card title="筛选" size="small">
              <Space direction="vertical" style={{ width: "100%" }}>
                <div>
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    朝代
                  </Typography.Text>
                  <Select
                    allowClear
                    placeholder="全部朝代"
                    style={{ width: "100%" }}
                    value={dynasty}
                    onChange={(v) => setDynasty(v ?? null)}
                    options={filters?.dynasties.map((d) => ({
                      label: d,
                      value: d,
                    }))}
                  />
                </div>
                <div>
                  <Typography.Text type="secondary" style={{ fontSize: 12 }}>
                    分类
                  </Typography.Text>
                  <Select
                    allowClear
                    placeholder="全部分类"
                    style={{ width: "100%" }}
                    value={category}
                    onChange={(v) => setCategory(v ?? null)}
                    options={filters?.categories.map((c) => ({
                      label: c,
                      value: c,
                    }))}
                  />
                </div>
              </Space>
            </Card>
          </Col>
        </Row>
      </Space>
    </div>
  );
}
