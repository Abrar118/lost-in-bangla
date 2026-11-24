"""Print one logged conversation in readable form.

    python scripts/show_conversation.py results/logs/smoke_gemma4-12b.jsonl <conversation_id> [--calls]
    python scripts/show_conversation.py results/logs/smoke_gemma4-12b.jsonl            (lists the ids)
"""
import argparse
import json
import sys

ap = argparse.ArgumentParser()
ap.add_argument("log")
ap.add_argument("conversation_id", nargs="?")
ap.add_argument("--calls", action="store_true", help="also print the simulator's calls")
args = ap.parse_args()
sys.stdout.reconfigure(encoding="utf-8")

with open(args.log, encoding="utf-8") as f:
    recs = [json.loads(line) for line in f if line.strip()]

if not args.conversation_id:
    for r in recs:
        print(r["conversation_id"], r["problem_id"], r["setting"], f"run{r['run_id']}", "correct" if r["correct_upstream"] else "wrong", "ERROR" if r["error"] else "")
    sys.exit()

matches = [r for r in recs if r["conversation_id"].startswith(args.conversation_id)]
if len(matches) != 1:
    sys.exit(f"{len(matches)} conversations match {args.conversation_id!r}")
r = matches[0]
print(f"{r['conversation_id']}  {r['problem_id']}  {r['setting']}  {r['language']}  run {r['run_id']}")
print(f"tested: {r['tested_model']} ({r['tested_quant']})   simulator: {r['simulator_model']} ({r['simulator_quant']})")
print(f"shard order: {r['shard_order']}   started {r['started_at']}   ended {r['ended_at']}")
print("=" * 70)
for i, t in enumerate(r["turns"]):
    extra = ""
    if t["role"] == "assistant":
        extra = f"  [{t.get('tokens')} tokens, finish: {t.get('finish_reason')}]"
    print(f"\n--- {t['role'].upper()} (turn {i}){extra}")
    if t.get("reasoning_text"):
        print(f"(thinking, hidden from the user) {t['reasoning_text']}\n")
    print(t["text"])
print("=" * 70)
print(f"extracted answer: {r['extracted_answer']!r}")
print(f"correct (upstream checker): {r['correct_upstream']}")
if r["error"]:
    print("ERROR:\n" + r["error"])
if args.calls:
    for c in r["simulator_calls"]:
        print(f"\n--- simulator call: {c['purpose']} [finish: {c['finish_reason']}]")
        print("output:", c["output"])
