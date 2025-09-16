# Day 1: GitHub Codespaces & Microsoft 365 Developer Setup

## 🎯 **Goal**: Set up cloud development environment and Microsoft 365 Developer Sandbox

**Time Required**: 30-45 minutes  
**Prerequisites**: GitHub account (free)  
**Outcome**: Cloud development environment with Teams bot registration ready

---

## **Step 1: Create GitHub Repository & Codespace (10 minutes)**

### 1.1 Create GitHub Repository
1. **Go to**: https://github.com
2. **Sign in** or create free account
3. **Click**: "New repository" (green button)
4. **Repository name**: `ai-learning-bot`
5. **Description**: `AI-powered learning bot for Microsoft Teams`
6. **Set**: Public (for free Codespaces hours)
7. **Check**: "Add a README file"
8. **Click**: "Create repository"

### 1.2 Launch GitHub Codespace
1. **In your new repository**, click "Code" button (green)
2. **Select**: "Codespaces" tab
3. **Click**: "Create codespace on main"
4. **Wait**: 2-3 minutes for environment setup
5. **Result**: Full VS Code environment in your browser!

**✅ Success**: You now have a cloud development environment with:
- Ubuntu Linux virtual machine
- Python 3.11 pre-installed
- VS Code web interface
- Terminal access
- Built-in ngrok tunneling

---

## **Step 2: Join Microsoft 365 Developer Program (10 minutes)**

### 1.1 Create Developer Account
1. **Go to**: https://developer.microsoft.com/microsoft-365/dev-program
2. **Click**: "Join now" button
3. **Sign in** with existing Microsoft account OR create new one
4. **Fill out** developer profile form:
   - Choose "Learning and development" 
   - Select "Microsoft Teams" as area of interest
   - Choose "Individual" for organization type

### 1.2 Set Up Instant Sandbox
1. **Select**: "Set up E5 subscription" 
2. **Choose**: "Instant sandbox" (fastest option)
3. **Configure** your sandbox:
   - **Admin username**: Choose something memorable (e.g., `admin`)
   - **Domain name**: Will be `yourname.onmicrosoft.com`
   - **Password**: Use strong password, save it securely
4. **Wait** 2-3 minutes for sandbox creation
5. **Record** your sandbox details:
   ```
   Sandbox Domain: [yourname].onmicrosoft.com
   Admin Email: admin@[yourname].onmicrosoft.com
   Admin Password: [your-password]
   ```

### 1.3 Verify Sandbox Access
1. **Go to**: https://admin.microsoft.com
2. **Sign in** with your sandbox admin credentials
3. **Verify** you can access Microsoft 365 admin center
4. **Open Teams**: https://teams.microsoft.com (sign in with sandbox account)
5. **Confirm** Teams is working in your sandbox tenant

---

## **Step 3: Set Up Development Environment in Codespace (10 minutes)**

### 3.1 Create Project Structure
```bash
# In your Codespace terminal, create project structure
mkdir -p src
mkdir -p .devcontainer
mkdir -p playground/data

# Create basic files
touch src/app.py
touch src/bot.py
touch src/config.py
touch requirements.txt
touch .env
```

### 3.2 Create DevContainer Configuration
1. **Create**: `.devcontainer/devcontainer.json`

```json
{
  "name": "AI Learning Bot",
  "image": "mcr.microsoft.com/devcontainers/python:3.11",
  "features": {
    "ghcr.io/devcontainers/features/ngrok:1": {}
  },
  "forwardPorts": [3978, 4040],
  "postCreateCommand": "pip install -r requirements.txt",
  "customizations": {
    "vscode": {
      "extensions": [
        "ms-python.python",
        "ms-python.pylint",
        "ms-python.debugpy"
      ],
      "settings": {
        "python.defaultInterpreterPath": "/usr/local/bin/python"
      }
    }
  },
  "remoteUser": "vscode"
}
```

### 3.3 Initialize Requirements
1. **Create**: `requirements.txt`

