# IT Job Market Tracker

[![daily snapshot](https://github.com/GideonNkrumah/it-job-trends/actions/workflows/daily.yml/badge.svg)](https://github.com/GideonNkrumah/it-job-trends/actions/workflows/daily.yml)

A small, fully automated data pipeline that answers one question every morning: **what is the IT job market actually hiring for right now?**

Three public sources, one snapshot a day, committed by a scheduled GitHub Action. No scraping, no fake data, no accounts.

| Source | What it contributes | Auth | Cadence |
| --- | --- | --- | --- |
| [Adzuna](https://developer.adzuna.com/) job search API | Live posting counts, salary samples and remote share for seven IT titles | free `app_id` + `app_key` | daily |
| [Hacker News](https://news.ycombinator.com/item?id=10313519) *Who is hiring?*, via [Algolia](https://hn.algolia.com/api) | Human-written job posts classified into IT tracks, plus tool mentions | none | continuously |
| [US Bureau of Labor Statistics](https://www.bls.gov/developers/) | Monthly JOLTS and CES figures for the information sector | none (v1 API) | monthly |

## Latest snapshot

<!-- BEGIN:GENERATED -->

_Updated **2026-11-26** · 8 snapshots collected · sources: Adzuna · Hacker News · US BLS_

### IT postings by title

_CA · postings from the last 30 days · 346 unique postings in the sample_

| Title | Postings | Median salary | Remote | Top employers |
| --- | ---: | ---: | ---: | --- |
| IT support | 1,973 | C$60,000 (n=15) | 12% | Northumberland Ferries Limited, TWD Technologies Ltd., Ocean Park Mechanical, Apex Industries, iFlow Inc |
| systems administrator | 1,611 | C$91,200 (n=24) | 10% | STACK IT Recruitment, Roadpost, Company3, Haisla Nation, Houle Electric Limited |
| cloud engineer | 803 | C$133,800 (n=16) | 10% | Artech LLC, Flexstaf IT, Scotiabank, Reitmans  Ltée/Ltd, Varicent |
| data analyst | 632 | C$83,500 (n=21) | 8% | Navitas, PCL Construction, Artech LLC, Konrad, 407 International |
| network engineer | 484 | C$110,000 (n=23) | 14% | Default Project, LanceSoft Inc, Artech LLC, TMX, Vail Resorts |
| help desk | 290 | C$59,300 (n=16) | 12% | VC3, Flexstaf IT, PHSA, Velocity Solutions, Jonas Software |
| security analyst | 157 | C$90,900 (n=17) | 8% | GoSecure, Toronto Parking Authority, TD Bank, samdesk Canada Inc., Intact Financial |

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="238" viewBox="0 0 760 238" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"><text x="0" y="22.8" font-size="12" fill="#57606a">IT support</text><rect x="220" y="6.0" width="464.0" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="691.0" y="22.8" font-size="12" fill="#57606a">1,973</text><text x="0" y="55.8" font-size="12" fill="#57606a">systems administrator</text><rect x="220" y="39.0" width="378.9" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="605.9" y="55.8" font-size="12" fill="#57606a">1,611</text><text x="0" y="88.8" font-size="12" fill="#57606a">cloud engineer</text><rect x="220" y="72.0" width="188.8" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="415.8" y="88.8" font-size="12" fill="#57606a">803</text><text x="0" y="121.8" font-size="12" fill="#57606a">data analyst</text><rect x="220" y="105.0" width="148.6" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="375.6" y="121.8" font-size="12" fill="#57606a">632</text><text x="0" y="154.8" font-size="12" fill="#57606a">network engineer</text><rect x="220" y="138.0" width="113.8" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="340.8" y="154.8" font-size="12" fill="#57606a">484</text><text x="0" y="187.8" font-size="12" fill="#57606a">help desk</text><rect x="220" y="171.0" width="68.2" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="295.2" y="187.8" font-size="12" fill="#57606a">290</text><text x="0" y="220.8" font-size="12" fill="#57606a">security analyst</text><rect x="220" y="204.0" width="36.9" height="24" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="263.9" y="220.8" font-size="12" fill="#57606a">157</text></svg>

_Each query is an independent Adzuna search, so rows overlap and do not add up._

#### Postings matching the queries, per run

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="200" viewBox="0 0 760 200" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"><line x1="58" y1="174.0" x2="742" y2="174.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="177.5" font-size="11" fill="#57606a" text-anchor="end">5,276</text><line x1="58" y1="95.0" x2="742" y2="95.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="98.5" font-size="11" fill="#57606a" text-anchor="end">7,728</text><line x1="58" y1="16.0" x2="742" y2="16.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="19.5" font-size="11" fill="#57606a" text-anchor="end">10,179</text><polyline points="58.0,34.2 155.7,149.5 253.4,150.9 351.1,150.0 448.9,147.8 546.6,154.4 644.3,155.8 742.0,152.3" fill="none" stroke="#2da44e" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="58.0" cy="34.2" r="2.6" fill="#2da44e"/><circle cx="155.7" cy="149.5" r="2.6" fill="#2da44e"/><circle cx="253.4" cy="150.9" r="2.6" fill="#2da44e"/><circle cx="351.1" cy="150.0" r="2.6" fill="#2da44e"/><circle cx="448.9" cy="147.8" r="2.6" fill="#2da44e"/><circle cx="546.6" cy="154.4" r="2.6" fill="#2da44e"/><circle cx="644.3" cy="155.8" r="2.6" fill="#2da44e"/><circle cx="742.0" cy="152.3" r="2.6" fill="#2da44e"/><text x="58" y="193" font-size="11" fill="#57606a">2026-11-18</text><text x="742" y="193" font-size="11" fill="#57606a" text-anchor="end">2026-11-26</text></svg>

_The searches overlap, so this total double-counts jobs matching more than one title._

### What Hacker News is hiring for

_[Ask HN: Who is hiring? (November 2026)](https://news.ycombinator.com/item?id=50338728) · 377 comments indexed · 329 substantive posts · 23% mention remote_

| Track | Posts mentioning it |
| --- | ---: |
| Cloud / DevOps | 62 |
| Data / analytics | 14 |
| IT management / PM | 15 |
| IT support / help desk | 5 |
| Networking | 2 |
| Security | 16 |
| Software engineering | 115 |
| Systems / infrastructure | 70 |

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="255" viewBox="0 0 760 255" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"><text x="0" y="21.4" font-size="12" fill="#57606a">Cloud / DevOps</text><rect x="220" y="6.0" width="250.2" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="477.2" y="21.4" font-size="12" fill="#57606a">62</text><text x="0" y="52.4" font-size="12" fill="#57606a">Data / analytics</text><rect x="220" y="37.0" width="56.5" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="283.5" y="52.4" font-size="12" fill="#57606a">14</text><text x="0" y="83.4" font-size="12" fill="#57606a">IT management / PM</text><rect x="220" y="68.0" width="60.5" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="287.5" y="83.4" font-size="12" fill="#57606a">15</text><text x="0" y="114.4" font-size="12" fill="#57606a">IT support / help desk</text><rect x="220" y="99.0" width="20.2" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="247.2" y="114.4" font-size="12" fill="#57606a">5</text><text x="0" y="145.4" font-size="12" fill="#57606a">Networking</text><rect x="220" y="130.0" width="8.1" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="235.1" y="145.4" font-size="12" fill="#57606a">2</text><text x="0" y="176.4" font-size="12" fill="#57606a">Security</text><rect x="220" y="161.0" width="64.6" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="291.6" y="176.4" font-size="12" fill="#57606a">16</text><text x="0" y="207.4" font-size="12" fill="#57606a">Software engineering</text><rect x="220" y="192.0" width="464.0" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="691.0" y="207.4" font-size="12" fill="#57606a">115</text><text x="0" y="238.4" font-size="12" fill="#57606a">Systems / infrastructure</text><rect x="220" y="223.0" width="282.4" height="22" rx="3" fill="#2da44e" fill-opacity="0.85"/><text x="509.4" y="238.4" font-size="12" fill="#57606a">70</text></svg>

Most-mentioned tools and platforms: `ansible` 2 · `aws` 33 · `azure` 5 · `docker` 13 · `gcp` 10 · `jira` 3 · `kubernetes` 15 · `linux` 17 · `python` 62 · `snowflake` 6 · `sql` 8 · `terraform` 12

### US information sector (BLS)

_Monthly, seasonally adjusted · reference month 2026-09_

| Series | Latest | MoM | YoY |
| --- | ---: | ---: | ---: |
| Information sector job openings | 116k | +25k | -3k |
| Information sector hires | 94k | +24k | +23k |
| Information sector quits | 39k | -1k | +17k |
| Information sector layoffs and discharges | 46k | +4k | +8k |
| Information sector employment | 2.7M | -1k | -119k |
| All US job openings (context) | 7.5M | +333k | +354k |

Information-sector postings are **1.5%** of all US job openings.

#### Information-sector job openings, last 21 months

<svg xmlns="http://www.w3.org/2000/svg" width="760" height="180" viewBox="0 0 760 180" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif"><line x1="58" y1="154.0" x2="742" y2="154.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="157.5" font-size="11" fill="#57606a" text-anchor="end">59k</text><line x1="58" y1="85.0" x2="742" y2="85.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="88.5" font-size="11" fill="#57606a" text-anchor="end">114k</text><line x1="58" y1="16.0" x2="742" y2="16.0" stroke="#d0d7de" stroke-width="1"/><text x="52" y="19.5" font-size="11" fill="#57606a" text-anchor="end">170k</text><polyline points="58.0,101.9 92.2,71.9 126.4,84.4 160.6,60.6 194.8,91.9 229.0,74.4 263.2,31.9 297.4,51.9 331.6,79.4 365.8,81.9 400.0,118.1 434.2,88.1 468.4,103.1 502.6,128.1 536.8,124.3 571.0,125.6 605.2,138.1 639.4,116.8 673.6,130.6 707.8,114.3 742.0,83.1" fill="none" stroke="#2da44e" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/><circle cx="58.0" cy="101.9" r="2.6" fill="#2da44e"/><circle cx="92.2" cy="71.9" r="2.6" fill="#2da44e"/><circle cx="126.4" cy="84.4" r="2.6" fill="#2da44e"/><circle cx="160.6" cy="60.6" r="2.6" fill="#2da44e"/><circle cx="194.8" cy="91.9" r="2.6" fill="#2da44e"/><circle cx="229.0" cy="74.4" r="2.6" fill="#2da44e"/><circle cx="263.2" cy="31.9" r="2.6" fill="#2da44e"/><circle cx="297.4" cy="51.9" r="2.6" fill="#2da44e"/><circle cx="331.6" cy="79.4" r="2.6" fill="#2da44e"/><circle cx="365.8" cy="81.9" r="2.6" fill="#2da44e"/><circle cx="400.0" cy="118.1" r="2.6" fill="#2da44e"/><circle cx="434.2" cy="88.1" r="2.6" fill="#2da44e"/><circle cx="468.4" cy="103.1" r="2.6" fill="#2da44e"/><circle cx="502.6" cy="128.1" r="2.6" fill="#2da44e"/><circle cx="536.8" cy="124.3" r="2.6" fill="#2da44e"/><circle cx="571.0" cy="125.6" r="2.6" fill="#2da44e"/><circle cx="605.2" cy="138.1" r="2.6" fill="#2da44e"/><circle cx="639.4" cy="116.8" r="2.6" fill="#2da44e"/><circle cx="673.6" cy="130.6" r="2.6" fill="#2da44e"/><circle cx="707.8" cy="114.3" r="2.6" fill="#2da44e"/><circle cx="742.0" cy="83.1" r="2.6" fill="#2da44e"/><text x="58" y="173" font-size="11" fill="#57606a">2025-01</text><text x="742" y="173" font-size="11" fill="#57606a" text-anchor="end">2026-09</text></svg>

### Recent runs

| Date | Matching postings | HN posts | Info openings |
| --- | ---: | ---: | ---: |
| 2026-11-26 | 5,950 | 329 | 116k |
| 2026-11-25 | 5,842 | 329 | 116k |
| 2026-11-24 | 5,885 | 330 | 116k |
| 2026-11-22 | 6,090 | 332 | 116k |
| 2026-11-21 | 6,021 | 333 | 116k |
| 2026-11-20 | 5,992 | 333 | 116k |
| 2026-11-19 | 6,035 | 332 | 116k |
| 2026-11-18 | 9,613 | 332 | 116k |

Full time series: [`data/history.csv`](data/history.csv)

<!-- END:GENERATED -->

## How it works

```
GitHub Actions (daily, 13:17 UTC)
        │
        ├── scripts/fetch_adzuna.py ── Adzuna API ──┐
        ├── scripts/fetch_hn.py ────── HN / Algolia ├──► data/YYYY-MM-DD.json
        └── scripts/fetch_bls.py ───── BLS API ─────┘
                                                         │
                                              scripts/render.py
                                                         │
                                        README.md + data/history.csv
                                                         │
                                                commit & push
```

| Path | Role |
| --- | --- |
| `config.json` | Countries, search queries, HN keyword tracks, BLS series — all tunable without touching code |
| `scripts/fetch_*.py` | One module per source; each returns a status (`ok` / `skipped` / `error`) instead of raising |
| `scripts/snapshot.py` | Orchestrator: fetch → `data/<date>.json` → render → step summary |
| `scripts/render.py` | Builds `data/history.csv` and the generated README block, including inline SVG charts |
| `.github/workflows/daily.yml` | Cron schedule, commit identity, push with rebase retry |

Design choices worth noting:

- **Fail soft, never fabricate.** A source that is down or unconfigured renders an explicit "skipped" note. The run only exits non-zero when *every* source fails, so a single flaky API doesn't paint the repo red.
- **Idempotent.** Running twice for the same date overwrites that day's JSON; `git diff --cached --quiet` means an unchanged day produces no commit.
- **Small diffs.** Charts are inline SVG text, so a day's data is a few KB in the git history instead of a checked-in PNG.

## What this measures — and what it doesn't

Being precise about limits is the difference between a data project and a green-square generator:

- **Adzuna counts are per-query totals** for the **Canadian** market. Seven overlapping keyword searches run; rows do *not* add up to a market total, and the trend line is their sum, so it double-counts jobs matching more than one title. "Unique postings" is only what appeared in the 50-result sample per query.
- **Salaries are a sample median** over the postings that publish a range — often only a handful of the 50 results, shown as `(n=…)`. Read it as direction, not the market rate.
- **The BLS block is US-only** while the Adzuna block is Canada. They answer different questions: Canadian demand today, and US sector-level context.
- **The HN thread is self-selected.** It skews to startups and software roles; IT support and sysadmin coverage is thinner there than on job boards. Treat it as a sentiment signal, not a census.
- **"Information sector" (NAICS 51) is broader than IT** — it includes publishing and broadcasting. It is a directional proxy for the sector that contains IT, and the most authoritative number in this repo.
- **All data is public and fetched from official APIs.** Nothing here is scraped from sites that forbid it, and nothing is generated to look like work.

## Run it locally

Copy `.env.example` to `.env` and fill in your Adzuna credentials (`.env` is gitignored), then:

```powershell
python scripts/snapshot.py                     # live run for today
python scripts/snapshot.py --date 2026-11-18   # backfill a specific date
python scripts/snapshot.py --fixtures tests/fixtures --data-dir .tmp/data --readme .tmp/README.md
```

The last form runs the full pipeline offline against recorded API payloads — useful for testing changes without spending Adzuna quota.

## Data

- `data/<YYYY-MM-DD>.json` — full snapshot for one run (Adzuna rows, HN tracks and mentions, BLS series with 24 months of history).
- `data/history.csv` — one row per run with the headline metrics, ready for a spreadsheet.

BLS data is produced by the U.S. Bureau of Labor Statistics and is public domain; Adzuna data is used under their API terms; Hacker News content belongs to its authors.
