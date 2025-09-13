# 🚀 Deploying NVIDIA AI Agent to Streamlit Cloud

## 📋 Required Keys and Configuration

### **Streamlit Cloud Secrets** (Required)
Add these to your Streamlit Cloud app's secrets dashboard:

```toml
# Required - OpenAI API Key
OPENAI_API_KEY = "sk-your-openai-api-key-here"

# Optional - Model Configuration  
OPENAI_MODEL = "gpt-4"  # or "gpt-3.5-turbo" for cheaper option

# Agent Configuration
AGENT_NAME = "NVIDIA AI Assistant"
MAX_CONVERSATION_HISTORY = "10"

# Cloud Deployment Flag
STREAMLIT_CLOUD = "true"
CLOUD_DEPLOYMENT = "true"

# Vector Database Settings
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
MAX_SEARCH_RESULTS = "5"
SEARCH_TIMEOUT = "30"

# Optional - Webhook Configuration (see webhook setup below)
WEBHOOK_SECRET = "your-webhook-secret-here"
EXTERNAL_WEBHOOK_URL = "https://your-webhook-service.com"
```

### **Required Files for Deployment**
- ✅ `streamlit_app.py` (main app)
- ✅ `requirements-cloud.txt` (cloud-optimized dependencies)
- ✅ `.streamlit/config.toml` (Streamlit configuration)
- ✅ All files in `src/` directory

## 🚀 Step-by-Step Deployment

### 1. **Prepare Repository**
```bash
# Ensure you have the cloud-optimized requirements
cp requirements-cloud.txt requirements.txt

# Create a deployment branch (optional)
git checkout -b streamlit-cloud-deploy

# Add all necessary files
git add .
git commit -m "Prepare for Streamlit Cloud deployment"
git push origin streamlit-cloud-deploy
```

### 2. **Deploy to Streamlit Cloud**

1. **Go to**: https://share.streamlit.io/
2. **Sign in** with GitHub account
3. **Click "New app"**  
4. **Configure deployment**:
   - **Repository**: `your-username/your-repo-name`
   - **Branch**: `main` (or `streamlit-cloud-deploy`)
   - **Main file path**: `nvidia_ai_agent/streamlit_app.py`
   - **Python version**: `3.11`

### 3. **Advanced Settings**
- **Requirements file**: `nvidia_ai_agent/requirements-cloud.txt`
- **Additional system packages**: None required

### 4. **Add Secrets**
In the "Advanced settings" section, add your secrets:

```
OPENAI_API_KEY = "sk-your-actual-openai-key"
STREAMLIT_CLOUD = "true"
AGENT_NAME = "NVIDIA AI Assistant"
```

### 5. **Deploy and Test**
- Click **"Deploy"**
- Wait for deployment (may take 5-10 minutes)
- Test the agent functionality

## 🔔 Webhook Setup for Cloud (Optional but Recommended)

Since Streamlit Cloud doesn't support webhook servers, use these alternatives:

### **Option 1: GitHub Actions + Zapier**

1. **Set up Zapier Zap**:
   - **Trigger**: RSS by Zapier
   - **Feed URLs**: 
     - `https://developer.nvidia.com/blog/feed`
     - `https://blogs.nvidia.com/feed`
   - **Action**: GitHub - Create File
   - **File Path**: `data/webhook_events/event_{{timestamp}}.json`

2. **JSON Format for GitHub**:
```json
{
  "title": "{{title}}",
  "url": "{{link}}",
  "content": "{{content}}",
  "published": "{{published}}",
  "source": "NVIDIA Developer Blog",
  "processed_at": "{{timestamp}}",
  "status": "success"
}
```

### **Option 2: External Webhook Service**

Deploy a simple webhook receiver on:
- **Vercel**: `vercel.com`
- **Netlify**: `netlify.com`  
- **Railway**: `railway.app`

Add the webhook URL to your Streamlit secrets:
```
EXTERNAL_WEBHOOK_URL = "https://your-webhook.vercel.app"
```

## 📊 Expected Performance

### **Streamlit Cloud Limitations**
- **Memory**: ~1GB RAM
- **Storage**: Ephemeral (resets on restart)
- **CPU**: Shared resources
- **Startup Time**: 30-60 seconds cold start

### **Optimizations Applied**
- ✅ Lightweight ChromaDB instead of Qdrant
- ✅ Reduced dependencies for faster startup
- ✅ Optimized embedding model size
- ✅ Cloud-compatible webhook handling
- ✅ Daily check frequency (not real-time)

## 🧪 Testing Your Deployment

Once deployed, test these features:

1. **Basic Chat**: Ask "What is NVIDIA NIM?"
2. **Knowledge Base**: Questions about course content
3. **Web Search**: "Latest NVIDIA announcements"
4. **Analytics**: Check the Analytics tab
5. **Agent Stats**: Use `/stats` command

## 🔧 Troubleshooting

### **Common Issues**

1. **"Import Error"**
   - Check `requirements-cloud.txt` is used
   - Verify all source files are in repository

2. **"OpenAI API Error"**
   - Verify API key in secrets
   - Check API key has credits
   - Try `gpt-3.5-turbo` instead of `gpt-4`

3. **"Knowledge Base Empty"**
   - Normal for first-time cloud deployment
   - Knowledge base builds on first use
   - May take 2-3 minutes initially

4. **"Webhook Not Working"**
   - Expected - requires external setup
   - Agent works fine without webhooks
   - Web search still provides current info

### **Performance Tips**
- Use `gpt-3.5-turbo` for faster responses
- Reduce `MAX_CONVERSATION_HISTORY` if memory issues
- Keep `MAX_SEARCH_RESULTS` at 5 or lower

## 🎯 URLs and Access

After successful deployment:
- **Your App**: `https://your-app-name.streamlit.app`
- **Logs**: Available in Streamlit Cloud dashboard
- **Secrets**: Manageable in app settings

## 🔄 Updates and Maintenance

To update your deployed app:
1. Make changes to your repository
2. Push to the deployment branch
3. Streamlit Cloud auto-redeploys
4. Changes appear within 1-2 minutes

## 📞 Support

If you encounter issues:
1. Check Streamlit Cloud logs
2. Verify all secrets are set correctly
3. Test locally first with `./run_web_app.sh`
4. Check GitHub repository permissions

---

**🎉 Your NVIDIA AI Assistant is now live on Streamlit Cloud!**
