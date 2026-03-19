from contextvars import ContextVar

import httpx
from fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware

from app import app as backend_app


user_auth_ctx: ContextVar[str | None] = ContextVar("user_auth", default=None)


class DynamicAuth(httpx.Auth):
    def auth_flow(self, request):
        raw_credential = user_auth_ctx.get()
        if raw_credential:
            # 统一透传到 Authorization，兼容 JWT 与 wlk_ 开头 API Key
            request.headers["Authorization"] = f"Bearer {raw_credential}"
            # 同时补充 X-API-Key，便于后续扩展按头部类型识别
            if raw_credential.startswith("wlk_"):
                request.headers["X-API-Key"] = raw_credential
        yield request


class AuthPropagationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        auth_header = (request.headers.get("Authorization") or "").strip()
        api_key_header = (request.headers.get("X-API-Key") or "").strip()

        raw_credential = ""
        if auth_header:
            parts = auth_header.split(" ", 1)
            if len(parts) == 2 and parts[0].lower() == "bearer":
                raw_credential = parts[1].strip()
            else:
                raw_credential = auth_header

        if not raw_credential and api_key_header:
            raw_credential = api_key_header

        reset_token = None
        if raw_credential:
            reset_token = user_auth_ctx.set(raw_credential)

        try:
            return await call_next(request)
        finally:
            if reset_token is not None:
                user_auth_ctx.reset(reset_token)


backend_app.add_middleware(AuthPropagationMiddleware)

mcp = FastMCP.from_fastapi(
    app=backend_app,
    exclude_tags=["AI Agent调用"],
    include_tags=["用户和家庭管理", "物品管理"],
    httpx_client_kwargs={
        "auth": DynamicAuth(),
        "timeout": 30.0,
    },
)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)
