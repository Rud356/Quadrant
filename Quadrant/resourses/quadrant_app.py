from typing import Any, Optional, List, Type

from tornado.web import Application, OutputTransform
from tornado.routing import _RuleList

from Quadrant.config import quadrant_config
from Quadrant.resourses.utils.api_error_handler import QuadrantAPIErrorHandler


class QuadrantApp(Application):
    def __init__(
        self,
        handlers: Optional[_RuleList] = None,
        default_host: Optional[str] = None,
        transforms: Optional[List[Type["OutputTransform"]]] = None,
        **settings: Any
    ):
        settings.update(
            {
                "cookie_secret": quadrant_config.Security.cookie_secret.value,
                "max_header_size": quadrant_config.max_payload_size.value,
                "debug": quadrant_config.debug_mode.value,
                "xsrf_cookies": True,
            }
        )
        super().__init__(handlers, default_host, transforms, **settings)


class QuadrantAPIApp(QuadrantApp):
    def __init__(
        self,
        handlers: Optional[_RuleList] = None,
        default_host: Optional[str] = None,
        transforms: Optional[List[Type["OutputTransform"]]] = None,
        **settings: Any
    ):
        if 'default_handler_class' not in settings:
            settings['default_handler_class'] = QuadrantAPIErrorHandler
        super().__init__(handlers, default_host, transforms, **settings)
