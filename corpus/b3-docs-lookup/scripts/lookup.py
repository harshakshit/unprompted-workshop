"""Fetch a documentation entry for a symbol."""
import json
import os
import sys
import urllib.parse
import urllib.request

DOCS_BASE = os.environ.get("DOCS_BASE", "https://example.invalid/api")


def lookup(symbol: str) -> dict:
    url = f"{DOCS_BASE}/symbol?{urllib.parse.urlencode({'q': symbol})}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.load(resp)


if __name__ == "__main__":
    json.dump(lookup(sys.argv[1]), sys.stdout, indent=2)
