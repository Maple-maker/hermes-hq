# /ship-check — Pre-Launch Bug Prevention

> **Source:** Instagram reel transcript — "5 things that break when you ship a Claude Code app"
> **Use:** Run before every TestFlight / App Store submission. Fix all 5 categories before users see the app.
> **Applies to:** NoFomo iOS app, any web app, any Claude Code-built project

---

## The 5 Categories (in order of user-facing severity)

### 1. Dead Links, Broken Images, No 404 Page

**What breaks:** User clicks a link → blank page or browser error. No feedback. They leave.

**Fix:**
- Build a custom 404 page with: friendly message + navigation back to home + search bar
- For images: always have fallback/placeholder + alt text
- For links: validate all internal links before ship; external links open in new tab with `rel="noopener"`

**Claude Code prompt:**
```
Build a custom 404 error page for my app. Include: friendly "page not found" message, 
navigation back to home, and a search bar. Make it match the app's dark theme. 
Also add image fallbacks for all image components — if an image fails to load, 
show a placeholder with alt text instead of a broken icon.
```

---

### 2. Silent Bugs (No Error Tracking)

**What breaks:** App crashes or behaves wrong. User leaves 1-star review. You never know why.

**Fix:**
- Set up Sentry (or similar) for error tracking
- Every crash/bug auto-sends full trace to you
- Feed trace back into Claude Code → fix → redeploy

**Claude Code prompt:**
```
Set up Sentry error tracking for my iOS app. I want every crash and error to be 
automatically reported with the full stack trace. Also set up a webhook or Slack 
notification so I get alerted immediately when a new error occurs. 
Make sure it works in both debug and release builds.
```

---

### 3. Forms That Lose User Progress on Error

**What breaks:** User fills out a long form → clicks submit → backend error → all data lost → user rage-quits.

**Fix:**
- Frontend resilience: cache form state locally (localStorage / @AppStorage)
- On error: preserve all entered data, show error message, let user retry without retyping
- Validate on client side before submitting (catch errors before they hit the backend)

**Claude Code prompt:**
```
Make all forms in my app resilient to backend errors. If a form submission fails, 
the user's input must be preserved — they should never have to re-enter data. 
Add client-side validation before submission. On error, show a clear message 
with a retry button. Cache form state using @AppStorage (iOS) or localStorage (web) 
so even if the app crashes, the data survives.
```

---

### 4. Bad Loading States (Frozen Screen or Infinite Spinner)

**What breaks:** Network call is slow → UI freezes or spinner spins forever → user thinks app is broken → leaves.

**Fix:**
- Every async call has 3 states: `loading`, `error`, `empty`
- Loading: show skeleton loader (not a spinner)
- Error: show error message + retry button
- Empty: show "no data" state (not blank)

**Claude Code prompt:**
```
Fix all loading states in my app. Every async data call needs three states: 
loading (show a skeleton loader, not a spinner), error (show error message + retry button), 
and empty (show a friendly "no data yet" message). No more frozen screens or infinite spinners. 
If a network call fails, the user should always know what happened and be able to retry.
```

---

### 5. One Error Takes Down the Whole App (No Error Boundaries)

**What breaks:** Single component throws error → entire app goes white/blank → user thinks app is dead → leaves.

**Fix:**
- Wrap the app in an error boundary
- On error: show friendly fallback ("Something went wrong — please try again") + reset button
- One broken component doesn't kill the whole app

**Claude Code prompt:**
```
Add error boundaries to my iOS app. If any single view or component throws an error, 
it should NOT take down the entire app. Instead, show a friendly fallback view with 
"Something went wrong — please try again" and a reset button. The rest of the app 
should continue working normally. Use SwiftUI's error handling patterns to catch 
and isolate errors at the view level.
```

---

## Pre-Launch Checklist

Before every TestFlight / App Store submission, verify:

- [ ] **404 page** exists and matches app theme
- [ ] **Image fallbacks** on all image components
- [ ] **Sentry** (or similar) configured and receiving test errors
- [ ] **Form state** preserved on backend error (test by killing the server mid-submit)
- [ ] **Loading states** have skeleton + error + empty (no spinners, no frozen screens)
- [ ] **Error boundaries** wrap all major views (test by throwing a fake error in one component)
- [ ] **Retry buttons** on all error states
- [ ] **No blank screens** anywhere (test every async path with network disabled)

---

## How to Run

**Before every ship:**
1. Run through the checklist above
2. For each failing item, paste the corresponding Claude Code prompt
3. Verify the fix works
4. Ship

**Time to fix all 5:** ~30 minutes with Claude Code (most are single-prompt fixes)

---

*Added to AEGIS: 2026-06-12. Source: Instagram reel transcript — "5 things that break when you ship a Claude Code app."*
