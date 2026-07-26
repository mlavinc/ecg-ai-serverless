import { Cpu, Timer } from 'lucide-react'

import { Card, CardContent } from '@/components/ui/card'
import { formatMs } from '@/utils/formatters'
import type { PredictMeta } from '@/types/ecg'

export function InferenceMetaPanel({ meta }: { meta: PredictMeta }) {
  return (
    <Card>
      <CardContent className="grid grid-cols-2 gap-4">
        <div className="flex items-center gap-2.5">
          <div className="bg-secondary flex size-8 items-center justify-center rounded-full">
            <Timer className="size-4" />
          </div>
          <div>
            <p className="font-mono-tabular text-sm font-semibold">{formatMs(meta.inference_time_ms)}</p>
            <p className="text-muted-foreground text-xs">Inference time</p>
          </div>
        </div>
        <div className="flex items-center gap-2.5">
          <div className="bg-secondary flex size-8 items-center justify-center rounded-full">
            <Cpu className="size-4" />
          </div>
          <div>
            <p className="text-sm font-semibold">{meta.model_version}</p>
            <p className="text-muted-foreground text-xs">Model version</p>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
