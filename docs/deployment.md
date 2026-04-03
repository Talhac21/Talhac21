# Deployment (Ubuntu VPS)

1. Install Docker and Docker Compose plugin.
2. Clone repo and set `.env` from `.env.example`.
3. Generate Fernet key:
   ```bash
   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
   ```
4. Start:
   ```bash
   ./scripts/start.sh
   ```
5. Validate:
   - `curl http://SERVER_IP/api/health`

## Backups
Run:
```bash
./scripts/backup.sh
```
This produces timestamped SQL dump and encrypted session export placeholder artifacts.
