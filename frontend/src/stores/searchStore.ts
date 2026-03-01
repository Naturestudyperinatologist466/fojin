import { create } from "zustand";

interface SearchState {
  query: string;
  page: number;
  dynasty: string | null;
  category: string | null;
  setQuery: (q: string) => void;
  setPage: (p: number) => void;
  setDynasty: (d: string | null) => void;
  setCategory: (c: string | null) => void;
  reset: () => void;
}

export const useSearchStore = create<SearchState>((set) => ({
  query: "",
  page: 1,
  dynasty: null,
  category: null,
  setQuery: (query) => set({ query, page: 1 }),
  setPage: (page) => set({ page }),
  setDynasty: (dynasty) => set({ dynasty, page: 1 }),
  setCategory: (category) => set({ category, page: 1 }),
  reset: () => set({ query: "", page: 1, dynasty: null, category: null }),
}));
