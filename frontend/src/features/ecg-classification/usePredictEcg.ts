import { useMutation } from '@tanstack/react-query'

import { predictEcg, type PredictPayload } from '@/services/api/ecgApi'

export function usePredictEcg() {
  return useMutation({
    mutationFn: (payload: PredictPayload) => predictEcg(payload),
  })
}
