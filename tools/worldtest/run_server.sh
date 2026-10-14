#!/usr/bin/env bash
# Starts a Fabric 1.20.1 server in ./server, pre-generates a square of terrain with Chunky,
# then saves and stops. Usage: run_server.sh <radius-in-blocks>
set -euo pipefail
RADIUS="${1:-2048}"
cd server
rm -f console && mkfifo console
tail -f console | java -Xms2G -Xmx11G -jar server.jar nogui > server.log 2>&1 &
PID=$!

wait_for() {
  local pattern="$1" timeout="$2"
  for _ in $(seq "$timeout"); do
    if grep -qiE "$pattern" server.log; then return 0; fi
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "::error::Server stopped unexpectedly"; tail -n 150 server.log; exit 1
    fi
    sleep 1
  done
  echo "::error::Timed out waiting for: $pattern"; tail -n 80 server.log; exit 1
}

wait_for 'Done \(' 1200
echo "Server started. Generating terrain (radius ${RADIUS})..."
echo "chunky center 0 0" > console
echo "chunky radius ${RADIUS}" > console
echo "chunky start" > console
wait_for 'task finished' 5400
grep -i 'chunky' server.log | tail -n 3
if [ -f commands.txt ]; then
  echo "Running test commands..."
  while IFS= read -r cmd; do
    [ -z "$cmd" ] && continue
    echo "$cmd" > console
    sleep 25
  done < commands.txt
  grep -E "Generated structure|nearest|Could not find|Failed|Unknown|Incorrect" server.log | tail -n 40 || true
fi
echo "save-all flush" > console
sleep 15
echo "stop" > console
wait "$PID" || true
echo "Server stopped."
