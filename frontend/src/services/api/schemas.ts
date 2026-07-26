import { z } from 'zod'

export const PredictionSchema = z.object({
  class_id: z.number(),
  class_name: z.string(),
  confidence: z.number(),
  probabilities: z.record(z.string(), z.number()),
})

export const PredictResponseSchema = z.object({
  prediction: PredictionSchema,
  features: z.record(z.string(), z.number()),
  signal: z.object({
    sampling_rate: z.number(),
    values: z.array(z.number()),
    total_samples: z.number(),
  }),
  meta: z.object({
    inference_time_ms: z.number(),
    model_version: z.string(),
    class_names: z.array(z.string()),
  }),
})

export const HealthResponseSchema = z.object({
  status: z.string(),
  model_loaded: z.boolean(),
})

export const ModelMetricsResponseSchema = z.object({
  model: z.string().optional(),
  model_version: z.string().optional(),
  dataset: z.string().optional(),
  dataset_size: z.number().optional(),
  num_classes: z.number().optional(),
  num_features: z.number().optional(),
  random_state: z.number().optional(),
  accuracy: z.number().optional(),
  balanced_accuracy: z.number().optional(),
  macro_precision: z.number().nullable().optional(),
  macro_recall: z.number().nullable().optional(),
  macro_f1_score: z.number().nullable().optional(),
  per_class: z
    .record(
      z.string(),
      z.object({
        precision: z.number(),
        recall: z.number(),
        f1_score: z.number(),
        support: z.number(),
      }),
    )
    .nullable()
    .optional(),
  class_distribution: z.record(z.string(), z.number()).optional(),
  confusion_matrix: z
    .object({
      labels: z.array(z.string()),
      matrix: z.array(z.array(z.number())),
    })
    .nullable()
    .optional(),
  note: z.string().optional(),
  available: z.boolean().optional(),
})

export const ApiErrorSchema = z.object({
  error: z.string(),
})
