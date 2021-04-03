defaults = {
    "Quadrant":
        {
            "debug_mode": False,
            "max_payload_size": "8M",
            "host_static_files_internally": True,
            "static_folder_location": './static',
            "media_folder_location": "./media",

            "db": {
                "db_uri": "postgresql+asyncpg://user:pass@hostname/quadrant_chat?prepared_statement_cache_size=1000",
                "pool_size": 15,
                "pool_kwargs": {},
                "kwargs": {}
            },

            "quadrant_logging": {
                "logs_dir": "./quadrant_logs",
                "format": "'%(asctime)s - %(name)s - %(levelname)s: %(message)s'",  # noqa: quadrant_logging format
                "date_format": "%y%m%d %H:%M:%S",
                "TornadoAppLogLevel": "ERROR",
                "TornadoAccessLogLevel": "ERROR",
                "TornadoGeneralLogLevel": "ERROR",

                "rotation": {
                    'when': 'h',
                    'interval': 6,
                    'backupCount': 5,
                    "encoding": "utf-8",
                    'utc': True,
                }
            },

            "security": {
                "cookie_secret": "EXAMPLE_COOKIE_SECRET",
                "default_host": r"(localhost|127\.0\.0\.1)"
            },

            "http_chat_server": {
                "port": 356,
            }
        },
}
