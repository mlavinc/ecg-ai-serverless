import { useQuery } from '@tanstack/react-query'

import type { EcgSampleMeta } from '@/types/ecg'

async function fetchSampleCatalog(): Promise<EcgSampleMeta[]> {
  const res = await fetch('/samples/index.json')
  if (!res.ok) throw new Error('Could not load sample catalog.')
  return res.json()
}

export function useEcgSamples() {
  return useQuery({
    queryKey: ['ecg-samples'],
    queryFn: fetchSampleCatalog,
    staleTime: Infinity,
  })
}
