import { Cloud, Cpu, Database, Globe, Zap } from 'lucide-react'
import { motion } from 'framer-motion'

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Separator } from '@/components/ui/separator'

const STEPS = [
  {
    icon: Globe,
    title: 'CloudFront (edge)',
    detail:
      'A single CDN distribution serves the React app from S3 and forwards any request under /api/* to the backend, so the browser only ever talks to one HTTPS domain.',
  },
  {
    icon: Database,
    title: 'Amazon S3 (private)',
    detail:
      'Hosts the compiled frontend. The bucket has no public access; CloudFront reaches it exclusively through an Origin Access Control (OAC).',
  },
  {
    icon: Zap,
    title: 'Lambda Function URL',
    detail:
      "The ECG file (header + signal, base64) is POSTed to /api/predict. The request hits the function's native HTTPS endpoint directly, without API Gateway.",
  },
  {
    icon: Cpu,
    title: 'Feature extraction + Random Forest',
    detail:
      '22 statistical, HRV and frequency-domain features are computed from the signal and fed to a scikit-learn RandomForestClassifier trained on 6 arrhythmia classes.',
  },
  {
    icon: Cloud,
    title: 'JSON response',
    detail:
      'The predicted class, per-class probabilities, extracted features and inference time travel back through the same path to render the results.',
  },
]

export function ArchitectureDrawer() {
  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="sm" className="gap-2">
          <Zap className="size-4" />
          How does this work?
        </Button>
      </SheetTrigger>
      <SheetContent className="w-full overflow-y-auto sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Request lifecycle</SheetTitle>
          <SheetDescription>
            What actually happens between dropping a file and seeing a prediction.
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-1 px-4 pb-4">
          <div className="bg-muted/50 rounded-lg border p-3 font-mono text-xs leading-relaxed">
            <div>CloudFront</div>
            <div className="pl-3">├── S3 (Frontend)</div>
            <div className="pl-3">└── Lambda Function URL</div>
            <div className="pl-6">↓</div>
            <div className="pl-6">Random Forest Model</div>
          </div>

          <Separator className="my-4" />

          <ol className="flex flex-col gap-4">
            {STEPS.map((step, i) => {
              const Icon = step.icon
              return (
                <motion.li
                  key={step.title}
                  initial={{ opacity: 0, x: -8 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.06 }}
                  className="flex gap-3"
                >
                  <div className="bg-primary/10 text-primary flex size-8 shrink-0 items-center justify-center rounded-full">
                    <Icon className="size-4" />
                  </div>
                  <div>
                    <p className="text-sm font-medium">
                      {i + 1}. {step.title}
                    </p>
                    <p className="text-muted-foreground mt-0.5 text-sm">{step.detail}</p>
                  </div>
                </motion.li>
              )
            })}
          </ol>

          <Separator className="my-4" />

          <div className="flex flex-wrap gap-1.5">
            <Badge variant="secondary">No API Gateway</Badge>
            <Badge variant="secondary">Cost: $0 always-free tier</Badge>
            <Badge variant="secondary">Infra as code (Terraform)</Badge>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  )
}
