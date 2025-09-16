# Day 1: GitHub Codespaces & Bot Framework Emulator Setup

## 🎯 **Goal**: Set up cloud development environment with local bot testing using Bot Framework Emulator

**Time Required**: 25-35 minutes  
**Prerequisites**: GitHub account (free)  
**Outcome**: Cloud development environment ready for AI bot development with local testing

---

## **Step 1: Create GitHub Repository & Codespace (10 minutes)**

### 1.1 Create GitHub Repository
1. **Go to**: https://github.com
2. **Sign in** or create free account
3. **Click**: "New repository" (green button)
4. **Repository name**: `ai-learning-bot`
5. **Description**: `AI-powered learning bot with Bot Framework Emulator testing`
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
- No external subscription requirements

---

## **Step 2: Install Bot Framework Emulator (5 minutes)**

### 2.1 Download Bot Framework Emulator
1. **Go to**: https://github.com/Microsoft/BotFramework-Emulator/releases
2. **Download**: Latest release for your operating system
   - Windows: `.exe` installer
   - macOS: `.dmg` file
   - Linux: `.AppImage` file
3. **Install** and launch the emulator

### 2.2 Verify Emulator Installation
1. **Launch** Bot Framework Emulator
2. **You should see**: Welcome screen with "Open Bot" option
3. **Keep it open** - we'll use it for testing later

**✅ Benefits of Bot Framework Emulator:**
- ✅ No Microsoft 365 subscription required
- ✅ Perfect for learning and development
- ✅ See conversation JSON and debug info
- ✅ Test all AI functionality locally
- ✅ Easy debugging and troubleshooting

---

## **Step 3: Set Up Development Environment in Codespace (10 minutes)**

### 3.1 Create Project Structure
```bash
# In your Codespace terminal, create project structure
mkdir -p src
mkdir -p .devcontainer
mkdir -p playground/data
mkdir -p playground/logs

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
  "forwardPorts": [3978],
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
openai==1.3.0
python-dotenv==1.0.0
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

**✅ Success**: Your cloud development environment is now configured for local bot testing!

---

## **Step 4: Configure Local Bot Settings (5 minutes)**

### 4.1 Set Up Environment Configuration
1. **In your Codespace**, create `.env` file:
   ```bash
   touch .env
   ```

2. **Add local testing configuration**:
   ```env
   # Local Bot Framework Emulator Configuration
   BOT_ID=00000000-0000-0000-0000-000000000000
   BOT_PASSWORD=dummy-password-for-local-testing

   # OpenAI Configuration
   OPENAI_API_KEY=your-openai-api-key
   OPENAI_MODEL=gpt-3.5-turbo

   # Local Environment Settings
   ENVIRONMENT=local-development
   STORAGE_TYPE=file
   DATA_DIRECTORY=playground/data
   LOG_DIRECTORY=playground/logs

   # Server Configuration
   PORT=3978
   BOT_EMULATOR=true
   ```

### 4.2 Get OpenAI API Key
1. **Go to**: https://platform.openai.com/
2. **Sign in** or create account
3. **Navigate** to: API Keys
4. **Click**: "Create new secret key"
5. **Copy** the key and replace `your-openai-api-key` in `.env` file

**💡 Note**: For local testing with Bot Framework Emulator, you don't need real Microsoft App ID and Password. The dummy values work perfectly for development and learning.

---

## **Step 5: Create Directory Structure (5 minutes)**

### 5.1 Create Required Directories
```bash
# Create playground directory structure
mkdir -p playground/data
mkdir -p playground/logs
mkdir -p playground/backups
mkdir -p playground/templates

# Create tests directory
mkdir -p tests

# Create scripts directory  
mkdir -p scripts
```

### 5.2 Verify Directory Structure
```
ai-learning-bot/
├── playground/
│   ├── data/           # User data storage
│   ├── logs/           # Application logs
│   ├── backups/        # Automated backups
│   └── templates/      # Question templates
├── tests/              # Test files
├── scripts/            # Utility scripts
├── src/                # Source code
├── .devcontainer/      # Codespace configuration
├── requirements.txt    # Python dependencies
└── .env               # Local configuration
```

---

## **✅ Day 1 Checklist**

Before proceeding to Day 2, verify:

### **Development Environment**
- [ ] GitHub Codespace successfully created and configured
- [ ] DevContainer configuration working properly
- [ ] Python environment set up and dependencies installed
- [ ] Project directory structure created
- [ ] Bot Framework Emulator installed on your local machine

### **Configuration**
- [ ] `.env` file created with local testing configuration
- [ ] OpenAI API key configured and valid
- [ ] Environment variables configured in Codespace
- [ ] All required directories created

### **Testing Setup**
- [ ] Bot Framework Emulator launched and ready
- [ ] Port 3978 configured for local testing
- [ ] Ready for local bot development and testing

---

## **🚀 What's Next?**

**Day 2**: We'll create the basic bot framework and test it using Bot Framework Emulator. You'll see your bot responding to commands locally while developing in the cloud!

---

## **💡 Troubleshooting**

### **Codespace Issues:**
**Issue**: Codespace not starting  
**Solution**: Check GitHub account status, try creating new codespace

**Issue**: DevContainer not building  
**Solution**: Check devcontainer.json syntax, rebuild container

**Issue**: Port forwarding not working  
**Solution**: Check forwarded ports tab, manually add port 3978

### **Bot Framework Emulator Issues:**
**Issue**: Can't download emulator  
**Solution**: Try different browser, check GitHub releases page directly

**Issue**: Emulator won't start  
**Solution**: Check system requirements, try running as administrator

### **Configuration Issues:**
**Issue**: OpenAI API key not working  
**Solution**: Verify key is active, check billing/usage limits at platform.openai.com

**Issue**: Environment variables not loading  
**Solution**: Check .env file syntax, ensure no extra spaces

### **General Tips:**
- Use the built-in Codespace terminal for all commands
- Files auto-save in cloud environment
- Can access from any device with browser
- Free tier provides 60 hours/month for Codespaces
- Bot Framework Emulator provides excellent debugging capabilities

### **Need Help?**
- Bot Framework Emulator documentation: https://docs.microsoft.com/en-us/azure/bot-service/
- GitHub Codespaces documentation: https://docs.github.com/en/codespaces
- OpenAI API documentation: https://platform.openai.com/docs

---

**🎉 Congratulations!** You've successfully set up your development environment for AI bot development with local testing. This approach gives you complete control and eliminates any subscription barriers while providing the full learning experience!