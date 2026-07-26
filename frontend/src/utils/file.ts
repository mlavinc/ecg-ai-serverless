export function fileToBase64(file: File | Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => {
      const result = reader.result as string
      // Strip the "data:...;base64," prefix added by readAsDataURL.
      const base64 = result.split(',', 2)[1] ?? ''
      resolve(base64)
    }
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export async function urlToBase64(url: string): Promise<string> {
  const response = await fetch(url)
  if (!response.ok) {
    throw new Error(`Could not fetch sample file: ${url}`)
  }
  const blob = await response.blob()
  return fileToBase64(blob)
}

/** Pairs dropped files into { header, signal } by matching basenames. */
export function pairEcgFiles(files: File[]): { header: File; signal: File } | null {
  const hea = files.find((f) => f.name.toLowerCase().endsWith('.hea'))
  const dat = files.find((f) => f.name.toLowerCase().endsWith('.dat'))
  if (!hea || !dat) return null
  return { header: hea, signal: dat }
}
