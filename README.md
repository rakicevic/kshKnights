# KshKnights

Weekly EuroLeague Fantasy Challenge analyzer. Every Monday a GitHub Action does the following:

1. Pulls EuroLeague box scores from the official public API. This is the same data shown on euroleaguebasketball.net player pages.
2. Computes fantasy points per game: PIR, with +10% when the team wins.
3. Projects next round's points per player and per coach.
4. Solves for the best legal roster.
5. Commits a report and opens a GitHub issue. GitHub emails you on every new issue.

## What the model does

- **Form.** It uses a recency-weighted average of the last 4 games (weights 4-3-2-1), plus the median and volatility of those games. This handles the "2 good, 1 bad" pattern instead of chasing the last game.
- **Season level.** The season-to-date average is shrunk toward last season's level while the sample is small. Players with no EuroLeague history get a prior derived from their price.
- **Context.**
  - Minutes trend.
  - Home or away.
  - Opponent's fantasy points conceded compared with the league average.
  - Win probability from team net ratings, which also drives the win bonus.
  - Double-game weeks.
- **Learning.**
  - A gradient-boosted model is trained on all historical games and scored on a hold-out set against the transparent formula.
  - The better of the two, or a blend, is used.
  - Validation error is printed in every report.
- **Risk.**
  - The volatility penalty is set by `risk_aversion`.
  - Recent DNPs are discounted.
  - Optionally, Claude (`ANTHROPIC_API_KEY`) searches the web for injury news: players reported `out` are excluded and `doubtful` or `questionable` players are discounted.
- **Coach.** Expected coach points are computed from the distribution of the game margin across the scoring bands (+10/+20/+25, −5/−10/−20).
- **Optimizer.** An exact mixed-integer program (HiGHS) respects all rules:
  - Formation (G-F-C) of 1-2-2, 1-3-1, 2-1-2, 2-2-1 or 3-1-1.
  - Main 6 = starting five plus sixth man, at 100%.
  - Bench of G, F, F, C at 50%.
  - One head coach.
  - Captain scores ×2.
  - Budget limit.
  - At most 6 players from one club.
  - At most 4 trades, with the coach counting toward the limit.
  - Locked and banned players.

The report contains:
- transfers to make (sell/buy) and the projected gain from them
- the full round roster with roles
- the top 8 core players
- the best alternatives by position
- value picks
- availability flags
- for each player: last game, last-4 average and season average

## Setup (one time)

1. **Create the repo.** On GitHub, go to **New repository**, name it `KshKnights`, and make it private or public. Public repos get unlimited free Actions minutes; private repos get 2,000 minutes a month on the free plan. One run takes about 3–8 minutes; the first run takes longer because it downloads last season.
2. **Upload the files.** On your computer:
   ```bash
   unzip KshKnights.zip && cd KshKnights
   git init -b main && git add . && git commit -m "Initial KshKnights"
   git remote add origin https://github.com/<your-user>/KshKnights.git
   git push -u origin main
   ```
   Alternatively, on the repo page choose **Add file → Upload files** and drag in the unzipped folder contents, including the `.github` folder. Hidden folders are easy to miss when dragging; if `.github/workflows/weekly-report.yml` does not appear, create it with **Add file → Create new file** and paste the contents in.
3. **Allow the workflow to write.** Go to **Settings → Actions → General → Workflow permissions**, select **Read and write permissions**, and save.
4. **Enable Issues** if they are off: **Settings → General → Features → Issues**.
5. **Optional AI news check.** Go to **Settings → Secrets and variables → Actions → New repository secret**, name it `ANTHROPIC_API_KEY`, and paste a key from console.anthropic.com. API usage is billed per request. Without the key, everything else still runs.
6. **Watch the repo** (Watch → All activity, or at least Issues) so the Monday issue reaches your email.
7. **First run.** Go to **Actions → KshKnights weekly report → Run workflow**.

## Weekly routine

1. **Export fantasy data.** After the round, export the player list from the fantasy game (the same format as `players_stats.xlsx`). Replace `data/fantasy/players_stats.xlsx` through **Add file → Upload files** with the same filename, then commit. This triggers a run automatically and adds a snapshot to `data/history/prices.csv`, which builds the season price history. If you forget, the Monday run uses the old prices and the report shows **STALE**.
2. **Update your squad.** After making trades, update `config/my_team.yaml`:
   - `players`: IDs from the export's ID column. Players listed with ID `-` are entered as `"Name Surname|TEAM"`.
   - `coach`: the team code, e.g. `PAO`.
   - `credits_in_bank`
   - `trades_available` (write `unlimited` during unlimited windows)
   - `lock` / `ban` lists

   With an empty `players` list, the report builds an optimal squad from scratch with 100 credits.
3. **Read the report.** On Monday, read the issue, or `reports/latest.md` in the repo.

## Configuration

| File | Purpose |
|---|---|
| `config/settings.yaml` | Season (`season: 2026` = 2026-27), rules, formations, bench, unlimited trade windows, model settings |
| `config/my_team.yaml` | Your current squad, bank and trade count |
| `config/overrides.yaml` | Manual player and club mappings when auto-matching fails (the report lists unmatched players) |

To change the run time, edit `cron` in `.github/workflows/weekly-report.yml`. The default is Monday 06:00 UTC.

## Local run

```bash
pip install -r requirements.txt
python -m pytest -q          # offline tests with synthetic data
python -m kshknights         # real run (needs internet)
python -m kshknights --date 2026-10-12
```

## Known limits

- **Stats source.** The EuroLeague API is public but unofficial for third parties, so endpoints can change without notice. Data comes through the `euroleague-api` Python package. If the API fails, the run falls back to cached data and says so.
- **Fantasy data is manual.** The fantasy game's prices and your squad sit behind your login and must be uploaded by you; nothing logs in on your behalf.
- **Rule details.** Rule details not listed here are taken from the published Classic-mode rules, including the win bonus and the coach bands. If the game changes a rule, update `config/settings.yaml`.
