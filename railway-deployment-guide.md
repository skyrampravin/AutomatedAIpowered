# Quick Railway Deployment Guide (Corporate Firewall Alternative)

## 🚀 Deploy Your Bot to Railway (No Local Development Required)

If your company firewall blocks ngrok, Railway provides the fastest way to deploy your bot to the cloud with zero configuration.

### **Prerequisites:**
- GitHub account
- Your bot code in a GitHub repository

### **Step 1: Prepare Your Repository**

Ensure your GitHub repository has these files:

**File: `requirements.txt`**
```txt
aiohttp==3.8.4
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
botbuilder-integration-aiohttp==4.15.0
teams-ai==1.0.0
openai==1.3.0
python-dotenv==1.0.0
```

**File: `railway.json`** (create this in your project root):
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python src/app.py",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**Update `src/app.py`** to get port from environment:
```python
import os

# At the bottom of app.py, change:
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    app.run(host="0.0.0.0", port=port, debug=False)
```

### **Step 2: Deploy to Railway**

1. **Go to** [railway.app](https://railway.app)
2. **Sign up** with GitHub account
3. **Click** "Deploy from GitHub repo"
4. **Select** your bot repository
5. **Click** "Deploy Now"

Railway will:
- ✅ Automatically detect Python project
- ✅ Install dependencies from requirements.txt
- ✅ Deploy your bot
- ✅ Provide HTTPS endpoint

### **Step 3: Configure Environment Variables**

1. **In Railway dashboard**, go to your project
2. **Click** "Variables" tab
3. **Add** these environment variables:
   ```
   BOT_ID=your-bot-id-from-teams-portal
   BOT_PASSWORD=your-bot-password-from-teams-portal
   OPENAI_API_KEY=your-openai-api-key
   ```

### **Step 4: Get Your Bot URL**

1. **In Railway dashboard**, go to "Deployments"
2. **Copy** the deployment URL (e.g., `https://your-bot.railway.app`)
3. **Your bot endpoint** will be: `https://your-bot.railway.app/api/messages`

### **Step 5: Update Teams Developer Portal**

1. **Go to** Teams Developer Portal
2. **Navigate** to your app → App features → Bot
3. **Update** "Messaging endpoint" to:
   ```
   https://your-bot.railway.app/api/messages
   ```
4. **Save** the changes

### **Step 6: Test Your Bot**

1. **Go to Teams**
2. **Search** for your bot
3. **Start chatting** - it should respond!

## 🎯 **Benefits of Railway Deployment:**

✅ **No Firewall Issues**: Runs entirely in the cloud  
✅ **Zero Configuration**: Detects Python projects automatically  
✅ **Free Tier**: 500 hours/month execution time  
✅ **Automatic HTTPS**: Secure endpoints provided  
✅ **GitHub Integration**: Auto-deploys on code changes  
✅ **Environment Variables**: Secure secret management  
✅ **Logs & Monitoring**: Built-in debugging tools  

## 🔄 **Updating Your Bot:**

1. **Push changes** to GitHub
2. **Railway auto-deploys** new version
3. **No manual intervention** required

## 💡 **Alternative Cloud Services:**

If Railway doesn't work, try these similar services:
- **Render**: render.com (similar zero-config deployment)
- **Heroku**: heroku.com (classic PaaS platform)
- **Vercel**: vercel.com (for web applications)
- **DigitalOcean App Platform**: cloud.digitalocean.com

## 🏆 **Success!**

Your bot is now running 24/7 in the cloud, accessible from Teams, with no local development or firewall restrictions!

**Next Steps:**
- Continue with Day 3 to add AI features
- Monitor your bot using Railway dashboard
- Scale resources as needed