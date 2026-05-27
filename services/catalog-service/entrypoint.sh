#!/bin/sh

# Wait for Postgres to become available before running migrations.
python - <<'PY'
import os
import time
import socket

url = os.environ.get('DATABASE_URL')
if not url:
    raise SystemExit('DATABASE_URL is not set')

# Extract host and port from DATABASE_URL
# Format: postgresql+asyncpg://user:pass@host:port/dbname
try:
    host_part = url.split('@')[1].split(':')[0]
    port_part = int(url.split('@')[1].split(':')[1].split('/')[0])
except (IndexError, ValueError):
    print("Could not parse DATABASE_URL, using defaults")
    host_part = "catalog-db"
    port_part = 5432

print(f"Waiting for database at {host_part}:{port_part}...")
for i in range(30):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host_part, port_part))
        sock.close()
        if result == 0:
            print("Database is ready!")
            break
    except:
        pass
    print(f"Attempt {i+1}/30: Database not ready, waiting...")
    time.sleep(1)
else:
    print("Database did not become available in time, but continuing...")
PY

alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload