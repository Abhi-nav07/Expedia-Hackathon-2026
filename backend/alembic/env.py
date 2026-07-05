"""
Alembic migration environment.

Uses the SYNC database URL (psycopg2) for migrations even though the app
runs on the async engine at runtime — this is the standard, most reliable
pattern since Alembic's autogenerate machinery is synchronous internally.
"""
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make `app` importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.db.base import Base  # noqa: E402

# Import every model module here so Base.metadata is fully populated
# before autogenerate runs. Add new model imports as new tables are added.
from app.models.user import User  # noqa: E402, F401

config = context.config
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

if settings.is_sqlite:
    # The running app's lifespan (main.py) creates this directory, but
    # Alembic runs standalone — without this, `alembic upgrade head` on a
    # fresh clone (outside Docker, whose Dockerfile happens to pre-create
    # /app/data and masks this) fails with "unable to open database
    # file". Caught by an actual clean-room clone-and-migrate test.
    db_path = settings.DATABASE_URL_SYNC.split("///")[-1]
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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
