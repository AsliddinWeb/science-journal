# Deploy — academicbook.uz (Ubuntu + Docker + host nginx + Certbot)

Bu qo'llanma **yangi / bo'sh Ubuntu server**ni noldan sozlashdan boshlab to ishlayotgan
`https://academicbook.uz` saytigacha olib boradi.

Serverda **boshqa loyihalar ham turadi** — shu sababli:

* Loyiha konteynerlari faqat `127.0.0.1` ga bog'lanadi (dunyoga `80/443` faqat host nginx).
* Tashqiga beradigan yagona port — `127.0.0.1:18801` (boshqa loyihalar port'lari bilan to'qnashmaslik uchun noyob raqam).
* `docker compose` loyiha nomi **`academicbook`** — konteyner nomlari ham shundan boshlanadi (`academicbook-api-1` va hk.), shu bois boshqa loyihalardagi `ilmiyjurnal-*` / `api-1` kabi nomlar bilan aralashmaydi.

Arxitektura:

```
Internet 80/443 ──► host nginx ──► 127.0.0.1:18801 (Docker nginx)
                                       │
                                       ├─► Vue SPA        (internal)
                                       ├─► FastAPI        (internal, :8000)
                                       └─► /api/uploads/  (docker volume)
```

---

## 0. DNS (birinchi bo'lib qiling)

Domen provayderingizda (academicbook.uz) A-yozuvlarni server IP ga yo'naltiring:

| Host | Type | Value |
| --- | --- | --- |
| `@`   | A | `SERVER_IP` |
| `www` | A | `SERVER_IP` |

`dig academicbook.uz +short` natijasi to'g'ri IP ga ishora qilgach keyingi bosqichga o'ting (propagation 5 daqiqadan 1–2 soatgacha).

---

## 1. Ubuntu serverni sozlash (faqat bir marta)

Quyidagi hamma komandalar **root yoki sudo user** dan bajariladi. Agar siz root bo'lsangiz `sudo` ni tushirib qoldiring.

### 1.1. Tizimni yangilash

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git ufw ca-certificates gnupg lsb-release
sudo timedatectl set-timezone Asia/Tashkent
```

### 1.2. Non-root deploy user (tavsiya etiladi)

```bash
# O'rniga istalgan nom — men "deploy" ishlataman
sudo adduser --disabled-password --gecos "" deploy
sudo usermod -aG sudo deploy

# SSH kalitlarini ko'chirish (agar root orqali SSH kirgan bo'lsangiz)
sudo rsync -a --chown=deploy:deploy /root/.ssh /home/deploy/

# Keyingi qadamlar uchun unga o'tib oling
su - deploy
```

### 1.3. Firewall (UFW)

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
sudo ufw status
```

> Docker o'z-o'zicha iptables'ni o'zgartiradi va UFW'ni aylanib o'tishi mumkin.
> Bizda tashqi bog'lanish faqat `127.0.0.1:18801` ga — UFW/Docker to'qnashuvi yuzaga kelmaydi.

### 1.4. Docker + Docker Compose plugin

```bash
# Docker repo
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
  | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Foydalanuvchini docker guruhiga qo'shish
sudo usermod -aG docker $USER
# Yangi guruh amalga oshishi uchun qayta kiring yoki:
newgrp docker

docker --version
docker compose version
```

### 1.5. Host nginx + Certbot

```bash
sudo apt install -y nginx certbot python3-certbot-nginx
sudo systemctl enable --now nginx
sudo nginx -v
```

### 1.6. (ixtiyoriy) fail2ban — SSH bruteforce himoyasi

```bash
sudo apt install -y fail2ban
sudo systemctl enable --now fail2ban
```

### 1.7. Swap (agar RAM ≤ 2 GB bo'lsa — build paytida OOM'dan saqlanish)

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 2. Loyihani serverga joylashtirish

```bash
sudo mkdir -p /opt/academicbook
sudo chown -R $USER:$USER /opt/academicbook
cd /opt/academicbook

git clone https://github.com/AsliddinWeb/science-journal.git .
# yoki boshqa remote — repo nomi muhim emas, katalog /opt/academicbook
```

---

## 3. `.env` tayyorlash

```bash
cp .env.example .env
nano .env
```

Quyidagi qiymatlar **albatta** to'ldirilishi kerak:

