# Deployment Guide - Render.com

This guide will help you deploy the Code Cleanup Agents application to Render.com.

## ✅ Pre-Deployment Checklist

All required files have been created:
- ✅ `requirements.txt` - Python dependencies (updated for Python 3.12/3.13 compatibility)
- ✅ `runtime.txt` - Specifies Python 3.12.7 for compatibility
- ✅ `Procfile` - Tells Render how to run the app
- ✅ `.gitignore` - Excludes unnecessary files from git
- ✅ `app.py` - Updated for production (uses PORT env var, debug=False)

## 🚀 Deployment Steps

### Step 1: Push to GitHub

1. Initialize git repository (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit - ready for deployment"
   ```

2. Connect to your GitHub repository and push:
   ```bash
   git remote add origin https://github.com/LuminArk-AI/code-cleanup-agents.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Create Render.com Account

1. Go to [render.com](https://render.com)
2. Sign up for a free account (GitHub OAuth recommended)
3. Connect your GitHub account

### Step 3: Create Web Service on Render

1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `code-cleanup-agents` (or your preferred name)
   - **Environment**: `Python 3` (will use Python 3.12.7 from runtime.txt)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (or leave blank - Procfile will be used)
   - **Plan**: Free (or paid if you need more resources)
   
   **Note**: The `runtime.txt` file specifies Python 3.12.7 for compatibility with SQLAlchemy.

### Step 4: Configure Environment Variables

In the Render dashboard, go to **Environment** section and add:

**Required:**
```
DATABASE_URL=postgresql://user:password@host:port/database
```

**Optional (for parallel processing):**
```
SECURITY_FORK_URL=postgresql://user:password@host:port/security_fork-db-60626
QUALITY_FORK_URL=postgresql://user:password@host:port/quality_fork-db-60626
PERFORMANCE_FORK_URL=postgresql://user:password@host:port/performance_fork-db-60626
BEST_PRACTICES_FORK_URL=postgresql://user:password@host:port/best_practices_fork-db-60626
```

### Step 5: Create PostgreSQL Database (if needed)

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `code-cleanup-db`
   - **Database**: `codecleanup`
   - **User**: Auto-generated
   - **Plan**: Free (or paid)
3. Copy the **Internal Database URL** and use it as `DATABASE_URL`
4. Enable `pg_trgm` extension (Render PostgreSQL supports it)

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies from `requirements.txt`
   - Start the app using `Procfile`
3. Wait for deployment to complete (usually 2-5 minutes)
4. Your app will be live at: `https://your-app-name.onrender.com`

## 🔧 Post-Deployment

### Verify Deployment

1. Visit your app URL
2. Check the `/status` endpoint to verify database connections
3. Test uploading a code file for analysis

### Monitor Logs

- View logs in Render dashboard under **"Logs"** tab
- Check for any errors or warnings

### Database Setup

On first deployment, the app will automatically create required tables. You can also run:

```bash
# SSH into Render (if available) or use Render Shell
python test_connection.py
```

## 🐛 Troubleshooting

### Common Issues

1. **Build Fails**
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility

2. **App Crashes on Start**
   - Check logs for error messages
   - Verify `DATABASE_URL` is set correctly
   - Ensure database is accessible from Render

3. **Database Connection Errors**
   - Use **Internal Database URL** (not external) for better performance
   - Verify database is running
   - Check firewall/security settings

4. **Extension Errors (pg_trgm)**
   - Render PostgreSQL supports `pg_trgm` by default
   - If issues occur, contact Render support

### Debugging

1. **View Logs**: Render dashboard → Your service → Logs
2. **Check Environment Variables**: Settings → Environment
3. **Restart Service**: Manual Deploy → Clear build cache & deploy

## 📊 Render.com Free Tier Limits

- **750 hours/month** of runtime (enough for 24/7 on one service)
- **512 MB RAM**
- **0.1 CPU**
- **Automatic sleep** after 15 minutes of inactivity (wakes on request)
- **PostgreSQL**: 90 days retention, 1 GB storage

## 🔄 Updating Your App

1. Make changes locally
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Your update message"
   git push
   ```
3. Render will automatically detect changes and redeploy

## 📝 Notes

- First deployment may take longer (5-10 minutes)
- Free tier services spin down after inactivity (first request after sleep takes ~30 seconds)
- Consider upgrading to paid plan for production use
- Database forks (Agentic Postgres) need to be configured separately if using external service

---

**Ready to deploy! 🚀**

