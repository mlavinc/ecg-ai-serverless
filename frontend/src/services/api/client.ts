import axios from 'axios'

/**
 * API base URL resolution:
 * - VITE_API_URL: preferred (Vercel / standalone Function URL)
 * - VITE_API_BASE_URL: legacy alias
 * - default `/api`: same-origin CloudFront proxy in AWS deploy
 */
function resolveApiBaseUrl(): string {
  const raw =
    import.meta.env.VITE_API_URL ||
    import.meta.env.VITE_API_BASE_URL ||
    '/api'
  return String(raw).replace(/\/$/, '')
}

const baseURL = resolveApiBaseUrl()

export const apiClient = axios.create({
  baseURL,
  timeout: 20_000,
})

export class ApiRequestError extends Error {
  status?: number

  constructor(message: string, status?: number) {
    super(message)
    this.name = 'ApiRequestError'
    this.status = status
  }
}

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status
    const message = error?.response?.data?.error || error.message || 'Unexpected network error.'
    return Promise.reject(new ApiRequestError(message, status))
  },
)
