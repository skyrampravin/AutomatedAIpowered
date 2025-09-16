# Microsoft 365 Developer Sandbox Setup Guide

Use this guide to run the Automated AI-Powered Learning Challenge bot fully inside a Microsoft 365 Developer (sandbox) tenant—isolated from your production organization.

---
## Phase Overview (High-Level)
| Phase | Goal | Outcome Artifacts |
|-------|------|-------------------|
| 0 | Prerequisites & Accounts | Dev Program tenant, admin user, OpenAI key |
| 1 | Bot Identity & Secrets | Bot (App ID + Secret) stored in `env/.env.playground` |
| 2 | Local Runtime & Tunneling | Bot reachable via tunnel endpoint (manual tests) |
| 3 | Teams App Packaging | `sandbox-app-package.zip` uploaded & bot responding |
| 4 | Proactive Foundations | Conversation reference captured; manual proactive POST works |
| 5 | (Optional) Azure Infra Deploy | App Service endpoint live & adopted in bot registration |
| 6 | Validation & Hardening | Checklist complete; migration path planned |

---
## Prerequisites Matrix
| Item | Required | Notes |
|------|----------|-------|
| Microsoft 365 Developer Tenant | Yes | Instant sandbox recommended |
| Global Admin Access | Yes | Needed to upload custom app / create bot |
| OpenAI or Azure OpenAI Key | Yes | For question generation |
| Azure Subscription | Optional | Only needed for hosting / infra tests |
| Tunnel Tool (ngrok/dev tunnel) | Recommended | Enables external callbacks during local dev |
| PowerShell 5+ / CLI tools | Yes | For packaging and automation |
| Python 3.8–3.11 | Yes | Runtime for bot |

---

---
## 1. Why Use a Sandbox?
| Benefit | Description |
|---------|-------------|
| Isolation | No impact on production Teams tenant/users |
| Full Admin Control | Ability to upload custom apps and configure bot channels |
| Sample Users | Pre-provisioned accounts for realistic multi-user testing |
| Safe Experimentation | Test proactive messaging, enrollment flows, scaling |

---
## 2. Create or Access a Microsoft 365 Developer Tenant
1. Visit: https://developer.microsoft.com/microsoft-365/dev-program
2. Join the Microsoft 365 Developer Program (use an existing Microsoft account).
3. Choose **Instant Sandbox** (preferred) or **Configurable sandbox**.
4. Record tenant domain (e.g., `yourtenant.onmicrosoft.com`).
5. Log into:
   - Admin Center: https://admin.microsoft.com
   - Teams Web: https://teams.microsoft.com

---
## 3. Enable Teams Developer Tools
### Developer Portal (Preferred)
1. Open https://dev.teams.microsoft.com within the sandbox session.
2. Sign in using the sandbox Global Admin user.
3. Go to: **Tools → Bot Management → Create a Bot**.
4. Provide a name (e.g., `AI Learning Challenge Bot`).
5. Copy the **Microsoft App ID** (this becomes `BOT_ID`).
6. Generate a **Client Secret**; store it securely (this becomes `BOT_PASSWORD`).

### Alternative (Legacy) – Azure Bot Channel Registration
If you prefer Azure Portal:
1. Go to https://portal.azure.com (sandbox subscription, if available).
2. Create **Azure Bot** (Channels Registration) resource.
3. Retrieve Microsoft App ID and create a Secret.
4. Enable **Microsoft Teams** channel.

---
## 4. Local Endpoint vs Hosted Endpoint
| Mode | When to Use | Messaging Endpoint Example |
|------|-------------|-----------------------------|
| Local + Tunnel | Early dev | `https://<ngrok-id>.ngrok.io/api/messages` |
| Hosted (App Service) | After infra deploy | `https://<appservice-name>.azurewebsites.net/api/messages` |

If local: run the bot + start an HTTPS tunnel (ngrok/dev tunnel) and update the bot configuration endpoint to match.

---
## 5. Configure Environment File for Sandbox
Edit `env/.env.playground` (create if missing) and populate:
```
ENVIRONMENT=playground
BOT_ID=<sandbox-microsoft-app-id>
BOT_PASSWORD=<sandbox-client-secret>
OPENAI_API_KEY=<your-openai-or-azure-openai-key>
OPENAI_MODEL=gpt-3.5-turbo
STORAGE_TYPE=file
QUIZ_QUESTIONS_PER_DAY=10
LOG_LEVEL=INFO
```
Optional (if using Azure OpenAI):
```
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_DEPLOYMENT=<deployment_name>
```

---
## 6. Update Teams App Manifest
Edit `appPackage/manifest.json`:
- Replace `botId` with `BOT_ID` from sandbox.
- Add your domain(s) under `validDomains` if hosted.
- (Optional) Generate a new GUID for the root `id` to keep sandbox app separate.

Example addition:
```json
"validDomains": [
  "<appservice-name>.azurewebsites.net",
  "<ngrok-subdomain>.ngrok.io"
]
```

