import { titleCase } from '@/utils/formatters'
import { cn } from '@/lib/utils'

interface ConfusionMatrixProps {
  labels: string[]
  matrix: number[][]
}

export function ConfusionMatrix({ labels, matrix }: ConfusionMatrixProps) {
  const max = Math.max(...matrix.flat())

  return (
    <div className="overflow-x-auto">
      <table className="border-separate border-spacing-1 text-xs">
        <thead>
          <tr>
            <th className="p-1" />
            {labels.map((label) => (
              <th
                key={label}
                className="text-muted-foreground max-w-16 truncate p-1 text-center font-medium"
                title={titleCase(label)}
              >
                {titleCase(label)}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {matrix.map((row, i) => (
            <tr key={labels[i]}>
              <th className="text-muted-foreground max-w-24 truncate p-1 text-right font-medium" title={titleCase(labels[i])}>
                {titleCase(labels[i])}
              </th>
              {row.map((value, j) => {
                const intensity = max > 0 ? value / max : 0
                const isDiagonal = i === j
                return (
                  <td
                    key={`${i}-${j}`}
                    className={cn(
                      'size-10 rounded-md text-center align-middle font-mono-tabular',
                      isDiagonal ? 'text-primary-foreground' : 'text-foreground',
                    )}
                    style={{
                      backgroundColor: isDiagonal
                        ? `color-mix(in srgb, var(--primary) ${20 + intensity * 80}%, transparent)`
                        : `color-mix(in srgb, var(--error) ${intensity * 55}%, transparent)`,
                    }}
                  >
                    {value}
                  </td>
                )
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
