import { motion } from 'framer-motion'
import { Info, Sparkles } from 'lucide-react'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { generateAiAnalysis } from '@/features/ecg-classification/generateAiAnalysis'
import type { EcgFeatures, Prediction } from '@/types/ecg'

export function AiAnalysisPanel({
  prediction,
  features,
}: {
  prediction: Prediction
  features: EcgFeatures
}) {
  const notes = generateAiAnalysis(prediction, features)

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Sparkles className="text-primary size-4" />
          Model interpretation
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col gap-3">
        <ul className="flex flex-col gap-2.5">
          {notes.map((note, i) => (
            <motion.li
              key={i}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              className="text-sm leading-relaxed"
            >
              {note}
            </motion.li>
          ))}
        </ul>

        <div className="bg-muted/60 mt-1 flex items-start gap-2 rounded-lg p-3 text-xs">
          <Info className="text-muted-foreground mt-0.5 size-3.5 shrink-0" />
          <p className="text-muted-foreground">
            Generated from the model output (probabilities and extracted features). This
            summarizes what the classifier computed. Not a clinical or diagnostic tool.
          </p>
        </div>
      </CardContent>
    </Card>
  )
}
