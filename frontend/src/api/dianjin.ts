import api, { type SearchHit } from "./client";

// ─── Types matching actual Dianjin API responses ───

export interface DianjinSearchHit {
  id: string;
  title: string;
  datasource_name: string | null;
  datasource_category: string | null;
  datasource_tags: string[];
  collection: string | null;
  main_responsibility: string | null;
  edition: string | null;
  detail_url: string | null;
  score: number | null;
}

export interface DianjinSearchResponse {
  total: number;
  page: number;
  size: number;
  results: DianjinSearchHit[];
  search_time: number | null;
  error: string | null;
}

export interface FederatedSearchResponse {
  local_total: number;
  local_results: SearchHit[];
  dianjin_total: number;
  dianjin_results: DianjinSearchHit[];
  dianjin_error: string | null;
  combined_total: number;
}

export interface DianjinHealthStatus {
  configured: boolean;
  public_api: boolean;
  search_api: boolean;
  datasource_count: number;
  error: string | null;
}

export interface DianjinDatasource {
  id: string;
  name: string;
  code: string;
  description: string;
  category: string;
  tags: string[];
  institution_code: string;
  record_count: number;
}

export interface DianjinDatasourcePage {
  items: DianjinDatasource[];
  total: number;
  page: number;
  size: number;
  total_pages: number;
}

// ─── API Functions ───

export async function getDianjinHealth(): Promise<DianjinHealthStatus> {
  const { data } = await api.get<DianjinHealthStatus>("/dianjin/health");
  return data;
}

export async function getDianjinDatasources(
  page: number = 1,
  size: number = 20,
): Promise<DianjinDatasourcePage> {
  const { data } = await api.get<DianjinDatasourcePage>("/dianjin/datasources", {
    params: { page, size },
  });
  return data;
}

export interface DianjinInstitution {
  id: string;
  name: string;
  code: string;
  countryRegion: string;
  logo: string | null;
}

export async function getDianjinRegionLabels(): Promise<Record<string, string>> {
  const { data } = await api.get<Record<string, string>>("/dianjin/region-labels");
  return data;
}

export async function getDianjinInstitutions(): Promise<DianjinInstitution[]> {
  const { data } = await api.get<DianjinInstitution[]>("/dianjin/institutions");
  return data;
}

export async function searchDianjin(
  query: string,
  page: number = 1,
  size: number = 20,
): Promise<DianjinSearchResponse> {
  const { data } = await api.post<DianjinSearchResponse>(
    `/dianjin/search?query=${encodeURIComponent(query)}&page=${page}&size=${size}`,
  );
  return data;
}

export async function federatedSearch(params: {
  q: string;
  page?: number;
  size?: number;
  dynasty?: string;
  category?: string;
  sources?: string;
  include_dianjin?: boolean;
}): Promise<FederatedSearchResponse> {
  const { data } = await api.get<FederatedSearchResponse>(
    "/search/federated",
    { params },
  );
  return data;
}
