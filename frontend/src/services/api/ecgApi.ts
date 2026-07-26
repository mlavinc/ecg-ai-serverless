import { apiClient } from './client'
import {
  HealthResponseSchema,
  ModelMetricsResponseSchema,
  PredictResponseSchema,
} from './schemas'
import type { HealthResponse, ModelMetricsResponse, PredictResponse } from '@/types/ecg'

export interface PredictPayload {
  header: string // base64-encoded .hea file contents
  signal: string // base64-encoded .dat file contents
}

export async function predictEcg(payload: PredictPayload): Promise<PredictResponse> {
  const { data } = await apiClient.post('/predict', payload)
  return PredictResponseSchema.parse(data) as PredictResponse
}

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await apiClient.get('/health')
  return HealthResponseSchema.parse(data)
}

export async function getModelMetrics(): Promise<ModelMetricsResponse> {
  const { data } = await apiClient.get('/metrics')
  return ModelMetricsResponseSchema.parse(data) as ModelMetricsResponse
}