```bash
# ── Database ──
POSTGRES_DB=academicbook
POSTGRES_USER=academicbook
POSTGRES_PASSWORD=<STRONG_RANDOM>                 # openssl rand -hex 24
DATABASE_URL=postgresql+asyncpg://academicbook:<STRONG_RANDOM>@db:5432/academicbook
SYNC_DATABASE_URL=postgresql://academicbook:<STRONG_RANDOM>@db:5432/academicbook

# ── JWT ──
SECRET_KEY=<VERY_LONG_RANDOM>                     # openssl rand -hex 64
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=30

# ── SMTP (ixtiyoriy, email uchun) ──
MAIL_USERNAME=noreply@academicbook.uz
MAIL_PASSWORD=...
MAIL_FROM=noreply@academicbook.uz
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Academic Book
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

# ── App ──
APP_NAME=Academic Book
APP_URL=https://academicbook.uz
ALLOWED_ORIGINS=https://academicbook.uz,https://www.academicbook.uz
DEBUG=False

# ── Redis ── (internal, qoldiring)
REDIS_URL=redis://redis:6379/0

# ── Docker tashqi nginx porti (boshqa loyiha egallagan bo'lsa o'zgartiring) ──
NGINX_HOST_PORT=18801
```

> `.env` **hech qachon git'ga commit qilinmasin** — `.gitignore` da turadi.

---

## 4. Docker konteynerlarni ishga tushirish

Loyiha nomini aniq belgilang — bu konteyner nomlari va volume nomlariga prefiks beradi, shu bois serverdagi boshqa loyihalar bilan aralashmaydi.

```bash
cd /opt/academicbook

docker compose \
  -p academicbook \
  -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --build
```

> **Muhim**: `docker-compose.override.yml` — dev rejim uchun. Production'da har doim `-f docker-compose.yml -f docker-compose.prod.yml` flaglarini bering, bu override'ni o'tkazib yuboradi.

Holat:

```bash
docker compose -p academicbook ps
# Hamma service "healthy" / "running" bo'lishi kerak
```

### Alias (ixtiyoriy)

Har safar uzun komanda yozmaslik uchun `~/.bashrc` ga qo'shing:

```bash
alias ab='docker compose -p academicbook -f /opt/academicbook/docker-compose.yml -f /opt/academicbook/docker-compose.prod.yml'
```

Keyin `ab ps`, `ab logs -f api`, `ab exec api bash` kabi ishlatasiz.

---

## 5. Migration + seed + birinchi admin

```bash
# Migratsiyalar
docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml \
  exec api alembic upgrade head

# Static sahifalar seed
docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml \
  exec api python seed_pages.py

# Superadmin yaratish
docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml \
  exec api python -c "
import asyncio, uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.user import User, UserRole
from app.services.auth import hash_password

async def main():
    engine = create_async_engine(settings.DATABASE_URL)
    S = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with S() as db:
        async with db.begin():
            db.add(User(
                id=uuid.uuid4(),
                email='admin@academicbook.uz',
                password_hash=hash_password('CHANGE_THIS_STRONG_PASSWORD'),
                full_name='Super Admin',
                role=UserRole.superadmin,
                is_active=True,
                is_verified=True,
            ))
    await engine.dispose()
    print('admin@academicbook.uz yaratildi')

asyncio.run(main())
"
```

