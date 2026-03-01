import axios from "axios";

const api = axios.create({
  baseURL: "/api",
  timeout: 15000,
});

export interface SearchHit {
  id: number;
  taisho_id: string | null;
  cbeta_id: string;
  title_zh: string;
  translator: string | null;
  dynasty: string | null;
  category: string | null;
  cbeta_url: string | null;
  score: number | null;
  highlight: Record<string, string[]> | null;
}

export interface SearchResponse {
  total: number;
  page: number;
  size: number;
  results: SearchHit[];
}

export interface TextDetail {
  id: number;
  taisho_id: string | null;
  cbeta_id: string;
  title_zh: string;
  title_sa: string | null;
  title_bo: string | null;
  title_pi: string | null;
  translator: string | null;
  dynasty: string | null;
  fascicle_count: number | null;
  category: string | null;
  subcategory: string | null;
  cbeta_url: string | null;
  created_at: string;
}

export interface Filters {
  dynasties: string[];
  categories: string[];
}

export interface Stats {
  total_texts: number;
}

export async function searchTexts(params: {
  q: string;
  page?: number;
  size?: number;
  dynasty?: string;
  category?: string;
}): Promise<SearchResponse> {
  const { data } = await api.get<SearchResponse>("/search", { params });
  return data;
}

export async function getTextDetail(id: number): Promise<TextDetail> {
  const { data } = await api.get<TextDetail>(`/texts/${id}`);
  return data;
}

export async function getFilters(): Promise<Filters> {
  const { data } = await api.get<Filters>("/filters");
  return data;
}

export async function getStats(): Promise<Stats> {
  const { data } = await api.get<Stats>("/stats");
  return data;
}

export default api;
