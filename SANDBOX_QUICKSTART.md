# Sandbox Quick Start (1-Page)

Use this compressed guide when you need to bring up the Automated AI-Powered Learning Challenge bot inside a Microsoft 365 Developer (sandbox) tenant quickly.

---
## 1. Accounts & Keys (5 min)
- Join Microsoft 365 Developer Program: https://developer.microsoft.com/microsoft-365/dev-program
- Get instant sandbox tenant (note domain: `<tenant>.onmicrosoft.com`).
- Ensure Global Admin role for initial setup.
- Obtain OpenAI (or Azure OpenAI) API key.

## 2. Create Bot Identity (Developer Portal) (5 min)
1. Go to https://dev.teams.microsoft.com (logged into sandbox admin).
2. Bot Management → Create a Bot.
3. Copy Microsoft App ID → store as `BOT_ID`.
4. Generate a client secret → store as `BOT_PASSWORD` (save immediately!).

## 3. Prepare Env File (2 min)
Create / edit `env/.env.playground` and add (DO NOT COMMIT):
```
BOT_ID=<sandbox-app-id>
BOT_PASSWORD=<sandbox-secret>
OPENAI_API_KEY=<openai-key>
OPENAI_MODEL=gpt-3.5-turbo
ENVIRONMENT=playground
STORAGE_TYPE=file
QUIZ_QUESTIONS_PER_DAY=10
```
Optional (Azure OpenAI):
```
AZURE_OPENAI_ENDPOINT=<endpoint>
AZURE_OPENAI_DEPLOYMENT=<deployment>
```

## 4. Install & Run (Python) (5–7 min)
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r src\requirements.txt
$env:ENV_FILE="env/.env.playground"
python src/app.py
```
(Optional) Tunnel:
```powershell
ngrok http 3978
```
Set messaging endpoint in Developer Portal: `https://<tunnelHost>/api/messages`.

## 5. Package Teams App (1 min)
If `scripts/package_teams_app.ps1` exists use it, otherwise manual:
```powershell
Compress-Archive -Path appPackage/* -DestinationPath sandbox-app-package.zip -Force
```

## 6. Upload to Teams (2 min)
Teams (sandbox) → Apps → Manage your apps → Upload an app → Upload for me or my teams → select `sandbox-app-package.zip`.

## 7. Smoke Test (3 min)
- Open 1:1 chat → send `hi` → expect welcome/response.
- Validate no warnings about missing env vars in console.
- Issue a sample command (if implemented) like `/enroll`.

## 8. Proactive (Manual) (Optional)
After first user message (conversation reference saved):
- POST JSON to `http://localhost:3978/api/proactive` or hosted equivalent to simulate reminder.

## 9. Done → Next
Proceed to detailed flow in `SANDBOX_SETUP.md` for deeper validation & production migration planning.

---
Checklist:
- [ ] Bot responds
- [ ] Correct Bot ID in manifest
- [ ] Env file populated
- [ ] Adaptive Card quiz prototype works (if implemented)
- [ ] Proactive test (optional)

FAST EXIT: You are sandbox-ready. Continue building features safely.
