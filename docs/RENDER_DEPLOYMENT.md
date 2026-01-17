# Render.com Deployment Guide

## 🚀 Quick Start

This guide will help you deploy the Private Claude Agent X5 application to Render.com.

## Prerequisites

- [Render.com](https://render.com) account (free tier available)
- GitHub repository connected to Render
- Required API keys (see Configuration section)

## Deployment Steps

### 1. Connect Repository

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository: `appsefilepro-cell/Private-Claude`
4. Render will automatically detect the `render.yaml` configuration

### 2. Configure Environment Variables

Before deploying, set up these environment variables in the Render dashboard:

#### Required Variables:

```bash
# AI API Keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here

# E2B Sandbox (Optional)
E2B_API_KEY=e2b_your-key-here

# Google API (Optional)
GOOGLE_API_KEY=your-google-key-here
```

#### How to Add Environment Variables:

1. Go to your service in Render dashboard
2. Click **"Environment"** tab
3. Click **"Add Environment Variable"**
4. Enter key-value pairs
5. Click **"Save Changes"**

### 3. Deploy

Once environment variables are configured:

1. Click **"Deploy"** or push to your main branch
2. Render will automatically:
   - Install dependencies (`npm install`)
   - Build the application (`npm run build`)
   - Start the server (`npm start`)

## Services Deployed

### Web Application
- **Name**: private-claude-web
- **Type**: Node.js Web Service
- **Port**: Auto-detected (Next.js default: 3000)
- **Health Check**: `/api/health`
- **Auto-Deploy**: Enabled (deploys on git push)

### Python Backend (Optional)
- **Name**: agentx5-orchestrator
- **Type**: Python Worker
- **Script**: `scripts/agent_x5_master_orchestrator.py`

## Health Check

Your application includes a health check endpoint that Render will monitor:

```
https://your-app.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-17T13:00:00.000Z",
  "uptime": 123.45,
  "version": "5.0.0",
  "services": {
    "api": "operational",
    "database": "not_configured",
    "agents": "operational"
  }
}
```

## Automatic Deployments

Render is configured for automatic deployments:

- **Trigger**: Push to `main` branch
- **Build**: Automatic
- **Deploy**: Automatic
- **Rollback**: Available in dashboard

## Monitoring

### View Logs

1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. View real-time application logs

### Metrics

Render provides built-in metrics:
- CPU usage
- Memory usage
- Request count
- Response times

## Custom Domain (Optional)

To use a custom domain:

1. Go to service **"Settings"**
2. Scroll to **"Custom Domain"**
3. Click **"Add Custom Domain"**
4. Follow DNS configuration instructions

## Scaling

### Free Tier
- 750 hours/month
- Auto-sleep after 15 minutes of inactivity
- Wakes up on request

### Paid Plans
- No auto-sleep
- Custom instance sizes
- Horizontal scaling
- Priority support

## Troubleshooting

### Build Fails

**Issue**: Build fails with dependency errors

**Solution**:
```bash
# Check package.json and ensure all dependencies are listed
# Verify Node.js version compatibility
```

### Application Crashes

**Issue**: Application starts but crashes immediately

**Solution**:
1. Check environment variables are set correctly
2. View logs for error messages
3. Verify API keys are valid

### Slow Performance

**Issue**: Application is slow or unresponsive

**Solution**:
1. Upgrade to paid plan (no auto-sleep)
2. Check if hitting rate limits on external APIs
3. Review application logs for bottlenecks

### API Keys Not Working

**Issue**: API calls fail with authentication errors

**Solution**:
1. Verify environment variables are set in Render dashboard
2. Check API keys are valid and not expired
3. Ensure no extra spaces in key values
4. Redeploy after updating environment variables

## Cost Estimates

### Free Tier
- Web service: 750 hours/month (free)
- Auto-sleep after inactivity
- Suitable for development/testing

### Starter Plan (~$7/month)
- 24/7 uptime
- No auto-sleep
- 512 MB RAM
- Suitable for production with light usage

### Standard Plan (~$25/month)
- 2 GB RAM
- Better performance
- Suitable for production with moderate usage

## Security Best Practices

1. **Never commit API keys** to your repository
2. **Use environment variables** for all secrets
3. **Enable HTTPS** (automatic on Render)
4. **Rotate API keys** regularly
5. **Monitor logs** for suspicious activity

## Support

- **Render Documentation**: [https://render.com/docs](https://render.com/docs)
- **Render Community**: [https://community.render.com](https://community.render.com)
- **Repository Issues**: [GitHub Issues](https://github.com/appsefilepro-cell/Private-Claude/issues)

## Next Steps

After successful deployment:

1. ✅ Test health endpoint: `https://your-app.onrender.com/api/health`
2. ✅ Test chat interface: `https://your-app.onrender.com`
3. ✅ Verify agent dashboard works
4. ✅ Configure custom domain (optional)
5. ✅ Set up monitoring alerts

---

**Note**: Replace `your-app` with your actual Render service name in all URLs above.
