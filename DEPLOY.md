# Production deploy — Ubuntu + Docker + host nginx + Certbot

Domain: `science.asliddin.me` (+ `www.science.asliddin.me`)

## Arxitektura

```
Internet
   │
   ▼
Host nginx (port 80/443, SSL)
   │
   ▼
Container nginx (127.0.0.1:8088)
   │
   ├─→ Vue frontend (Docker)
   ├─→ FastAPI backend (Docker)
   └─→ /api/uploads/ → Docker volume
```

---

## 1. Serverga loyihani yuklash

```bash
# Server-da
cd /opt
sudo git clone https://github.com/USERNAME/IlmiyJurnal.git
sudo chown -R $USER:$USER IlmiyJurnal
cd IlmiyJurnal
```

## 2. .env yaratish (root da, yagona fayl)

```bash
cp .env.example .env
nano .env
```

To'ldirish kerak:
- `POSTGRES_PASSWORD` — kuchli parol
- `DATABASE_URL` va `SYNC_DATABASE_URL` — yangi parol bilan
- `SECRET_KEY` — `openssl rand -hex 64` bilan generatsiya qiling
- `MAIL_*` — SMTP credentials (Gmail App Password yoki boshqa)
- `APP_URL=https://science.asliddin.me`
- `ALLOWED_ORIGINS=https://science.asliddin.me,https://www.science.asliddin.me`
- `DEBUG=False`

## 3. Docker containerlarni ishga tushirish

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

> **Diqqat**: `docker-compose.override.yml` development uchun. Production da `-f docker-compose.yml -f docker-compose.prod.yml` flag-larini ishlating — bu override ni o'tkazib yuboradi.

## 4. Migration ishga tushirish

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

## 5. Initial admin user va seed data

```bash
# Static sahifalarni yaratish
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api python seed_pages.py

# Admin user yaratish (interactive)
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api python -c "
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User, UserRole
from app.utils.security import get_password_hash
import uuid

async def create_admin():
    engine = create_async_engine(settings.DATABASE_URL)
    S = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with S() as db:
        async with db.begin():
            user = User(
                id=uuid.uuid4(),
                email='admin@science.asliddin.me',
                password_hash=get_password_hash('CHANGE_ME_strong_password'),
                full_name='Super Admin',
                role=UserRole.superadmin,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
    await engine.dispose()
    print('Admin created: admin@science.asliddin.me')

asyncio.run(create_admin())
"
```

## 6. Tekshirish

```bash
# Container ichida API ishlayaptimi
curl http://127.0.0.1:8088/api/health

# Frontend
curl -I http://127.0.0.1:8088/
```

## 7. Host nginx config (siz o'zingiz qilasiz)

`/etc/nginx/sites-available/science.asliddin.me`:

```nginx
server {
    listen 80;
    server_name science.asliddin.me www.science.asliddin.me;

    # Certbot ACME challenge
    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    # Redirect to HTTPS
    location / {
        return 301 https://$host$request_uri;
    }
}

server {
    listen 443 ssl http2;
    server_name science.asliddin.me www.science.asliddin.me;

    ssl_certificate /etc/letsencrypt/live/science.asliddin.me/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/science.asliddin.me/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # File upload limit
    client_max_body_size 50m;

    # Reverse proxy to docker container
    location / {
        proxy_pass http://127.0.0.1:8088;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 120s;
    }

    # Logs
    access_log /var/log/nginx/science.asliddin.me-access.log;
    error_log /var/log/nginx/science.asliddin.me-error.log;
}
```

## 8. SSL — Certbot

```bash
# Symlink yaratish va nginx tekshirish
sudo ln -s /etc/nginx/sites-available/science.asliddin.me /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Certbot bilan SSL olish
sudo certbot --nginx -d science.asliddin.me -d www.science.asliddin.me

# Avto-renewal tekshirish
sudo certbot renew --dry-run
```

## 9. Yangilanishlar

```bash
cd /opt/IlmiyJurnal
git pull
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec api alembic upgrade head
```

## 10. Backup (cron-da)

```bash
# DB backup
docker compose -f docker-compose.yml -f docker-compose.prod.yml exec -T db \
  pg_dump -U journal_user journal_db > /backups/journal_$(date +%Y%m%d).sql

# Uploads backup
docker run --rm -v ilmiyjurnal_uploads_data:/data -v /backups:/backup \
  alpine tar czf /backup/uploads_$(date +%Y%m%d).tar.gz -C /data .
```

## 11. Logs ko'rish

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f api
docker compose -f docker-compose.yml -f docker-compose.prod.yml logs -f nginx
```
