import type { EcgFeatures, Prediction } from '@/types/ecg'
import { CLASS_LABELS } from '@/utils/constants'
import type { ClassName } from '@/types/ecg'
import { titleCase } from '@/utils/formatters'

/**
 * Produces a short, rule-based explanation of the model's output.
 *
 * This is NOT a clinical interpretation and makes no diagnostic claims. It
 * only describes, in plain language, what the statistical model computed:
 * which class scored highest, how separated it is from the runner-up, and
 * which extracted signal features are numerically consistent with that
 * class (e.g. heart-rate-adjacent RR interval, signal variability).
 */
export function generateAiAnalysis(prediction: Prediction, features: EcgFeatures): string[] {
  const notes: string[] = []

  const sorted = Object.entries(prediction.probabilities).sort((a, b) => b[1] - a[1])
  const [topClass, topProb] = sorted[0]
  const [runnerUpClass, runnerUpProb] = sorted[1] ?? ['', 0]
  const margin = topProb - runnerUpProb

  const className = CLASS_LABELS[topClass as ClassName] ?? titleCase(topClass)
  notes.push(
    `The model assigns the highest probability (${(topProb * 100).toFixed(1)}%) to "${className}".`,
  )

  if (margin > 0.4) {
    notes.push(
      `This is a clear separation from the second-most-likely class (${titleCase(runnerUpClass)}, ${(runnerUpProb * 100).toFixed(1)}%), indicating the extracted features sit well within the region the model associates with this class.`,
    )
  } else if (margin > 0.15) {
    notes.push(
      `The runner-up class (${titleCase(runnerUpClass)}, ${(runnerUpProb * 100).toFixed(1)}%) is moderately close, so this fragment shares some statistical characteristics with both.`,
    )
  } else {
    notes.push(
      `The margin over the runner-up class (${titleCase(runnerUpClass)}, ${(runnerUpProb * 100).toFixed(1)}%) is narrow, so the model is comparatively uncertain between these two classes for this fragment.`,
    )
  }

  if (features.mean_rr > 0) {
    const bpm = 60 / features.mean_rr
    notes.push(
      `Estimated heart rate from detected R-peaks is ~${bpm.toFixed(0)} bpm (mean RR interval ${features.mean_rr.toFixed(2)}s), with an RR variability (RMSSD) of ${features.rmssd.toFixed(3)}s.`,
    )
  } else {
    notes.push(
      'Fewer than two R-peaks were reliably detected in this fragment, so heart-rate-derived features defaulted to zero and carried little weight in this prediction.',
    )
  }

  if (features.spectral_entropy > 0) {
    const complexity = features.spectral_entropy > 6 ? 'high' : features.spectral_entropy > 4 ? 'moderate' : 'low'
    notes.push(
      `Spectral entropy is ${features.spectral_entropy.toFixed(2)} (${complexity} frequency-domain complexity), one of the 22 engineered features driving this classification alongside signal amplitude and waveform shape statistics.`,
    )
  }

  notes.push(
    'This output reflects a statistical pattern learned from a public arrhythmia dataset. It is not a clinical or diagnostic assessment.',
  )

  return notes
}
