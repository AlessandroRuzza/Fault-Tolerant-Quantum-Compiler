#!/usr/bin/env bash
#
# Expose the local web interface on a public URL via a Cloudflare quick tunnel.
#
#   ./webserver/tunnel.sh                # tunnel to an already-running server
#   ./webserver/tunnel.sh --serve        # start the server too, stop it on exit
#   ./webserver/tunnel.sh --port 8080
#   ./webserver/tunnel.sh --install      # fetch cloudflared into webserver/.bin
#
# A quick tunnel needs no Cloudflare account and no DNS. It hands out a random
# https://<something>.trycloudflare.com hostname that lives as long as this
# script runs, which is what makes it useful for showing someone a compilation
# without deploying anything.
#
# Note what that means: while it runs, anyone holding the URL can reach the
# compiler and spend your CPU on circuits of their choosing. There is no
# authentication in front of it. Keep the tunnel short-lived, and prefer the
# Render deployment for anything long-running.

set -euo pipefail

PORT=8000
START_SERVER=0
DO_INSTALL=0

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$SCRIPT_DIR/.bin"

usage() {
    # Print the header comment as the help text, stopping at the first line
    # that is not a comment — a fixed line range silently rots the moment the
    # header grows or shrinks.
    awk 'NR < 3 { next } /^#/ { sub(/^# ?/, ""); print; next } { exit }' \
        "${BASH_SOURCE[0]}"
    exit "${1:-0}"
}

while [ $# -gt 0 ]; do
    case "$1" in
        --port)    PORT="${2:?--port needs a value}"; shift 2 ;;
        --serve)   START_SERVER=1; shift ;;
        --install) DO_INSTALL=1; shift ;;
        -h|--help) usage 0 ;;
        *) echo "unknown option: $1" >&2; usage 1 >&2 ;;
    esac
done

# --- locate cloudflared -----------------------------------------------------

find_cloudflared() {
    if [ -x "$BIN_DIR/cloudflared" ]; then
        echo "$BIN_DIR/cloudflared"
    elif command -v cloudflared >/dev/null 2>&1; then
        command -v cloudflared
    fi
}

install_cloudflared() {
    local arch url
    case "$(uname -m)" in
        x86_64|amd64) arch=amd64 ;;
        aarch64|arm64) arch=arm64 ;;
        *) echo "error: no prebuilt cloudflared for $(uname -m)." >&2; exit 1 ;;
    esac
    url="https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${arch}"

    echo "downloading cloudflared from:"
    echo "  $url"
    mkdir -p "$BIN_DIR"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$url" -o "$BIN_DIR/cloudflared"
    else
        wget -qO "$BIN_DIR/cloudflared" "$url"
    fi
    chmod +x "$BIN_DIR/cloudflared"
    echo "installed: $BIN_DIR/cloudflared"
}

if [ "$DO_INSTALL" -eq 1 ]; then
    install_cloudflared
fi

CLOUDFLARED="$(find_cloudflared)"
if [ -z "$CLOUDFLARED" ]; then
    cat >&2 <<EOF
error: cloudflared not found.

Install it with any of:
  ./webserver/tunnel.sh --install     # downloads it into webserver/.bin
  brew install cloudflared
  sudo apt install cloudflared
EOF
    exit 1
fi

# --- pick an interpreter ----------------------------------------------------

pick_python() {
    if [ -n "${PYTHON:-}" ]; then echo "$PYTHON"
    elif [ -x "$REPO_ROOT/.venv/bin/python" ]; then echo "$REPO_ROOT/.venv/bin/python"
    else echo "python3"
    fi
}

# --- lifecycle --------------------------------------------------------------

SERVER_PID=""
CF_PID=""
CF_LOG="$(mktemp -t ftqc-tunnel-XXXXXX.log)"

cleanup() {
    trap - EXIT INT TERM
    [ -n "$CF_PID" ] && kill "$CF_PID" 2>/dev/null || true
    if [ -n "$SERVER_PID" ]; then
        echo
        echo "stopping the web server (pid $SERVER_PID)"
        kill "$SERVER_PID" 2>/dev/null || true
        wait "$SERVER_PID" 2>/dev/null || true
    fi
    rm -f "$CF_LOG"
}
trap cleanup EXIT INT TERM

server_is_up() {
    curl -sf "http://127.0.0.1:$PORT/api/health" >/dev/null 2>&1
}

if server_is_up; then
    echo "found a web server already listening on port $PORT"
    if [ "$START_SERVER" -eq 1 ]; then
        echo "  (--serve ignored: reusing the running one)"
        START_SERVER=0
    fi
elif [ "$START_SERVER" -eq 1 ]; then
    PY="$(pick_python)"
    echo "starting the web server: $PY $SCRIPT_DIR/serve.py --port $PORT"
    "$PY" "$SCRIPT_DIR/serve.py" --port "$PORT" &
    SERVER_PID=$!
    for _ in $(seq 1 40); do
        server_is_up && break
        kill -0 "$SERVER_PID" 2>/dev/null || { echo "error: the server exited during startup." >&2; exit 1; }
        sleep 0.5
    done
    server_is_up || { echo "error: the server did not come up on port $PORT." >&2; exit 1; }
else
    cat >&2 <<EOF
error: nothing is listening on port $PORT.

Start the server first, or let this script do it:
  ./webserver/tunnel.sh --serve --port $PORT
EOF
    exit 1
fi

# --- tunnel -----------------------------------------------------------------

echo "opening a Cloudflare quick tunnel to http://127.0.0.1:$PORT"
"$CLOUDFLARED" tunnel --no-autoupdate --url "http://127.0.0.1:$PORT" \
    >"$CF_LOG" 2>&1 &
CF_PID=$!

PUBLIC_URL=""
for _ in $(seq 1 60); do
    PUBLIC_URL="$(grep -oE 'https://[a-z0-9-]+\.trycloudflare\.com' "$CF_LOG" | head -1 || true)"
    [ -n "$PUBLIC_URL" ] && break
    kill -0 "$CF_PID" 2>/dev/null || break
    sleep 1
done

if [ -z "$PUBLIC_URL" ]; then
    echo "error: cloudflared did not report a URL. Its output was:" >&2
    cat "$CF_LOG" >&2
    exit 1
fi

cat <<EOF

  ┌────────────────────────────────────────────────────────────┐
     Public URL:  $PUBLIC_URL
  └────────────────────────────────────────────────────────────┘

  Anyone with this link can compile circuits on this machine.
  There is no authentication. Ctrl-C closes the tunnel.

EOF

# cloudflared keeps running until interrupted; the EXIT trap tears down both it
# and the server we may have started.
wait "$CF_PID"
