import { motion } from 'framer-motion'
import { AlertTriangle, CheckCircle2, ShieldAlert, TriangleAlert } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { ConfidenceGauge } from '@/features/ecg-classification/ConfidenceGauge'
import { CLASS_LABELS, CLASS_SEVERITY, SEVERITY_LABEL } from '@/utils/constants'
import type { ClassName, Prediction } from '@/types/ecg'

const SEVERITY_ICON = {
  safe: CheckCircle2,
  caution: TriangleAlert,
  warning: AlertTriangle,
  danger: ShieldAlert,
} as const

export function ResultCard({ prediction }: { prediction: Prediction }) {
  const className = prediction.class_name as ClassName
  const severity = CLASS_SEVERITY[className] ?? 'caution'
  const label = CLASS_LABELS[className] ?? className
  const Icon = SEVERITY_ICON[severity]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-base">
          Classification result
          <Badge variant={severity}>{SEVERITY_LABEL[severity]}</Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-5">
        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex items-center gap-3"
        >
          <div
            className="flex size-11 shrink-0 items-center justify-center rounded-full"
            style={{ backgroundColor: `var(--severity-${severity})`, opacity: 0.15 }}
          >
            <Icon className="size-5" style={{ color: `var(--severity-${severity})` }} />
          </div>
          <div>
            <p className="text-lg font-semibold">{label}</p>
            <p className="text-muted-foreground text-sm">{className.replace(/_/g, ' ')}</p>
          </div>
        </motion.div>

        <ConfidenceGauge confidence={prediction.confidence} severity={severity} />
      </CardContent>
    </Card>
  )
}
