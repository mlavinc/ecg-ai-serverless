import { useCallback, useState } from 'react'
import { useDropzone, type FileRejection } from 'react-dropzone'
import { FileWarning, UploadCloud } from 'lucide-react'
import { motion } from 'framer-motion'

import { cn } from '@/lib/utils'
import { pairEcgFiles } from '@/utils/file'

interface EcgDropzoneProps {
  onFilesReady: (files: { header: File; signal: File }) => void
  disabled?: boolean
}

export function EcgDropzone({ onFilesReady, disabled }: EcgDropzoneProps) {
  const [error, setError] = useState<string | null>(null)

  const onDrop = useCallback(
    (accepted: File[], rejections: FileRejection[]) => {
      setError(null)

      if (rejections.length > 0) {
        setError('Only .hea and .dat files are supported.')
        return
      }

      const pair = pairEcgFiles(accepted)
      if (!pair) {
        setError('Drop both the .hea (header) and .dat (signal) files together.')
        return
      }

      onFilesReady(pair)
    },
    [onFilesReady],
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    disabled,
    multiple: true,
    accept: {
      'application/octet-stream': ['.dat', '.hea'],
    },
  })

  return (
    <div>
      <div
        {...getRootProps()}
        className={cn(
          'group relative flex flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed p-10 text-center transition-colors',
          isDragActive ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50',
          disabled && 'pointer-events-none opacity-60',
        )}
      >
        <input {...getInputProps()} />
        <motion.div
          animate={isDragActive ? { scale: 1.08 } : { scale: 1 }}
          className="bg-primary/10 text-primary flex size-14 items-center justify-center rounded-full"
        >
          <UploadCloud className="size-6" />
        </motion.div>
        <div>
          <p className="font-medium">
            {isDragActive ? 'Drop the files here' : 'Drag & drop an ECG record'}
          </p>
          <p className="text-muted-foreground mt-1 text-sm">
            WFDB format: select both the <code className="font-mono">.hea</code> and{' '}
            <code className="font-mono">.dat</code> files, or pick a sample below.
          </p>
        </div>
      </div>

      {error && (
        <p className="text-destructive mt-2 flex items-center gap-1.5 text-sm">
          <FileWarning className="size-4" />
          {error}
        </p>
      )}
    </div>
  )
}
