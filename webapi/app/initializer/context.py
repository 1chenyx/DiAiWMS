from contextvars import ContextVar

request_id_var: ContextVar[str] = ContextVar("request_id", default="N/A")


class GlobalContext:
    def __init__(self):
        self.config = None


g = GlobalContext()
