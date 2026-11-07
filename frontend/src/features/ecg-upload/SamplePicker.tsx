import { Sparkles } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { useEcgSamples } from '@/features/ecg-upload/useEcgSamples'

interface SamplePickerProps {
  onSelect: (sampleFile: string) => void
  disabled?: boolean
  activeSampleId?: string | null
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
        Explore synthetic signal patterns
      </p>
      <div className="flex flex-wrap gap-2">
        {samples.map((sample) => {
          return (
            <Button
              key={sample.id}
              variant={activeSampleId === sample.id ? 'default' : 'outline'}
              size="sm"
              disabled={disabled}
              onClick={() => onSelect(sample.file)}
              className="gap-2"
            >
              <span className="bg-primary/50 size-1.5 rounded-full" aria-hidden="true" />
              {sample.label}
            </Button>
          )
        })}
      </div>
      <p className="text-muted-foreground mt-2 max-w-2xl text-xs leading-relaxed">
        These labels describe how each synthetic signal was constructed, not the result the
        model is expected to return. Samples are illustrations, not patient recordings.
      </p>
    </div>
  )
}
