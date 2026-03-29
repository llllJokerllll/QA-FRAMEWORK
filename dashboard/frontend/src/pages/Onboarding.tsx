import { useNavigate } from 'react-router-dom'
import { OnboardingWizard } from '../components/OnboardingWizard'

export default function Onboarding() {
  const navigate = useNavigate()

  const handleComplete = () => {
    navigate('/dashboard', { replace: true })
  }

  return <OnboardingWizard onComplete={handleComplete} />
}
