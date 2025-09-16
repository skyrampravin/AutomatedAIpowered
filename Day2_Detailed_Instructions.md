# Day 2: Detailed Step-by-Step Instructions - Sandbox to Infrastructure Transition

## Important: Sandbox Development First
**You should have completed Day 1 with a working bot in your Microsoft 365 Developer sandbox.** Day 2 focuses on transitioning to Azure infrastructure while maintaining your sandbox environment for development and testing.

## Task 1: Review Infrastructure as Code Files (20 minutes)

### 1.1 Understanding Azure Bicep Templates
1. Open `infra/azure.bicep` in VS Code
2. Review what resources will be created:
   - **User-assigned Managed Identity**: For secure access between Azure services
   - **App Service Plan**: Linux-based hosting plan for your bot
   - **Web App**: The actual hosting environment for your Python bot
   - **Bot Registration**: Links your web app to Teams (alternative to Developer Portal bot)
3. Note the parameters required:
   - `resourceBaseName`: Base name for all resources
   - `openaiKey`: OpenAI or Azure OpenAI API key
   - `webAppSKU`: Pricing tier (B1 = Basic)
   - `botDisplayName`: Display name for your bot
   - `linuxFxVersion`: Python version (3.11)

**Sandbox Integration Note**: Your existing sandbox bot from Day 1 can continue working alongside this Azure infrastructure. You can choose which bot to use for different testing scenarios.

### 1.2 Understanding Parameters File
1. Open `infra/azure.parameters.json`
2. Notice the placeholder values with `${{}}` syntax:
   - `${{RESOURCE_SUFFIX}}`: Will be replaced with a unique suffix
   - `${{SECRET_OPENAI_API_KEY}}`: Will be replaced with your API key
3. These placeholders are filled by the Microsoft 365 Agents Toolkit during deployment

### 1.3 Bot Registration Review
1. Open `infra/botRegistration/azurebot.bicep`
2. This creates the Azure Bot resource (alternative to your Developer Portal bot from Day 1)
3. **Options**:
   - **Option A**: Use your existing sandbox bot (from Developer Portal) and skip Azure Bot creation
   - **Option B**: Create new Azure Bot for production and keep sandbox bot for development
   - **Option C**: Migrate from sandbox bot to Azure Bot completely

## Task 2: Prepare for Infrastructure Deployment (15 minutes)

### 2.1 Environment Strategy Decision
**Choose your deployment approach**:

**Option A: Sandbox-First Development (Recommended)**
- Continue using your sandbox bot for development
- Deploy Azure infrastructure for production readiness
- Use `env/.env.playground` for sandbox, `env/.env.dev` for Azure
- Test in sandbox, then promote to Azure when ready

**Option B: Azure-First Development**
- Deploy Azure infrastructure immediately
- Migrate your sandbox bot configuration to Azure Bot
- Use Azure resources for all development and testing

### 2.2 Install Prerequisites
1. **Azure CLI**: Download and install from https://docs.microsoft.com/en-us/cli/azure/install-azure-cli
2. **Verify installation**:
   ```powershell
   az --version
   ```
3. **Login to Azure**:
   ```powershell
   az login
   ```
4. **Set your subscription** (if you have multiple):
   ```powershell
   az account set --subscription "your-subscription-id"
   ```

### 2.3 Create Resource Group (if needed)
1. **Check existing resource groups**:
   ```powershell
   az group list --output table
   ```
2. **Create new resource group** (if needed):
   ```powershell
   az group create --name "AutomatedAI-RG" --location "East US"
   ```
   - Choose a location close to your users
   - Use a descriptive name for easy identification

## Task 3: Update Infrastructure Configuration (20 minutes)

### 3.1 Customize Bicep Parameters
1. Open `infra/azure.parameters.json`
2. Update values as needed:
   ```json
   {
     "$schema": "https://schema.management.azure.com/schemas/2015-01-01/deploymentParameters.json#",
     "contentVersion": "1.0.0.0",
     "parameters": {
       "resourceBaseName": {
         "value": "ailearning${{RESOURCE_SUFFIX}}"
       },
       "openaiKey": {
         "value": "${{SECRET_OPENAI_API_KEY}}"
       },
       "webAppSKU": {
         "value": "B1"
       },
       "botDisplayName": {
         "value": "AI Learning Challenge Bot"
       },
       "linuxFxVersion": {
         "value": "PYTHON|3.11"
       }
     }
   }
   ```

