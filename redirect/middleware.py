# Copyright (c) 2026, Camptocamp SA

"""Middleware that trims whitespace from response header values."""

from starlette.types import ASGIApp, Message, Receive, Scope, Send


class TrimResponseHeadersMiddleware:
    """Trim leading and trailing whitespace from all response header values."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                message["headers"] = [(name, value.strip()) for name, value in message.get("headers", [])]
            await send(message)

        await self.app(scope, receive, send_wrapper)
