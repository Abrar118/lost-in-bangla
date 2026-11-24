# 03. Reproduce the paper (math only)

Read `00-context.md` and `STATE.md` first.

**Goal:** show that our local set-up behaves like the paper's. Matching its numbers exactly is not the goal; their simulator was GPT-4o-mini, ours is Qwen.

## Tasks

1. **Data:** the math items in upstream `data/sharded_instructions_600.json`. Report the count; the paper says 103. Upstream rules apply here: upstream checker, and shard rewording by the simulated user.

2. **Paper numbers:** one person copies the paper's math results for Llama-3.1-8B and Phi-4 into `data/paper_numbers.csv` (columns: model, setting, metric, value, table, page). A second person checks them. Also note how many runs per setting the paper used.

3. **Runs:** Llama-3.1-8B-Instruct and Phi-4 × FULL, CONCAT, SHARDED × the number of runs chosen at Checkpoint 2. Temperature 1.0; check this matches upstream's default (`--assistant_temperature 1.0`).

4. **Metrics**, as in paper §4.2:
   - **Average accuracy (P):** the mean score over runs and problems.
   - **Best-case score (A90):** for each problem, the 90th percentile of its run scores, then the average over problems.
   - **Run-to-run spread (U):** for each problem, 90th minus 10th percentile, then the average over problems.
   - Use numpy's default percentile method and say so in the report.

5. **Comparison table:** ours next to the paper's, from `data/paper_numbers.csv`.

6. **Hand-check file:** export 20 random SHARDED conversations to a readable file. A person checks each one for:
   - the simulator revealing too much
   - the simulator leaking the answer
   - a correct answer marked wrong, or the reverse

   Record the counts.

7. **Gate:** SHARDED must be **at least 10 points below FULL for both models**. If not, **stop and report.** Don't go on to Phase 4.

## Checkpoint 3 report
- our numbers vs. the paper's in one table
- the simulator error counts from the hand-check
- the time taken, compared with the Phase 2 estimate
- whether the gate passed
