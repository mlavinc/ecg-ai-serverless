import { createBrowserRouter } from 'react-router-dom'

import { Layout } from '@/components/layout/Layout'
import { AnalyzePage } from '@/pages/Analyze/AnalyzePage'
import { ModelPerformancePage } from '@/pages/ModelPerformance/ModelPerformancePage'
import { HowItWorksPage } from '@/pages/HowItWorks/HowItWorksPage'
import { AboutPage } from '@/pages/About/AboutPage'

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <AnalyzePage /> },
      { path: 'performance', element: <ModelPerformancePage /> },
      { path: 'how-it-works', element: <HowItWorksPage /> },
      { path: 'about', element: <AboutPage /> },
    ],
  },
])
