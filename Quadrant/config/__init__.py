import logging
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from sys import exit

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
    raise ValueError("[--config] launch argument accepts path to config file only")

yaml_path = launch_args.config_path

if launch_args.create_config:
    yaml_path.touch()
    yaml_loader = loaders.YAMLLoader(data=defaults, defaults={}, config_path=yaml_path)
    yaml_loader.dump()
    print(f"Quadrant config has been initialized. Edit config at {yaml_path}")
    exit(1)

yaml_loader = loaders.YAMLLoader.load(yaml_path)
env_loader = loaders.EnvLoader.load()
composite_loader = loaders.CompositeLoader.load(env_loader, yaml_loader)


class QuadrantConfig(BaseConfig):
    # Represents max size of payloads
    debug_mode = BoolVar("Quadrant/debug_mode", composite_loader, default=False)
    max_payload_size = ConfigVar(
        "Quadrant/max_payload_size", composite_loader, validator=lambda v: v >= 0, default='8M',
        caster=casters.file_size_caster, constant=True
    )
    static_folder_location = ConfigVar(
        "Quadrant/static_folder_location", composite_loader, caster=Path,
        default=Path(__file__).parent.parent / "static"
    )
    media_folder_location = ConfigVar(
        "Quadrant/media_folder_location", composite_loader, caster=Path,
        default=Path(__file__).parent.parent / "media"
    )
    host_static_files_internally = BoolVar(
        "Quadrant/host_static_files_internally", composite_loader, default=True
    )

    class DBConfig(BaseConfig):
        # This chat supports only postgresql
        db_uri = ConfigVar("Quadrant/db/db_uri", composite_loader, validator=validators.validate_is_postgresql)
        # Number of connections to database app will be using
        pool_size = IntVar("Quadrant/db/pool_size", composite_loader, default=15, validator=lambda v: v >= 0)
        # Any keyword args for sqlalchemy engine
        kwargs = ConfigVar("Quadrant/db/kwargs", yaml_loader, default={})

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
        logs_dir = ConfigVar(
            "Quadrant/quadrant_logging/logs_dir", composite_loader, caster=Path,
            default=Path(__file__).parent.parent / "logs", constant=True
        )
        date_format = ConfigVar(
            "Quadrant/quadrant_logging/date_format", yaml_loader, validator=datetime.now().strftime, constant=True
        )
        log_format = ConfigVar("Quadrant/quadrant_logging/format", yaml_loader, caster=logging.Formatter, constant=True)
        tornado_app_log_level = ConfigVar(
            "Quadrant/quadrant_logging/TornadoAppLogLevel", yaml_loader,
            caster=lambda level: getattr(logging, level),
            constant=True
        )
        tornado_access_log_level = ConfigVar(
            "Quadrant/quadrant_logging/TornadoAccessLogLevel", yaml_loader,
            caster=lambda level: getattr(logging, level),
            constant=True
        )
        tornado_general_log_level = ConfigVar(
            "Quadrant/quadrant_logging/TornadoGeneralLogLevel", yaml_loader,
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
            when = ConfigVar("Quadrant/quadrant_logging/rotation/when", yaml_loader, constant=True)
            interval = IntVar(
                "Quadrant/quadrant_logging/rotation/interval", yaml_loader, validator=lambda v: v >= 1,
                constant=True
            )
            backup_count = IntVar(
                "Quadrant/quadrant_logging/rotation/backupCount", yaml_loader, validator=lambda v: v >= 1, constant=True
            )
            encoding = ConfigVar(
                "Quadrant/quadrant_logging/rotation/encoding", yaml_loader, validator=validators.validate_encoding,
                default='utf-8', constant=True
            )
            utc_time = BoolVar("Quadrant/quadrant_logging/rotation/utc", yaml_loader, default=True, constant=True)

    class Security(BaseConfig):
        cookie_secret = ConfigVar(
            "Quadrant/security/cookie_secret", composite_loader, validator=lambda v: v != "EXAMPLE_COOKIE_SECRET"
        )
        default_host = ConfigVar("Quadrant/security/default_host", composite_loader)

    class HttpChatServer:
        port = IntVar("Quadrant/http_chat_server/port", composite_loader, validator=lambda v: v in range(1, 65535+1))

    def __post_init__(self, *args, **kwargs):
        static_location: Path = self.static_folder_location.value
        static_location.mkdir(exist_ok=True)

        media_location: Path = self.media_folder_location.value
        media_location.mkdir(exist_ok=True)
        self.uploads = (media_location / "uploads")
        self.profile_pictures = (media_location / "profile_pictures")
        self.uploads.mkdir(exist_ok=True)
        self.profile_pictures.mkdir(exist_ok=True)


quadrant_config = QuadrantConfig()