```txt
aiohttp==3.8.4
botbuilder-core==4.15.0
botbuilder-schema==4.15.0
botbuilder-integration-aiohttp==4.15.0
teams-ai==1.0.0
openai==1.3.0
python-dotenv==1.0.0
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**✅ Success**: Your cloud development environment is now configured with all necessary tools!

---

## **Step 4: Register Bot in Teams Developer Portal (15 minutes)**

### 2.1 Access Teams Developer Portal
1. **Go to**: https://dev.teams.microsoft.com/
2. **Sign in** with your **sandbox admin account**
3. **Accept** any permission prompts for Teams Developer Portal

### 2.2 Create New Teams App
1. **Click**: "Apps" in left navigation
2. **Click**: "+ New app" button
3. **Fill out** basic app information:
   ```
   App name: AI Learning Bot
   Short description: AI-powered learning assistant
   Long description: Daily quiz bot with progress tracking and adaptive learning
   Version: 1.0.0
   Developer name: [Your Name]
   Website: https://yourname.onmicrosoft.com
   Privacy policy: https://yourname.onmicrosoft.com/privacy
   Terms of use: https://yourname.onmicrosoft.com/terms
   ```
4. **Click**: "Save"

### 2.3 Configure Bot
1. **Go to**: "App features" → "Bot" in left menu
2. **Click**: "Create new bot"
3. **Fill out** bot details:
   ```
   Bot name: AI Learning Bot
   ```
4. **Click**: "Create"
5. **IMPORTANT**: Copy and save these credentials:
   ```
   Bot ID (Microsoft App ID): [copy-this-value]
   Client Secret: [will-generate-next]
   ```

### 2.4 Generate Client Secret
1. **Click**: "Generate new password" 
2. **Copy** the client secret immediately (you can't see it again)
3. **Save** securely:
   ```
   BOT_ID=[your-bot-id]
   BOT_PASSWORD=[your-client-secret]
   ```

### 2.5 Configure Bot Settings
1. **Under** "Configuration":
   - **Messaging endpoint**: Leave blank for now (will update with Codespace URL)
   - **Enable** "Messages" capability
2. **Under** "Scopes":
   - ✅ **Check** "Personal"
   - ✅ **Check** "Team" 
   - ✅ **Check** "Group Chat"

---

## **Step 3: Set Up Local Development Environment (10 minutes)**

### 3.1 Install Required Tools
1. **Install Python 3.11+**:
   ```powershell
   # Check if Python is installed
   python --version
   
   # If not installed, download from: https://python.org
   ```

2. **Install ngrok**:
   ```powershell
   # Download from: https://ngrok.com/download
   # Or use chocolatey:
   choco install ngrok
   ```

3. **Verify installations**:
   ```powershell
   python --version    # Should show 3.11+
   ngrok version       # Should show ngrok version
   ```

---

## **Step 5: Configure Environment Variables (5 minutes)**

### 5.1 Set Up Environment Configuration in Codespace
1. **In your Codespace**, create `.env` file:
   ```bash
   # Create environment file
   touch .env
   ```

2. **Edit** `.env` file with your credentials:
   ```env
   # Sandbox Bot Configuration (from Teams Developer Portal)
   BOT_ID=your-bot-id-from-step-4
   BOT_PASSWORD=your-client-secret-from-step-4
   
   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-3.5-turbo
   
   # Sandbox Settings
   ENVIRONMENT=sandbox
   STORAGE_TYPE=file
   DATA_DIRECTORY=playground/data
   LOG_DIRECTORY=playground/logs
   
   # Server Configuration
   PORT=3978
   ```

### 3.3 Get OpenAI API Key
1. **Go to**: https://platform.openai.com/
2. **Sign in** or create account
3. **Navigate** to: API Keys
4. **Click**: "Create new secret key"
5. **Copy** the key and add to `.env.sandbox`

---

## **Step 4: Update Teams App Manifest (5 minutes)**

### 4.1 Update Manifest File
1. **Open**: `appPackage/manifest.json`
2. **Update** the botId field:
   ```json
   {
     "bots": [
       {
         "botId": "your-bot-id-from-step-2",
         "scopes": ["personal", "team", "groupchat"],
         "supportsFiles": false,
         "isNotificationOnly": false
       }
     ]
   }
   ```

3. **Update** developer information:
   ```json
   {
     "developer": {
       "name": "Your Name",
       "websiteUrl": "https://yourname.onmicrosoft.com",
       "privacyUrl": "https://yourname.onmicrosoft.com/privacy",
       "termsOfUseUrl": "https://yourname.onmicrosoft.com/terms"
     }
   }
   ```

### 4.2 Update App Information
```json
{
  "name": {
    "short": "AI Learning Bot",
    "full": "AI-Powered Learning Assistant"
  },
  "description": {
    "short": "AI-powered learning assistant with daily quizzes",
    "full": "An intelligent learning bot that provides personalized daily quizzes, tracks progress, and adapts to your learning pace"
  }
}
```

---

## **Step 5: Create Sandbox Directory Structure (5 minutes)**

### 5.1 Create Sandbox Directories
```powershell
# Create playground directory structure
New-Item -Path "playground" -ItemType Directory -Force
New-Item -Path "playground/data" -ItemType Directory -Force
New-Item -Path "playground/logs" -ItemType Directory -Force
New-Item -Path "playground/backups" -ItemType Directory -Force
New-Item -Path "playground/templates" -ItemType Directory -Force

