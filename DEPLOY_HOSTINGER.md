# 🚀 Deploy to Hostinger VPS - Complete Guide

## ✅ Quick Answer: YES!

**Yes, you can use Hostinger!** The **VPS plan** is perfect for your FastAPI application.

---

## 🎯 Which Hostinger Plan?

| Plan | Works? | Cost | Notes |
|------|--------|------|-------|
| **Shared Hosting** | ❌ No | $2-8/mo | Can't run Python apps |
| **VPS** | ✅✅ **YES** | $3-6/mo (promo) | **RECOMMENDED** |
| **Cloud Hosting** | ✅ Yes | $4-8/mo | Good alternative |
| **WordPress Hosting** | ❌ No | $3-15/mo | WordPress only |

**👉 Choose: Hostinger VPS with Ubuntu 22.04**

---

## 📋 Deployment Steps

### Step 1: Get Hostinger VPS Account

1. Visit: https://www.hostinger.com/vps-hosting
2. Choose **VPS Plan** (2GB RAM minimum, 2+ CPU cores)
3. Select **Ubuntu 22.04** OS
4. Complete purchase
5. Get SSH credentials from Hostinger dashboard

### Step 2: Connect to Your Server

**On Windows (using PowerShell):**
```powershell
ssh root@YOUR_HOSTINGER_IP
```

You'll be prompted for password (from Hostinger email).

**Example:**
```powershell
ssh root@203.0.113.45
# Password: **** (paste from email)
```

### Step 3: Run Automated Deployment

Once connected to SSH:

```bash
# Download and run deployment script
curl -O https://raw.githubusercontent.com/your-repo/news-aggregator/main/scripts/deploy_hostinger.sh
bash deploy_hostinger.sh
```

**Or manually follow the steps below:**

---

## 🔧 Manual Deployment (If Script Fails)

### Step 1: Update System
```bash
apt update
apt upgrade -y
```

### Step 2: Install Required Packages
```bash
apt install -y python3.11 python3.11-venv python3-pip \
    postgresql postgresql-contrib redis-server \
    nginx git curl wget certbot python3-certbot-nginx \
    supervisor
```

### Step 3: Create Application User
```bash
useradd -m -s /bin/bash appuser
```

### Step 4: Clone Your Repository
```bash
cd /home/appuser
git clone https://github.com/YOUR-USERNAME/news-aggregator.git
cd news-aggregator
```

### Step 5: Setup Python Environment
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

### Step 6: Setup PostgreSQL

```bash
sudo -u postgres psql
```

In the PostgreSQL prompt:
```sql
CREATE DATABASE news_aggregator;
CREATE USER newsuser WITH PASSWORD 'your_secure_password';
ALTER ROLE newsuser SET client_encoding TO 'utf8';
ALTER ROLE newsuser SET default_transaction_isolation TO 'read committed';
GRANT ALL PRIVILEGES ON DATABASE news_aggregator TO newsuser;
\q
```

### Step 7: Create .env File
```bash
cat > /home/appuser/news-aggregator/.env <<EOF
# Production Settings
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://newsuser:your_secure_password@localhost:5432/news_aggregator
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=sk-your-key
ANTHROPIC_API_KEY=your-key
NEWS_API_KEY=your-key

# Security
SECRET_KEY=your-very-long-random-string-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Logging
LOG_LEVEL=INFO
EOF
```

### Step 8: Initialize Database
```bash
cd /home/appuser/news-aggregator
python scripts/init_db.py
```

### Step 9: Setup Nginx (Web Server)

Create config:
```bash
cat > /etc/nginx/sites-available/news-aggregator <<'EOF'
upstream gunicorn_app {
    server 127.0.0.1:8000 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    client_max_body_size 50M;

    location / {
        proxy_pass http://gunicorn_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
```

Enable it:
```bash
ln -s /etc/nginx/sites-available/news-aggregator /etc/nginx/sites-enabled/
nginx -t  # Test config
systemctl restart nginx
```

### Step 10: Setup Process Manager (Supervisor)

```bash
cat > /etc/supervisor/conf.d/news-aggregator.conf <<'EOF'
[program:news-aggregator]
directory=/home/appuser/news-aggregator
command=/home/appuser/news-aggregator/venv/bin/gunicorn news_aggregator.src.app:app -w 4 -b 127.0.0.1:8000
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/appuser/news-aggregator/logs/gunicorn.log

[program:celery_worker]
directory=/home/appuser/news-aggregator
command=/home/appuser/news-aggregator/venv/bin/celery -A news_aggregator.src.tasks.celery_app worker
user=appuser
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/home/appuser/news-aggregator/logs/celery.log
EOF
```

Create logs directory:
```bash
mkdir -p /home/appuser/news-aggregator/logs
chown -R appuser:appuser /home/appuser/news-aggregator/logs
```

Start services:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start news-aggregator celery_worker
```

### Step 11: Setup SSL Certificate (HTTPS)

```bash
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### Step 12: Enable Auto-Start

```bash
systemctl enable nginx
systemctl enable postgresql
systemctl enable redis-server
systemctl enable supervisor
```

---

## ✅ Verify Deployment

Check if everything is running:

```bash
# Check supervisor services
supervisorctl status

# Check Nginx
systemctl status nginx

# Check Redis
systemctl status redis-server

# Check PostgreSQL
systemctl status postgresql

# Check if API is responding
curl http://localhost:8000/

# View app logs
tail -f /home/appuser/news-aggregator/logs/gunicorn.log
```

