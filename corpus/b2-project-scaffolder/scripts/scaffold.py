"""Write a new module skeleton from the project template."""
import pathlib
import sys

TEMPLATE = '''"""{name}."""


def main() -> None:
    raise NotImplementedError
'''


def scaffold(name: str) -> list[pathlib.Path]:
    target = pathlib.Path("src") / name
    if target.exists():
        raise SystemExit(f"refusing to overwrite {target}")
    target.mkdir(parents=True)
    written = []
    for filename, body in (
        ("__init__.py", ""),
        (f"{name}.py", TEMPLATE.format(name=name)),
        ("test_" + name + ".py", f"from {name} import main  # noqa: F401\n"),
    ):
        path = target / filename
        path.write_text(body, encoding="utf-8")
        written.append(path)
    return written


if __name__ == "__main__":
    for path in scaffold(sys.argv[1]):
        print(path)
