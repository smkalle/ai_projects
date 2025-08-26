# Deployment Guide

## Table of Contents
- [Development Setup](#development-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Development Setup

### Prerequisites
- Python 3.8+
- 4GB RAM minimum
- 10GB free disk space

### Quick Start

```bash
# Using the automated script
./start.sh

# Or manual setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python app/main.py --mode ui
```

## Production Deployment

### System Requirements

**Minimum**:
- 2 vCPUs
- 8GB RAM
- 50GB SSD storage
- Ubuntu 20.04+ or RHEL 8+

**Recommended**:
- 4+ vCPUs
- 16GB RAM
- 100GB SSD storage
- GPU for faster embeddings (optional)

### Installation Steps

#### 1. System Dependencies

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y python3.10 python3-pip python3-venv \
    build-essential libssl-dev libffi-dev python3-dev \
    nginx supervisor redis-server

# RHEL/CentOS
sudo yum install -y python3.10 python3-pip python3-venv \
    gcc openssl-devel python3-devel \
    nginx supervisor redis
```

#### 2. Application Setup

```bash
# Create application user
sudo useradd -m -s /bin/bash energydoc
sudo su - energydoc

# Clone repository
git clone https://github.com/your-org/energy-document-ai.git
cd energy-document-ai

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Add your configuration
```

#### 3. Systemd Service

Create `/etc/systemd/system/energy-doc-ai.service`:

```ini
[Unit]
Description=Energy Document AI Service
After=network.target

[Service]
Type=simple
User=energydoc
Group=energydoc
WorkingDirectory=/home/energydoc/energy-document-ai
Environment="PATH=/home/energydoc/energy-document-ai/venv/bin"
ExecStart=/home/energydoc/energy-document-ai/venv/bin/python app/main.py --mode both
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable energy-doc-ai
sudo systemctl start energy-doc-ai
sudo systemctl status energy-doc-ai
```

#### 4. Nginx Configuration

Create `/etc/nginx/sites-available/energy-doc-ai`:

```nginx
upstream streamlit {
    server localhost:8501;
}

upstream fastapi {
    server localhost:8000;
}

server {
    listen 80;
    server_name your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /etc/ssl/certs/your-cert.pem;
    ssl_certificate_key /etc/ssl/private/your-key.pem;
    
    # Streamlit UI
    location / {
        proxy_pass http://streamlit;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # FastAPI
    location /api {
        rewrite ^/api(.*)$ $1 break;
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket support
    location /ws {
        proxy_pass http://fastapi;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    client_max_body_size 50M;
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/energy-doc-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Docker Deployment

### Using Docker Compose

```bash
# Build and run
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8501:8501"
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_HOST=qdrant
      - QDRANT_PORT=6333
    volumes:
      - ./data:/app/data
    depends_on:
      - qdrant
    restart: unless-stopped

  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  qdrant_data:
```

## Cloud Deployment

### AWS EC2

1. **Launch Instance**:
   - AMI: Ubuntu 22.04 LTS
   - Instance Type: t3.large (minimum)
   - Security Group: Open ports 80, 443, 8501, 8000

2. **Install Dependencies**:
```bash
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin
```

3. **Deploy Application**:
```bash
git clone https://github.com/your-org/energy-document-ai.git
cd energy-document-ai
sudo docker compose up -d
```

### Google Cloud Platform

1. **Using Cloud Run**:
```bash
# Build and push image
gcloud builds submit --tag gcr.io/PROJECT_ID/energy-doc-ai

# Deploy
gcloud run deploy energy-doc-ai \
  --image gcr.io/PROJECT_ID/energy-doc-ai \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --set-env-vars OPENAI_API_KEY=$OPENAI_API_KEY
```

### Azure Container Instances

```bash
# Create resource group
az group create --name energy-doc-rg --location eastus

# Create container
az container create \
  --resource-group energy-doc-rg \
  --name energy-doc-ai \
  --image your-registry.azurecr.io/energy-doc-ai:latest \
  --cpu 2 \
  --memory 8 \
  --ports 8501 8000 \
  --environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    QDRANT_HOST=localhost
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: energy-doc-ai
spec:
  replicas: 3
  selector:
    matchLabels:
      app: energy-doc-ai
  template:
    metadata:
      labels:
        app: energy-doc-ai
    spec:
      containers:
      - name: app
        image: your-registry/energy-doc-ai:latest
        ports:
        - containerPort: 8501
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
---
apiVersion: v1
kind: Service
metadata:
  name: energy-doc-ai-service
spec:
  selector:
    app: energy-doc-ai
  ports:
    - name: streamlit
      port: 8501
      targetPort: 8501
    - name: fastapi
      port: 8000
      targetPort: 8000
  type: LoadBalancer
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-...

# Qdrant Configuration
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_API_KEY=optional-key

# Application Settings
APP_ENV=production
DEBUG=false
LOG_LEVEL=info

# Performance Tuning
PDF_DPI=300
MAX_FILE_SIZE_MB=50
CHUNK_SIZE=800
MAX_WORKERS=4

# Security
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=your-domain.com
CORS_ORIGINS=https://your-domain.com

# Rate Limiting
RATE_LIMIT_UPLOADS=10/minute
RATE_LIMIT_QUERIES=100/minute
```

### SSL/TLS Setup

Using Let's Encrypt:
```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Streamlit health
curl http://localhost:8501/healthz

# Qdrant health
curl http://localhost:6333/health
```

### Logging

Configure logging in `.env`:
```bash
LOG_LEVEL=info
LOG_FILE=/var/log/energy-doc-ai/app.log
LOG_MAX_SIZE=100MB
LOG_BACKUP_COUNT=10
```

### Metrics with Prometheus

Add to `docker-compose.yml`:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3000:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

## Troubleshooting

### Common Issues

**1. Out of Memory**
```bash
# Increase Docker memory
docker update --memory="4g" container_name

# Or adjust systemd limits
sudo systemctl edit energy-doc-ai
# Add: MemoryLimit=4G
```

**2. Slow OCR Processing**
- Reduce PDF_DPI to 150-200
- Enable GPU acceleration
- Increase worker processes

**3. Connection Refused**
```bash
# Check service status
sudo systemctl status energy-doc-ai
docker ps
netstat -tlnp | grep -E "8501|8000|6333"

# Check firewall
sudo ufw status
sudo ufw allow 8501,8000,6333/tcp
```

**4. API Key Issues**
```bash
# Verify environment
python -c "import os; print(os.getenv('OPENAI_API_KEY'))"

# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Performance Optimization

1. **Enable Redis Caching**:
```python
# In config.py
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CACHE_TTL = 900  # 15 minutes
```

2. **Optimize Qdrant**:
```yaml
# qdrant_config.yaml
storage:
  optimizer_interval_sec: 600
  max_optimization_threads: 4
```

3. **Use CDN for Static Assets**:
```nginx
location /static {
    alias /app/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/backup/energy-doc-ai"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup Qdrant data
docker exec qdrant tar czf - /qdrant/storage | \
    gzip > $BACKUP_DIR/qdrant_$DATE.tar.gz

# Backup application data
tar czf $BACKUP_DIR/data_$DATE.tar.gz /app/data

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /home/energydoc/backup.sh
```

### Restore

```bash
# Restore Qdrant
docker exec -i qdrant tar xzf - < qdrant_backup.tar.gz

# Restore application data
tar xzf data_backup.tar.gz -C /
```