Ishlayotganini tekshiring (loopback'dan):

```bash
curl -s http://127.0.0.1:18801/api/health
# {"status":"ok"}

curl -I http://127.0.0.1:18801/
# HTTP/1.1 200 OK
```

---

## 6. Host nginx — reverse proxy

```bash
sudo nano /etc/nginx/sites-available/academicbook.uz
```

Konfiguratsiya (**SSL bloklari yo'q** — Certbot o'zi qo'shadi):

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name academicbook.uz www.academicbook.uz;

    # Katta PDF yuklash uchun
    client_max_body_size 210m;

    # Real IP va proxy headers
    location / {
        proxy_pass http://127.0.0.1:18801;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Uzoq so'rovlar (fayl yuklash va hk.)
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }

    access_log /var/log/nginx/academicbook-access.log;
    error_log  /var/log/nginx/academicbook-error.log;
}
```

Faollashtiring va tekshirib oling:

```bash
sudo ln -s /etc/nginx/sites-available/academicbook.uz /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# DNS hali propagatsiya bo'lgan bo'lsa:
curl -I http://academicbook.uz
```

---

## 7. SSL — Certbot (HTTPS)

```bash
sudo certbot --nginx \
  -d academicbook.uz -d www.academicbook.uz \
  --redirect \
  --agree-tos \
  -m admin@academicbook.uz \
  --no-eff-email
```

Certbot:

* 443 uchun `ssl_certificate`, `ssl_certificate_key` bloklarini **avtomatik yozadi**.
* 80 → 443 redirect'ni qo'shadi (chunki `--redirect`).
* Cron yoki systemd timer'ga 90 kunlik renewal'ni qo'shadi.

Test:

```bash
curl -I https://academicbook.uz
sudo certbot renew --dry-run
```

---

## 8. Yangilanishlar (kelajakdagi deploy)

```bash
cd /opt/academicbook
git pull

docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml \
  up -d --build

docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml \
  exec api alembic upgrade head
```

---

## 9. Backup (cron-da)

`/etc/cron.d/academicbook-backup`:

```cron
# Har kuni 03:00 — DB + uploads
0 3 * * * deploy /opt/academicbook/scripts/backup.sh >> /var/log/academicbook-backup.log 2>&1
```

`/opt/academicbook/scripts/backup.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
STAMP=$(date +%Y%m%d-%H%M)
DEST=/opt/academicbook/backups
mkdir -p "$DEST"

# Database
docker compose -p academicbook -f /opt/academicbook/docker-compose.yml -f /opt/academicbook/docker-compose.prod.yml \
  exec -T db pg_dump -U academicbook academicbook | gzip > "$DEST/db-$STAMP.sql.gz"

# Uploads
docker run --rm \
  -v academicbook_uploads_data:/data:ro \
  -v "$DEST":/backup \
  alpine tar czf "/backup/uploads-$STAMP.tar.gz" -C /data .

# 30 kundan eski backuplarni tozalash
find "$DEST" -type f -mtime +30 -delete
```

```bash
chmod +x /opt/academicbook/scripts/backup.sh
```

---

## 10. Kundalik operatsiyalar

```bash
# Statuslar
docker compose -p academicbook ps

# Real-time log
docker compose -p academicbook logs -f api
docker compose -p academicbook logs -f nginx

# API ichiga kirish
docker compose -p academicbook exec api bash

# Container qayta ishga tushirish
docker compose -p academicbook restart api

# To'liq to'xtatish
docker compose -p academicbook down

# To'liq qayta ishga tushirish
docker compose -p academicbook -f docker-compose.yml -f docker-compose.prod.yml up -d
```

---

## Port xaritasi (qisqa ma'lumot)

| Xizmat | Ichki (docker net) | Hostga chiqqan | Tashqi |
| --- | --- | --- | --- |
| Docker nginx | `nginx:80` | `127.0.0.1:18801` | — |
| FastAPI | `api:8000` | — | — |
| Vue frontend | `frontend:80` | — | — |
| Postgres | `db:5432` | — | — |
| Redis | `redis:6379` | — | — |
| **Host nginx** | — | `0.0.0.0:80`, `0.0.0.0:443` | Internet |

Serverda ikkinchi loyiha qo'shsangiz — faqat `NGINX_HOST_PORT=18802` (yoki boshqa) berib, yangi `/etc/nginx/sites-available/…` faylida uning o'z `server_name` ini ishlating. Host nginx `server_name` bo'yicha marshrutlaydi, port kollizyasi bo'lmaydi.

---

## Troubleshooting

* **`502 Bad Gateway`** → host nginx docker nginx'ga ulana olmayapti. `docker compose -p academicbook ps` va `curl http://127.0.0.1:18801/api/health` tekshiring.
* **`403 Forbidden` nginx-da** → SELinux/AppArmor odatda Ubuntu'da to'siq qilmaydi; `sudo tail -n 100 /var/log/nginx/academicbook-error.log` ga qarang.
* **Certbot `Connection refused`** → DNS hali propagatsiya bo'lmagan yoki firewall 80'ni bloklagan. `sudo ufw status` + `dig academicbook.uz +short`.
* **Build OOM** (RAM kam) → 1.7 bo'limdagi swap'ni yoqing, yoki `docker compose … build --memory=1g` bilan cheklang.
* **Email yuborilmayapti** → `docker compose -p academicbook logs -f worker`; SMTP credentials va firewall/port 587'ni tekshiring.
