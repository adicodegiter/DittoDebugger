#!/usr/bin/env bash
# Stop the Ditto stack and start it again clean, then wait until it is healthy.
# By default MongoDB data (named volume ditto_mongodb_data) is KEPT.
# --wipe-data also deletes that volume, but only after an explicit confirmation.
set -euo pipefail

usage() {
  cat <<EOF
Usage: deploy/reset.sh [--wipe-data] [--yes] [--wait SECONDS]

Stops all Ditto containers (docker compose down), recreates them
(docker compose up -d) and waits for deploy/health_check.sh to pass.

Options:
  --wipe-data     ALSO delete the MongoDB data volume (all twins/policies are lost).
                  Asks for confirmation unless --yes is given.
  --yes           Skip the confirmation prompt for --wipe-data
  --wait SECONDS  How long to wait for the stack to become healthy (default: 300)
  -h, --help      Show this help

Only affects containers/volumes of the 'ditto' compose project (deploy/ditto, pins from deploy/image-pins.env).
EOF
}

WIPE=0
YES=0
WAIT=300
while [[ $# -gt 0 ]]; do
  case "$1" in
    --wipe-data) WIPE=1; shift ;;
    --yes) YES=1; shift ;;
    --wait) WAIT="${2:?--wait needs a number of seconds}"; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE=(docker compose --env-file "$SCRIPT_DIR/image-pins.env" -f "$SCRIPT_DIR/ditto/docker-compose.yml")

if [[ $WIPE -eq 1 ]]; then
  echo "WARNING: --wipe-data will DELETE the MongoDB volume (all things, policies, search index)."
  if [[ $YES -ne 1 ]]; then
    read -r -p "Type 'yes' to delete the data volume: " answer
    if [[ "$answer" != "yes" ]]; then
      echo "Aborted. Nothing was changed."
      exit 1
    fi
  fi
  echo "[reset] Stopping stack and removing its volumes..."
  "${COMPOSE[@]}" down --volumes --remove-orphans
else
  echo "[reset] Stopping stack (data volume kept)..."
  "${COMPOSE[@]}" down --remove-orphans
fi

echo "[reset] Pulling pinned images and starting stack..."
"${COMPOSE[@]}" pull --quiet
"${COMPOSE[@]}" up -d

echo "[reset] Waiting up to ${WAIT}s for all services to be healthy..."
exec "$SCRIPT_DIR/health_check.sh" --wait "$WAIT"
