from __future__ import annotations

import logging
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from sys import exit
from os import environ

from ConfigFramework import BaseConfig, loaders
from ConfigFramework.variables import BoolVar, ConfigVar, IntVar
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import AsyncAdaptedQueuePool

from Quadrant.config import casters, validators
from Quadrant.config.defaults import defaults

parser = ArgumentParser()
parser.add_argument(
    "--config", "-c", action="store", dest="config_path",
    default=Path(__file__).parent / "config.yaml", type=Path
)
parser.add_argument("--make-config", "--new-config", action="store_true", dest="create_config", default=False)

launch_args, unknown = parser.parse_known_args()
if not launch_args.config_path.is_file() and not launch_args.create_config:
    raise ValueError("[--config] launch argument accepts path to config upload only")

yaml_path = launch_args.config_path

if environ.get("testing"):
    yaml_path = Path(__file__).parent / "test_config.yaml"

if launch_args.create_config:
    yaml_path.touch()
    yaml_loader = loaders.YAMLLoader(data=defaults, defaults={}, config_path=yaml_path)
    yaml_loader.dump()
    print(f"Quadrant config has been initialized. Edit config at {yaml_path}")
    exit(1)

env_loader = loaders.EnvLoader.load()
yaml_loader = loaders.YAMLLoader.load(yaml_path)
composite_loader = loaders.CompositeLoader.load(env_loader, yaml_loader, defaults=defaults)


class QuadrantConfig(BaseConfig):
    # Represents max size of payloads
    debug_mode: ConfigVar[bool] = BoolVar("Quadrant/debug_mode", composite_loader, default=False)
    disable_registration = BoolVar("Quadrant/disable_registration", composite_loader, default=False)
    static_folder_location: ConfigVar[Path] = ConfigVar(
        "Quadrant/static_folder_location", composite_loader, caster=Path,
        default=Path(__file__).parent.parent / "static"
    )
    media_folder_location: ConfigVar[Path] = ConfigVar(
        "Quadrant/media_folder_location", composite_loader, caster=Path,
        default=Path(__file__).parent.parent / "media"
    )
    host_static_files_internally: ConfigVar[bool] = BoolVar(
        "Quadrant/host_static_files_internally", composite_loader, default=True
    )

    class DBConfig(BaseConfig):
        # This chat supports only postgresql
        db_uri: ConfigVar[str] = ConfigVar(
            "Quadrant/db/db_uri", composite_loader, validator=validators.validate_is_postgresql
        )
        # Number of connections to database app will be using
        pool_size: ConfigVar[int] = IntVar(
            "Quadrant/db/pool_size", composite_loader, default=15, validator=lambda v: v >= 0
        )
        # Any keyword args for sqlalchemy engine
        kwargs: ConfigVar[dict] = ConfigVar("Quadrant/db/kwargs", yaml_loader, default={})

        def __post_init__(self, *args, **kwargs):
            self.kwargs.value.pop('pool_size', None)
            self.kwargs.value.pop('poolclass', None)

            self.async_base_engine = create_async_engine(
                self.db_uri.value,
                poolclass=AsyncAdaptedQueuePool,
                pool_size=self.pool_size.value,
                **self.kwargs.value
            )

    class LoggingConfig(BaseConfig):
        logs_dir: ConfigVar[Path] = ConfigVar(
            "Quadrant/quadrant_logging/logs_dir", composite_loader, caster=Path,
            default=Path(__file__).parent.parent / "logs", constant=True
        )
        date_format: ConfigVar[str] = ConfigVar(
            "Quadrant/quadrant_logging/date_format", yaml_loader,
            validator=lambda v: bool(datetime.now().strftime(v)), constant=True
        )
        log_format: ConfigVar[str] = ConfigVar(
            "Quadrant/quadrant_logging/format", yaml_loader, validator=lambda v: bool(logging.Formatter(v)),
            constant=True
        )
        app_log_level: ConfigVar[int] = ConfigVar(
            "Quadrant/quadrant_logging/AppLogLevel", yaml_loader,
            caster=lambda level: getattr(logging, level),
            constant=True
        )
        access_log_level: ConfigVar[int] = ConfigVar(
            "Quadrant/quadrant_logging/AccessLogLevel", yaml_loader,
            caster=lambda level: getattr(logging, level),
            constant=True
        )
        general_log_level: ConfigVar[int] = ConfigVar(
            "Quadrant/quadrant_logging/GeneralLogLevel", yaml_loader,
            caster=lambda level: getattr(logging, level),
            constant=True
        )

        def __post_init__(self, *args, **kwargs):
            self.logs_dir.value.mkdir(exist_ok=True)
            self.app_log_path: Path = self.logs_dir.value / "app_log_path"
            self.app_log_path.mkdir(exist_ok=True)

            self.access_log_path: Path = self.logs_dir.value / "access_log_path"
            self.access_log_path.mkdir(exist_ok=True)

            self.general_log_path: Path = self.logs_dir.value / "general_log_path"
            self.general_log_path.mkdir(exist_ok=True)

        class LogsRotationConfig(BaseConfig):
            when: ConfigVar[str] = ConfigVar("Quadrant/quadrant_logging/rotation/when", yaml_loader, constant=True)
            interval: ConfigVar[int] = IntVar(
                "Quadrant/quadrant_logging/rotation/interval", yaml_loader, validator=lambda v: v >= 1,
                constant=True
            )
            backup_count: ConfigVar[str] = IntVar(
                "Quadrant/quadrant_logging/rotation/backupCount", yaml_loader,
                validator=lambda v: v >= 1, constant=True
            )
            encoding: ConfigVar[str] = ConfigVar(
                "Quadrant/quadrant_logging/rotation/encoding", yaml_loader,
                validator=validators.validate_encoding,
                default='utf-8', constant=True
            )
            utc_time: ConfigVar[bool] = BoolVar(
                "Quadrant/quadrant_logging/rotation/utc", yaml_loader,
                default=True, constant=True
            )

    class Security(BaseConfig):
        cookie_secret: ConfigVar[str] = ConfigVar(
            "Quadrant/security/cookie_secret", composite_loader, validator=lambda v: v != "EXAMPLE_COOKIE_SECRET"
        )
        csrf_secret: ConfigVar[str] = ConfigVar(
            "Quadrant/security/csrf_secret", composite_loader, validator=lambda v: v != "EXAMPLE_CSRF_SECRET"
        )
        default_host: ConfigVar[str] = ConfigVar("Quadrant/security/default_host", composite_loader)

    def __post_init__(self, *args, **kwargs):
        static_location: Path = self.static_folder_location.value
        static_location.mkdir(exist_ok=True)

        media_location: Path = self.media_folder_location.value
        media_location.mkdir(exist_ok=True)
        self.uploads = (media_location / "uploads")
        self.profile_pictures_dir = (media_location / "profile_pictures")
        self.uploads.mkdir(exist_ok=True)
        self.profile_pictures_dir.mkdir(exist_ok=True)


quadrant_config = QuadrantConfig()
