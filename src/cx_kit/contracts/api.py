# cx-kit/src/cx_kit/contracts/api.py

"""
Defines the contract for pluggable API Middleware.

Syncropel's API server adheres to the standard ASGI (Asynchronous Server
Gateway Interface) specification. Any class that follows the ASGI
middleware pattern can be registered as a `syncropel.api.middleware`
plugin.
"""

from typing import Protocol, Callable, Awaitable

# These are the standard type hints for an ASGI application
Scope = dict
Receive = Callable[[], Awaitable[dict]]
Send = Callable[[dict], Awaitable[None]]
ASGIApp = Callable[[Scope, Receive, Send], Awaitable[None]]


class BaseApiMiddleware(Protocol):
    """
    A structural type hint (Protocol) for an ASGI middleware class.

    A valid middleware must have an `__init__` that accepts the next app in
    the chain and an `async __call__` method with the standard ASGI signature.
    """

    def __init__(self, app: ASGIApp): ...

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None: ...
