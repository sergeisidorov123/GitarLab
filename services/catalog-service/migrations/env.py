import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine.url import make_url
from alembic import context

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.core.database import Base
from app.models.song import Song
from app.models.tuning import Tuning

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata


def get_database_url() -> str:
    url = config.get_main_option("sqlalchemy.url")
    if not url or url == "driver://user:pass@localhost/dbname":
        url = settings.DATABASE_URL
    return url


def get_sync_url(url: str) -> str:
    parsed = make_url(url)
    if parsed.drivername.endswith("+asyncpg"):
        parsed = parsed.set(drivername="postgresql")
    return str(parsed)


def run_migrations_offline():
    url = get_database_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        {"sqlalchemy.url": get_sync_url(get_database_url())},
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()