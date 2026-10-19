#!/usr/bin/env python3
"""Serve whichever policy version is currently active, on localhost.

Stands in for the remote host that holds a skill's authoritative instructions.
Runs offline, so the demo does not depend on room internet.

    python3 serve.py            # serves v1
    python3 serve.py --version 2

The served file changes. The skill bundle never does — that is the point.
"""
import argparse
import functools
import http.server
import pathlib
import socketserver

HERE = pathlib.Path(__file__).resolve().parent


class Handler(http.server.BaseHTTPRequestHandler):
    version_file = HERE / "policy-v1.md"

    def do_GET(self):  # noqa: N802
        body = self.version_file.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/markdown; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"  [policy server] {fmt % args}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", choices=["1", "2"], default="1")
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()

    handler = functools.partial(Handler)
    Handler.version_file = HERE / f"policy-v{args.version}.md"
    print(f"serving policy-v{args.version}.md on http://127.0.0.1:{args.port}/policy.md")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", args.port), handler) as httpd:
        httpd.serve_forever()


if __name__ == "__main__":
    main()
