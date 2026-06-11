# NoFomo — Session 2 Handoff
**Date:** 2026-06-12
**Branch:** `feat/session-1-discovery-and-ui`
**PR:** [#2](https://github.com/Maple-maker/No-Fomo/pull/2) — OPEN, merge with `gh pr merge 2 --merge`
**Last commit:** `4d4441d` — feat: onboarding redesign + custom radar thesis builder (52 files, +6,721/−313)

---

## Session Summary
Session 2 was a high-output build session that completed the onboarding redesign (Wealthstyle-style 4-page flow with auto-rotating teasers), rebuilt auth (split sign-up/sign-in, Supabase error handling, email-confirmation flow), added the notification primer screen, and built the full Custom Radar — Signal Builder feature (iOS editor + server routes + Supabase migration + push notification foundation).

## What Was Done
- [x] **Onboarding sequence** — 3 feature slides + teaser page, auto-rotating OpportunityCards, capsule indicators, gold CTA
- [x] **Auth (rebuilt)** — sign-up/sign-in modes, Supabase error surfacing, email-confirmation handling, Apple Sign-In
- [x] **Notifications** — NotificationPrimerView, silent re-registration, one-time ask pattern
- [x] **SF Symbol bug fix** — antenna.radiowaves.left.and.right.fill was invalid → replaced
- [x] **Custom Radar iOS** — CustomThesis model, 10 templates, RadarViewModel, RadarView, ThesisDetailView, ThesisEditorView, Radar tab
- [x] **Custom Radar server** — routes/thesis.ts mounted, Supabase migration (user_theses + thesis_matches), push route, signal expansion foundation
- [x] **Verified** — xcodebuild clean build, fresh-install simulator run, secret scan clean

## Where Things Stand

| Task | Status | Progress | Notes |
|------|--------|----------|-------|
| Onboarding sequence | complete | 100% | Verified on simulator |
| Auth system | complete | 100% | Both modes working |
| Notifications primer | complete | 100% | Permission flow done |
| Custom Radar iOS | complete | 100% | Editor, list, detail, tab |
| Custom Radar server | complete | 100% | Routes mounted, DB migrated |
| radar→thesis notify hook | incomplete | 0% | **Must be done next session** |
| Vercel env config | incomplete | 0% | INTERNAL_BASE_URL / NOTIFY_URL |
| End-to-end thesis test | not-started | 0% | Full flow verification |
| Physical device pass | not-started | 0% | Real APNs |
| Server-side thesis limit | not-started | 0% | Client-only cap needs backend enforcement |

## Code State
- **Branch:** `feat/session-1-discovery-and-ui` (pushed, tracking origin)
- **Last commit:** `4d4441d` — feat: onboarding redesign + custom radar thesis builder
- **Working tree:** clean (all committed)
- **Server:** `NoFomo/NoFomo/server/`, running on port 3001 (TS) and 3002 (Python MVP)
- **Build:** clean on xcodebuild

## Next Actions (Prioritized)

### P0 — Session Start
1. **Merge PR #2** — `gh pr merge 2 --merge` (skip `--delete-branch`). Watch Vercel auto-deploy.
2. **Wire radar→thesis notify hook** — Add fire-and-forget call to `POST /thesis/notify-check` after `radar_opportunities` upsert in `radar.ts`. Without this, active theses never get push notifications. See Task 4 in the Custom Radar handoff plan for the code snippet.
3. **Set Vercel env vars** — `INTERNAL_BASE_URL` and `NOTIFY_URL` in Vercel project settings. Then verify `GET /thesis/templates` returns 10 templates on the deployed URL.

### P1 — Before Beta
4. **End-to-end thesis verification** — Create thesis in editor → row in `user_theses` → `POST /thesis/match` returns opportunities → trigger radar → `thesis_matches` row + APNs push → toggle inactive stops pushes → RLS blocks cross-user access.
5. **Physical device pass** — Real Apple Sign-In + APNs token registration (simulator can't fully verify; 5 tokens already in `push_tokens`).
6. **Server-side thesis limit** — Free tier 1-active-thesis cap is currently client-only (`RadarViewModel.save`). Need API or Supabase policy enforcement.

### P2 — When Ready
7. **Forgot-password flow** — Not implemented yet.
8. **Password-rule hint** — Supabase default is min 6 chars, no hint shown to user.

### Backlog (pull from when above is done)
- `ROADMAP_TO_BETA.md`
- `API_SOURCES_TODO.md`
- `SIGNAL_EXPANSION_TODO.md`

## Blockers
- None currently. Supabase service role key is set. Server is running.

## Key Decisions
- **Free tier thesis cap:** 1 active thesis, enforced client-side (needs backend enforcement in P1)
- **Notification primer:** Only asks once, gated by `@AppStorage("hasSeenNotificationPrimer")`
- **PR #2 merge:** Triggers Vercel auto-deploy — be aware when merging

## Gotchas Carried Forward
- Run `xcodegen generate` after **adding** new Swift files (edits don't need it) or build fails with "cannot find X in scope"
- Invalid SF Symbol names compile clean and render blank — always screenshot-verify new icons
- Simulator keychain survives app uninstall → use `xcrun simctl keychain booted reset` for fresh onboarding test
- Parallel opencode agents can restructure repo and orphan files — commit/push promptly
- Server lives at nested path: `NoFomo/NoFomo/server/`
