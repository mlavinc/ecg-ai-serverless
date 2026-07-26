import { Code2 } from 'lucide-react'

import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import type { PredictResponse } from '@/types/ecg'

export function RawResponseDialog({ response }: { response: PredictResponse }) {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm" className="gap-1.5 text-xs">
          <Code2 className="size-3.5" />
          View raw JSON response
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Raw API response</DialogTitle>
        </DialogHeader>
        <pre className="bg-muted max-h-[60vh] overflow-auto rounded-lg p-4 text-xs">
          {JSON.stringify(
            { ...response, signal: { ...response.signal, values: '[...omitted for brevity...]' } },
            null,
            2,
          )}
        </pre>
      </DialogContent>
    </Dialog>
  )
}
