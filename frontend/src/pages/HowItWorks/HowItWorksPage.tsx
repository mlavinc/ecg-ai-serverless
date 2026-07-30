import { motion } from 'framer-motion'
import { Cloud, Cpu, Database, FileJson, Globe, Zap } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'

const PIPELINE = [
  {
    icon: Globe,
    title: 'Browser → CloudFront',
    description:
      'The React SPA (built with Vite) is loaded from a single CloudFront distribution, which is the only domain the browser ever contacts.',
  },
  {
    icon: Database,
    title: 'CloudFront → S3 (static assets)',
    description:
      'Requests for the app shell and assets are served from a private S3 bucket, reachable only via an Origin Access Control (OAC). The bucket is never public.',
  },
  {
    icon: Zap,
    title: 'CloudFront /api/* → Lambda Function URL',
    description:
      'Requests to /api/* are routed to a Lambda Function URL as a second CloudFront origin behavior. Skipping API Gateway keeps the stack inside AWS always-free tier limits.',
  },
  {
    icon: FileJson,
    title: 'Lambda: parse + extract features',
    description:
      'The function decodes the base64 WFDB header/signal, reconstructs the physical ECG signal, and computes 22 statistical, HRV and frequency-domain features.',
  },
  {
    icon: Cpu,
    title: 'Random Forest inference',
    description:
      'A scikit-learn RandomForestClassifier (trained on the PhysioNet ECG Fragment Database) scores the feature vector across 6 arrhythmia classes.',
  },
  {
    icon: Cloud,
    title: 'JSON response → UI',
    description:
      'Prediction, per-class probabilities, features and timing metadata are returned as JSON and rendered with live charts on the Analyze page.',
  },
]

const FAQ = [
  {
    q: 'Why no API Gateway?',
    a: 'Lambda Function URLs provide a direct HTTPS endpoint with zero extra cost beyond the Lambda invocation itself. API Gateway free tier only lasts 12 months on new accounts; Function URLs plus CloudFront/Lambda\'s always-free tiers keep this project at $0 indefinitely. API Gateway would be reintroduced if this needed request throttling, usage plans, or multiple downstream integrations.',
  },
  {
    q: 'Where does the model live?',
    a: 'The trained joblib model is stored in S3 and downloaded once into the Lambda\'s /tmp cache on a cold start, then reused across warm invocations.',
  },
  {
    q: 'Is this a medical device?',
    a: 'No. This is a technical portfolio project for an end-to-end ML and serverless pipeline. It makes no clinical or diagnostic claims.',
  },
  {
    q: 'How is the infrastructure deployed?',
    a: 'Everything (S3, OAC, CloudFront, Lambda, IAM) is defined in Terraform, so the stack can be created with `terraform apply` and torn down with `terraform destroy`.',
  },
]

export function HowItWorksPage() {
  return (
    <div className="mx-auto max-w-4xl px-4 py-10 sm:px-6">
      <div className="mb-8 text-center">
        <Badge variant="outline" className="mb-3">
          Architecture
        </Badge>
        <h1 className="text-2xl font-semibold tracking-tight">How It Works</h1>
        <p className="text-muted-foreground mx-auto mt-2 max-w-xl text-sm">
          A serverless pipeline with no idle servers and infrastructure that can be
          destroyed and rebuilt on demand.
        </p>
      </div>

      <Card className="mb-8">
        <CardContent className="py-6">
          <pre className="overflow-x-auto text-center font-mono text-xs sm:text-sm">
{`CloudFront
├── S3 (Frontend)
└── Lambda Function URL
        ↓
Random Forest Model`}
          </pre>
        </CardContent>
      </Card>

      <div className="mb-10 flex flex-col gap-4">
        {PIPELINE.map((step, i) => {
          const Icon = step.icon
          return (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: '-40px' }}
              transition={{ delay: i * 0.05 }}
            >
              <Card>
                <CardContent className="flex gap-4 py-5">
                  <div className="bg-primary/10 text-primary flex size-10 shrink-0 items-center justify-center rounded-full font-semibold">
                    <Icon className="size-5" />
                  </div>
                  <div>
                    <p className="flex items-center gap-2 font-medium">
                      <span className="text-muted-foreground text-xs">{i + 1}</span>
                      {step.title}
                    </p>
                    <p className="text-muted-foreground mt-1 text-sm leading-relaxed">{step.description}</p>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">FAQ</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible>
            {FAQ.map((item) => (
              <AccordionItem key={item.q} value={item.q}>
                <AccordionTrigger>{item.q}</AccordionTrigger>
                <AccordionContent className="text-muted-foreground">{item.a}</AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  )
}
