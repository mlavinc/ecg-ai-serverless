import { Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useEcgSamples } from '@/features/ecg-upload/useEcgSamples'
import { CLASS_SEVERITY } from '@/utils/constants'
import type { ClassName } from '@/types/ecg'
import { cn } from '@/lib/utils'

interface SamplePickerProps {
  onSelect: (sampleFile: string) => void
  disabled?: boolean
  activeSampleId?: string | null
}

const SEVERITY_DOT: Record<string, string> = {
  safe: 'bg-severity-safe',
  caution: 'bg-severity-caution',
  warning: 'bg-severity-warning',
  danger: 'bg-severity-danger',
}

export function SamplePicker({ onSelect, disabled, activeSampleId }: SamplePickerProps) {
  const { data: samples, isLoading } = useEcgSamples()

  if (isLoading || !samples) {
    return <p className="text-muted-foreground text-sm">Loading samples...</p>
  }

  return (
    <div>
      <p className="text-muted-foreground mb-2 flex items-center gap-1.5 text-sm font-medium">
        <Sparkles className="size-3.5" />
        Or try a synthetic sample per class
      </p>
      <div className="flex flex-wrap gap-2">
        {samples.map((sample) => {
          const severity = CLASS_SEVERITY[sample.className as ClassName]
          return (
            <Button
              key={sample.id}
              variant={activeSampleId === sample.id ? 'default' : 'outline'}
              size="sm"
              disabled={disabled}
              onClick={() => onSelect(sample.file)}
              className="gap-1.5"
            >
              <span className={cn('size-1.5 rounded-full', SEVERITY_DOT[severity])} />
              {sample.label}
            </Button>
          )
        })}
      </div>
      <Badge variant="outline" className="mt-2 text-[11px]">
        Synthetic demo signals, not real patient data
      </Badge>
    </div>
  )
}
