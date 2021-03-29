import logging
from pathlib import Path
from sys import exit
from datetime import datetime

from ConfigFramework import BaseConfig, loaders
from ConfigFramework.variables import ConfigVar, IntVar, BoolVar
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool
from Quadrant.config import casters, validators
from .defaults import defaults

yaml_path = Path(__file__).parent / "config.yaml"

if not yaml_path.is_file():
    # Init config
    yaml_path.touch()
    yaml_loader = loaders.YAMLLoader.load(yaml_path, defaults)
    yaml_loader.dump(include_defaults=True)
    print(f"Quadrant config has been initialized. Edit config at {yaml_path}")
    exit(1)

yaml_loader = loaders.YAMLLoader.load(yaml_path)
env_loader = loaders.EnvLoader.load()
composite_loader = loaders.CompositeLoader.load(yaml_loader, env_loader)


class QuadrantConfig(BaseConfig):
    # Represents max size of payloads
    max_upload_file_size = ConfigVar(
        "Quadrant/max_upload_file_size", composite_loader, validator=lambda v: v >= 0, default='8M',
        caster=casters.file_size_caster, constant=True
    )
    static_folder_location = ConfigVar(
        "Quadrant/static_folder_location", composite_loader, caster=Path, validator=Path.is_dir,
        default=Path(__file__).parent.parent / "static"
    )
    media_folder_location = ConfigVar(
        "Quadrant/media_folder_location", composite_loader, caster=Path, validator=Path.is_dir,
        default=Path(__file__).parent.parent / "media"
    )
    host_static_files_internally = BoolVar(
        "Quadrant/host_static_files_internally", composite_loader, default=True
    )

    class DBConfig(BaseConfig):
        # This chat supports only postgresql
        db_uri = ConfigVar("Quadrant/db/db_uri", composite_loader, validator=validators.validate_is_postgresql)
        # Statements cache is useful to speed up app. If you can - set its value higher
        statements_cache_size = IntVar(
            "Quadrant/db/statements_cache_size", composite_loader, default=1000, validator=lambda v: v >= 0
        )
        # Number of connections to database app will be using
        pool_size = IntVar("Quadrant/db/pool_size", composite_loader, default=15, validator=lambda v: v >= 0)
        # Any keyword args for sqlalchemy engine
        kwargs = ConfigVar("Quadrant/db/kwargs", yaml_loader, default={})

        def __post_init__(self, *args, **kwargs):
            self.async_engine = create_async_engine(
                self.db_uri.value, dialect="asyncpg",
                prepared_statement_cache_size=self.statements_cache_size.value,
                pool=AsyncAdaptedQueuePool, pool_size=self.pool_size.value,
                **self.kwargs.value
            )

    class LoggingConfig(BaseConfig):
        logs_dir = ConfigVar(
            "Quadrant/logging/logs_dir", composite_loader, caster=Path, validator=Path.is_dir,
            default=Path(__file__).parent.parent / "logging/logs", constant=True
        )
        date_format = ConfigVar(
            "Quadrant/logging/date_format", yaml_loader, validator=datetime.now().strftime, constant=True
        )
        log_format = ConfigVar("Quadrant/logging/format", yaml_loader, caster=logging.Formatter, constant=True)
        tornado_app_log_level = ConfigVar(
            "Quadrant/logging/TornadoAppLogLevel", yaml_loader, caster=lambda level: getattr(logging, level),
            constant=True
        )
        tornado_access_log_level = ConfigVar(
            "Quadrant/logging/TornadoAccessLogLevel", yaml_loader, caster=lambda level: getattr(logging, level),
            constant=True
        )
        tornado_general_log_level = ConfigVar(
            "Quadrant/logging/TornadoGeneralLogLevel", yaml_loader, caster=lambda level: getattr(logging, level),
            constant=True
        )

        def __post_init__(self, *args, **kwargs):
            self.logs_dir.value.mkdir(exists_ok=True)
            self.app_log_path: Path = self.logs_dir.value / "app_log_path"
            self.app_log_path.mkdir(exist_ok=True)

            self.access_log_path: Path = self.logs_dir.value / "access_log_path"
            self.access_log_path.mkdir(exist_ok=True)

            self.general_log_path: Path = self.logs_dir.value / "general_log_path"
            self.general_log_path.mkdir(exist_ok=True)

        class LogsRotationConfig(BaseConfig):
            when = ConfigVar("Quadrant/logging/rotation/when", yaml_loader, constant=True)
            interval = IntVar(
                "Quadrant/logging/rotation/interval", yaml_loader, validator=lambda v: v >= 1,
                constant=True
            )
            backup_count = IntVar(
                "Quadrant/logging/rotation/backupCount", yaml_loader, validator=lambda v: v >= 1, constant=True
            )
            encoding = ConfigVar(
                "Quadrant/logging/rotation/encoding", yaml_loader, validator=validators.validate_encoding,
                default='utf-8', constant=True
            )
            utc_time = BoolVar("Quadrant/logging/rotation/utc", yaml_loader, default=True, constant=True)

    def __post_init__(self, *args, **kwargs):
        static_location: Path = self.static_folder_location.value
        static_location.mkdir(exist_ok=True)

        media_location: Path = self.media_folder_location.value
        media_location.mkdir(exist_ok=True)


quadrant_config = QuadrantConfig()