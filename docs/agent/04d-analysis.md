# 04d. Analysis and write-up

Read `00-context.md` and `STATE.md` first. Every table and plot is made by a script in `scripts/` from the logs. No hand-typed numbers.

## Tasks

1. **Main table:** P, A90 and U per model × language × setting.

2. **Losses**, in points:
   - L_EN = CONCAT − SHARDED in English
   - L_BN = the same in Bangla
   - Δ = L_BN − L_EN

3. **95% range for Δ.** Method for the code: resample **problems** with replacement 10,000 times, with a fixed seed, keeping each problem's English and Bangla runs together. In human-facing text, call it "95% range", and explain it once as "we reshuffled the problem list 10,000 times".

4. **How to read Δ** (put this table in the summary):

   | 95% range | Meaning |
   | --- | --- |
   | Entirely above 0 | Bangla loses more |
   | Entirely below 0 | Bangla loses less |
   | Includes 0 | We can't tell |

5. **Second result:** the share of the score lost, (CONCAT − SHARDED) / CONCAT, per language, with the same kind of 95% range.

6. **SNOWBALL:** its gain over SHARDED on the same 30 problems, per language, with a 95% range.

7. **Simulator errors per language:** export 30 random conversations per language to a readable file for people to check, as in Phase 3. Report the error rate per language.

8. **Other checks to report:**
   - the cut-off rate per language
   - how often the two checkers disagree
   - the Bangla FULL − CONCAT gap, as a check on translation quality

9. **Outputs:**
   - plots: English vs. Bangla bars per setting, one per model
   - `results/summary.md` with every table, following the writing rule in `00-context.md`

## Checkpoint 4d report
The summary, the plots, the error rates, and anything unexpected.
