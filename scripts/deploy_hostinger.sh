#!/bin/bash
# News Aggregator Deployment Script for Hostinger VPS
# Run this once on your new VPS: bash deploy_hostinger.sh

set -e  # Exit on error

echo "🚀 News Aggregator - Hostinger VPS Deployment"
echo "=============================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables - EDIT THESE
APP_NAME="news-aggregator"
DOMAIN="your-domain.com"
REPO_URL="https://github.com/your-username/news-aggregator.git"
APP_USER="appuser"
APP_DIR="/home/$APP_USER/$APP_NAME"

echo -e "${YELLOW}Please configure these variables first:${NC}"
echo "  DOMAIN: $DOMAIN"
echo "  REPO_URL: $REPO_URL"
echo "  APP_USER: $APP_USER"
echo ""

# Update system
echo -e "${YELLOW}📦 Updating system packages...${NC}"
apt update
apt upgrade -y

# Install dependencies
echo -e "${YELLOW}📥 Installing dependencies...${NC}"
apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nginx git curl wget nano certbot python3-certbot-nginx \
    supervisor

# Create app user
echo -e "${YELLOW}👤 Creating application user...${NC}"
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    echo -e "${GREEN}✓ User $APP_USER created${NC}"
else
    echo -e "${GREEN}✓ User $APP_USER already exists${NC}"
fi

# Clone repository
echo -e "${YELLOW}📂 Cloning repository...${NC}"
if [ ! -d "$APP_DIR" ]; then
    sudo -u $APP_USER git clone $REPO_URL $APP_DIR
    echo -e "${GREEN}✓ Repository cloned${NC}"
else
    echo -e "${YELLOW}⚠ Directory already exists${NC}"
fi

# Create virtual environment
echo -e "${YELLOW}🐍 Setting up Python virtual environment...${NC}"
sudo -u $APP_USER python3.11 -m venv $APP_DIR/venv
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip

# Install Python dependencies
echo -e "${YELLOW}📚 Installing Python dependencies...${NC}"
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt
sudo -u $APP_USER $APP_DIR/venv/bin/pip install gunicorn

# Setup PostgreSQL
echo -e "${YELLOW}🗄️  Setting up PostgreSQL...${NC}"
sudo -u postgres psql <<EOF
CREATE DATABASE news_aggregator;
CREATE USER newsuser WITH PASSWORD 'change_this_password';
ALTER ROLE newsuser SET client_encoding TO 'utf8';
ALTER ROLE newsuser SET default_transaction_isolation TO 'read committed';
ALTER ROLE newsuser SET default_transaction_deferrable TO on;
ALTER ROLE newsuser SET default_transaction_read_committed TO on;
GRANT ALL PRIVILEGES ON DATABASE news_aggregator TO newsuser;
EOF

# Initialize database
echo -e "${YELLOW}📊 Initializing application database...${NC}"
cd $APP_DIR
sudo -u $APP_USER $APP_DIR/venv/bin/python scripts/init_db.py

# Create .env file
echo -e "${YELLOW}⚙️  Creating environment configuration...${NC}"
sudo -u $APP_USER cat > $APP_DIR/.env <<EOF
# Production Environment
ENVIRONMENT=production
DEBUG=False
APP_NAME=News Aggregator

# Database
DATABASE_URL=postgresql://newsuser:change_this_password@localhost:5432/news_aggregator

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Keys (Add your keys here)
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
NEWS_API_KEY=your_key_here

# Application
SECRET_KEY=change-this-to-a-random-string-$(date +%s)
ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,localhost,127.0.0.1

# Logging
LOG_LEVEL=INFO
EOF

echo -e "${GREEN}✓ Environment file created at $APP_DIR/.env${NC}"

# Setup Nginx
echo -e "${YELLOW}🌐 Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/$APP_NAME <<EOF
upstream gunicorn_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;
    client_max_body_size 50M;

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static/ {
        alias $APP_DIR/static/;
        expires 30d;
    }

    location /media/ {
        alias $APP_DIR/media/;
        expires 7d;
    }
}
EOF

# Enable Nginx site
if [ -L /etc/nginx/sites-enabled/$APP_NAME ]; then
    rm /etc/nginx/sites-enabled/$APP_NAME
fi
ln -s /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

# Test Nginx
nginx -t
systemctl restart nginx
echo -e "${GREEN}✓ Nginx configured${NC}"

# Setup Supervisor for Gunicorn
echo -e "${YELLOW}🔧 Setting up Supervisor (process manager)...${NC}"
cat > /etc/supervisor/conf.d/$APP_NAME.conf <<EOF
[program:$APP_NAME]
directory=$APP_DIR
command=$APP_DIR/venv/bin/gunicorn news_aggregator.src.app:app -w 4 -b 127.0.0.1:8000 --timeout 120
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/gunicorn.log
environment=PATH="$APP_DIR/venv/bin",DATABASE_URL="postgresql://newsuser:change_this_password@localhost:5432/news_aggregator"

[program:celery_worker]
directory=$APP_DIR
command=$APP_DIR/venv/bin/celery -A news_aggregator.src.tasks.celery_app worker --loglevel=info
user=$APP_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/celery.log
environment=PATH="$APP_DIR/venv/bin"
EOF

mkdir -p $APP_DIR/logs
chown -R $APP_USER:$APP_USER $APP_DIR/logs

supervisorctl reread
supervisorctl update
supervisorctl start $APP_NAME celery_worker
echo -e "${GREEN}✓ Supervisor configured${NC}"

# Setup SSL Certificate
echo -e "${YELLOW}🔒 Setting up SSL certificate...${NC}"
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

# Start services
echo -e "${YELLOW}🚀 Starting services...${NC}"
systemctl enable nginx redis-server postgresql supervisor
systemctl restart nginx redis-server postgresql supervisor

# Print summary
echo ""
echo -e "${GREEN}✅ Deployment Complete!${NC}"
echo ""
echo "📋 Summary:"
echo "  App Directory: $APP_DIR"
echo "  App User: $APP_USER"
echo "  Domain: $DOMAIN"
echo "  API URL: https://$DOMAIN"
echo "  Docs: https://$DOMAIN/docs"
echo ""
echo "⚠️  IMPORTANT - Edit these before production:"
echo "  1. $APP_DIR/.env - Update all API keys and passwords"
echo "  2. Change PostgreSQL password in .env"
echo "  3. Change SECRET_KEY in .env"
echo ""
echo "📊 Check status:"
echo "  supervisorctl status"
echo "  docker logs"
echo ""
echo "🔗 Your application is ready at: https://$DOMAIN"
echo ""