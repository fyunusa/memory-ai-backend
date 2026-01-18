# Memory AI Backend - Deployment Guide

## Deploy to Render

### Prerequisites
1. Create account at [Render](https://render.com)
2. Have your environment variables ready (see below)

### Automatic Deployment

1. **Connect GitHub Repository**
   - Go to Render Dashboard
   - Click "New" → "Blueprint"
   - Connect your GitHub account
   - Select `memory-ai-backend` repository
   - Render will auto-detect `render.yaml`

2. **Set Environment Variables**
   
   After deployment starts, add these in Render Dashboard:
   
   **Required:**
   - `QDRANT_URL` - Your Qdrant Cloud URL
   - `QDRANT_API_KEY` - Your Qdrant Cloud API key
   - `COHERE_API_KEY` - Your Cohere API key
   
   **Optional (for OAuth integrations):**
   - `LINKEDIN_CLIENT_ID`
   - `LINKEDIN_CLIENT_SECRET`
   - `NOTION_CLIENT_ID`
   - `NOTION_CLIENT_SECRET`
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `TWITTER_BEARER_TOKEN`
   - `GMAIL_CLIENT_ID`
   - `GMAIL_CLIENT_SECRET`
   - `OPENAI_API_KEY` (if using OpenAI embeddings)

3. **Deploy**
   - Click "Apply"
   - Render will create:
     - Web Service (FastAPI backend)
     - PostgreSQL database
     - Redis instance
   - First deploy takes ~5-10 minutes

4. **Get Your Backend URL**
   - After deployment: `https://memory-ai-backend.onrender.com`
   - Use this URL in your frontend `.env`:
     ```
     VITE_API_URL=https://memory-ai-backend.onrender.com
     ```

### Database Migrations

After first deployment, run migrations:

```bash
# In Render Shell (Dashboard → Shell tab)
alembic upgrade head
```

### Verify Deployment

1. Check health: `https://your-app.onrender.com/`
2. Check docs: `https://your-app.onrender.com/docs`
3. Test API: `https://your-app.onrender.com/memory/list`

### Update Frontend

After backend is deployed, update frontend environment:

```bash
cd frontend
echo "VITE_API_URL=https://memory-ai-backend.onrender.com" > .env
git add .env
git commit -m "Update API URL for production"
git push
```

Then redeploy frontend on Netlify.

---

## Troubleshooting

**Issue:** Database connection failed
- **Fix:** Check DATABASE_URL in environment variables

**Issue:** Qdrant connection failed
- **Fix:** Verify QDRANT_URL and QDRANT_API_KEY are set correctly

**Issue:** Service keeps sleeping (free tier)
- **Note:** Render free tier spins down after 15min inactivity
- First request after sleep takes ~30 seconds
- Consider upgrading to paid tier ($7/mo) for always-on

---

## Free Tier Limits

- **Web Service:** 750 hours/month (enough for always-on)
- **PostgreSQL:** Free forever (new free tier)
- **Redis:** 25MB storage
- **Spin down:** After 15min inactivity (wakes on request)

---

## Manual Deployment (Alternative)

If not using render.yaml:

1. Create Web Service manually
2. Connect GitHub repo
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add PostgreSQL and Redis from dashboard
6. Set environment variables
7. Deploy
