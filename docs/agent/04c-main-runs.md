# 04c. Main runs

Read `00-context.md` and `STATE.md` first. Check the dataset hash before starting.

## Tasks

1. Each kept model × {English, Bangla} × {FULL, CONCAT, SHARDED} × the chosen number of runs, on the main set.

2. **SNOWBALL** on a fixed random 30 main-set problems:
   - pick them once with a fixed seed and save the list to `data/final/snowball_30.json`
   - use the same 30 for every model, in both languages, 5 runs

3. **Shard order:** upstream's rule (shard 1 first, then the simulator picks). Pasted word for word (see 00-context). Log the order.

4. **Checking:** our checker decides; also log upstream's checker result.

5. **Resumable:** a crash must not lose finished conversations. Check this by killing a run halfway and restarting it.

6. **Progress:** every few hours, write a short status file (done / total, per model) to `results/progress.md`.

## Checkpoint 4c report
- the counts of finished conversations per model × language × setting, with any missing or failed ones
- the time taken, compared with the estimate
