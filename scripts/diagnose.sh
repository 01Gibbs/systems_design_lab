#!/bin/bash
# Quick diagnostic script for backend issues

echo "=== Container Status ==="
docker ps --filter "name=sysdesign" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\n=== Backend Logs (last 30 lines) ==="
docker logs sysdesign_backend --tail 30 2>&1

echo -e "\n=== Test Backend Health ==="
sleep 2
curl -v http://localhost:8000/api/health 2>&1 | grep -E "HTTP|Connection|curl:"

echo -e "\n=== Backend Process Check ==="
docker exec sysdesign_backend ps aux 2>&1 | grep -E "PID|uvicorn" || echo "No uvicorn process found"
