# Setup

Fifteen minutes, once. After that the repo updates itself every morning.

**Fast path:** run this in your own terminal (not in an IDE task runner or the DSH sandbox):

```powershell
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

It installs the GitHub CLI if needed, signs you in through the browser, creates the repo, pushes `main`, sets the Actions secrets from `.env`, and triggers the first snapshot. The manual steps below are the fallback — and they explain exactly what the script does, so nothing is hidden.

## 1. Push the repo to GitHub

Create an **empty** repository called `it-job-trends` at <https://github.com/new> — no README, no `.gitignore`, no licence (this folder already has them). Then, from this folder:

```powershell
cd C:\Users\gideo\Documents\AIAgents\it-job-trends
git init -b main
git add -A
git commit -m "feat: IT job market tracker pipeline"
git remote add origin https://github.com/GideonNkrumah/it-job-trends.git
git push -u origin main
```

Make it **public**. A public repo shows contributions on your profile with no extra setting, and the README is the point of the project.

## 2. Get an Adzuna key (the only signup)

1. Go to <https://developer.adzuna.com/> and register (free).
2. Open the dashboard → create an app if prompted.
3. Copy the **Application ID** and **Application Key**.

Free tier is ~250 calls/day; this pipeline uses 7 per run, so a daily run is ~3% of it.

The config is already set to `ca` / `CAD`, so this is the Canadian market.

Keep the key out of git: it belongs in the repository secret above (for Actions) and in a local `.env` (gitignored, never committed). If a key is ever pasted somewhere public or shared, rotate it in the Adzuna dashboard — it takes a click and costs nothing.

## 3. Add the secrets

Repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Name | Value | Required |
| --- | --- | --- |
| `ADZUNA_APP_ID` | your application id | yes |
| `ADZUNA_APP_KEY` | your application key | yes |
| `BLS_API_KEY` | from <https://data.bls.gov/registrationEngine/> | optional |

`BLS_API_KEY` is optional but worth adding: without it the script uses BLS v1, which allows 25 queries/day **per IP**, and GitHub-hosted runners share IPs. With a key it uses v2 and gets 500/day. The pipeline only needs 1.

## 4. Run it once by hand

**Actions → daily-snapshot → Run workflow → Run workflow.**

Watch the log for:

```
[13:18:02] adzuna: ok
[13:18:03] hn: ok - ...
[13:18:04] bls: ok
[13:18:05] snapshot complete for 2026-11-18
```

Then reload the repo. `README.md` should now have populated tables and charts, and there should be a commit from *you* (not `github-actions[bot]`) touching `data/2026-11-18.json`.

If the log says `adzuna: skipped`, the secrets are missing or misnamed — that's the only path to a skipped Adzuna section.

## 5. Confirm the contribution graph

Open your profile and check the square for today. Two things must be true:

1. The commit is authored with `50252812+GideonNkrumah@users.noreply.github.com` — set in `daily.yml` under `GIT_AUTHOR_EMAIL`. A commit authored as the Actions bot does **not** count toward your graph.
2. The repo is public, **or** you enable **Settings → Public profile → Include private contributions on my profile**.

## 6. Tune it

Everything lives in `config.json`:

- `adzuna.country` — already `ca` (Canada), with `currency` set to `CAD`. Other supported codes: `us`, `gb`, `de`, `fr`, `nl`, `au`, `nz`, `in`, `sg`, `za`, `br`, `mx`, `it`, `es`, `at`, `be`, `ch`, `pl`.
- `adzuna.queries` — the job titles you actually care about. Each query costs one API call per run. Keep it under ~15.
- `adzuna.where` — a city/region filter, e.g. `"Toronto"` or `"Vancouver"`. Empty means country-wide.
- `hn.tracks` / `hn.mentions` — the keyword vocabularies. Add role names you see in real postings; entries are matched case-insensitively on word boundaries.
- `bls.series` — BLS series IDs. `JTS510000000000000JOL` and `CES5000000001` are information-sector figures; swap in other series IDs from <https://data.bls.gov> if you want a different slice.

## Troubleshooting

| Symptom | Cause and fix |
| --- | --- |
| Scheduled run never fired | Cron on GitHub runs only on the default branch and can be delayed under load. Check **Actions** for the run; if the workflow is disabled, enable it (public repos disable schedules after 60 days of no repository activity — daily commits prevent that). |
| `adzuna: skipped` | Secrets absent or named differently. Re-add as `ADZUNA_APP_ID` / `ADZUNA_APP_KEY`. |
| `bls: error` mentioning a limit | Shared-runner IP hit the v1 quota. Add `BLS_API_KEY`. |
| Workflow green but no commit | `git diff --cached --quiet` found no change — that day's data was byte-identical. Harmless. |
| Push rejected: `refusing to allow an OAuth App to create or update workflow ... without 'workflow' scope` | The GitHub CLI token lacks the scope needed to push `.github/workflows/*`. Fix: `gh auth refresh -h github.com -s workflow`, then push again. `setup.ps1` now requests this scope automatically. |
| Push rejected: `fetch first` | The remote already has commits (e.g. you created it with a README). Fix: `git pull --rebase origin main` then `git push -u origin main`. |
| Charts don't render on GitHub | Inline SVG is supported in READMEs; if a future sanitizer strips it, the tables still carry the data and `data/history.csv` is authoritative. |

## Local test without keys

```powershell
python scripts\snapshot.py --fixtures tests\fixtures --data-dir .tmp\data --readme .tmp\README.md
```

This exercises the full parse → aggregate → render path against recorded payloads, so you can change the code or keyword vocabularies and see the effect immediately.
