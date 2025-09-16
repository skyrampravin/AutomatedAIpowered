# Day 2 Checklist - AutomatedAIpowered Project - Sandbox to Infrastructure Transition

## Pre-requisites Check ✓/✗
- [ ] Day 1 completed (sandbox bot working in Teams)
- [ ] Azure CLI installed and accessible (if deploying infrastructure)
- [ ] Active Azure subscription with permissions to create resources (if deploying)
- [ ] Internet connection and Azure Portal access
- [ ] OpenAI or Azure OpenAI API key ready

## Environment Strategy Decision ✓/✗
**Choose your approach for Day 2:**

### Option A: Sandbox-First Development (Recommended)
- [ ] Continue using Day 1 sandbox bot for development
- [ ] Use `env/.env.playground` for all Day 3-5 development
- [ ] Deploy Azure infrastructure later (optional)
- [ ] Skip to Day 3 if choosing this approach

### Option B: Azure Infrastructure Deployment
- [ ] Deploy Azure infrastructure immediately
- [ ] Set up dual environment (sandbox + Azure)
- [ ] Use `env/.env.dev` for Azure environment
- [ ] Complete all deployment tasks below

---

## Task 1: Review Infrastructure as Code Files
**Estimated Time: 20 minutes**

### 1.1 Azure Bicep Template Review
- [ ] Opened and reviewed `infra/azure.bicep`
- [ ] Understood resources to be created:
  - [ ] User-assigned Managed Identity
  - [ ] App Service Plan (Linux)
  - [ ] Web App (Python hosting)
  - [ ] Bot Registration (alternative to Day 1 sandbox bot)
- [ ] Noted required parameters and their purposes
- [ ] Reviewed resource naming conventions

### 1.2 Parameters File Review
- [ ] Opened and reviewed `infra/azure.parameters.json`
- [ ] Understood placeholder syntax (`${{}}`)
- [ ] Identified values that need customization

### 1.3 Bot Registration Decision
- [ ] Reviewed `infra/botRegistration/azurebot.bicep`
- [ ] **Decision Made**:
  - [ ] Keep using sandbox bot from Day 1
  - [ ] Create new Azure Bot for production
  - [ ] Migrate completely from sandbox to Azure Bot

**Notes/Issues:**
```
[Add any notes about the infrastructure setup or questions]
```

---

## Task 2: Prepare for Infrastructure Deployment (Skip if using Sandbox-First)
**Estimated Time: 15 minutes**

### 2.1 Prerequisites Installation
- [ ] Azure CLI installed
- [ ] Verified Azure CLI version: ________________
- [ ] Successfully logged into Azure: `az login`
- [ ] Set correct subscription (if multiple available)
- [ ] Current subscription verified: ________________

### 2.2 Resource Group Preparation
- [ ] Listed existing resource groups
- [ ] Created new resource group (if needed):
  - [ ] Resource Group Name: ________________
  - [ ] Location: ________________
  - [ ] Creation successful

**Azure Setup Status:**
```
Azure CLI Version: [VERSION]
Logged in: [YES/NO]
Subscription ID: [SUBSCRIPTION_ID]
Resource Group: [RG_NAME]
Location: [LOCATION]
```

---

## Task 3: Update Infrastructure Configuration
**Estimated Time: 20 minutes**

### 3.1 Bicep Parameters Customization
- [ ] Opened `infra/azure.parameters.json`
- [ ] Updated `resourceBaseName` for your project
- [ ] Verified `botDisplayName` is appropriate
- [ ] Confirmed `webAppSKU` (B1 recommended for dev)
- [ ] Verified `linuxFxVersion` (Python 3.11)
- [ ] Saved parameters file

### 3.2 Optional Bicep Modifications
- [ ] Reviewed main Bicep template for modifications
- [ ] Added Azure OpenAI resources (if using Azure OpenAI)
- [ ] Added Storage Account (if needed for user data)
- [ ] Saved any Bicep template changes

**Configuration Updates:**
```
Resource Base Name: [NAME]
Bot Display Name: [NAME]
Additional Resources Added: [LIST]
Modifications Made: [DESCRIBE]
```

---

## Task 4: Deploy Infrastructure
**Estimated Time: 30 minutes**

### 4.1 Deployment Method Selection
- [ ] Chose deployment method:
  - [ ] Microsoft 365 Agents Toolkit (recommended)
  - [ ] Azure CLI directly

### 4.2 Deployment Execution
- [ ] Started deployment process
- [ ] Provided required parameters
- [ ] Monitored deployment progress
- [ ] Deployment completed successfully
- [ ] No deployment errors encountered

### 4.3 Deployment Verification
- [ ] Checked Azure Portal for created resources
- [ ] Verified all expected resources are present
- [ ] Noted any warnings or issues

**Deployment Results:**
```
Deployment Method: [TOOLKIT/CLI]
Start Time: [TIME]
End Time: [TIME]
Status: [SUCCESS/PARTIAL/FAILED]
Resources Created: [COUNT]
Web App Name: [NAME]
Web App URL: [URL]
Issues Encountered: [LIST]
```

---

## Task 5: Configure Environment Variables
**Estimated Time: 15 minutes**

### 5.1 Gather Resource Information
- [ ] Listed all deployed resources
- [ ] Retrieved Web App name and URL
- [ ] Identified bot messaging endpoint URL
- [ ] Gathered any additional connection strings needed

