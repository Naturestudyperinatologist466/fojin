import { create } from "zustand";
import { persist } from "zustand/middleware";

type ThemeMode = "light" | "dark";

interface ThemeState {
  mode: ThemeMode;
  toggleMode: () => void;
}

const STORAGE_KEY = "fojin-theme";

function applyMode(mode: ThemeMode) {
  document.documentElement.dataset.theme = mode;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set, get) => ({
      mode: "light" as ThemeMode,
      toggleMode: () => {
        const next = get().mode === "light" ? "dark" : "light";
        applyMode(next);
        set({ mode: next });
      },
    }),
    {
      name: STORAGE_KEY,
    },
  ),
);

// Apply theme on initial load (before rehydration completes)
const stored = localStorage.getItem(STORAGE_KEY);
if (stored) {
  try {
    const parsed = JSON.parse(stored);
    if (parsed?.state?.mode) {
      applyMode(parsed.state.mode);
    }
  } catch {
    // ignore
  }
}