Repackage for upload:
```
# From project root (PowerShell)
Compress-Archive -Path appPackage/* -DestinationPath sandbox-app-package.zip -Force
```

---
## 7. Upload App to Sandbox Teams
1. Open Teams (sandbox tenant): https://teams.microsoft.com
2. Apps → Manage your apps → **Upload an app** → **Upload for me or my teams**.
3. Select `sandbox-app-package.zip`.
4. Open a chat with the bot and send `hi` or `/help`.

---
## 8. Run the Bot Locally (Sandbox Context)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
$env:ENV_FILE="env/.env.playground"
# If your app.py loads .env automatically, ensure it points to .env.playground or copy contents to root .env temporarily
python src/app.py
```
If using dev tunnel:
```powershell
# Example using dev tunnels (if available) or ngrok
ngrok http 3978
```
Update your bot endpoint in the Developer Portal to the HTTPS tunnel.

---
## 9. Proactive Messaging Testing in Sandbox
1. Interact with the bot first (stores conversation reference).
2. Manually POST to `/api/proactive` (if implemented) with a sandbox user ID.
3. (Later) Deploy Azure Function in sandbox subscription for automated daily reminders.

---
## 10. Deploy Infra to Sandbox (Optional Early)
If you have a sandbox Azure subscription:
```powershell
az login
az group create --name rg-ai-learning-sandbox --location eastus
az deployment group create `
  --resource-group rg-ai-learning-sandbox `
  --template-file infra/azure.bicep `
  --parameters @infra/azure.parameters.json
```
Set the Web App URL as the messaging endpoint.

---
## 11. Validation Checklist
| Item | Status |
|------|--------|
| Bot responds in sandbox tenant |  |
| `/enroll` works |  |
| Daily quiz flow manual trigger |  |
| Wrong answer queue cycles |  |
| Proactive test message delivered |  |
| Streak tracking increments |  |

---
## 12. Common Sandbox Issues & Deep Dive
| Symptom | Probable Cause | Diagnostic Step | Fix |
|---------|---------------|-----------------|-----|
| 401 Unauthorized on reply | Secret mismatch or expired | Check `BOT_PASSWORD` vs portal secret timestamp | Regenerate secret & update `.env.playground` |
| Bot not found / inactive | Manifest `botId` mismatch | Open manifest and compare with Bot App ID | Update manifest & repackage |
| Proactive endpoint 200 but no user message | No conversation reference stored | Inspect logs for saved reference on initial user message | Have user send a message first, then retry proactive POST |
| Upload blocked (policy) | Not actually in sandbox tenant | Verify tenant domain in profile | Switch to sandbox M365 account |
| Adaptive Card submit ignored | Wrong activity handler or missing verb | Log incoming invoke payload | Align card action `id` / handler code |
| Tunnel disconnects frequently | Free tunnel timeouts | Observe tunnel uptime | Use dev tunnels or restart ngrok, consider hosted deploy |
| Rate limit / OpenAI errors | Exceeding RPM or invalid key | Log response error codes | Add retry/backoff, verify key correctness |
| Stale validDomains error | Missing domain in manifest | Check dev tools console in Teams | Add domain to `validDomains`, repackage |
| Teams shows old icons/name | Cached app version | Increment `version` in manifest | Re-upload package |

---
## 13. Migration Path to Production
| Phase | Action |
|-------|--------|
| 1 | Stabilize in sandbox |
| 2 | Add Table/Cosmos DB & Key Vault |
| 3 | Introduce CI/CD & monitoring |
| 4 | Register production bot & swap IDs |
| 5 | Pilot rollout & measure engagement |

---
## 14. Security & Compliance Notes
- Avoid real employee data in sandbox.
- Treat sandbox secrets as disposable.
- Do not embed secrets in code; use env vars.

---
## 15. Quick Commands Reference
```powershell
# Package Teams app
Compress-Archive -Path appPackage/* -DestinationPath sandbox-app-package.zip -Force

# Run locally with playground env
$env:ENV_FILE="env/.env.playground"; python src/app.py

# Deploy infra (optional)
az deployment group create --resource-group rg-ai-learning-sandbox --template-file infra/azure.bicep --parameters @infra/azure.parameters.json
```

---
## 16. Next Steps After Sandbox Success
1. Add persistent cloud storage.
2. Implement metrics & App Insights.
3. Add admin/reporting view.
4. Harden prompts & AI validation.
5. Prepare production governance checklist.

---
## 17. Phase Completion Gate
All of the following should be true before leaving the sandbox phase:
- [ ] Bot responds to at least one test message in personal scope
- [ ] Daily quiz simulation (manual trigger) produces Adaptive Card
- [ ] Wrong answer flow recorded and re-asked
- [ ] Manual proactive call succeeded for at least one user
- [ ] Packaging script (`package_teams_app.ps1`) produces zip without warnings
- [ ] `SANDBOX_END_TO_END.md` steps reproducible by another dev

---
*Sandbox setup complete. Continue development with confidence before production rollout.*
