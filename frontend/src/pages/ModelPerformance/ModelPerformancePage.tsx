import { BarChart3, Database, Layers, Target } from 'lucide-react'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import { Badge } from '@/components/ui/badge'
import { ConfusionMatrix } from '@/components/charts/ConfusionMatrix'
import { useModelMetrics } from '@/features/model-metrics/useModelMetrics'
import { formatPercent, titleCase } from '@/utils/formatters'
import { CLASS_SEVERITY } from '@/utils/constants'
import type { ClassName } from '@/types/ecg'

const SEVERITY_COLOR: Record<string, string> = {
  safe: 'var(--severity-safe)',
  caution: 'var(--severity-caution)',
  warning: 'var(--severity-warning)',
  danger: 'var(--severity-danger)',
}

function MetricCard({ icon: Icon, label, value }: { icon: typeof Target; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 py-4">
        <div className="bg-primary/10 text-primary flex size-9 items-center justify-center rounded-full">
          <Icon className="size-4" />
        </div>
        <div>
          <p className="font-mono-tabular text-xl font-semibold">{value}</p>
          <p className="text-muted-foreground text-xs">{label}</p>
        </div>
      </CardContent>
    </Card>
  )
}

export function ModelPerformancePage() {
  const { data: metrics, isLoading, isError } = useModelMetrics()

  const distributionData = metrics
    ? Object.entries(metrics.class_distribution).map(([name, count]) => ({
        name: titleCase(name),
        value: count,
        severity: CLASS_SEVERITY[name as ClassName] ?? 'caution',
      }))
    : []

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      <div className="mb-8">
        <h1 className="text-2xl font-semibold tracking-tight">Model Performance</h1>
        <p className="text-muted-foreground mt-1 text-sm">
          Evaluation metrics for the Random Forest classifier, computed on a held-out test split.
        </p>
      </div>

      {isLoading && (
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20" />
          ))}
        </div>
      )}

      {isError && (
        <Card className="border-destructive/40">
          <CardContent className="py-6 text-sm">Could not load model metrics from the API.</CardContent>
        </Card>
      )}

      {metrics && (
        <div className="flex flex-col gap-6">
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
            <MetricCard icon={Target} label="Accuracy" value={formatPercent(metrics.accuracy ?? 0)} />
            <MetricCard
              icon={BarChart3}
              label="Balanced Accuracy"
              value={formatPercent(metrics.balanced_accuracy ?? 0)}
            />
            <MetricCard
              icon={Layers}
              label="Macro F1-score"
              value={metrics.macro_f1_score != null ? formatPercent(metrics.macro_f1_score) : '—'}
            />
            <MetricCard icon={Database} label="Dataset size" value={String(metrics.dataset_size ?? '—')} />
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Class distribution</CardTitle>
                <CardDescription>{metrics.dataset}</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={260}>
                  <PieChart>
                    <Pie
                      data={distributionData}
                      dataKey="value"
                      nameKey="name"
                      innerRadius={55}
                      outerRadius={90}
                      paddingAngle={2}
                    >
                      {distributionData.map((entry) => (
                        <Cell key={entry.name} fill={SEVERITY_COLOR[entry.severity]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend wrapperStyle={{ fontSize: 12 }} />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Per-class metrics</CardTitle>
                <CardDescription>Precision / Recall / F1-score</CardDescription>
              </CardHeader>
              <CardContent>
                {metrics.per_class ? (
                  <div className="flex flex-col gap-2 text-sm">
                    {Object.entries(metrics.per_class).map(([name, m]) => (
                      <div key={name} className="flex items-center justify-between border-b py-1.5 last:border-0">
                        <span className="text-muted-foreground">{titleCase(name)}</span>
                        <span className="font-mono-tabular">
                          P {m.precision.toFixed(2)} · R {m.recall.toFixed(2)} · F1 {m.f1_score.toFixed(2)}
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-muted-foreground text-sm">
                    Not available yet &mdash; per-class precision/recall/F1 are generated by re-running{' '}
                    <code className="font-mono">scripts/train_model.py</code> with the full dataset present.
                  </p>
                )}
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Confusion matrix</CardTitle>
              <CardDescription>Rows: actual class · Columns: predicted class</CardDescription>
            </CardHeader>
            <CardContent>
              {metrics.confusion_matrix ? (
                <ConfusionMatrix
                  labels={metrics.confusion_matrix.labels}
                  matrix={metrics.confusion_matrix.matrix}
                />
              ) : (
                <p className="text-muted-foreground text-sm">
                  Not available yet &mdash; the raw PhysioNet dataset is not bundled in this repository.
                  {metrics.note && <span className="mt-1 block italic">{metrics.note}</span>}
                </p>
              )}
            </CardContent>
          </Card>

          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">Model: {metrics.model}</Badge>
            <Badge variant="outline">Version: {metrics.model_version}</Badge>
            <Badge variant="outline">Features: {metrics.num_features}</Badge>
            <Badge variant="outline">Classes: {metrics.num_classes}</Badge>
          </div>
        </div>
      )}
    </div>
  )
}
