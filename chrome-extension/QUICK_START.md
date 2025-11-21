# Quick Render Deployment Guide

## You're Almost There! 🚀

All your code is ready and pushed to GitHub. Now just deploy to Render:

### 5-Minute Deployment Steps

1. **Go to Render**  
   👉 https://dashboard.render.com/register
   - Sign up with GitHub (it's free!)

2. **Connect Your Repo**
   - Click **"New +"** → **"Web Service"**
   - Authorize Render to access your GitHub
   - Select repository: **mushfiqk47/ctrl-s-tube**

3. **Configure the Service**
   ```
   Name: ctrl-s-tube-backend
   Region: Oregon (Free)
   Branch: main
   Root Directory: chrome-extension/backend
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 300 server:app
   Plan: Free
   ```

4. **Add FFmpeg (IMPORTANT!)**
   - Scroll down to **"Advanced"** → **"Add Buildpack"**
   - Paste: `https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git`
   - Click **"Add"**

5. **Create Service**
   - Click **"Create Web Service"**
   - Wait 5-10 minutes for build & deploy
   - Watch the logs - you'll see "Starting Ctrl+S Tube Backend Server..."

6. **Get Your URL**
   - After deployment, copy the URL from dashboard
   - It will look like: `https://ctrl-s-tube-backend.onrender.com`
   - Test it: Visit `https://YOUR-URL.onrender.com/health`
   - Should see: `{"status": "ok", "message": "Ctrl+S Tube Backend is running"}`

7. **Update Your Extension**
   - Open `config.js` in your extension
   - Find line 10: `PRODUCTION_URL: 'https://ctrl-s-tube-backend.onrender.com'`
   - Replace with YOUR actual Render URL
   - Save the file
   - Go to `chrome://extensions` and reload your extension

8. **Test It!**
   - Go to any YouTube video
   - Click your extension
   - Download a video - it should work via the cloud! ☁️

---

## What Happens on Free Tier

**Cold Starts**: Server sleeps after 15 minutes of inactivity
- First request: Takes 30-60 seconds to wake up
- Shows: "Connecting to server..." in extension
- After wake-up: Downloads work normally for next 15 minutes

**This is completely normal for free tier!**

---

## Troubleshooting

### Build Fails
- Check you added the FFmpeg buildpack
- Look at build logs for errors
- Make sure Python 3.9+ is detected

### Can't Connect
- Verify URL is HTTPS (not HTTP)
- Check service is "Live" (green status)
- Test `/health` endpoint in browser first

### Downloads Fail
- Check logs for FFmpeg errors
- Verify buildpack installed correctly
- Look for Python errors in logs

---

## Your Extension is Now Smart! 🧠

The extension will automatically:
1. Try to connect to local backend (http://localhost:5000)
2. If local fails, use production Render URL
3. Show appropriate error messages

So you can:
- Use local backend when developing
- Use cloud backend when just browsing
- **No manual switching needed!**

---

## Need Help?

Full deployment guide available at:
[`DEPLOYMENT.md`](./DEPLOYMENT.md)

---

**Ready? Go deploy!** 🚀
It takes ~10 minutes total, and then your extension works everywhere, anytime!
