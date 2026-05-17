import {create} from 'zustand';
import {TestResponse} from '@/shared/api/client/testConstructorAPI.schemas';

interface CatalogState {
  tests: TestResponse[];
  setTests: (t: TestResponse[]) => void;
  query: string;
  setQuery: (q: string) => void;
  tags: string[];
  setTags: (t: string[]) => void;
}

export const useCatalogStore = create<CatalogState>((set) => ({
  tests: [],
  setTests: (tests) => set({tests}),
  query: '',
  setQuery: (query) => set({query}),
  tags: [],
  setTags: (tags) => set({tags}),
}));
