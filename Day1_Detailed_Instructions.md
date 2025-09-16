# Day 1: Detailed Step-by-Step Instructions

## Task 1: Review Project Materials (15 minutes)

### 1.1 R**Why is this needed?**  
This connects your Teams app to your sandbox bot. Teams uses this Bot ID to route messages to your bot service.  
Use the Microsoft App ID from either the Developer Portal or Azure Bot registration above.

**After updating:**  
- Save the manifest file.
- Double-check that the Bot ID matches your sandbox Bot's Microsoft App ID.

### 4.3 Update App Details for Sandbox
- Replace `${{TEAMS_APP_ID}}` with a new GUID (you can generate one online)
- Update the app name to include "(Sandbox)" to distinguish from production:
  ```json
  "name": {
      "short": "AutomatedAI (Sandbox)",
      "full": "Automated AI-Powered 30-Day Learning Challenge (Sandbox)"
  }
  ```
- Keep the existing icon referencesRequirements
- Open `instructions.txt` in your editor
- Review the goal: 30-day AI course challenge with MCQs
- Note key features: enrollment, daily questions, wrong answer tracking

### 1.2 Explore Project Structure
- Open the AutomatedAIpowered folder in VS Code
- Review these key files:
  - `appPackage/manifest.json` (Teams app configuration)
  - `src/bot.py` (main bot logic)
  - `src/config.py` (environment configuration)
  - `infra/azure.bicep` (infrastructure)
  - `env/.env.local` (environment variables)

## Task 2: Register Bot (30 minutes) - Sandbox Approach

### 2.1 Set Up Microsoft 365 Developer Sandbox (Recommended)
1. Go to https://developer.microsoft.com/microsoft-365/dev-program
2. Join the Microsoft 365 Developer Program (if not already a member)
3. Create an instant sandbox tenant
4. Note your sandbox domain (e.g., `yourdevtenant.onmicrosoft.com`)
5. Sign into Teams with your sandbox admin account

### 2.2 Create Bot via Teams Developer Portal (Preferred for Sandbox)
1. Go to https://dev.teams.microsoft.com/ (logged into sandbox)
2. Navigate to "Tools" → "Bot Management"
3. Click "Create a Bot"
4. Fill in bot details:
   - **Name**: "AI Learning Challenge Bot (Sandbox)"
   - **Description**: "30-day AI-powered learning challenge"
5. Copy the **Microsoft App ID** (this becomes your `BOT_ID`)
6. Click "Generate a client secret"
7. **IMMEDIATELY COPY** the client secret value (this becomes your `BOT_PASSWORD`)

### 2.3 Alternative: Azure Bot Resource (If You Prefer Azure Portal)
If you want to use Azure instead:
1. Go to https://portal.azure.com/ (with sandbox subscription if available)
2. Search for "Azure Bot" and select it
3. Click "Create"
4. Fill in the details:
   - **Bot handle**: Choose a unique name (e.g., "automatedai-learning-bot-sandbox")
   - **Subscription**: Select your subscription
   - **Resource group**: Create new or use existing
   - **Pricing tier**: F0 (Free) for development
   - **Microsoft App ID**: Select "Create new Microsoft App ID"
5. Click "Review + create" then "Create"

