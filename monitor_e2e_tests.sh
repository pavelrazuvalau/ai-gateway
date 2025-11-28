#!/bin/bash
# Monitor E2E tests execution (LOCAL development)
# Run this in a separate terminal to monitor test execution locally

echo "📊 E2E Tests Monitor"
echo "==================="
echo ""

while true; do
    clear
    echo "📊 E2E Tests Monitor - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "==================="
    echo ""
    
    echo "1. E2E Test Containers:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "ai-gateway-e2e|NAMES" || echo "   (no E2E containers running)"
    echo ""
    
    echo "2. E2E Test Networks:"
    docker network ls --format "table {{.Name}}\t{{.Driver}}\t{{.Scope}}" | grep -E "ai-gateway-e2e|NAME" || echo "   (no E2E networks)"
    echo ""
    
    echo "3. Docker Resource Usage:"
    docker system df --format "   {{.Type}}: {{.Size}} ({{.TotalCount}} items)" | head -4
    echo ""
    
    echo "4. Recent Docker Events (E2E related):"
    docker events --since 30s --filter "name=ai-gateway-e2e" --format "   {{.Time}} {{.Action}} {{.Actor.Attributes.name}}" 2>/dev/null | tail -5 || echo "   (no recent events)"
    echo ""
    
    echo "Press Ctrl+C to stop monitoring"
    sleep 5
done

