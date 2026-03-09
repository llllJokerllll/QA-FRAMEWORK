"""
Onboarding Wizard - Multi-step onboarding flow

Steps:
1. Welcome + video demo
2. Connect GitHub repo
3. Create first test suite
4. Run first test
5. Setup notifications
"""

import React, { useState } from 'react';
import {
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Box,
  Card,
  CardContent
} from '@mui/material';

const steps = [
  'Welcome',
  'Connect Repository',
  'Create Test Suite',
  'Run First Test',
  'Setup Notifications'
];

interface OnboardingWizardProps {
  onComplete: () => void;
}

export const OnboardingWizard: React.FC<OnboardingWizardProps> = ({ onComplete }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [completed, setCompleted] = useState<{ [k: number]: boolean }>({});

  const handleNext = () => {
    const newCompleted = completed;
    newCompleted[activeStep] = true;
    setCompleted(newCompleted);
    setActiveStep((prev) => prev + 1);
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const handleComplete = () => {
    handleNext();
    onComplete();
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return <WelcomeStep />;
      case 1:
        return <ConnectRepoStep />;
      case 2:
        return <CreateTestSuiteStep />;
      case 3:
        return <RunFirstTestStep />;
      case 4:
        return <SetupNotificationsStep />;
      default:
        return null;
    }
  };

  return (
    <Card sx={{ maxWidth: 800, mx: 'auto', mt: 4 }}>
      <CardContent>
        <Stepper activeStep={activeStep}>
          {steps.map((label, index) => (
            <Step key={label} completed={completed[index]}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mt: 4, mb: 2 }}>
          {activeStep === steps.length ? (
            <Box>
              <Typography variant="h5" gutterBottom>
                🎉 Onboarding Complete!
              </Typography>
              <Typography>
                You're ready to start testing. Your test suite has been created.
              </Typography>
            </Box>
          ) : (
            <Box>
              {renderStepContent(activeStep)}
              <Box sx={{ display: 'flex', flexDirection: 'row', pt: 2 }}>
                <Button
                  color="inherit"
                  disabled={activeStep === 0}
                  onClick={handleBack}
                  sx={{ mr: 1 }}
                >
                  Back
                </Button>
                <Box sx={{ flex: '1 1 auto' }} />
                <Button
                  variant="contained"
                  onClick={activeStep === steps.length - 1 ? handleComplete : handleNext}
                >
                  {activeStep === steps.length - 1 ? 'Finish' : 'Next'}
                </Button>
              </Box>
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

const WelcomeStep: React.FC = () => (
  <Box>
    <Typography variant="h4" gutterBottom>
      Welcome to QA-FRAMEWORK! 🚀
    </Typography>
    <Typography paragraph>
      Let's get you set up with automated testing in just a few minutes.
    </Typography>
    <Typography paragraph>
      <strong>What you'll learn:</strong>
    </Typography>
    <ul>
      <li>Connect your GitHub repository</li>
      <li>Create your first test suite</li>
      <li>Run tests with AI-powered self-healing</li>
      <li>Setup notifications for test results</li>
    </ul>
  </Box>
);

const ConnectRepoStep: React.FC = () => {
  const [repoUrl, setRepoUrl] = useState('');

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Connect Your Repository
      </Typography>
      <Typography paragraph>
        Enter your GitHub repository URL to connect it with QA-FRAMEWORK.
      </Typography>
      <input
        type="text"
        placeholder="https://github.com/username/repo"
        value={repoUrl}
        onChange={(e) => setRepoUrl(e.target.value)}
        style={{ width: '100%', padding: '12px', fontSize: '16px' }}
      />
    </Box>
  );
};

const CreateTestSuiteStep: React.FC = () => {
  const [suiteName, setSuiteName] = useState('My First Test Suite');

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Create Your First Test Suite
      </Typography>
      <Typography paragraph>
        A test suite organizes related tests together.
      </Typography>
      <input
        type="text"
        value={suiteName}
        onChange={(e) => setSuiteName(e.target.value)}
        style={{ width: '100%', padding: '12px', fontSize: '16px' }}
      />
    </Box>
  );
};

const RunFirstTestStep: React.FC = () => (
  <Box>
    <Typography variant="h5" gutterBottom>
      Run Your First Test
    </Typography>
    <Typography paragraph>
      Let's create a simple test to verify everything is working.
    </Typography>
    <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
      <code>
        def test_homepage_loads():<br />
        &nbsp;&nbsp;response = client.get('/')<br />
        &nbsp;&nbsp;assert response.status_code == 200
      </code>
    </Box>
  </Box>
);

const SetupNotificationsStep: React.FC = () => (
  <Box>
    <Typography variant="h5" gutterBottom>
      Setup Notifications
    </Typography>
    <Typography paragraph>
      Get notified when tests complete or fail.
    </Typography>
    <Box>
      <label>
        <input type="checkbox" defaultChecked /> Email notifications
      </label>
      <br />
      <label>
        <input type="checkbox" /> Slack notifications
      </label>
      <br />
      <label>
        <input type="checkbox" /> Discord notifications
      </label>
    </Box>
  </Box>
);

export default OnboardingWizard;
