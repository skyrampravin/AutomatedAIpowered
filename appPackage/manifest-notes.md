# Manifest Guidance (Sandbox vs Production)

Since `manifest.json` cannot contain comments, use this reference when adjusting for sandbox or production.

## Fields To Adjust
| Field | Sandbox Action | Production Action |
|-------|----------------|-------------------|
| `id` | (Optional) Generate new GUID to differentiate from production | Stable GUID for versioned rollout |
| `version` | Increment whenever packaging new build | Increment per release policy |
| `bots[0].botId` | Set to sandbox Bot (Microsoft App) ID | Set to production Bot ID |
| `validDomains` | Include tunnel host or `<appservice>.azurewebsites.net` | Include production domains / custom DNS |
| `name.short` / `name.full` | Append `(Sandbox)` suffix if desired | Remove sandbox suffix |

## Update Procedure
1. Open `appPackage/manifest.json`.
2. Replace `botId` with value of `BOT_ID` from `.env.playground` (sandbox) or production env file.
3. Add domains:
```json
"validDomains": [
  "<tunnel-subdomain>.ngrok.io",
  "<appservice-name>.azurewebsites.net"
]
```
4. Increment `version` (e.g., `1.0.1`).
5. Repackage (see packaging script) and upload to Teams.

## Validation Checklist
- [ ] Bot responds after upload
- [ ] No domain warnings in Teams client
- [ ] Commands appear (if defined)
- [ ] App name reflects correct environment

## Migration Hint
Keep a separate copy of production manifest (or branch) to avoid accidental sandbox ID leakage into production packages.
