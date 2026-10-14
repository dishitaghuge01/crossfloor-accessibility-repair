import json
from pathlib import Path
import subprocess
import sys


def test_one_command_demo_verifies_repair_and_preserves_existing_output(tmp_path):
    output = tmp_path/"demo"
    script = Path(__file__).resolve().parents[1]/"scripts"/"run_project_demo.py"
    args = [sys.executable, str(script), "--output", str(output)]
    run = subprocess.run(args, capture_output=True, text=True)
    assert run.returncode == 0, run.stderr
    summary = json.loads((output/"summary.json").read_text())
    assert (summary["before_satisfied"], summary["after_satisfied"], summary["obligations"]) == (1,4,4)
    assert (summary["cost"], summary["selected"], summary["delta_A"]) == ("3",["A"],0)
    assert summary["certificate_valid"]
    original = (output/"report.md").read_bytes()
    assert b"originality remains provisional" in original
    manifest = json.loads((output/"manifest.json").read_text())
    assert manifest["seed"] == 0 and manifest["solver_status"] == "optimal"
    again = subprocess.run(args, capture_output=True, text=True)
    assert again.returncode == 2
    assert (output/"report.md").read_bytes() == original
