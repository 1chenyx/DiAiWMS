from .cors import CorsMiddleware as StarletteCorsMiddleware
from .http import HttpMiddleware
from .exceptions import ExceptionsHandler
from app.api.exceptions import CustomException
from fastapi.exceptions import RequestValidationError

__all__ = [
    "StarletteCorsMiddleware",
    "HttpMiddleware",
    "ExceptionsHandler"
]


def register_middlewares(app):
    app.add_middleware(StarletteCorsMiddleware)
    app.add_middleware(HttpMiddleware)
    app.add_exception_handler(CustomException, ExceptionsHandler.custom_exception_handler)
    app.add_exception_handler(RequestValidationError, ExceptionsHandler.request_validation_handler)
    app.add_exception_handler(Exception, ExceptionsHandler.http_exception_handler)
