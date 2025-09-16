# Day 1 Checklist - AutomatedAIpowered Project

## Pre-requisites Check ✓/✗
- [ ] Visual Studio Code installed
- [ ] Azure subscription access
- [ ] Microsoft 365 account for development
- [ ] Internet connection and browser access
- [ ] OpenAI account and API key ready

---

## Task 1: Review Project Materials
**Estimated Time: 15 minutes**

- [ ] 1.1 Read `instructions.txt` completely
- [ ] 1.2 Review `Project_Documentation.md` 
- [ ] 1.3 Explore project folder structure
- [ ] 1.4 Open and review `appPackage/manifest.json`
- [ ] 1.5 Open and review `src/bot.py`
- [ ] 1.6 Open and review `src/config.py`
- [ ] 1.7 Open and review `infra/azure.bicep`
- [ ] 1.8 Understand the project goal and workflow

**Notes/Issues:**
```
[Add any notes about what you learned or issues encountered]
```

---

## Task 2: Register Azure Bot Resource
**Estimated Time: 30 minutes**

### 2.1 Azure Portal Access
- [ ] Successfully logged into https://portal.azure.com/
- [ ] Verified active Azure subscription
- [ ] Can create resources in subscription

### 2.2 Create Azure Bot Resource
- [ ] Navigated to "Create a resource"
- [ ] Found and selected "Azure Bot"
- [ ] Filled in bot details:
  - [ ] Bot handle: ________________
  - [ ] Subscription selected
  - [ ] Resource group: ________________
  - [ ] Pricing tier: F0 (Free)
  - [ ] Microsoft App ID: "Create new"
- [ ] Successfully created bot resource
- [ ] Bot deployment completed without errors

### 2.3 Get Bot Credentials
- [ ] Navigated to bot Configuration page
- [ ] Copied Microsoft App ID: ________________
- [ ] Clicked "Manage" next to Microsoft App ID
- [ ] Navigated to "Certificates & secrets"
- [ ] Created new client secret
- [ ] Copied client secret value: ________________
- [ ] **CRITICAL**: Secret is saved securely (you cannot retrieve it again!)

**Credentials Recorded:**
```
Microsoft App ID: [RECORDED SECURELY]
Client Secret: [RECORDED SECURELY]
Resource Group: [NAME HERE]
Bot Handle: [NAME HERE]
```

---

## Task 3: Enable Microsoft Teams Channel
**Estimated Time: 10 minutes**

- [ ] 3.1 Navigated to bot "Channels" section
- [ ] 3.2 Found Microsoft Teams channel
- [ ] 3.3 Clicked configure/enable Teams channel
- [ ] 3.4 Applied configuration successfully
- [ ] 3.5 Verified Teams channel shows "Enabled" status
- [ ] 3.6 Set placeholder messaging endpoint: `https://placeholder.ngrok.io/api/messages`
- [ ] 3.7 Applied endpoint configuration

**Channel Status:**
```
Microsoft Teams: [Enabled/Disabled]
Messaging Endpoint: [URL SET]
```

---

## Task 4: Update Teams App Manifest
**Estimated Time: 15 minutes**

- [ ] 4.1 Opened `appPackage/manifest.json` in VS Code
- [ ] 4.2 Generated new GUID for TEAMS_APP_ID
- [ ] 4.3 Replaced `${{BOT_ID}}` with actual Microsoft App ID
- [ ] 4.4 Updated bot configuration section
- [ ] 4.5 Updated app name and description appropriately
- [ ] 4.6 Verified icon file references are correct
- [ ] 4.7 Saved manifest.json file

**Manifest Updates:**
```
New TEAMS_APP_ID: [GUID HERE]
Bot ID updated: [YES/NO]
App name: [NEW NAME]
```

---

## Task 5: Store Credentials Securely
**Estimated Time: 10 minutes**

### 5.1 Environment File Updates
- [ ] Created/opened `env/.env.local.user`
- [ ] Added SECRET_OPENAI_API_KEY (if available)
- [ ] Opened `env/.env.local`
- [ ] Added BOT_ID with Microsoft App ID
- [ ] Added BOT_PASSWORD with client secret
- [ ] Added TEAMS_APP_ID with new GUID

### 5.2 Security Verification
- [ ] Verified `.env*` files are in `.gitignore`
- [ ] Confirmed no credentials are in version control
- [ ] Double-checked all credentials are correctly entered

**Environment Files Updated:**
```
.env.local: [UPDATED/NOT_UPDATED]
.env.local.user: [CREATED/UPDATED]
Credentials secured: [YES/NO]
```

---

## Task 6: Verify Setup
**Estimated Time: 10 minutes**

### 6.1 Azure Resource Verification
- [ ] Azure Bot resource shows healthy status
- [ ] Teams channel is enabled and working
- [ ] Messaging endpoint is set (placeholder)
- [ ] Resource group contains bot resource

### 6.2 Local File Verification
- [ ] manifest.json contains correct Bot ID
- [ ] Environment files contain all required credentials
- [ ] No sensitive data in git-tracked files
- [ ] Project structure is intact

**Verification Results:**
```
Azure Bot Status: [HEALTHY/ISSUES]
Local Files Status: [COMPLETE/MISSING_ITEMS]
Security Check: [PASSED/FAILED]
```

---

## Task 7: Prepare for Day 2
**Estimated Time: 5 minutes**

- [ ] 7.1 Read `day2.txt` for tomorrow's tasks
- [ ] 7.2 Verified Azure CLI access or portal access for infrastructure
- [ ] 7.3 Confirmed OpenAI API key availability
- [ ] 7.4 Documented any issues or questions

**Day 2 Preparation:**
```
Azure CLI ready: [YES/NO]
OpenAI key ready: [YES/NO]
Questions for tomorrow: [LIST ANY]
```

---

## Overall Day 1 Status

### Summary
- [ ] All tasks completed successfully
- [ ] All credentials secured properly
- [ ] No critical issues blocking Day 2
- [ ] Ready to proceed with infrastructure setup

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

---
## Sandbox Mode Checklist Addendum (Day 1)
- [ ] Using Microsoft 365 Developer sandbox tenant (not production)
- [ ] Bot created via Developer Portal (optional alternative to Azure Bot)
- [ ] `env/.env.playground` prepared (even if `env/.env.local` also exists)
- [ ] Placeholder endpoint uses tunnel or dummy host (acceptable for now)
- [ ] Decided whether to suffix app name with `(Sandbox)`
- [ ] No production secrets present in playground file
- [ ] Read `SANDBOX_QUICKSTART.md`
- [ ] Logged raw Bot ID & secret location in secure notes

Notes:
```
Add any sandbox-specific observations or decisions.
```

### Time Taken
```
Planned: 1.5-2 hours
Actual: _____ hours
```

### Next Day Prerequisites
- [ ] Azure CLI installed/accessible
- [ ] OpenAI API key obtained
- [ ] Resource group and subscription confirmed
- [ ] Bot credentials tested and working

---

**Checklist completed by:** ________________  
**Date:** ________________  
**Ready for Day 2:** YES / NO  

**Day 1 Status: COMPLETE / PARTIAL / BLOCKED**