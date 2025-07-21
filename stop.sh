#!/bin/bash
# SmartSwapML Stop Script

echo "Stopping SmartSwapML Application..."

# Stop all services
docker-compose down

echo "✅ SmartSwapML has been stopped."
echo ""
echo "To remove all data volumes, run: docker-compose down -v"
