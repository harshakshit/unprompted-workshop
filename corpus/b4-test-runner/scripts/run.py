"""Run pytest and return its exit status."""
import os
import subprocess
import sys


def run(target: str | None = None) -> int:
    cmd = [sys.executable, "-m", "pytest", "-q"]
    if target:
        cmd.append(target)
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(cmd, env=env, check=False).returncode


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else None))
