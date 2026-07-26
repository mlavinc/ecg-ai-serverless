import axios from 'axios'

// In production, CloudFront serves the frontend and proxies /api/* to the
// Lambda Function URL under the SAME domain (see infra/cloudfront.tf), so
// the default of a relative "/api" base URL requires no CORS handling.
// VITE_API_BASE_URL can override this for local development against a
// standalone Function URL.
const baseURL = import.meta.env.VITE_API_BASE_URL || '/api'

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
