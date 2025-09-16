# Sandbox End-to-End Execution Guide

This document stitches together every step—from zero to a validated sandbox run—using the artifacts in this repository.

---
## 0. Outcomes You Will Achieve
By the end you will have:
- A Microsoft 365 sandbox tenant with the bot installed
- Local runtime or hosted endpoint responding inside Teams
- Configured environment + validation logs clean
- A packaged Teams app (`sandbox-app-package.zip`)
- (Optional) Manual proactive message test completed

---
## 1. Provision & Identity
| Step | Action | Artifact |
|------|--------|----------|
| 1.1 | Join Dev Program & get instant sandbox | Dev Program Portal |
| 1.2 | Create Bot in Developer Portal | Microsoft App ID + Secret |
| 1.3 | Store credentials (do NOT commit) | `env/.env.playground` |
| 1.4 | (Optional) Reserve Azure subscription | Azure Portal |

---
## 2. Environment Configuration
1. Open `env/.env.playground` and populate required variables (see template comments).
2. Decide provider path:
   - Standard OpenAI: Set `OPENAI_API_KEY` + `OPENAI_MODEL`.
   - Azure OpenAI: Set `OPENAI_API_KEY` (or `AZURE_OPENAI_API_KEY` if adapted), plus `AZURE_OPENAI_ENDPOINT` & `AZURE_OPENAI_DEPLOYMENT`.
3. Keep `STORAGE_TYPE=file` for sandbox simplicity.
4. (Optional) Adjust `QUIZ_QUESTIONS_PER_DAY`.

Validation on start will warn about missing items.

---
## 3. Install Dependencies & Run Locally
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
$env:ENV_FILE="env/.env.playground"
python src/app.py
```
If using a tunnel:
```powershell
ngrok http 3978
```
Update messaging endpoint in Developer Portal to: `https://<tunnelHost>/api/messages`.

---
## 4. Manifest Preparation
1. Review `appPackage/manifest-notes.md` for guidance.
2. Set `botId` to your sandbox `BOT_ID`.
3. Add any domains to `validDomains`.
4. Increment `version` if repackaging.

---
## 5. Packaging
Preferred:
```powershell
pwsh scripts/package_teams_app.ps1 -Force
```
Manual fallback:
```powershell
Compress-Archive -Path appPackage/* -DestinationPath sandbox-app-package.zip -Force
```

---
## 6. Upload to Teams
Teams (sandbox) → Apps → Manage your apps → Upload an app → Upload for me or my teams → choose the zip.

Validate:
- Open 1:1 chat → send `hi`.
- Confirm bot replies.

---
## 7. Quiz / Feature Smoke (If Implemented)
| Test | Expectation |
|------|-------------|
| Enrollment command | Acknowledgement message |
| Daily quiz trigger (manual) | Adaptive Card with MCQs |
| Wrong answer cycle | Re-asked in subsequent test invocation |

---
## 8. Proactive Messaging (Manual Exercise)
1. Send at least one message in chat (saves conversation reference).
2. Use a REST client to POST to `http://localhost:3978/api/proactive` with a JSON body (structure depends on implementation stub).
3. Confirm Teams chat receives proactive message.

---
## 9. Optional Azure Hosting
Deploy infrastructure (if subscription available):
```powershell
az group create --name rg-ai-learning-sandbox --location eastus
az deployment group create --resource-group rg-ai-learning-sandbox --template-file infra/azure.bicep --parameters @infra/azure.parameters.json
```
Set messaging endpoint to the resulting App Service URL.

---
## 10. Validation Checklist
| Item | Status |
|------|--------|
| Bot responds in sandbox |  |
| Manifest botId correct |  |
| Tunnel/hosted endpoint stable |  |
| Env validation no critical warnings |  |
| Quiz flow smoke tested |  |
| Proactive manual test (optional) |  |
| Packaging script success output |  |

---
## 11. Exit Criteria for Sandbox Phase
All validation items checked PLUS decision recorded for production storage & monitoring strategy.

---
## 12. Migration Preview
| Sandbox Element | Production Replacement |
|-----------------|------------------------|
| `STORAGE_TYPE=file` | Azure Table / Cosmos DB |
| Local secrets in env file | Key Vault / secure pipeline vars |
| Manual packaging | Automated CI/CD (GitHub Actions) |
| Manual proactive test | Scheduled Azure Function / Logic App |
| Basic logging | Application Insights telemetry |

---
## 13. References
- `SANDBOX_QUICKSTART.md` (fast path)
- `SANDBOX_SETUP.md` (deep guide)
- `appPackage/manifest-notes.md` (manifest deltas)
- `scripts/package_teams_app.ps1` (packaging automation)

---
You now have a complete sandbox baseline. Proceed to harden for production following the migration table.
