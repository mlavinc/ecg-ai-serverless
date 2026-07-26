import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'

import { CLASS_SEVERITY } from '@/utils/constants'
import type { ClassName } from '@/types/ecg'
import { formatPercent, titleCase } from '@/utils/formatters'

interface ProbabilityBarChartProps {
  probabilities: Record<string, number>
}

const SEVERITY_COLOR: Record<string, string> = {
  safe: 'var(--severity-safe)',
  caution: 'var(--severity-caution)',
  warning: 'var(--severity-warning)',
  danger: 'var(--severity-danger)',
}

export function ProbabilityBarChart({ probabilities }: ProbabilityBarChartProps) {
  const data = Object.entries(probabilities)
    .map(([name, value]) => ({
      name: titleCase(name),
      value: Number((value * 100).toFixed(1)),
      severity: CLASS_SEVERITY[name as ClassName] ?? 'caution',
    }))
    .sort((a, b) => b.value - a.value)

  return (
    <ResponsiveContainer width="100%" height={220}>
      <BarChart data={data} layout="vertical" margin={{ left: 8, right: 24 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} className="stroke-border" />
        <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} fontSize={12} />
        <YAxis type="category" dataKey="name" width={150} fontSize={12} />
        <Tooltip
          formatter={(value) => formatPercent(Number(value) / 100)}
          contentStyle={{ fontSize: 13, borderRadius: 8 }}
        />
        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
          {data.map((entry) => (
            <Cell key={entry.name} fill={SEVERITY_COLOR[entry.severity]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