### 3.2 Review Bicep Template (Optional Modifications)
1. Open `infra/azure.bicep`
2. **For Azure OpenAI users**: If using Azure OpenAI instead of OpenAI, you may need to add Azure OpenAI resources:
   ```bicep
   // Add this if you want to provision Azure OpenAI in the same deployment
   resource cognitiveService 'Microsoft.CognitiveServices/accounts@2021-10-01' = {
     name: '${resourceBaseName}-openai'
     location: location
     kind: 'OpenAI'
     sku: {
       name: 'S0'
     }
     properties: {
       customSubDomainName: '${resourceBaseName}-openai'
     }
   }
   ```
3. **Storage Account**: Consider adding storage for user progress tracking:
   ```bicep
   resource storageAccount 'Microsoft.Storage/storageAccounts@2021-04-01' = {
     name: '${resourceBaseName}storage'
     location: location
     sku: {
       name: 'Standard_LRS'
     }
     kind: 'StorageV2'
   }
   ```

## Task 4: Deploy Infrastructure (30 minutes)

### 4.1 Method 1: Using Microsoft 365 Agents Toolkit (Recommended)
1. Open terminal in VS Code (Ctrl+`)
2. **Provision resources**:
   ```powershell
   # If you have Teams Toolkit CLI installed
   teamsfx provision
   ```
   Or using the VS Code extension:
   - Open Command Palette (Ctrl+Shift+P)
   - Type "Teams: Provision"
   - Select your environment (local/dev)
   - Follow the prompts

### 4.2 Method 2: Using Azure CLI Directly
1. **Navigate to your project directory**:
   ```powershell
   cd "C:\Users\rajaseharanr\AgentsToolkitProjects\AutomatedAIpowered"
   ```
2. **Deploy the Bicep template**:
   ```powershell
   az deployment group create `
     --resource-group "AutomatedAI-RG" `
     --template-file "infra/azure.bicep" `
     --parameters "infra/azure.parameters.json" `
     --parameters resourceBaseName="ailearning$(Get-Random)" `
     --parameters openaiKey="your-openai-api-key-here"
   ```
   - Replace `"your-openai-api-key-here"` with your actual OpenAI key
   - The `$(Get-Random)` adds a unique suffix to avoid naming conflicts

### 4.3 Monitor Deployment
1. **Watch deployment progress**:
   ```powershell
   # Check deployment status
   az deployment group list --resource-group "AutomatedAI-RG" --output table
   ```
2. **View in Azure Portal**:
   - Go to your resource group in Azure Portal
   - Check "Deployments" section for progress and any errors

## Task 5: Configure Environment Variables (15 minutes)

### 5.1 Get Deployed Resource Information
1. **List deployed resources**:
   ```powershell
   az resource list --resource-group "AutomatedAI-RG" --output table
   ```
2. **Get Web App details**:
   ```powershell
   az webapp show --name "your-web-app-name" --resource-group "AutomatedAI-RG"
   ```
3. **Note the Web App URL** - this will be your bot endpoint

### 5.2 Update Environment Files
1. **For Azure deployment, update `env/.env.dev`**:
   ```bash
   # Bot Configuration for Azure Environment
   BOT_ID=your_azure_bot_microsoft_app_id_here
   BOT_PASSWORD=your_azure_bot_secret_here
   TEAMS_APP_ID=your_teams_app_guid_here
   
   # Azure Infrastructure Values
   BOT_DOMAIN=your-web-app-name.azurewebsites.net
   BOT_ENDPOINT=https://your-web-app-name.azurewebsites.net/api/messages
   WEBSITE_NODE_DEFAULT_VERSION=~18
   ENVIRONMENT=dev
   ```

2. **For continued sandbox development, keep `env/.env.playground`**:
   ```bash
   # Sandbox Bot Configuration (unchanged from Day 1)
   BOT_ID=your_sandbox_microsoft_app_id_here
   BOT_PASSWORD=your_sandbox_bot_secret_here
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-3.5-turbo
   ENVIRONMENT=playground
   STORAGE_TYPE=file
   QUIZ_QUESTIONS_PER_DAY=10
   ```

3. **Update corresponding user files**:
   - **`env/.env.dev.user`** for Azure OpenAI secrets
   - **`env/.env.playground.user`** for sandbox OpenAI secrets

**Strategy**: This dual-environment approach lets you develop in sandbox and promote to Azure when ready.

## Task 6: Update Bot Messaging Endpoint (10 minutes)

### 6.1 Update Azure Bot Configuration
1. **Go to Azure Portal** → Your Bot Resource
2. **Navigate to Configuration**
3. **Update Messaging endpoint** with your Web App URL:
   ```
   https://your-web-app-name.azurewebsites.net/api/messages
   ```
4. **Click Apply** to save changes
5. **Test the endpoint** (optional):
   ```powershell
   # Test if the endpoint is reachable (should return 404 for now, which is expected)
   curl https://your-web-app-name.azurewebsites.net/api/messages
   ```

## Task 7: Verify Deployment (15 minutes)

### 7.1 Check Azure Resources
1. **Resource Group**: Verify all resources are created successfully
2. **Web App**: Check if it's running (may show 404 until code is deployed)
3. **Bot Registration**: Ensure messaging endpoint is updated
4. **Managed Identity**: Verify it's created and assigned to Web App

### 7.2 Test Environment Configuration
1. **Verify environment files are complete**
2. **Check that secrets are not in version control**:
   ```powershell
   git status
   # Ensure .env.local.user is not listed (should be in .gitignore)
   ```

## Task 8: Prepare for Day 3 (10 minutes)

### 8.1 Review Backend Code Structure
1. Open `src/bot.py` and understand the current structure
2. Open `src/app.py` and see how it handles HTTP requests
3. Open `src/config.py` and understand environment variable loading

### 8.2 Document Deployment Information
1. **Create a deployment info file**:
   ```
   Deployment Information:
   - Resource Group: AutomatedAI-RG
   - Web App Name: ailearning12345
   - Web App URL: https://ailearning12345.azurewebsites.net
   - Bot Messaging Endpoint: https://ailearning12345.azurewebsites.net/api/messages
   - Deployment Date: [Today's date]
   ```

---

## Important Notes:
- **Environment Strategy**: You can maintain both sandbox and Azure environments simultaneously
- **Keep your OpenAI/Azure OpenAI keys secure** - never commit them to git
- **Test connectivity** between services before proceeding
- **Sandbox Development**: Continue using your Day 1 sandbox bot for rapid development
- **Azure Production**: Use Azure infrastructure for production-ready deployment

## Common Issues:
- **Deployment fails**: Check resource name uniqueness and subscription limits
- **Web App not accessible**: Wait a few minutes after deployment
- **Bot endpoint not working**: Ensure the URL is correct and Web App is running
- **Authentication errors**: Verify all credentials are correctly set in environment files
- **Sandbox vs Azure confusion**: Use clear naming conventions to distinguish environments

## Success Criteria:
- ✅ All Azure resources deployed successfully (OR sandbox environment ready for Day 3)
- ✅ Web App is accessible (if deployed) or sandbox bot still working
- ✅ Bot messaging endpoint is updated (for Azure) or placeholder maintained (for sandbox)
- ✅ Environment variables are configured for chosen approach
- ✅ Ready for Day 3 bot development in either environment

**Total estimated time: 2-2.5 hours (Infrastructure) OR 30 minutes (Sandbox preparation)**

---
## Sandbox Mode Notes
| Aspect | Sandbox Adjustment |
|--------|------------------|
| **Development Approach** | Continue using Developer Portal bot from Day 1 for immediate development. Deploy Azure infrastructure when ready for production. |
| **Environment Files** | Use `env/.env.playground` for sandbox development, `env/.env.dev` for Azure deployment. |
| **Bot Endpoint** | Keep placeholder endpoint for sandbox (e.g., https://placeholder.ngrok.io/api/messages) or set up ngrok for local testing. |
| **Testing Strategy** | Develop and test features in sandbox first, then deploy to Azure infrastructure when stable. |
| **Cost Management** | Sandbox development is free; deploy Azure resources only when needed for production features. |

**Sandbox Advantage**: You can complete Days 3-5 development entirely in sandbox, then deploy infrastructure only when ready for production features like scheduling or advanced storage.
|--------|--------------------|
| Infra Deployment | Optional on Day 2—can defer full Bicep deployment; continue local+tunnel. |
| Resource Group | Skip creation if avoiding Azure costs early. |
| Parameters File | Keep placeholders; only finalize when committing to deploy. |
| Storage | Still using `STORAGE_TYPE=file`; no cloud storage required yet. |
| Validation | Ensure Day 1 bot still responds after any manifest or ID changes. |
| Migration Prep | Note desired resource names now to avoid later renaming. |

You can postpone cloud deployment until proactive messaging or persistence scalability becomes a necessity.