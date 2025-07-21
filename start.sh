#!/bin/bash
# SmartSwapML Start Script

echo "Starting SmartSwapML Application..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed. Please install docker-compose and try again."
    exit 1
fi

# Build and start the application
echo "Building and starting services..."
docker-compose up --build -d

echo "Waiting for services to be ready..."
sleep 10

# Check if services are running
echo "Checking service status..."
docker-compose ps

echo ""
echo "✅ SmartSwapML is now running!"
echo ""
echo "Access your application:"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📡 Backend API: http://localhost:8000"
echo "📊 API Documentation: http://localhost:8000/docs"
echo "🗄️ MongoDB UI: http://localhost:8081 (admin/admin)"
echo "🔴 Redis UI: http://localhost:8082"
echo ""
echo "Login credentials:"
echo "Username: demo"
echo "Password: demo123"
echo ""
echo "To stop the application, run: docker-compose down"
