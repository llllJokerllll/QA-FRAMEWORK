# 🚀 Getting Started - QA-FRAMEWORK

Welcome to QA-FRAMEWORK, the AI-powered testing platform that heals itself.

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Node.js** 18+ (for frontend)
- **Python** 3.11+ (for backend)
- **PostgreSQL** 14+ (for database)
- **Redis** 6+ (for caching)

## 🏃 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/llllJokerllll/QA-FRAMEWORK.git
cd QA-FRAMEWORK
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run database migrations
alembic upgrade head

# Start the server
uvicorn main:app --reload
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Start development server
npm run dev
```

### 4. Access the Application

- **Frontend:** http://localhost:5173
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## 🔑 Authentication

### Using Google OAuth

1. Go to the login page
2. Click "Sign in with Google"
3. Authorize the application
4. You'll be redirected to the dashboard

### Using GitHub OAuth

1. Go to the login page
2. Click "Sign in with GitHub"
3. Authorize the application
4. You'll be redirected to the dashboard

### Using Email/Password

1. Go to the login page
2. Click "Create Account"
3. Enter your email and password
4. Verify your email address
5. Log in with your credentials

## 🧪 Running Your First Test

### Using the Dashboard

1. Navigate to **Test Suites**
2. Click **Create New Suite**
3. Add test cases to your suite
4. Click **Run Suite**
5. View results in **Executions** tab

### Using the API

```bash
# Create a test suite
curl -X POST http://localhost:8000/api/v1/suites \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Suite",
    "description": "Example test suite"
  }'

# Run the suite
curl -X POST http://localhost:8000/api/v1/suites/{suite_id}/run \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🤖 AI Features

### Self-Healing Tests

When a selector breaks, QA-FRAMEWORK automatically:

1. Detects the broken selector
2. Analyzes the page structure
3. Generates alternative selectors
4. Applies the best match
5. Updates your test

**Confidence Score:** Each healing attempt is scored 0-100%. Only high-confidence fixes are applied automatically.

### AI Test Generation

Generate tests from requirements:

1. Go to **AI Test Generation**
2. Paste your requirements (Gherkin or natural language)
3. Click **Generate Tests**
4. Review and customize generated tests
5. Add to your test suite

### Flaky Test Detection

The system automatically:

1. Monitors test execution history
2. Detects inconsistent results
3. Quarantines flaky tests
4. Provides root cause analysis
5. Suggests fixes

## 📊 Monitoring & Analytics

### Dashboard Metrics

- **Test Coverage:** Percentage of code covered by tests
- **Success Rate:** Percentage of passing tests
- **Execution Time:** Average test duration
- **Flaky Tests:** Number of quarantined tests

### Reports

Generate detailed reports:

- **HTML Reports:** Visual test results
- **JSON Reports:** Machine-readable data
- **Allure Reports:** Advanced analytics

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/qaframework

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# AI
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Stripe
STRIPE_API_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret
```

### Feature Flags

Enable/disable features in `config/features.py`:

```python
FEATURES = {
    "self_healing": True,
    "ai_generation": True,
    "flaky_detection": True,
    "billing": True,
}
```

## 🐛 Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Verify connection string
echo $DATABASE_URL
```

#### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# Should return: PONG
```

#### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Getting Help

- **Documentation:** https://docs.qa-framework.io
- **GitHub Issues:** https://github.com/llllJokerllll/QA-FRAMEWORK/issues
- **Discord:** https://discord.gg/qa-framework
- **Email:** support@qa-framework.io

## 📚 Next Steps

- [ ] Create your first test suite
- [ ] Explore AI features
- [ ] Set up CI/CD integration
- [ ] Invite team members
- [ ] Configure billing (Pro/Enterprise)

## 🎯 Best Practices

1. **Organize Tests:** Group related tests into suites
2. **Use Tags:** Tag tests for easy filtering
3. **Monitor Flaky Tests:** Review quarantine regularly
4. **Review AI Suggestions:** Always verify AI-generated tests
5. **Set Up Alerts:** Configure notifications for failures

---

**Need help?** Join our [Discord community](https://discord.gg/qa-framework) or check our [FAQ](https://docs.qa-framework.io/faq).
