# Claude Code Cheatsheet — Temple Recommendation Site

Open Claude Code in your project folder and use these prompts.

---

## First Time Setup (do once)

### 1. Initialize Git + GitHub + Netlify

```
cd "C:\Users\NattawatVittayakoons\OneDrive - AICONIC VENTURES PTE. LTD\Desktop\Claude skills\Temple DB\Netlify"
claude
```

Then give Claude Code:
```
Initialize a git repo here with main as the default branch. Create a GitHub repo called "temple-recommendation-site", commit all files with the message "Initial commit — temple recommendation site with Supabase auth", and push to GitHub.
```

### 2. Connect Netlify to GitHub

After the repo is on GitHub:
1. Go to https://app.netlify.com
2. Click your site (endearing-arithmetic-14d68e)
3. Site settings → Build & deploy → Link to Git
4. Choose GitHub → select "temple-recommendation-site"
5. Branch: `main`, Publish directory: `/` (root)
6. Done! Now every `git push` auto-deploys.

### 3. Update Supabase Auth Redirect URLs

Go to Supabase dashboard → Authentication → URL Configuration:
- **Site URL:** `https://endearing-arithmetic-14d68e.netlify.app`
- **Redirect URLs:** add `https://endearing-arithmetic-14d68e.netlify.app/**`

If you later add a custom domain, add that too.

---

## Daily Development Workflow

Open Claude Code:
```
cd "C:\Users\NattawatVittayakoons\OneDrive - AICONIC VENTURES PTE. LTD\Desktop\Claude skills\Temple DB\Netlify"
claude
```

Make changes, then:
```
git add -A && git commit -m "your message" && git push
```

Netlify auto-deploys in ~10 seconds.

---

## Common Prompts for Claude Code

### Add a new temple
```
I want to add a new temple to the database. Here are the details:
- ชื่อไทย: [name]
- ชื่ออังกฤษ: [name]
- จังหวัด: [province]
- อำเภอ: [district]
- สาย: [tradition]
- กิจกรรม: [activities]
- รายละเอียด: [description]

Please add this to all 3 HTML files (directory, recommendation, detail) and commit.
```

### Update temple info
```
Update the information for temple TH-BKK-001 (สวนโมกข์กรุงเทพ). Change the blurb to: [new text]. Update all 3 HTML files and commit.
```

### Change design/colors
```
Change the primary color from green (#4A7C59) to [new color] across all files. Update the :root CSS variables.
```

### Fix a bug
```
The auth modal isn't closing after login. Debug and fix it in supabase-config.js.
```

### Add a new feature
```
Add a "favorite temples" feature where logged-in users can bookmark temples from the directory page. Save favorites to Supabase.
```

---

## Supabase Database Management

### Access the Dashboard
Go to: https://supabase.com/dashboard/project/uopxibyowyqirpeuylot

### View Data
- Table Editor → select a table → browse rows
- Or SQL Editor → `select * from saved_recommendations;`

### Add a New Table
In Claude Code:
```
Create a new Supabase table called "temple_reviews" with columns: id (auto), user_id (uuid, references auth.users), temple_id (text), rating (int 1-5), comment (text), created_at (timestamp). Enable RLS so users can only see/edit their own reviews. Give me the SQL to run in the Supabase dashboard.
```

Then paste the SQL into Supabase Dashboard → SQL Editor → Run.

### Update RLS Policies
```
Update the RLS policy on temple_submissions so that all logged-in users can read approved submissions (status = 'approved'), not just their own.
```

### View User Signups
SQL Editor:
```sql
select id, email, created_at from auth.users order by created_at desc;
```

### View Saved Recommendations
```sql
select sr.*, u.email
from saved_recommendations sr
join auth.users u on sr.user_id = u.id
order by sr.updated_at desc;
```

### View Temple Submissions
```sql
select ts.*, u.email
from temple_submissions ts
join auth.users u on ts.user_id = u.id
order by ts.created_at desc;
```

### Approve a Temple Submission
```sql
update temple_submissions
set status = 'approved', admin_notes = 'Verified and approved'
where id = [submission_id];
```

### Export Data
Dashboard → Table Editor → select table → Export → CSV

### Backup Database
Dashboard → Settings → Database → Backups (Supabase auto-backs up daily on paid plans)

---

## Project Structure

```
Netlify/
├── index.html                  ← Redirects to directory
├── temple-directory.html       ← Browse all temples (landing page)
├── temple-recommendation.html  ← Quiz engine
├── temple-detail.html          ← Dynamic detail (reads ?id= param)
├── supabase-config.js          ← Auth + DB helpers (shared)
├── .claude/
│   └── project-instructions.md ← Claude Code reads this automatically
├── .gitignore
└── CLAUDE-CODE-CHEATSHEET.md   ← This file
```

## Supabase Tables

| Table | Purpose | RLS |
|-------|---------|-----|
| `saved_recommendations` | User's quiz results | Users see own only |
| `temple_submissions` | User-submitted temples | Users see own only |

## Key URLs

| What | URL |
|------|-----|
| Live site | https://endearing-arithmetic-14d68e.netlify.app |
| Netlify dashboard | https://app.netlify.com |
| Supabase dashboard | https://supabase.com/dashboard/project/uopxibyowyqirpeuylot |
| GitHub repo | (will be created when you run the setup) |
