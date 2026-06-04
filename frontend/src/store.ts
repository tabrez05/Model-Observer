import { create } from 'zustand';

interface CompareStore {
  selectedIds: string[];
  toggle: (id: string) => void;
  clear: () => void;
}

export const useCompareStore = create<CompareStore>(set => ({
  selectedIds: [],
  toggle: id =>
    set(s => ({
      selectedIds: s.selectedIds.includes(id)
        ? s.selectedIds.filter(x => x !== id)
        : s.selectedIds.length < 5
        ? [...s.selectedIds, id]
        : s.selectedIds,
    })),
  clear: () => set({ selectedIds: [] }),
}));
