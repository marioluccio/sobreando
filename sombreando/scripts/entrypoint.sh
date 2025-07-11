#!/bin/bash

# Sombreando - Docker Entrypoint Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Starting Sombreando Backend...${NC}"

# Wait for database to be ready
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
while ! pg_isready -h ${DB_HOST:-db} -p ${DB_PORT:-5432} -U ${DB_USER:-sombreando} -d ${DB_NAME:-sombreando_dev}; do
  echo "Database is unavailable - sleeping"
  sleep 1
done
echo -e "${GREEN}✅ Database is ready!${NC}"

# Run database migrations
echo -e "${YELLOW}🔄 Running database migrations...${NC}"
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo -e "${YELLOW}👤 Creating superuser...${NC}"
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@sombreando.com').exists():
    User.objects.create_superuser(
        email='admin@sombreando.com',
        username='admin',
        password='admin123',
        first_name='Admin',
        last_name='Sombreando'
    )
    print('Superuser created successfully!')
else:
    print('Superuser already exists.')
EOF

# Collect static files
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Load initial data (if exists)
if [ -f "fixtures/initial_data.json" ]; then
    echo -e "${YELLOW}📊 Loading initial data...${NC}"
    python manage.py loaddata fixtures/initial_data.json
fi

# Create necessary directories
mkdir -p /app/logs
mkdir -p /app/media
mkdir -p /app/staticfiles

# Set proper permissions
chmod -R 755 /app/media
chmod -R 755 /app/staticfiles
chmod -R 755 /app/logs

echo -e "${GREEN}✅ Initialization complete!${NC}"

# Execute the main command
exec "$@"

