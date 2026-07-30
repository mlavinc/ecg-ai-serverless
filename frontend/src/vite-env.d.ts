/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API base URL (Lambda Function URL or CloudFront `/api` origin). */
  readonly VITE_API_URL?: string
  /** @deprecated Prefer VITE_API_URL. Kept for local overrides. */
  readonly VITE_API_BASE_URL?: string
  readonly VITE_DEV_API_PROXY_TARGET?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
