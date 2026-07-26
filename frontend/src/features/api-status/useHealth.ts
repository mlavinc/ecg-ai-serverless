import { useQuery } from '@tanstack/react-query'

import { getHealth } from '@/services/api/ecgApi'

export function useHealth() {
  return useQuery({
    queryKey: ['health'],
    queryFn: getHealth,
    staleTime: 30_000,
    retry: 0,
  })
}