# Create tests directory
New-Item -Path "tests" -ItemType Directory -Force

# Create scripts directory
New-Item -Path "scripts" -ItemType Directory -Force
```

### 5.2 Verify Directory Structure
```
AutomatedAIpowered/
├── playground/
│   ├── data/           # User data storage
│   ├── logs/           # Application logs
│   ├── backups/        # Automated backups
│   └── templates/      # Question templates
├── tests/              # Test files
├── scripts/            # Utility scripts
├── src/                # Source code
├── appPackage/         # Teams app package
└── .env.sandbox        # Sandbox configuration
```

---

## **Step 6: Test Basic Setup (5 minutes)**

### 6.1 Install Dependencies
```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r src/requirements.txt
```

### 6.2 Test Configuration
```powershell
# Test environment loading
python -c "
import os
from dotenv import load_dotenv
load_dotenv('.env.sandbox')
print('BOT_ID:', os.getenv('BOT_ID'))
print('OPENAI_API_KEY:', 'Set' if os.getenv('OPENAI_API_KEY') else 'Missing')
print('Environment loaded successfully!')
"
```

---

## **✅ Day 1 Checklist**

Before proceeding to Day 2, verify:

- [ ] Microsoft 365 Developer sandbox created and accessible
- [ ] Bot registered in Teams Developer Portal
- [ ] Bot ID and Client Secret saved securely
- [ ] `.env.sandbox` file created with all credentials
- [ ] OpenAI API key configured
- [ ] `appPackage/manifest.json` updated with bot ID
- [ ] GitHub Codespace successfully created and configured
- [ ] DevContainer configuration working properly
- [ ] Playground directory structure created
- [ ] Python environment set up and dependencies installed
- [ ] Environment variables configured in Codespace

---

## **🚀 What's Next?**

**Day 2**: We'll set up the basic bot framework and test connectivity with Teams using the built-in Codespace tunnel. You'll have a working bot that responds to messages in your sandbox Teams environment.

---

## **💡 Troubleshooting**

### Common Issues:

**Issue**: Codespace not starting  
**Solution**: Check GitHub account status, try creating new codespace

**Issue**: DevContainer not building  
**Solution**: Check devcontainer.json syntax, rebuild container

**Issue**: Can't access Microsoft 365 Developer Program  
**Solution**: Use incognito/private browser window, clear cookies

**Issue**: Teams Developer Portal not loading  
**Solution**: Ensure you're signed in with sandbox admin account

**Issue**: OpenAI API key not working  
**Solution**: Verify key is active, check billing/usage limits

**Issue**: Port forwarding not working in Codespace  
**Solution**: Check forwarded ports tab, manually add port 3978

### Codespace-Specific Tips:
- Use the built-in terminal for all commands
- Files auto-save in cloud environment
- Can access from any device with browser
- Free tier provides 60 hours/month

### Need Help?
- Check GitHub Codespaces documentation
- Verify all credentials are copied correctly
- Ensure you're using the sandbox admin account consistently

---

**🎉 Congratulations!** You've successfully set up your cloud development environment with GitHub Codespaces. Your AI learning bot foundation is ready for development - no local installation or firewall issues!