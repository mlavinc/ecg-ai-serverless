import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion'
import { formatFeatureName } from '@/utils/formatters'
import type { EcgFeatures } from '@/types/ecg'

export function FeaturesAccordion({ features }: { features: EcgFeatures }) {
  return (
    <Accordion type="single" collapsible>
      <AccordionItem value="features">
        <AccordionTrigger className="text-sm">View the 22 extracted features</AccordionTrigger>
        <AccordionContent>
          <div className="grid grid-cols-2 gap-2 sm:grid-cols-3">
            {Object.entries(features).map(([key, value]) => (
              <div key={key} className="bg-muted/50 rounded-md px-2.5 py-1.5">
                <p className="text-muted-foreground text-[11px]">{formatFeatureName(key)}</p>
                <p className="font-mono-tabular text-sm">{value.toFixed(4)}</p>
              </div>
            ))}
          </div>
        </AccordionContent>
      </AccordionItem>
    </Accordion>
  )
}
