from .cors import CorsMiddleware as StarletteCorsMiddleware
from .http import HttpMiddleware
from .exceptions import ExceptionsHandler

__all__ = [
    "StarletteCorsMiddleware",
    "HttpMiddleware",
    "ExceptionsHandler"
]


def register_middlewares(app):
    app.add_middleware(StarletteCorsMiddleware)
    app.add_middleware(HttpMiddleware)
    app.add_exception_handler(Exception, ExceptionsHandler.http_exception_handler)
    app.add_exception_handler(Exception, ExceptionsHandler.custom_exception_handler)
    app.add_exception_handler(Exception, ExceptionsHandler.request_validation_handler)
