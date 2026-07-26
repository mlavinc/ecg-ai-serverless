import type { ClassName, Severity } from '@/types/ecg'

export const CLASS_LABELS: Record<ClassName, string> = {
  Dangerous_VFL_VF: 'Ventricular Fibrillation / Flutter',
  Special_Form_VTTdP: 'Torsade de Pointes (VT)',
  Threatening_VT: 'Threatening Ventricular Tachycardia',
  Potential_Dangerous: 'Potentially Dangerous Rhythm',
  Supraventricular: 'Supraventricular Arrhythmia',
  Sinus_rhythm: 'Normal Sinus Rhythm',
}

export const CLASS_SEVERITY: Record<ClassName, Severity> = {
  Dangerous_VFL_VF: 'danger',
  Special_Form_VTTdP: 'danger',
  Threatening_VT: 'warning',
  Potential_Dangerous: 'caution',
  Supraventricular: 'caution',
  Sinus_rhythm: 'safe',
}

export const SEVERITY_LABEL: Record<Severity, string> = {
  safe: 'Low concern',
  caution: 'Caution',
  warning: 'Elevated concern',
  danger: 'High concern',
}

export const CLASS_ORDER: ClassName[] = [
  'Dangerous_VFL_VF',
  'Special_Form_VTTdP',
  'Threatening_VT',
  'Potential_Dangerous',
  'Supraventricular',
  'Sinus_rhythm',
]
