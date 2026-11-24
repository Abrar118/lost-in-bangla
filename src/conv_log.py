"""One JSONL line per finished conversation (format: docs/agent/00-context.md). Append-only."""
import json
import threading

_lock = threading.Lock()


def key_of(rec):
    return (rec["problem_id"], rec["setting"], rec["language"], rec["run_id"], rec["tested_model"])


def done_keys(path):
    """Conversations already logged without an error. A rerun skips these and retries the rest."""
    done = set()
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    rec = json.loads(line)
                    if not rec.get("error"):
                        done.add(key_of(rec))
    except FileNotFoundError:
        pass
    return done


def append(path, rec):
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock, open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
