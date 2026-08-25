"""
Lista e compara as execuções salvas por dpr.py em runs/<config>_<timestamp>/.

Uso:
    python compare_runs.py
"""

import json
from pathlib import Path

RUNS_DIR = Path(__file__).parent / "runs"


def load_runs():
    runs = []
    if not RUNS_DIR.exists():
        return runs
    for run_dir in sorted(RUNS_DIR.iterdir()):
        config_path = run_dir / "config.json"
        if not config_path.exists():
            continue
        config = json.loads(config_path.read_text(encoding="utf-8"))
        config["run_dir"] = str(run_dir)
        config["has_model"] = (run_dir / "model").exists()

        results_path = run_dir / "results.json"
        if results_path.exists():
            results = json.loads(results_path.read_text(encoding="utf-8"))
            config["dev_acc"] = results.get("dev", {}).get("accuracy")
            config["test_acc"] = results.get("test", {}).get("accuracy")
        else:
            config["dev_acc"] = config["test_acc"] = None

        runs.append(config)
    return runs


def main():
    runs = load_runs()
    if not runs:
        print(f"Nenhuma run encontrada em {RUNS_DIR}. Rode `python dpr.py --run baseline` primeiro.")
        return

    fields = [
        "run",
        "timestamp",
        "query_model",
        "passage_model",
        "train_filename",
        "n_epochs",
        "batch_size",
        "num_hard_negatives",
        "dev_acc",
        "test_acc",
        "has_model",
    ]
    widths = {f: max(len(f), *(len(str(r.get(f, ""))) for r in runs)) for f in fields}

    header = " | ".join(f.ljust(widths[f]) for f in fields)
    print(header)
    print("-" * len(header))
    for r in runs:
        print(" | ".join(str(r.get(f, "")).ljust(widths[f]) for f in fields))

    print()
    for r in runs:
        log_path = Path(r["run_dir"]) / "train.log"
        print(f"[{r['run']} @ {r['timestamp']}] {r.get('description', '')}")
        print(f"  log: {log_path}")


if __name__ == "__main__":
    main()