---

## 🌐 Access Your Application

Once everything is running:

- **API Base:** https://your-domain.com
- **Interactive Docs:** https://your-domain.com/docs
- **Alternative Docs:** https://your-domain.com/redoc

---

## ⚙️ Configuration Tips

### Production Settings (.env)
```
DEBUG=False              # Never enable in production
ENVIRONMENT=production
LOG_LEVEL=ERROR          # Reduce noise in production
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
```

### Database Backups
```bash
# Backup PostgreSQL
pg_dump -U newsuser news_aggregator > backup.sql

# Restore from backup
psql -U newsuser news_aggregator < backup.sql
```

### Monitor Logs
```bash
# Gunicorn logs
tail -f /home/appuser/news-aggregator/logs/gunicorn.log

# Celery logs
tail -f /home/appuser/news-aggregator/logs/celery.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart app
supervisorctl restart news-aggregator

# Restart celery worker
supervisorctl restart celery_worker

# Restart web server
systemctl restart nginx
```

---

## 🐛 Troubleshooting

### Issue: "Connection refused" when accessing site
```bash
# Check if Nginx is running
systemctl status nginx

# Check if gunicorn is running
supervisorctl status

# Restart both
systemctl restart nginx
supervisorctl restart news-aggregator
```

### Issue: Database connection error
```bash
# Verify PostgreSQL is running
systemctl status postgresql

# Check credentials in .env
grep DATABASE_URL /home/appuser/news-aggregator/.env

# Restart PostgreSQL
systemctl restart postgresql
```

### Issue: "Domain not found" error
```bash
# Make sure DNS is pointing to Hostinger IP
# (Check your domain registrar DNS settings)

# Test DNS
nslookup your-domain.com

# Should show Hostinger's IP
```

### Issue: SSL certificate not working
```bash
# Renew certificate
certbot renew --force-renewal

# Check certificate status
certbot certificates
```

### Issue: Out of memory
```bash
# Reduce Gunicorn workers
# In /etc/supervisor/conf.d/news-aggregator.conf:
# Change: -w 4 
# To: -w 2

supervisorctl restart news-aggregator
```

---

## 📊 Performance Optimization

### Scale Gunicorn Workers
Edit `/etc/supervisor/conf.d/news-aggregator.conf`:
```
command=/home/appuser/news-aggregator/venv/bin/gunicorn \
    news_aggregator.src.app:app -w 4 -b 127.0.0.1:8000
```

Recommended workers: `number_of_cpu_cores * 2 + 1`

### Enable Caching
Edit `.env`:
```
REDIS_URL=redis://localhost:6379/0
CACHE_ENABLED=true
```

### Database Query Optimization
```sql
-- Check slow queries
SELECT query, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

---

## 🔐 Security Checklist

- [x] SSH key authentication (instead of password)
- [x] Firewall configured (UFW)
- [x] SSL/TLS enabled (HTTPS)
- [x] Strong database passwords
- [x] API keys not in version control
- [x] Debug mode disabled in production
- [x] Regular backups configured
- [x] Fail2Ban installed (optional, for DDoS protection)

### Setup Firewall
```bash
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

---

## 💰 Cost Estimation

**Hostinger VPS (recommended):**
- **Initial:** $3-6/month (promotional pricing)
- **Renewal:** $12-15/month
- **Domain:** $8-12/year
- **SSL Certificate:** Free (Let's Encrypt via Certbot)

**Total Monthly:** ~$12-15/month

---

## 📈 Next Steps After Deployment

1. ✅ Test the application
2. ✅ Setup monitoring (New Relic, DataDog, etc.)
3. ✅ Configure email notifications
4. ✅ Setup automated backups
5. ✅ Create CI/CD pipeline (GitHub Actions)
6. ✅ Setup CDN for static files (Cloudflare)
7. ✅ Monitor resource usage
8. ✅ Create update/rollback procedures

---

## 🎯 Hostinger-Specific Tips

### Via Hostinger Control Panel
1. Login to Hostinger Control Panel
2. Navigate to VPS → Your Server
3. SSH Access: Get SSH credentials
4. File Manager: Upload files via browser (slower)
5. Backups: Enable automatic backups

### Connect via Hostinger's Terminal
Instead of SSH, you can use Hostinger's web-based terminal:
1. Go to VPS Dashboard
2. Click "Terminal"
3. Paste commands directly

### Monitor Resources
- Hostinger Dashboard shows CPU, RAM, Disk usage in real-time
- Setup alerts if resources exceed threshold

---

## 🚀 One-Line Deployment (Automated)

If you push your code to GitHub:

```bash
# SSH into your Hostinger server
ssh root@your-hostinger-ip

# Clone repo and run deployment
git clone https://github.com/your-username/news-aggregator.git
cd news-aggregator
bash scripts/deploy_hostinger.sh
```

---

## 📞 Support Resources

- **Hostinger Support:** https://www.hostinger.com/help (24/7 chat)
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Gunicorn Docs:** https://docs.gunicorn.org
- **PostgreSQL Docs:** https://www.postgresql.org/docs/

---

**You're all set! Your News Aggregator will be live on Hostinger VPS in under 30 minutes!** 🎉