### 5.2 Update Environment Files
- [ ] Updated `env/.env.local` with:
  - [ ] BOT_DOMAIN (Web App domain)
  - [ ] BOT_ENDPOINT (messaging endpoint URL)
  - [ ] Additional Azure resource configurations
- [ ] Updated `env/.env.local.user` with:
  - [ ] OpenAI API key (if using OpenAI)
  - [ ] Azure OpenAI credentials (if using Azure OpenAI)
- [ ] Verified all secrets are properly configured
- [ ] Ensured no credentials are in version control

**Environment Configuration:**
```
BOT_DOMAIN: [DOMAIN]
BOT_ENDPOINT: [FULL_URL]
API Keys Configured: [OPENAI/AZURE_OPENAI/NONE]
Environment Files Updated: [YES/NO]
Security Check Passed: [YES/NO]
```

---

## Task 6: Update Bot Messaging Endpoint
**Estimated Time: 10 minutes**

### 6.1 Azure Bot Configuration Update
- [ ] Accessed Azure Bot resource in portal
- [ ] Navigated to Configuration section
- [ ] Updated messaging endpoint with Web App URL
- [ ] Applied configuration changes
- [ ] Verified endpoint update was saved

### 6.2 Endpoint Testing
- [ ] Tested endpoint accessibility (optional)
- [ ] Documented endpoint URL for reference

**Bot Configuration:**
```
Bot Resource Name: [NAME]
Old Endpoint: [OLD_URL]
New Endpoint: [NEW_URL]
Update Successful: [YES/NO]
Endpoint Tested: [YES/NO]
```

---

## Task 7: Verify Deployment
**Estimated Time: 15 minutes**

### 7.1 Azure Resources Verification
- [ ] Resource Group contains all expected resources
- [ ] Web App is in "Running" state
- [ ] Bot registration is properly configured
- [ ] Managed Identity is created and assigned
- [ ] No error status on any resources

### 7.2 Configuration Verification
- [ ] Environment files are complete and accurate
- [ ] Secrets are not in version control
- [ ] Bot messaging endpoint is correctly set
- [ ] All resource URLs are documented

**Verification Results:**
```
All Resources Present: [YES/NO]
Web App Status: [RUNNING/STOPPED/ERROR]
Bot Configuration: [COMPLETE/INCOMPLETE]
Environment Setup: [COMPLETE/INCOMPLETE]
Security Check: [PASSED/FAILED]
```

---

## Task 8: Prepare for Day 3
**Estimated Time: 10 minutes**

### 8.1 Backend Code Review
- [ ] Reviewed `src/bot.py` structure
- [ ] Reviewed `src/app.py` HTTP handling
- [ ] Reviewed `src/config.py` environment loading
- [ ] Identified areas for Day 3 development

### 8.2 Documentation and Planning
- [ ] Created deployment information document
- [ ] Listed all resource names and URLs
- [ ] Noted any issues or considerations for Day 3
- [ ] Prepared development environment for coding

**Day 3 Preparation:**
```
Code Structure Understood: [YES/NO]
Development Environment Ready: [YES/NO]
Resources Documented: [YES/NO]
Issues to Address: [LIST]
```

---

## Overall Day 2 Status

### Summary
- [ ] All infrastructure deployed successfully
- [ ] Environment variables configured properly
- [ ] Bot messaging endpoint updated
- [ ] No critical issues blocking Day 3
- [ ] Ready to proceed with bot development

### Resource Information
```
Resource Group: [NAME]
Web App Name: [NAME]
Web App URL: [URL]
Bot Messaging Endpoint: [URL]
Storage Account: [NAME_IF_CREATED]
Azure OpenAI Resource: [NAME_IF_CREATED]
```

### Issues Encountered
```
[List any problems, solutions, or items that need follow-up]

1. 
2. 
3. 
```

### Missing Items
```
[List anything that couldn't be completed and why]

1. 
2. 
3. 
```

### Time Taken
```
Planned: 2-2.5 hours
Actual: _____ hours
```

### Next Day Prerequisites
- [ ] All Azure resources are running
- [ ] Environment variables are complete
- [ ] Bot endpoint is configured
- [ ] Development environment is ready
- [ ] Python dependencies are ready to install

---

**Checklist completed by:** ________________  
**Date:** ________________  
**Ready for Day 3:** YES / NO  

**Day 2 Status: COMPLETE / PARTIAL / BLOCKED**

### Deployment Summary
```
Total Resources Created: [NUMBER]
Total Cost Impact: [ESTIMATED_MONTHLY]
Security Posture: [GOOD/NEEDS_ATTENTION]
Scalability: [READY/NEEDS_REVIEW]
Ready for Development: [YES/NO]
```

---
## Sandbox Mode Checklist Addendum (Day 2)
- [ ] Chose to defer full Azure deployment (if staying tunnel-only)
- [ ] Recorded intended future resourceBaseName for consistency
- [ ] Verified local bot still functions in sandbox after any manifest edits
- [ ] `env/.env.playground` remains source of truth (no prod keys mixed)
- [ ] Documented which infra components will actually be needed (App Service? Storage?)
- [ ] Decided on storage migration target (Azure Table vs Cosmos) for later Day 5/7 planning

Notes:
```
Sandbox decision log for infra scope.
```