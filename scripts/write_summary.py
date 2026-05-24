"""Write a pipeline status table + plan.md to $GITHUB_STEP_SUMMARY."""
import os
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit(0)

run_folder = Path(os.environ["RUNNER_TEMP"]) / "cco-run"
summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
state_path = run_folder / "_state.yaml"
plan_path = run_folder / "plan.md"

if not summary_path:
    sys.exit(0)

with open(summary_path, "a") as out:
    state = yaml.safe_load(state_path.read_text()) if state_path.exists() else {}
    stages = state.get("stages", {})
    elapsed = state.get("elapsed", {})
    profile = state.get("profile", "unknown")
    branch = state.get("branch", "")

    PRECEDENCE = ["failed", "blocked", "changes-requested", "in_progress", "passed", "skipped", "pending"]
    all_statuses = list(stages.values())
    overall = next((s for s in PRECEDENCE if s in all_statuses), "pending") if all_statuses else "pending"
    icon = {"passed": "✅", "failed": "❌", "blocked": "🚫", "in_progress": "⏳"}.get(overall, "⏳")

    out.write(f"## {icon} cco — {profile}\n\n")
    if branch:
        out.write(f"**Branch:** `{branch}`\n\n")

    if stages:
        out.write("| Stage | Status | Elapsed |\n")
        out.write("|---|---|---|\n")
        for stage, status in stages.items():
            si = {"passed": "✅", "failed": "❌", "blocked": "🚫", "skipped": "⏭️",
                  "changes-requested": "🔄", "in_progress": "⏳"}.get(status, "⏳")
            secs = int(elapsed.get(stage, 0))
            mins, s = divmod(secs, 60)
            elapsed_str = f"{mins}m {s}s" if mins else f"{s}s"
            out.write(f"| `{stage}` | {si} {status} | {elapsed_str} |\n")
        out.write("\n")

    if plan_path.exists():
        out.write("---\n\n")
        out.write(plan_path.read_text())
    elif not stages:
        out.write("_Pipeline did not start — no plan.md or state found._\n")
