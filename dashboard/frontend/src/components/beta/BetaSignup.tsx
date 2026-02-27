import { useState } from 'react'
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  MenuItem,
  Stepper,
  Step,
  StepLabel,
  CircularProgress,
} from '@mui/material'
import {
  CheckCircle as CheckIcon,
  Email as EmailIcon,
} from '@mui/icons-material'
import { useMutation } from 'react-query'
import { betaAPI } from '../api/client'
import toast from 'react-hot-toast'

type TeamSize = '1-5' | '6-20' | '21-50' | '50+'

interface BetaSignupFormData {
  email: string
  company: string
  use_case: string
  team_size: TeamSize | ''
}

const TEAM_SIZES = [
  { value: '1-5', label: '1-5 people' },
  { value: '6-20', label: '6-20 people' },
  { value: '21-50', label: '21-50 people' },
  { value: '50+', label: '50+ people' },
]

const STEPS = ['Your Info', 'About Your Team', 'Confirm']

interface BetaSignupProps {
  source?: string
  onSuccess?: () => void
  compact?: boolean
}

export default function BetaSignup({ source, onSuccess, compact = false }: BetaSignupProps) {
  const [activeStep, setActiveStep] = useState(0)
  const [submitted, setSubmitted] = useState(false)
  const [formData, setFormData] = useState<BetaSignupFormData>({
    email: '',
    company: '',
    use_case: '',
    team_size: '',
  })

  const signupMutation = useMutation(
    () => betaAPI.signup({
      ...formData,
      source: source || 'landing_page',
    }),
    {
      onSuccess: () => {
        setSubmitted(true)
        toast.success('Successfully registered for beta!')
        onSuccess?.()
      },
      onError: (error: any) => {
        if (error.response?.status === 409) {
          toast.error('This email is already registered for beta')
        } else {
          toast.error(error.response?.data?.detail || 'Failed to sign up')
        }
      },
    }
  )

  const handleNext = () => {
    if (activeStep === 0 && !formData.email) {
      toast.error('Please enter your email')
      return
    }
    if (activeStep === 1 && !formData.use_case) {
      toast.error('Please tell us about your use case')
      return
    }
    setActiveStep((prev) => prev + 1)
  }

  const handleBack = () => {
    setActiveStep((prev) => prev - 1)
  }

  const handleSubmit = () => {
    signupMutation.mutate()
  }

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              required
              type="email"
              label="Email Address"
              placeholder="you@company.com"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              helperText="We'll send your beta invite here"
            />
            <TextField
              fullWidth
              label="Company Name (Optional)"
              placeholder="Acme Inc."
              value={formData.company}
              onChange={(e) => setFormData({ ...formData, company: e.target.value })}
            />
          </Box>
        )

      case 1:
        return (
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              fullWidth
              required
              multiline
              rows={4}
              label="What do you want to use QA-FRAMEWORK for?"
              placeholder="E.g., Automated testing for our CI/CD pipeline, reducing flaky tests, etc."
              value={formData.use_case}
              onChange={(e) => setFormData({ ...formData, use_case: e.target.value })}
            />
            <TextField
              select
              fullWidth
              label="Team Size"
              value={formData.team_size}
              onChange={(e) => setFormData({ ...formData, team_size: e.target.value as TeamSize })}
            >
              {TEAM_SIZES.map((size) => (
                <MenuItem key={size.value} value={size.value}>
                  {size.label}
                </MenuItem>
              ))}
            </TextField>
          </Box>
        )

      case 2:
        return (
          <Box sx={{ textAlign: 'center', py: 2 }}>
            <Typography variant="h6" gutterBottom>
              Review Your Information
            </Typography>
            <Box sx={{ textAlign: 'left', bgcolor: 'grey.100', p: 2, borderRadius: 1, mb: 2 }}>
              <Typography variant="body2" color="textSecondary">
                Email: <strong>{formData.email}</strong>
              </Typography>
              {formData.company && (
                <Typography variant="body2" color="textSecondary">
                  Company: <strong>{formData.company}</strong>
                </Typography>
              )}
              <Typography variant="body2" color="textSecondary">
                Team Size: <strong>{formData.team_size || 'Not specified'}</strong>
              </Typography>
              <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
                Use Case:
              </Typography>
              <Typography variant="body2">{formData.use_case}</Typography>
            </Box>
            <Typography variant="body2" color="textSecondary">
              By signing up, you agree to receive updates about the beta program.
              We'll never spam you or share your email.
            </Typography>
          </Box>
        )

      default:
        return null
    }
  }

  if (submitted) {
    return (
      <Card sx={{ width: '100%', textAlign: 'center' }}>
        <CardContent sx={{ py: 4 }}>
          <CheckIcon sx={{ fontSize: 64, color: 'success.main', mb: 2 }} />
          <Typography variant="h5" gutterBottom>
            You're on the list!
          </Typography>
          <Typography variant="body1" color="textSecondary" sx={{ mb: 2 }}>
            We've sent a confirmation email to <strong>{formData.email}</strong>
          </Typography>
          <Typography variant="body2" color="textSecondary">
            We'll be in touch soon with your beta access details.
          </Typography>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card sx={{ width: '100%' }}>
      <CardContent>
        {!compact && (
          <>
            <Typography variant="h5" gutterBottom align="center">
              Join the Beta Program
            </Typography>
            <Typography variant="body2" color="textSecondary" align="center" sx={{ mb: 3 }}>
              Get early access to QA-FRAMEWORK and help shape the future of testing
            </Typography>
          </>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 3 }}>
          {STEPS.map((label) => (
            <Step key={label}>
              <StepLabel>{compact ? '' : label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {renderStepContent(activeStep)}

        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>
          
          {activeStep === STEPS.length - 1 ? (
            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={signupMutation.isLoading}
              startIcon={signupMutation.isLoading ? <CircularProgress size={20} /> : <EmailIcon />}
            >
              {signupMutation.isLoading ? 'Signing up...' : 'Sign Up for Beta'}
            </Button>
          ) : (
            <Button
              variant="contained"
              color="primary"
              onClick={handleNext}
            >
              Next
            </Button>
          )}
        </Box>

        {signupMutation.isError && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {signupMutation.error?.response?.data?.detail || 'Failed to sign up. Please try again.'}
          </Alert>
        )}
      </CardContent>
    </Card>
  )
}
