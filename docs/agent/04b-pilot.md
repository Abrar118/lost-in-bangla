# 04b. Pilot: pick the tested models

Read `00-context.md` and `STATE.md` first. Use the frozen dataset (check its hash).

## Tasks

1. Run every tested model on the **50 Bangla pilot problems**, FULL, 3 runs. Our checker; log both checkers.

2. **Keep a model only if its accuracy is at least 30%.** Below that, there is too little score left to lose. Excluded models are reported, never hidden.

3. **Cut-off check:** report the share of replies cut off by the token limit, per model. If it is above 1%, raise the limit and rerun before deciding.

4. **How many problems do we need?** Use the pilot results to estimate how wide the 95% range for Δ would be with 100 problems. If it would likely be too wide to tell anything, propose a larger main set. That is a design change, so **ask**.

## Checkpoint 4b report
- the pilot table: model, accuracy, cut-off rate, kept or not
- the estimate from step 4, in plain words
