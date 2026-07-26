import { useQuery } from '@tanstack/react-query'

import { getModelMetrics } from '@/services/api/ecgApi'

export function useModelMetrics() {
  return useQuery({
    queryKey: ['model-metrics'],
    queryFn: getModelMetrics,
    staleTime: 5 * 60_000,
  })
}
