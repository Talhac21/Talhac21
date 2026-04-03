# Rival Regions Control Panel (v1)

Bu repo, **en fazla 2 kullanıcıya ait hesap** için tasarlanmış güvenli ve küçük ölçekli bir RR kontrol panelidir.

## Güvenlik ve kapsam
- Proxy rotation / ban evasion / anti-detection / CAPTCHA bypass **yok**.
- Combat automation / farm-refill automation **yok**.
- Hesap bilgileri repo içinde tutulmaz.
- Session bootstrap manuel browser login ile yapılır.
- Session verisi şifreli saklanır (Fernet).

## Monorepo
- `apps/web` Next.js admin panel
- `apps/api` FastAPI API
- `apps/worker` DB-backed low-frequency scheduler worker
- `infra` Docker Compose + Caddy
- `docs` mimari ve deployment
- `scripts` start/backup yardımcıları

## Hızlı başlatma (lokal)
```bash
cp .env.example .env
# .env içinde SESSION_ENCRYPTION_KEY üret:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
./scripts/start.sh
```

## Servisler
- Web: `http://localhost:3000`
- API: `http://localhost:8000`
- API docs: `http://localhost:8000/docs`
- Caddy reverse proxy: `http://localhost`

## Smoke test
```bash
curl -s http://localhost:8000/health
curl -s -H "x-admin-token: $API_ADMIN_TOKEN" http://localhost:8000/dashboard
```

## Test komutları
```bash
docker compose -f infra/docker-compose.yml run --rm api pytest
docker compose -f infra/docker-compose.yml run --rm worker pytest
```

## Gerçekten çalışan v1 akışları
1. Hesap oluşturma (max 2 enforce).
2. Session bootstrap kaydetme + anlık session doğrulama.
3. Session healthcheck endpointi.
4. Dashboard’ın API’dan gerçek hesap/job/log verisi çekmesi.
5. Run-now perk çağrısı (başarısız/unsupported durumları fake success yerine açıkça döner).
6. Worker’ın sadece `enabled + valid + auto_enabled + due` hesaplarda job planlaması.
7. Audit/worker/error log endpointleri.
8. SQL migration tabanlı startup.

## Known limitations
- RR üzerinde güvenli ve kalıcı selector garantisi olmadan perk execution “unsupported” döndürür; fake success yok.
- Tags CRUD UI ve calculators UI minimaldir; backend veri akışı odaklı v1 tamamlanmıştır.
- Telegram entegrasyonu env verilmeden pasif kalır.
