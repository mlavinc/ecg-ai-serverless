import { AlertTriangle, GraduationCap, Target } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

const STACK = {
  Frontend: ['React 19', 'TypeScript', 'Vite', 'Tailwind CSS', 'shadcn/ui', 'TanStack Query', 'Framer Motion', 'uPlot', 'Recharts'],
  Backend: ['Python 3.11', 'AWS Lambda', 'scikit-learn', 'NumPy', 'SciPy'],
  Infrastructure: ['Amazon S3', 'CloudFront', 'Lambda Function URLs', 'Terraform', 'IAM'],
}

export function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-4 py-10 sm:px-6">
      <div className="mb-8 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">About this project</h1>
        <p className="text-muted-foreground mt-2 text-sm">
          A portfolio project demonstrating an end-to-end, cost-aware serverless ML pipeline.
        </p>
      </div>

      <div className="flex flex-col gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Target className="size-4" /> Objective
            </CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground text-sm leading-relaxed">
            ECG AI classifies short ECG fragments into six arrhythmia-related rhythm classes using
            a Random Forest model trained on statistical, heart-rate-variability, and
            frequency-domain features. The goal is to showcase practical skills across machine
            learning, frontend architecture, and serverless AWS infrastructure — not to ship a
            production medical tool.
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Technology stack</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            {Object.entries(STACK).map(([group, items]) => (
              <div key={group}>
                <p className="text-muted-foreground mb-2 text-xs font-medium tracking-wide uppercase">{group}</p>
                <div className="flex flex-wrap gap-1.5">
                  {items.map((item) => (
                    <Badge key={item} variant="secondary">
                      {item}
                    </Badge>
                  ))}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <GraduationCap className="size-4" /> Dataset
            </CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground text-sm leading-relaxed">
            PhysioNet ECG Fragment Database for Dangerous Arrhythmia (2022) — 1,016 labeled
            single-lead ECG fragments across 6 classes. Used strictly for educational and research
            purposes.
          </CardContent>
        </Card>

        <Card className="border-severity-warning/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <AlertTriangle className="text-severity-warning size-4" /> Limitations
            </CardTitle>
          </CardHeader>
          <CardContent className="text-muted-foreground flex flex-col gap-2 text-sm leading-relaxed">
            <p>
              This is <strong>not a medical device</strong> and makes no clinical or diagnostic
              claims. It is trained on a small, public research dataset (1,016 fragments) and its
              accuracy (~77%) reflects that scale.
            </p>
            <p>
              Sample ECGs bundled with the demo are synthetic, generated to illustrate each class
              visually — they are not real patient recordings.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
