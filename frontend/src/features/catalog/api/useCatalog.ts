import {useQuery} from '@tanstack/react-query';
import {searchCatalogApiV1CatalogGet} from '@/shared/api/client/catalog';

export function useCatalogSearch(q?: string, tags?: string[], skip?: number, limit?: number) {
  return useQuery({
    queryKey: ['catalog', q, tags, skip, limit],
    queryFn: () => searchCatalogApiV1CatalogGet({q, tags, skip: skip || 0, limit: limit || 20}),
  });
}
