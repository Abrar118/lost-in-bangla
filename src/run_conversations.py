"""Run conversations with upstream's simulators and log each one in our JSONL format.

Example (smoke test):
    python src/run_conversations.py --phase smoke --model gemma4-12b --problems 3 --settings full sharded --runs 1

Needs the tested-model server and the simulator server running (scripts/serve.py).
Upstream code expects to run from the upstream/ folder, so this script changes into it.
"""
import argparse
import hashlib
import json
import os
import random
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from config import load_config  # noqa: E402

CFG = load_config()
UPSTREAM = ROOT / CFG["paths"]["upstream_dir"]
os.chdir(UPSTREAM)
sys.path.insert(0, str(UPSTREAM))

import conv_log  # noqa: E402
import model_local  # noqa: E402
from simulator_full import ConversationSimulatorFull  # noqa: E402
from simulator_sharded import ConversationSimulatorSharded  # noqa: E402

SETTINGS = {"full": "FULL", "concat": "CONCAT", "sharded": "SHARDED"}


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def shard_order(setting, sample, trace):
    if setting == "full":
        return []
    if setting == "concat":
        return [s["shard_id"] for s in sample["shards"]]
    return [m["content"]["shard_id"] for m in trace if m["role"] == "log" and m["content"]["type"] == "shard_revealed"]


def build_turns(trace, tested_calls):
    turns, k = [], 0
    for m in trace:
        if m["role"] not in ("system", "user", "assistant"):
            continue
        turn = {"role": m["role"], "text": m["content"]}
        if m["role"] == "assistant" and k < len(tested_calls):
            c = tested_calls[k]
            k += 1
            turn.update({"reasoning_text": c["reasoning_text"], "finish_reason": c["finish_reason"], "tokens": c["tokens"]})
        turns.append(turn)
    return turns


def run_one(job):
    sample, setting, run_id, args, sim_key = job["sample"], job["setting"], job["run"], job["args"], CFG["simulator"]["key"]
    model_cfg = CFG["tested_models"][args.model]
    problem_id = sample["task_id"]
    started = now()
    model_local.start_conversation(f"{problem_id}|{setting}|{args.language}|{run_id}")
    sim, error, is_correct = None, None, None
    try:
        if setting == "sharded":
            sim = ConversationSimulatorSharded(sample, assistant_model=args.model, system_model=sim_key, user_model=sim_key,
                                               dataset_fn=args.dataset, log_folder=None)
        else:
            sim = ConversationSimulatorFull(sample, assistant_model=args.model, system_model=sim_key,
                                            run_concat=(setting == "concat"), dataset_fn=args.dataset, log_folder=None)
        is_correct, _ = sim.run(save_log=False)
    except Exception:
        error = traceback.format_exc()
    calls = model_local.end_conversation()
    trace = getattr(sim, "trace", [])
    evals = [m["content"] for m in trace if m["role"] == "log" and m["content"]["type"] == "answer-evaluation"]
    tested = [c for c in calls if c["role"] == "tested"]
    sim_name = next((c["model"] for c in calls if c["role"] == "simulator"), sim_key)  # name the server itself reports
    rec = {
        "conversation_id": hashlib.sha1(f"{args.phase}|{problem_id}|{setting}|{args.language}|{run_id}|{args.model}".encode()).hexdigest()[:12],
        "phase": args.phase, "task": "math", "setting": SETTINGS[setting], "language": args.language,
        "problem_id": problem_id, "run_id": run_id,
        "tested_model": args.model, "tested_quant": model_cfg["quant"], "tested_file_sha256": model_cfg["sha256"],
        "simulator_model": sim_name, "simulator_quant": CFG["simulator"]["quant"] if sim_name == sim_key else "unknown (not the configured simulator)",
        "seed": {"salt": CFG["seed_salt"], "per_request": [c["seed"] for c in calls]},
        "sampling": {"tested": CFG["tested_sampling"], "simulator": "temperature set by upstream per call; rest is llama-server default"},
        "max_tokens": CFG["tested_max_tokens"],
        "shard_order": shard_order(setting, sample, trace),
        "turns": build_turns(trace, tested),
        "extracted_answer": evals[-1]["exact_answer"] if evals else None,
        "correct_upstream": bool(is_correct),
        "correct_ours": None,  # our checker comes in Phase 4
        "simulator_calls": [{"purpose": c["purpose"], "prompt": c["prompt"], "output": c["output"], "reasoning_text": c["reasoning_text"],
                             "finish_reason": c["finish_reason"], "seed": c["seed"], "tokens": c["tokens"]} for c in calls if c["role"] == "simulator"],
        "started_at": started, "ended_at": now(), "error": error,
    }
    conv_log.append(job["log_path"], rec)
    status = "ERROR" if error else ("correct" if rec["correct_upstream"] else "wrong")
    print(f"[{rec['conversation_id']}] {problem_id} {rec['setting']} run{run_id}: {status}", flush=True)
    if error:
        print(error, file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--phase", required=True, help="label written to the log, e.g. smoke, repro")
    ap.add_argument("--model", required=True, help="tested-model key from config.yaml")
    ap.add_argument("--language", default="en")
    ap.add_argument("--dataset", default=CFG["paths"]["dataset"], help="relative to the upstream folder")
    ap.add_argument("--problems", type=int, default=None, help="use a seeded random sample of this many math problems")
    ap.add_argument("--settings", nargs="+", default=["full", "sharded"], choices=SETTINGS)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--workers", type=int, default=1)
    args = ap.parse_args()
    if args.model not in CFG["tested_models"]:
        raise SystemExit(f"Unknown model {args.model!r}; see tested_models in configs/config.yaml")

    with open(args.dataset, encoding="utf-8") as f:
        samples = sorted((s for s in json.load(f) if s["task"] == "math"), key=lambda s: s["task_id"])
    if args.problems:
        samples = random.Random(CFG["seed_salt"]).sample(samples, args.problems)

    log_path = ROOT / CFG["paths"]["logs_dir"] / f"{args.phase}_{args.model}.jsonl"
    done = conv_log.done_keys(log_path)
    jobs = [{"sample": s, "setting": st, "run": r, "args": args, "log_path": log_path}
            for s in samples for st in args.settings for r in range(args.runs)
            if (s["task_id"], SETTINGS[st], args.language, r, args.model) not in done]
    print(f"{len(jobs)} conversations to run ({len(done)} already logged) -> {log_path}", flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        list(ex.map(run_one, jobs))


if __name__ == "__main__":
    main()
