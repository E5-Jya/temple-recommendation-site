# Temple Recommendation Website — Project Instructions

## Overview
A Thai temple/meditation center recommendation website with 3 main pages:
- **temple-directory.html** — Browse & search all temples (landing page)
- **temple-recommendation.html** — Quiz-based recommendation engine
- **temple-detail.html** — Dynamic detail page (reads `?id=TH-XXX-001` from URL)
- **index.html** — Redirects to temple-directory.html
- **supabase-config.js** — Shared auth, database, and UI helpers

## Tech Stack
- **Frontend:** Pure HTML/CSS/JS (no build step, no framework)
- **Backend:** Supabase (auth + Postgres database)
- **Hosting:** Netlify (auto-deploys from GitHub on push to `main`)
- **Design:** Custom CSS with `:root` variables (green-primary palette), Thai language UI

## Supabase Setup
- **Project URL:** `https://uopxibyowyqirpeuylot.supabase.co`
- **Database tables:**
  - `saved_recommendations` — stores user quiz results (user_id, answers, results)
  - `temple_submissions` — user-submitted new temples (pending admin review)
- **Auth:** Email/password + Google OAuth
- **RLS:** Enabled on both tables — users can only access their own rows

## Key Architecture Decisions
- All temple data is embedded as JavaScript arrays inside each HTML file (no API calls to load data)
- `supabase-config.js` is shared across all 3 pages and handles: auth modal, user menu, save/load recommendations, temple submissions, localStorage fallback for anonymous users
- The detail page reads `?id=` URL parameter and dynamically populates content from an embedded `TEMPLES_DETAIL` object
- Anonymous users can save recommendations to localStorage; data auto-syncs to Supabase when they later register/login

## Data Source
- Temple data comes from `temples_database.csv` (10 temples, 49 columns)
- When updating temples, regenerate the JS arrays using the Python scripts in the outputs folder
- The recommendation page uses a `scores` object per temple for quiz matching

## CSS Design System
- Primary: `#4A7C59` (green)
- Accent: `#D4A847` (gold)
- Background: `#F7F5F0` (warm cream)
- Font: Sarabun (Thai) + Cormorant Garamond (English)
- All icons are inline SVGs (no emoji)

## Common Tasks

### Add a new temple
1. Add row to `temples_database.csv`
2. Re-run the Python conversion scripts to regenerate JS data
3. Update the TEMPLES arrays in all 3 HTML files
4. Commit and push

### Change styling
All CSS uses `:root` variables. Change the variables to update the entire site.

### Deploy
Just `git push origin main` — Netlify auto-deploys.

## Files NOT to commit
- `.env` files with secrets
- `node_modules/`
- Any file with the Supabase service_role key
