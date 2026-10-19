# Point the corpus samples at the local remote-content server.
#
#   source sandbox/remote/env.sh
#
# These are the same environment variables the samples already read. That the
# fetch destination is overridable by an environment variable is row 2 of the
# Module 1 capability map — you are using the finding to run the exercise.

PORT="${REMOTE_PORT:-8799}"

export DRIVESYNC_MANIFEST="http://127.0.0.1:${PORT}/drive-sync/manifest.json"
export DOCSYNC_GUIDE_URL="http://127.0.0.1:${PORT}/style/latest.md"
export DOCS_BASE="http://127.0.0.1:${PORT}/api"

echo "  DRIVESYNC_MANIFEST  $DRIVESYNC_MANIFEST"
echo "  DOCSYNC_GUIDE_URL   $DOCSYNC_GUIDE_URL"
echo "  DOCS_BASE           $DOCS_BASE"
