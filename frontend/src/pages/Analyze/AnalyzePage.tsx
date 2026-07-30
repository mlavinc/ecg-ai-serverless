import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, HeartPulse } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { EcgDropzone } from '@/features/ecg-upload/EcgDropzone'
import { SamplePicker } from '@/features/ecg-upload/SamplePicker'
import { usePredictEcg } from '@/features/ecg-classification/usePredictEcg'
import { LoadingPipeline } from '@/features/ecg-classification/LoadingPipeline'
import { ResultCard } from '@/features/ecg-classification/ResultCard'
import { AiAnalysisPanel } from '@/features/ecg-classification/AiAnalysisPanel'
import { InferenceMetaPanel } from '@/features/ecg-classification/InferenceMetaPanel'
import { FeaturesAccordion } from '@/features/ecg-classification/FeaturesAccordion'
import { RawResponseDialog } from '@/features/ecg-classification/RawResponseDialog'
import { EcgSignalChart } from '@/components/charts/EcgSignalChart'
import { ProbabilityBarChart } from '@/components/charts/ProbabilityBarChart'
import { ArchitectureDrawer } from '@/components/layout/ArchitectureDrawer'
import { fileToBase64 } from '@/utils/file'
import { ApiRequestError } from '@/services/api/client'

export function AnalyzePage() {
  const { mutate, data, isPending, isError, error, reset } = usePredictEcg()
  const [activeSampleId, setActiveSampleId] = useState<string | null>(null)

  async function runPrediction(header: string, signal: string, sampleId: string | null) {
    setActiveSampleId(sampleId)
    mutate({ header, signal })
  }

  async function handleFiles({ header, signal }: { header: File; signal: File }) {
    const [headerB64, signalB64] = await Promise.all([fileToBase64(header), fileToBase64(signal)])
    runPrediction(headerB64, signalB64, null)
  }

  async function handleSampleSelect(sampleFile: string) {
    const res = await fetch(`/samples/${sampleFile}`)
    const payload = await res.json()
    runPrediction(payload.header, payload.signal, sampleFile)
  }

  const errorMessage = error instanceof ApiRequestError ? error.message : 'Something went wrong.'

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
      {/* Hero */}
      <section className="mb-10 flex flex-col items-center gap-4 text-center">
        <Badge variant="outline" className="gap-1.5">
          <HeartPulse className="size-3" />
          Not for clinical use
        </Badge>
        <h1 className="max-w-2xl text-3xl font-semibold tracking-tight sm:text-4xl">
          ECG arrhythmia classification on a serverless AWS pipeline
        </h1>
        <p className="text-muted-foreground max-w-xl text-sm sm:text-base">
          Upload an ECG record or try a sample. A Random Forest model on AWS Lambda
          classifies the signal into one of six rhythm classes.
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          <ArchitectureDrawer />
          <Button variant="ghost" size="sm" className="gap-2" asChild>
            <a href="https://github.com" target="_blank" rel="noreferrer">
              View source
            </a>
          </Button>
        </div>
      </section>

      {/* Upload zone */}
      <section className="mb-8 flex flex-col gap-4">
        <EcgDropzone onFilesReady={handleFiles} disabled={isPending} />
        <SamplePicker onSelect={handleSampleSelect} disabled={isPending} activeSampleId={activeSampleId} />
      </section>

      {/* States */}
      <AnimatePresence mode="wait">
        {isPending && (
          <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Card>
              <CardContent className="py-8">
                <LoadingPipeline />
              </CardContent>
            </Card>
          </motion.div>
        )}

        {isError && !isPending && (
          <motion.div key="error" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Card className="border-destructive/40">
              <CardContent className="flex items-start gap-3 py-6">
                <AlertCircle className="text-destructive mt-0.5 size-5 shrink-0" />
                <div>
                  <p className="font-medium">Could not analyze this record</p>
                  <p className="text-muted-foreground mt-1 text-sm">{errorMessage}</p>
                  <Button variant="outline" size="sm" className="mt-3" onClick={() => reset()}>
                    Try again
                  </Button>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {data && !isPending && (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex flex-col gap-6"
          >
            <Card>
              <CardHeader>
                <CardTitle className="text-base">ECG signal</CardTitle>
              </CardHeader>
              <CardContent>
                <EcgSignalChart values={data.signal.values} samplingRate={data.signal.sampling_rate} />
                <p className="text-muted-foreground mt-2 text-xs">
                  {data.signal.total_samples} samples at {data.signal.sampling_rate} Hz
                  {data.signal.total_samples !== data.signal.values.length &&
                    ` (downsampled to ${data.signal.values.length} points for display)`}
                  .
                </p>
              </CardContent>
            </Card>

            <div className="grid gap-6 lg:grid-cols-2">
              <ResultCard prediction={data.prediction} />
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Probabilities by class</CardTitle>
                </CardHeader>
                <CardContent>
                  <ProbabilityBarChart probabilities={data.prediction.probabilities} />
                </CardContent>
              </Card>
            </div>

            <div className="grid gap-6 lg:grid-cols-2">
              <AiAnalysisPanel prediction={data.prediction} features={data.features} />
              <div className="flex flex-col gap-6">
                <InferenceMetaPanel meta={data.meta} />
                <Card>
                  <CardContent className="flex flex-col gap-3 py-4">
                    <FeaturesAccordion features={data.features} />
                    <RawResponseDialog response={data} />
                  </CardContent>
                </Card>
              </div>
            </div>
          </motion.div>
        )}

        {!data && !isPending && !isError && (
          <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            <Card className="border-dashed">
              <CardContent className="text-muted-foreground py-10 text-center text-sm">
                Results will appear here once you drop a record or pick a sample above.
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
