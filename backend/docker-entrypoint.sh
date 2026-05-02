#!/bin/sh
set -e

# Выполнить миграции (если нужно) – для SQLite можно создать таблицы через create_all
python -c "from app.models.database import Base, engine; Base.metadata.create_all(bind=engine)"

exec "$@"