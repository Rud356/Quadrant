defaults = {
    "Quadrant":
        {
            "max_upload_file_size": "8M",
            "host_static_files_internally": True,
            "static_folder_location": './static',
            "media_folder_location": "./media",

            "db": {
                "db_uri": "postgresql://user:pass@hostname/quadrant_chat",
                "pool_size": 15,
                "statements_cache_size": 1000,
                "kwargs": {}
            },

            "logging": {
                "logs_dir": "./logging/logs",
                "format": "'%(asctime)s - %(name)s - %(levelname)s: %(message)s'",  # noqa: logging format
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
            }
        },
}
