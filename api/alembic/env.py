from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
from infrastructure.configuracion import configuracion
from infrastructure.models.base import Base
from infrastructure.models.usuario import Usuario, RefreshToken
from infrastructure.models.ruta import Ruta, AsignacionRuta, rutas_favoritas
from infrastructure.models.bus import Bus, Empresa 
from infrastructure.models.rastreador import Rastreador, OperadorRedMovil, AsignacionRastreador
from infrastructure.models.paradero import Paradero
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Tablas que Alembic gestiona. El resto de las tablas mapeadas en Base
# (busadmin_*, loginuser_*, paraderosadmin_*, rutasadmin_*, rastreadoresadmin_*)
# son creadas y migradas por Django; se excluyen del autogenerate para que
# Alembic nunca intente dropearlas ni alterarlas.
ALEMBIC_MANAGED_TABLES = {"refresh_token","usuario_rutafavorita","secretorastreador"}


def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return name in ALEMBIC_MANAGED_TABLES
    return True

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
database_url: str = f"postgresql+psycopg2://{configuracion.db_user}:{configuracion.db_password}@{configuracion.db_host}:{configuracion.db_port}/{configuracion.db_name}"
config.set_main_option("sqlalchemy.url", database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
