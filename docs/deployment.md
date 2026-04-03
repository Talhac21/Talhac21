# Deployment (Single Ubuntu VPS)

## 1) Prerequisites
```bash
sudo apt update
sudo apt install -y docker.io docker-compose-plugin
sudo systemctl enable --now docker
```

## 2) Configure
```bash
cp .env.example .env
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# çıktıdaki key'i .env içindeki SESSION_ENCRYPTION_KEY ile değiştirin
```

## 3) Start stack
```bash
./scripts/start.sh
```

## 4) Verify
```bash
curl -s http://localhost:8000/health
curl -s -H "x-admin-token: $API_ADMIN_TOKEN" http://localhost:8000/dashboard
```

## 5) Backup
```bash
./scripts/backup.sh
```

## 6) Restart policy
Compose dosyasında tüm servisler `restart: unless-stopped` ile tanımlıdır.
