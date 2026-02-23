# 🚀 QA-FRAMEWORK SaaS - Deployment Guide

**Target Platform:** Railway
**Last Updated:** 2026-02-23

---

## 📋 Prerequisites

### 1. Accounts Needed
- [x] GitHub account (repo already exists)
- [ ] Railway account (create at railway.app)
- [ ] Domain name (optional but recommended)

### 2. Tools Required
- [x] Git
- [ ] Railway CLI: `npm install -g @railway/cli`
- [ ] PostgreSQL client (for debugging)

---

## 🎯 Quick Deploy (5 steps)

### Step 1: Create Railway Account (2 min)
1. Go to [railway.app](https://railway.app)
2. Click "Start a New Project"
3. Sign up with GitHub
4. Add payment method (credit card) - won't be charged until deploy

### Step 2: Create PostgreSQL Database (1 min)
1. In Railway dashboard, click "+ New"
2. Select "Database" → "PostgreSQL"
3. Database will be created automatically
4. Note the connection details in "Variables" tab

### Step 3: Create Redis Instance (1 min)
1. Click "+ New"
2. Select "Database" → "Redis"
3. Redis will be created automatically
4. Note the `REDIS_URL` in "Variables" tab

### Step 4: Deploy Backend Service (3 min)
1. Click "+ New" → "GitHub Repo"
2. Select `llllJokerllll/QA-FRAMEWORK`
3. Configure:
   - **Root Directory:** `dashboard/backend`
   - **Dockerfile:** `Dockerfile.prod`
   - **Port:** `8000` (auto-detected)

4. Add environment variables:
   ```bash
   SECRET_KEY=<generate with: openssl rand -hex 32>
   JWT_SECRET_KEY=<generate with: openssl rand -hex 32>
   CORS_ORIGINS=https://qaframework.io,http://localhost:3000
   ENVIRONMENT=production
   DEBUG=false
   LOG_LEVEL=info
   ```

5. Click "Deploy"

### Step 5: Verify Deployment (1 min)
1. Check logs: Railway → Your Service → "Logs"
2. Visit health endpoint: `https://your-service.railway.app/health`
3. Should return: `{"status": "healthy", "service": "qa-framework-dashboard-api"}`

---

## 🔧 Detailed Configuration

### Environment Variables

#### Required
| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection | Auto-provided by Railway |
| `REDIS_URL` | Redis connection | Auto-provided by Railway |
| `SECRET_KEY` | App secret key | `openssl rand -hex 32` |
| `JWT_SECRET_KEY` | JWT signing key | `openssl rand -hex 32` |
| `CORS_ORIGINS` | Allowed origins | `https://qaframework.io` |

#### Optional
| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Environment name | `production` |
| `DEBUG` | Debug mode | `false` |
| `LOG_LEVEL` | Logging level | `info` |
| `PORT` | Server port | `8000` |
| `OPENAI_API_KEY` | OpenAI key for AI features | - |
| `ZHIPUAI_API_KEY` | ZhipuAI key (free tier) | - |

### Database Setup

#### Run Migrations
```bash
# Connect to Railway backend
railway run alembic upgrade head

# Or via Railway CLI
railway connect
cd /app
alembic upgrade head
```

#### Create Admin User
```bash
railway run python scripts/create_admin.py
```

Default credentials:
- Email: `admin@qaframework.io`
- Password: `changeme123`
- ⚠️ **CHANGE IMMEDIATELY**

### Custom Domain Setup

1. **Add domain in Railway:**
   - Go to your service → "Settings" → "Domains"
   - Add domain: `api.qaframework.io`

2. **Configure DNS:**
   - Add CNAME record:
     ```
     api.qaframework.io → your-service.railway.app
     ```

3. **SSL is automatic** (Railway provides Let's Encrypt)

---

## 📊 Monitoring & Logs

### View Logs
```bash
# Via CLI
railway logs

# Via Dashboard
Railway → Your Service → "Logs"
```

### Metrics
Railway provides built-in metrics:
- CPU usage
- Memory usage
- Network I/O
- Request rate

### Health Checks
- **Endpoint:** `/health`
- **Interval:** 30s
- **Timeout:** 10s
- **Retries:** 3

### Alerts
Configure alerts in Railway:
1. Go to "Settings" → "Alerts"
2. Add rules:
   - CPU > 80% for 5 min
   - Memory > 80% for 5 min
   - Response time > 2s
3. Add notification channel (email, Slack, etc.)

---

## 🔄 CI/CD Pipeline

### GitHub Actions (Already configured)
- **Trigger:** Push to `main` branch
- **Jobs:**
  1. Run tests
  2. Deploy to Railway
  3. Run migrations

### Required GitHub Secrets
Set in: GitHub repo → Settings → Secrets → Actions

| Secret | How to get |
|--------|------------|
| `RAILWAY_TOKEN` | Railway dashboard → Settings → API Tokens |
| `RAILWAY_SERVICE_URL` | Your Railway service URL |
| `RAILWAY_DATABASE_URL` | Railway PostgreSQL connection string |

### Manual Deploy
```bash
# From local machine
railway login
railway up
```

---

## 💰 Cost Estimation

### Railway Pricing (as of 2026-02)

| Resource | Starter | Pro | Enterprise |
|----------|---------|-----|------------|
| **Price** | $5/mes | $20/mes | Custom |
| **RAM** | 512MB | 2GB | Custom |
| **CPU** | Shared | 1 vCPU | Custom |
| **Database** | $5/mes (1GB) | $10/mes (5GB) | Custom |
| **Bandwidth** | 100GB | 500GB | Unlimited |

### MVP Estimated Cost
```
Backend service: $5-10/mes
PostgreSQL: $5/mes (1GB)
Redis: $5/mes (25MB)
Total: $15-20/mes
```

### Growth Projection
```
Month 1-3: $20/mes (10-50 users)
Month 4-6: $50/mes (100 users)
Month 7-12: $100-300/mes (500+ users)
```

---

## 🔐 Security Checklist

### Before Deploy
- [x] Generate strong `SECRET_KEY` (32+ bytes)
- [x] Generate strong `JWT_SECRET_KEY` (32+ bytes)
- [x] Set `DEBUG=false`
- [x] Set `ENVIRONMENT=production`
- [x] Configure `CORS_ORIGINS` properly
- [x] Enable SSL (automatic with Railway)

### After Deploy
- [ ] Change admin password
- [ ] Review database access logs
- [ ] Set up monitoring alerts
- [ ] Configure backup schedule
- [ ] Review security headers
- [ ] Enable rate limiting

---

## 🐛 Troubleshooting

### Issue: "Database connection failed"
**Solution:**
```bash
# Check DATABASE_URL format
railway variables

# Test connection
railway run python -c "from database import engine; print(engine.url)"
```

### Issue: "Port already in use"
**Solution:**
```bash
# Railway auto-sets PORT env var
# Make sure your app uses: port = int(os.getenv("PORT", 8000))
```

### Issue: "Build failed"
**Solution:**
```bash
# Check Dockerfile path
# Ensure .dockerignore doesn't exclude required files
# Check build logs: Railway → Service → "Build Logs"
```

### Issue: "Health check failing"
**Solution:**
```bash
# Verify /health endpoint works
curl https://your-service.railway.app/health

# Check logs for errors
railway logs
```

---

## 📞 Support

### Railway Support
- Documentation: [docs.railway.app](https://docs.railway.app)
- Discord: [railway.app/discord](https://railway.app/discord)
- Status: [status.railway.app](https://status.railway.app)

### QA-FRAMEWORK Support
- GitHub Issues: [github.com/llllJokerllll/QA-FRAMEWORK/issues](https://github.com/llllJokerllll/QA-FRAMEWORK/issues)
- Email: support@qaframework.io (after launch)

---

## ✅ Deployment Checklist

### Pre-Deploy
- [ ] Railway account created
- [ ] PostgreSQL created
- [ ] Redis created
- [ ] Environment variables set
- [ ] GitHub secrets configured
- [ ] Domain registered (optional)

### Deploy
- [ ] Backend deployed successfully
- [ ] Health check passing
- [ ] Migrations run
- [ ] Admin user created
- [ ] Custom domain configured (if applicable)

### Post-Deploy
- [ ] Admin password changed
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Backup schedule enabled
- [ ] Team members invited

---

**Estimated Total Time:** 15-30 minutes for first deploy

**Next Steps:**
1. Create Railway account
2. Follow "Quick Deploy" steps above
3. Test health endpoint
4. Document deployed URL

---

*Guide created: 2026-02-23*
*Target deploy date: 2026-02-24*
