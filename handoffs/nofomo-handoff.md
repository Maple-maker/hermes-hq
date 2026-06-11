# AEGIS Handoff — NoFomo
## Date: 2026-06-05

---

## What Was Done (Recent Sessions)
- Connected ERA Context MCP for live financial data (24 accounts, tools working)
- Created FINANCIAL_SNAPSHOT.md with LES + ERA data
- Updated dashboard API spec with /api/v1/financials and /api/v1/era/* endpoints
- Added VPS operations Section 8 to config.yaml (crash prevention)
- Rebuilt CSV with 109 army equipment rows linked to Google Drive images
- Uploaded 27 real equipment photos to Google Drive (Wikimedia Commons)
- Set up Claude Code course tracker (6 courses, Mon/Wed/Fri 18:00 UTC checks)
- AnyAPI free tier configured, sequential council + retry logic implemented
- iOS app stripped of 399 lines mock data, calls 72.61.206.167:3002/radar
- Frontend rework handoff spec written (Max Johnson 13 design tips integrated)
- Dashboard API spec written (FastAPI port 3003)
- AEGIS handoff system created (template, prompt, SOP)

## Last Commit
```
cce677a — add AEGIS handoff system: template, prompt, SOP, project registry
```

## What's Next (Priority Order)
1. **Build Dashboard API** — FastAPI on port 3003 per spec at `/opt/data/hermes-hq/tasks/aegis-dashboard-api-spec.md`. This is the read-only aggregation layer. Hand off to Claude Code.
2. **iOS app clean build verification** — User still reports build failures. All code fixes committed but needs clean build confirmation. Debug chain: clean build folder, remove derived data, fresh sim.
3. **Wire up Jelly Signals module** — Kalshi, CoinGecko, Binance integrations + orchestration layer + scoring (0-100). Depends on dashboard API for signal display.

## Blockers
- **iOS build failures** — User can't get clean build. May be Xcode cache issue or code signing. Needs debugging session.
- **Supabase service role key missing** — Dashboard API can't write opportunities. Get from supabase dashboard.
- **NoFomo TS server port conflict** — Shares port 3001 with Hermes gateway. Needs port change to 3004 or consolidation.

## Key Decisions
- **AnyAPI over OpenRouter** — Billing issue on OpenRouter. AnyAPI free tier works for multi-model access.
- **Dashboard API separate from NoFomo server** — Read-only on port 3003, doesn't touch the radar pipeline.
- **Two-server architecture maintained** — TypeScript (3001) for LLM council, Python (3002) for fast rule-based radar. Dashboard (3003) for read-only aggregation.
- **Superpowers for new projects** — brainstorm → plan → TDD build → review → commit.

## Files Modified This Session
| File | Change Summary |
|---|---|
| `/opt/data/FINANCIAL_SNAPSHOT.md` | Created — LES May 2026 + ERA balances |
| `/opt/data/hermes-hq/tasks/aegis-dashboard-api-spec.md` | Added financials + ERA endpoints |
| `/opt/data/hermes-hq/handoffs/` | Created — template, prompt, SOP |
| `/opt/data/config.yaml` | VPS operations Section 8 |

## Environment / Context
- **Branch:** main (all repos)
- **Servers:** 3001 (TS gateway, PM2), 3002 (Python MVP, PM2), 3003 (dashboard — not yet built)
- **ERA Context:** Connected at https://context.era.app — working
- **ElevenLabs TTS:** Connected, "aegis voice mkv" active
- **API keys:** AnyAPI (free tier), Brave, ElevenLabs — all in .env
- **Supabase:** URL configured, missing service role key

## Notes for Next Session
- The dashboard API spec is complete and ready for Claude Code handoff
- The iOS app needs a clean build debugging session — this has been blocked for a while
- Jelly Signals content from YouTube video (Jelly Cubes) mapped to NoFomo stack — 5 new integrations identified
- User's next pay: ~$2,779.31 on the 15th (semimonthly)
