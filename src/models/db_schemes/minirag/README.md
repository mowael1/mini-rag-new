## Run Alembic Migrations

### Configrations

```bash
cp alembic-example.ini alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)

### (Optional) Create a new migration

```bash
alembic revision --autogenrate -m "Add ..."
```

### Upgrade the database

```bash
alembic upgrade head
```