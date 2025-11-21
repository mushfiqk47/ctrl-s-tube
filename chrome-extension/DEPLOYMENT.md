# Ctrl+S Tube - Render Deployment Guide

## Prerequisites
1. GitHub account
2. Render account (sign up at https://render.com - it's free!)
3. Your YouTube downloader extension code pushed to GitHub

## Step-by-Step Deployment

### 1. Prepare Your Repository

Make sure your code is pushed to GitHub with the following structure:
```
chrome-extension/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── downloads/
├── render.yaml
└── (other extension files)
```

### 2. Create FFmpeg Buildpack File

Create a file named `.buildpacks` in the `chrome-extension` directory:
```
https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
```

This tells Render to install FFmpeg during deployment.

### 3. Deploy to Render

#### Option A: Using Render Blueprint (Automatic)

1. Go to https://dashboard.render.com
2. Click "New +" → "Blueprint"
3. Connect your GitHub repository
4. Render will detect `render.yaml` and configure everything automatically
5. Click "Apply" to start deployment

#### Option B: Manual Setup

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure:
   - **Name**: `ctrl-s-tube-backend`
   - **Region**: Oregon (Free)
   - **Branch**: main
   - **Root Directory**: `chrome-extension/backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 server:app`
5. Add FFmpeg buildpack:
   - Go to "Environment" tab
   - Add buildpack URL: `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
6. Click "Create Web Service"

### 4. Get Your Production URL

After deployment completes (5-10 minutes):
1. Go to your service dashboard
2. Copy the URL (will be something like: `https://ctrl-s-tube-backend.onrender.com`)
3. Test it by visiting: `https://your-url.onrender.com/health`

You should see:
```json
{"status": "ok", "message": "Ctrl+S Tube Backend is running"}
```

### 5. Update Chrome Extension

Update `config.js` with your production URL:

```javascript
export const CONFIG = Object.freeze({
    BACKEND: Object.freeze({
        DEFAULT_URL: 'https://your-url.onrender.com',  // Change this!
        PRODUCTION_URL: 'https://your-url.onrender.com',  // Add this line
        LOCAL_URL: 'http://localhost:5000',  // Keep for development
        TIMEOUT_MS: 30_000,
        RETRY_ATTEMPTS: 3,
        RETRY_DELAY_MS: 1_000,
    }),
    // ... rest of config
});
```

### 6. Reload Extension

1. Go to `chrome://extensions`
2. Find your extension
3. Click the reload icon
4. Test downloading a video!

## Important Notes

### Free Tier Limitations
- ✅ 750 hours/month (plenty for personal use)
- ⚠️ Spins down after 15 minutes of inactivity
- ⚠️ Cold start: 30-60 seconds on first request after sleep
- ⚠️ No persistent storage (files deleted on restart)

### Cold Start Behavior
When the server is asleep:
1. First request will take 30-60 seconds
2. Extension will show "Connecting to server..."
3. Subsequent requests will be fast
4. Server stays awake for 15 minutes after last request

### Staying Awake (Optional)
To prevent sleep, you can:
1. Use a service like UptimeRobot (free) to ping `/health` every 10 minutes
2. **Warning**: This uses more of your 750 hours/month
3. Only do this if you need instant response times

## Troubleshooting

### Build Fails
- Check logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Make sure FFmpeg buildpack is added

### Server Won't Start
- Check that `PORT` environment variable exists
- Verify `server.py` binds to `0.0.0.0`
- Check logs for Python errors

### Downloads Fail
- Verify FFmpeg is installed (check logs for ffmpeg messages)
- Test with simple YouTube URL first
- Check CORS is enabled in server.py

### Extension Can't Connect
- Verify production URL is correct
- Check browser console for errors
- Test `/health` endpoint in browser
- Ensure HTTPS (not HTTP) is used

## Monitoring

### View Logs
```bash
# In Render dashboard
1. Go to your service
2. Click "Logs" tab
3. Watch real-time logs
```

### Check Health
Visit: `https://your-url.onrender.com/health`

Should return:
```json
{"status": "ok", "message": "Ctrl+S Tube Backend is running"}
```

## Updating Your Deployment

Whenever you push to GitHub:
1. Render automatically detects changes
2. Rebuilds and redeploys (takes ~5 minutes)
3. No manual intervention needed!

## Cost Breakdown

**Free Tier:**
- Web Services: 750 hours/month
- Build Minutes: 500 minutes/month
- Bandwidth: 100 GB/month

**Your Usage:**
- If always on: ~720 hours/month ✅
- If on-demand: ~50-200 hours/month ✅
- Build: ~3 minutes per deploy ✅

**Result: COMPLETELY FREE** 🎉

## Support

If you encounter issues:
1. Check Render status: https://status.render.com
2. Review logs in dashboard
3. Test locally first with `python backend/server.py`
4. Verify all files are committed to GitHub
