from typing import Any

from tornado.web import Application

from Quadrant.config import quadrant_config
from Quadrant.resourses.utils.api_error_handler import QuadrantAPIErrorHandler


class QuadrantApp(Application):
    def __init__(self, **settings: Any):
        settings.update(
            {
                "cookie_secret": quadrant_config.Security.cookie_secret.value,
                "max_header_size": quadrant_config.max_payload_size.value,
                "debug": quadrant_config.debug_mode.value,
                "xsrf_cookies": True,
            }
        )
        super().__init__(**settings)


class QuadrantAPIApp(QuadrantApp):
    def __init__(self, **settings: Any):
        if 'default_handler_class' not in settings:
            settings['default_handler_class'] = QuadrantAPIErrorHandler
        super().__init__(**settings)
