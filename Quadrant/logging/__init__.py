import logging
from functools import partial
from logging.handlers import TimedRotatingFileHandler

from tornado.log import access_log, app_log, gen_log

from Quadrant.config import quadrant_config

log_config = quadrant_config.LoggingConfig
rotation_config = log_config.LogsRotationConfig

logging.basicConfig(
    format=log_config.log_format.value,
    datefmt=log_config.date_format.value
)

rotating_file_handler_creator = partial(
    TimedRotatingFileHandler,
    when=rotation_config.when.value, interval=rotation_config.interval.value,
    backupCount=rotation_config.backup_count.value, encoding=rotation_config.encoding.value,
    utc=rotation_config.utc_time.value
)

app_log.setLevel(log_config.tornado_app_log_level.value)
gen_log.setLevel(log_config.tornado_general_log_level.value)
access_log.setLevel(log_config.tornado_access_log_level.value)

app_log.addHandler(rotating_file_handler_creator(filename=log_config.app_log_path / "tornado_app.log"))
gen_log.addHandler(rotating_file_handler_creator(filename=log_config.app_log_path / "tornado_general.log"))
access_log.addHandler(rotating_file_handler_creator(filename=log_config.app_log_path / "tornado_access.log"))
