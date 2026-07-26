import { useEffect, useRef } from 'react'
import uPlot from 'uplot'
import 'uplot/dist/uPlot.min.css'

import { useTheme } from '@/hooks/useTheme'

interface EcgSignalChartProps {
  values: number[]
  samplingRate: number
  height?: number
}

/**
 * Renders the ECG waveform with uPlot: a canvas-based charting library
 * chosen specifically for its performance on dense time series (thousands
 * of points redraw smoothly, unlike SVG-based chart libraries).
 */
export function EcgSignalChart({ values, samplingRate, height = 260 }: EcgSignalChartProps) {
  const containerRef = useRef<HTMLDivElement>(null)
  const plotRef = useRef<uPlot | null>(null)
  const { theme } = useTheme()

  useEffect(() => {
    if (!containerRef.current) return

    const time = values.map((_, i) => i / samplingRate)
    const isDark = theme === 'dark'
    const lineColor = isDark ? '#e3a98d' : '#cc7a58'
    const gridColor = isDark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.05)'
    const textColor = isDark ? '#b8ae9f' : '#9a8f80'

    const opts: uPlot.Options = {
      width: containerRef.current.clientWidth,
      height,
      padding: [12, 12, 0, 8],
      cursor: { drag: { x: true, y: false } },
      scales: { x: { time: false } },
      axes: [
        {
          stroke: textColor,
          grid: { stroke: gridColor },
          values: (_u, splits) => splits.map((s) => `${s.toFixed(1)}s`),
        },
        {
          stroke: textColor,
          grid: { stroke: gridColor },
          values: (_u, splits) => splits.map((s) => s.toFixed(2)),
        },
      ],
      series: [
        {},
        {
          label: 'mV',
          stroke: lineColor,
          width: 1.5,
          points: { show: false },
        },
      ],
      legend: { show: false },
    }

    const plot = new uPlot(opts, [time, values], containerRef.current)
    plotRef.current = plot

    const onResize = () => {
      if (containerRef.current) {
        plot.setSize({ width: containerRef.current.clientWidth, height })
      }
    }
    window.addEventListener('resize', onResize)

    return () => {
      window.removeEventListener('resize', onResize)
      plot.destroy()
      plotRef.current = null
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [values, samplingRate, theme, height])

  return <div ref={containerRef} className="w-full" />
}
