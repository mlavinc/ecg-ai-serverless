export type ClassName =
  | 'Dangerous_VFL_VF'
  | 'Special_Form_VTTdP'
  | 'Threatening_VT'
  | 'Potential_Dangerous'
  | 'Supraventricular'
  | 'Sinus_rhythm'

export type Severity = 'safe' | 'caution' | 'warning' | 'danger'

export interface Prediction {
  class_id: number
  class_name: ClassName
  confidence: number
  probabilities: Record<string, number>
}

export interface EcgFeatures {
  [key: string]: number
}

export interface EcgSignal {
  sampling_rate: number
  values: number[]
  total_samples: number
}

export interface PredictMeta {
  inference_time_ms: number
  model_version: string
  class_names: string[]
}

export interface PredictResponse {
  prediction: Prediction
  features: EcgFeatures
  signal: EcgSignal
  meta: PredictMeta
}

export interface HealthResponse {
  status: string
  model_loaded: boolean
}

export interface PerClassMetric {
  precision: number
  recall: number
  f1_score: number
  support: number
}

export interface ConfusionMatrix {
  labels: string[]
  matrix: number[][]
}

export interface ModelMetricsResponse {
  model: string
  model_version: string
  dataset: string
  dataset_size: number
  num_classes: number
  num_features: number
  random_state: number
  accuracy: number
  balanced_accuracy: number
  macro_precision: number | null
  macro_recall: number | null
  macro_f1_score: number | null
  per_class: Record<string, PerClassMetric> | null
  class_distribution: Record<string, number>
  confusion_matrix: ConfusionMatrix | null
  note?: string
}

export interface EcgSampleMeta {
  id: string
  label: string
  className: ClassName
  description: string
  file: string
}
