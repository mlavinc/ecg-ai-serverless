import { motion } from 'framer-motion'

import { Progress } from '@/components/ui/progress'
import { formatPercent } from '@/utils/formatters'
import { cn } from '@/lib/utils'
import type { Severity } from '@/types/ecg'

const SEVERITY_TEXT: Record<Severity, string> = {
  safe: 'text-severity-safe',
  caution: 'text-severity-caution',
  warning: 'text-severity-warning',
  danger: 'text-severity-danger',
}

const SEVERITY_INDICATOR: Record<Severity, string> = {
  safe: 'bg-severity-safe',
  caution: 'bg-severity-caution',
  warning: 'bg-severity-warning',
  danger: 'bg-severity-danger',
}

export function ConfidenceGauge({ confidence, severity }: { confidence: number; severity: Severity }) {
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-muted-foreground text-sm">Model confidence</span>
        <motion.span
          key={confidence}
          initial={{ opacity: 0, y: -4 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn('font-mono-tabular text-lg font-semibold', SEVERITY_TEXT[severity])}
        >
          {formatPercent(confidence)}
        </motion.span>
      </div>
      <Progress value={confidence * 100} indicatorClassName={SEVERITY_INDICATOR[severity]} />
    </div>
  )
}
