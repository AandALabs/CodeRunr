#!/bin/bash
set -e

# ── cgroup v2 setup for isolate ──────────────────────────────────────────
# When running privileged, ensure the cgroup subtree exists and is writable.
if [ -d /sys/fs/cgroup ]; then
    mkdir -p /sys/fs/cgroup/system.slice/isolate.scope 2>/dev/null || true
    # Enable controllers for the isolate scope
    if [ -f /sys/fs/cgroup/cgroup.subtree_control ]; then
        echo "+memory +pids +cpu" > /sys/fs/cgroup/cgroup.subtree_control 2>/dev/null || true
    fi
fi

# ── Kernel tuning ────────────────────────────────────────────────────────
sysctl -w fs.protected_hardlinks=1 2>/dev/null || true

# ── Mount root as bind (required by isolate in containers) ───────────────
mount --bind / / 2>/dev/null || true

# ── Disable swap ────────────────────────────────────────────────────────
swapoff -a 2>/dev/null || true

# ── Start the requested service ─────────────────────────────────────────
case "${SERVICE_MODE:-api}" in
    api)
        echo "Running database migrations..."
        uv run alembic upgrade head

        echo "Seeding languages..."
        uv run python -m db.seeds.languages

        echo "Starting API server..."
        exec uv run uvicorn main:app --host 0.0.0.0 --port 8000
        ;;
    worker)
        echo "Starting Celery worker..."
        exec uv run celery --app=worker.celery worker --loglevel=INFO
        ;;
    *)
        echo "Unknown SERVICE_MODE: ${SERVICE_MODE}"
        exit 1
        ;;
esac
