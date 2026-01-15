#!/bin/bash

# Drop Me Recycling Backend - Automated Setup Script
# This script sets up the entire development environment in one command

set -e  # Exit on any error

echo "🚀 Drop Me Recycling Backend - Automated Setup"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from prod_env.txt..."
    cp prod_env.txt .env
    echo "✅ .env file created"
else
    echo "ℹ️  .env file already exists"
fi

# Build and start services
echo "🏗️  Building and starting Docker services..."
docker-compose up -d --build

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run database migrations
echo "🗄️  Running database migrations..."
docker-compose exec -T web python manage.py migrate

# Create superuser (optional, with default credentials)
echo "👤 Creating default superuser (admin/admin123)..."
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Superuser already exists')" | docker-compose exec -T web python manage.py shell

# Collect static files (for production)
echo "📦 Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput

echo ""
echo "🎉 Setup completed successfully!"
echo "=================================="
echo ""
echo "🌐 Access Points:"
echo "   API:        http://localhost:8080"
echo "   Swagger:    http://localhost:8080/api/swagger/"
echo "   Admin:      http://localhost:8080/admin/"
echo ""
echo "👤 Default Admin Credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📚 Useful Commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop services: docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""
echo "📖 Next Steps:"
echo "   1. Test the API using the examples in api_examples.http"
echo "   2. Check the Swagger documentation"
echo "   3. Review the README.md for detailed documentation"
echo ""
echo "Happy coding! 🎯"