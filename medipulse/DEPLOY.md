# 🚀 MediPulse Deployment Guide

## Quick Start (Local Development)

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/medipulse
cd medipulse

# 2. Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# 3. Run with Docker Compose
docker-compose up

# Access:
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🎯 YC Demo Deployment (5 Minutes)

### Option 1: Railway (Recommended for YC Demo)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and initialize
railway login
railway init

# Deploy backend
cd backend
railway up

# Deploy frontend (get backend URL first)
cd ../frontend
# Update NEXT_PUBLIC_API_URL in .env with Railway backend URL
railway up
```

**URLs:**
- Backend: `https://medipulse-backend.railway.app`
- Frontend: `https://medipulse.railway.app`

### Option 2: Vercel + Render

**Frontend (Vercel):**
```bash
# Install Vercel CLI
npm install -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

**Backend (Render):**
1. Create account at https://render.com
2. Connect GitHub repo
3. Create new Web Service
4. Set environment variables
5. Deploy

### Option 3: Single VPS (DigitalOcean/AWS)

```bash
# SSH into server
ssh root@your-server-ip

# Clone and setup
git clone https://github.com/yourusername/medipulse
cd medipulse
cp .env.example .env
# Edit .env with your OPENAI_API_KEY

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
apt install docker-compose

# Run production
docker-compose --profile production up -d

# Setup SSL with Certbot
apt install certbot python3-certbot-nginx
certbot --nginx -d yourdomain.com
```

## 📱 Mobile Demo Setup

For YC partners viewing on phones:

```bash
# Use ngrok for instant mobile access
ngrok http 3000

# Share the HTTPS URL
# https://abc123.ngrok.io
```

## 🔥 Performance Optimization

### 1. Frontend CDN (Cloudflare)
```bash
# Add domain to Cloudflare
# Update DNS records
# Enable:
- Auto Minify
- Brotli Compression  
- HTTP/3
- Early Hints
```

### 2. Backend Scaling
```yaml
# docker-compose.prod.yml
services:
  backend:
    deploy:
      replicas: 3
    environment:
      - WORKERS=4
```

### 3. Database Connection Pooling
```python
# backend/database.py
DATABASE_URL = "postgresql://user:pass@localhost/db?pool_size=20&max_overflow=40"
```

## 🎬 Demo Day Checklist

### 24 Hours Before:
- [ ] Deploy to production
- [ ] Test all features
- [ ] Warm up API (pre-cache responses)
- [ ] Create backup deployment
- [ ] Test on multiple devices
- [ ] Prepare offline demo video

### 1 Hour Before:
- [ ] Clear browser cache
- [ ] Open all necessary tabs
- [ ] Test internet connection
- [ ] Have mobile hotspot ready
- [ ] Load sample documents

### During Demo:
- [ ] Use production URL
- [ ] Have localhost backup running
- [ ] Keep terminal open for monitoring
- [ ] Record screen for backup

## 📊 Monitoring Setup

### 1. Basic Monitoring (Free)
```bash
# Uptime monitoring
curl https://uptimerobot.com/api
# Add https://medipulse.com/health

# Error tracking
# Add Sentry DSN to .env
SENTRY_DSN=your-sentry-dsn
```

### 2. Analytics (Posthog)
```javascript
// frontend/app/layout.tsx
import posthog from 'posthog-js'
posthog.init('your-key', {api_host: 'https://app.posthog.com'})
```

## 🚨 Troubleshooting

### WebSocket Connection Issues
```nginx
# nginx/nginx.conf
location /ws {
    proxy_pass http://backend:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### CORS Errors
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Slow Processing
```python
# Enable caching
from functools import lru_cache

@lru_cache(maxsize=100)
def process_document(doc_hash):
    # Processing logic
```

## 🎯 YC Interview Setup

For live coding during interview:

```bash
# Terminal 1: Backend with live reload
cd backend && uvicorn main:app --reload --host 0.0.0.0

# Terminal 2: Frontend with fast refresh  
cd frontend && npm run dev

# Terminal 3: Logs
docker-compose logs -f

# Terminal 4: Database
docker exec -it medipulse-postgres psql -U medipulse
```

## 💰 Cost Optimization

### Estimated Monthly Costs:
- **Hobby Tier**: $0-50/month
  - Vercel (Frontend): Free
  - Render (Backend): $7/month
  - Supabase (DB): Free tier
  - OpenAI API: ~$30/month

- **Growth Tier**: $200-500/month
  - Vercel Pro: $20/month
  - Render Pro: $25/month
  - Supabase Pro: $25/month
  - OpenAI API: ~$400/month
  - CDN: $20/month

## 🔒 Security Checklist

Before going live:
- [ ] Environment variables secured
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Input validation active
- [ ] SQL injection prevention
- [ ] XSS protection headers
- [ ] CORS properly configured
- [ ] Secrets rotated
- [ ] Backups configured
- [ ] Monitoring active

## 📞 Support During Demo

**Quick Fixes:**
```bash
# Restart everything
docker-compose restart

# Clear cache
docker system prune -a

# Check logs
docker-compose logs --tail=100

# Emergency local demo
python backend/main.py & 
cd frontend && npm run dev
```

**Backup Contacts:**
- Railway Support: support@railway.app
- Vercel Support: support@vercel.com
- Emergency DevOps: your-phone-number

---

Remember: **Keep it simple for the demo**. Focus on the wow factor, not infrastructure complexity. Good luck! 🚀