### 2.4 Get Bot Credentials (For Azure Bot Method)
1. Once deployed, go to the bot resource
2. Navigate to "Configuration" in the left menu
3. **IMPORTANT**: Copy and save these values:
   - **Microsoft App ID** (also called Bot ID)
   - Click "Manage" next to Microsoft App ID
   - In the new tab, go to "Certificates & secrets"
   - Click "New client secret"
   - Add description: "AutomatedAI Bot Secret"
   - Select expiry: 24 months
   - Click "Add"
   - **IMMEDIATELY COPY** the secret value (you won't see it again!)

## Task 3: Enable Microsoft Teams Channel (10 minutes)

### 3.1 Configure Teams Channel (Developer Portal Method)
If you used Developer Portal:
1. In the Developer Portal bot page, Teams channel is enabled by default
2. Your messaging endpoint will be set later when you have a tunnel or hosted service

### 3.2 Configure Teams Channel (Azure Bot Method)
If you used Azure Bot:
1. In your Azure Bot resource, go to "Channels"
2. Find "Microsoft Teams" channel
3. Click "Configure" or the Teams icon
4. Click "Apply" to enable it
5. Verify it shows as "Enabled"

### 3.3 Set Placeholder Endpoint (For Azure Bot Only)
If you used Azure Bot:
1. Go to "Configuration" in your bot resource
2. In "Messaging endpoint" field, enter: `https://placeholder.ngrok.io/api/messages`
3. Click "Apply" (we'll update this later with real endpoint)

## Task 4: Update Teams App Manifest (15 minutes)

### 4.1 Open Manifest File
1. In VS Code, open `appPackage/manifest.json`
2. This file defines your Teams app configuration

### 4.2 Update Bot Configuration
Find the "bots" section and update it with your Bot ID:
```json
"bots": [
    {
        "botId": "YOUR_SANDBOX_MICROSOFT_APP_ID_HERE",
        "scopes": [
            "team",
            "groupChat", 
            "personal"
        ],
        "supportsFiles": false,
        "isNotificationOnly": false,
        ...
    }
]
```
**Why is this needed?**  
This connects your Teams app to your Azure Bot. Teams uses this Bot ID to route messages to your bot service.  
Even though you store credentials in your `.env` files for your backend code, the manifest must have the actual Bot ID hardcoded so Teams knows which bot to communicate with.

**After updating:**  
- Save the manifest file.
- Double-check that the Bot ID matches your Azure Bot’s Microsoft App ID.

### 4.3 Update App Details
- Replace `${{TEAMS_APP_ID}}` with a new GUID (you can generate one online)
- Update the app name and description to reflect your learning platform
- Keep the existing icon references

## Task 5: Store Credentials Securely (10 minutes)

### 5.1 Update Sandbox Environment Files
1. Open `env/.env.playground` (this is your sandbox environment file)
2. Add your sandbox bot credentials:
```
# Sandbox Bot Configuration
BOT_ID=your_sandbox_microsoft_app_id_here
BOT_PASSWORD=your_sandbox_bot_secret_here
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
ENVIRONMENT=playground
STORAGE_TYPE=file
QUIZ_QUESTIONS_PER_DAY=10
```

3. If you are using **Azure OpenAI Service** instead of standard OpenAI, also add:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT=your-deployment-name
   ```

### 5.2 Alternative: Local Environment Files (For Testing)
You can also populate the local files if needed:
1. Open `env/.env.local.user` (create if it doesn't exist)
2. Add your credentials:
```
SECRET_OPENAI_API_KEY=your_openai_api_key_here
```

3. Open `env/.env.local`
4. Update with your bot credentials:
```
BOT_ID=your_sandbox_microsoft_app_id_here
BOT_PASSWORD=your_sandbox_bot_secret_here
```

### 5.2 Verify Security
- Check that `.env*` files are listed in `.gitignore`
- Never commit these files to version control
- Keep your credentials secure

## Task 6: Prepare and Upload Sandbox Teams App (15 minutes)

### 6.1 Create Manifest File for Sandbox
1. Open `appPackage/manifest.json`
2. Update the manifest for sandbox usage:
   - **${{TEAMS_APP_ID}}**: Replace with a new GUID (generate one online)
   - **name.short**: Add "(Sandbox)" to your app name, e.g., "AI Learning Bot (Sandbox)"
   - **name.full**: Include "(Sandbox)" here too, e.g., "AI-Powered Learning Assistant (Sandbox)"
   - Verify **bots[0].botId** has your sandbox Microsoft App ID: "YOUR_SANDBOX_MICROSOFT_APP_ID_HERE"

### 6.2 Create Teams App Package for Sandbox
1. **Option A: Use PowerShell Script (Recommended)**
   ```powershell
   # Run from project root
   .\scripts\package_teams_app.ps1
   ```

2. **Option B: Manual Packaging**
   - Select all files in the `appPackage/` folder (manifest.json, color.png, outline.png)
   - Right-click and create a ZIP file
   - Rename to `sandbox-app.zip`

### 6.3 Upload to Sandbox Teams
1. Open **Microsoft Teams** in your **Sandbox Tenant**
2. Click on **Apps** in the left sidebar
3. Click **Manage your apps** in the lower left
4. Click **Upload an app**
5. Choose **Upload a custom app**
6. Select your `sandbox-app.zip` file
7. Click **Add** to install the bot

**Note**: You are installing this in your sandbox tenant, so there are no organizational restrictions or approval processes.

## Task 7: Verify Sandbox Setup (10 minutes)

### 7.1 Check Bot Registration
- **Developer Portal Method**: Confirm your bot appears in Developer Portal with valid endpoint
- **Azure Bot Method**: Verify Azure Bot shows "Enabled" status and Teams channel is enabled
- Ensure you have both App ID and secret saved securely

### 7.2 Check Local Files
- Verify `manifest.json` has your sandbox Bot ID
- Confirm `env/.env.playground` contains your credentials
- Ensure no credentials are in version-controlled files

### 7.3 Test Teams App Installation
- Confirm the app appears in your sandbox Teams "Manage your apps" section
- Try opening a chat with the bot (it won't respond yet - that's expected)
- Verify the app name shows "(Sandbox)" to distinguish from production

## Task 8: Prepare for Day 2 (5 minutes)

## Task 8: Prepare for Day 2 (5 minutes)

### 8.1 Review Next Steps
- Read `Day2_Detailed_Instructions.md` to understand tomorrow's infrastructure tasks
- Check that you have Azure CLI installed or access to Azure portal
- Ensure your OpenAI API key is ready for integration

### 8.2 Document Issues
- Note any problems encountered today
- List any missing information or resources needed
- Prepare questions for troubleshooting

---

## Important Notes:
- **Save your Bot credentials immediately** - you cannot retrieve the secret later from Developer Portal or Azure
- **Keep credentials secure** - never commit them to git
- **Test sandbox access** - ensure you can access your M365 Developer sandbox
- **Get OpenAI key** - you'll need this for Day 4

## Common Issues:
- **M365 Developer Program access** - ensure sandbox tenant is properly set up
- **Bot name already taken** - try different unique names in Developer Portal
- **Credentials not working** - double-check copy/paste accuracy
- **Teams app upload fails** - verify manifest.json has valid botId

Total estimated time: 1.5-2 hours

---
## Sandbox Mode Notes
| Aspect | Sandbox Guidance |
|--------|------------------|
| Bot Registration | **Recommended**: Use Developer Portal for simplified sandbox workflow. Azure Bot optional. |
| Endpoint | Use placeholder endpoint (e.g., https://placeholder.ngrok.io/api/messages) until you deploy infrastructure. |
| Secrets | Store only in `env/.env.playground` (never commit to git). |
| Manifest | Add "(Sandbox)" suffix to app name to distinguish from future production deployment. |
| Next Step | Confirm Teams app installation works in sandbox tenant before moving to infrastructure on Day 2. |

**Key Advantage**: This sandbox approach allows you to test the full Teams integration without requiring Azure resource deployment, making Day 1 faster and risk-free.