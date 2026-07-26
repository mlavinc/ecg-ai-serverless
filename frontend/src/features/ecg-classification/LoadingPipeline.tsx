import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { Check, Loader2 } from 'lucide-react'

const STEPS = [
  'Reading ECG signal',
  'Extracting 22 features (statistical, HRV, spectral)',
  'Running Random Forest inference',
  'Preparing results',
]

export function LoadingPipeline() {
  const [activeStep, setActiveStep] = useState(0)

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((s) => Math.min(s + 1, STEPS.length - 1))
    }, 550)
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex flex-col gap-3 py-2">
      {STEPS.map((step, i) => {
        const done = i < activeStep
        const active = i === activeStep
        return (
          <motion.div
            key={step}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            className="flex items-center gap-3 text-sm"
          >
            <span
              className={
                done
                  ? 'flex size-5 items-center justify-center rounded-full bg-severity-safe/20 text-severity-safe'
                  : active
                    ? 'flex size-5 items-center justify-center rounded-full bg-primary/15 text-primary'
                    : 'flex size-5 items-center justify-center rounded-full bg-muted text-muted-foreground'
              }
            >
              {done ? <Check className="size-3" /> : active ? <Loader2 className="size-3 animate-spin" /> : null}
            </span>
            <span className={done || active ? 'text-foreground' : 'text-muted-foreground'}>{step}</span>
          </motion.div>
        )
      })}
    </div>
  )
}
