#!/usr/bin/env bash
# Build the workshop image, stamped with the commit it was built from.
#
#   ./sandbox/build.sh          # full image, with the baked model
#   ./sandbox/build.sh --slim   # scanners only, no model, tagged :slim
#   ./sandbox/build.sh --model qwen3:1.7b   # a different model
#   ./sandbox/build.sh --check  # is the built image current? (morning pre-flight)
#
# Always build through this rather than calling docker build directly. The repo
# is copied into the image, not mounted, so an unstamped image cannot be told
# apart from a current one — and a stale image is the quietest way for this
# workshop to fail, because every lab still runs, just from older material.
set -euo pipefail

cd "$(dirname "$0")/.."

SHA="$(git rev-parse --short HEAD 2>/dev/null || echo unstamped)"
git diff --quiet HEAD 2>/dev/null || SHA="${SHA}-dirty"

if [ "${1:-}" = "--check" ]; then
  TAG="${2:-sleeper-workshop}"
  BUILT="$(docker run --rm --entrypoint printenv "$TAG" WORKSHOP_BUILD_SHA 2>/dev/null || true)"
  if [ -z "$BUILT" ]; then
    echo "FAIL  $TAG has no build stamp — it predates sandbox/build.sh. Rebuild:" >&2
    echo "        ./sandbox/build.sh" >&2
    exit 1
  fi
  if [ "$BUILT" != "$SHA" ]; then
    echo "FAIL  $TAG was built from $BUILT, the tree is at $SHA. Rebuild:" >&2
    echo "        ./sandbox/build.sh" >&2
    exit 1
  fi
  echo "ok    $TAG is current ($BUILT)"
  exit 0
fi

TAG=sleeper-workshop
EXTRA=()
case "${1:-}" in
  --slim)
    TAG=sleeper-workshop:slim
    EXTRA=(--build-arg WITH_MODEL=0)
    ;;
  --model)
    EXTRA=(--build-arg "MODEL=${2:?--model needs a model name, e.g. qwen3:1.7b}")
    ;;
  "") ;;
  *)
    echo "usage: build.sh [--slim | --model <name> | --check [tag]]" >&2
    exit 2
    ;;
esac

echo "building ${TAG} from ${SHA}"
docker build -f sandbox/Dockerfile \
  --build-arg "GIT_SHA=${SHA}" \
  "${EXTRA[@]}" \
  -t "${TAG}" .

echo
echo "built ${TAG}  WORKSHOP_BUILD_SHA=${SHA}"
