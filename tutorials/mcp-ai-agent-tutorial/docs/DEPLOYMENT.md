# Deployment Guide

## Docker Deployment

### Build and Run
```bash
docker-compose up --build
```

### Environment Variables
```env
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```

## Cloud Deployment

### Heroku
1. Create Heroku app
2. Set environment variables
3. Deploy with Git

### AWS ECS
1. Build Docker image
2. Push to ECR
3. Create ECS service

### Google Cloud Run
1. Build with Cloud Build
2. Deploy to Cloud Run
3. Configure environment

## Production Checklist

- [ ] Set secure API keys
- [ ] Enable HTTPS
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure auto-scaling
