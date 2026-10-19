"""Reconcile a local folder with the team drive."""
import pathlib
import sys

from drive_sync_helper import client  # noqa: F401  (installed by preflight)


def sync(folder: str) -> None:
    root = pathlib.Path(folder).resolve()
    if not root.is_dir():
        raise SystemExit(f"not a directory: {folder}")
    print(f"Would reconcile {root} with the team drive")


if __name__ == "__main__":
    sync(sys.argv[1])
