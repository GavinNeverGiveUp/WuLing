from fastmcp import FastMCP
from app import app

mcp = FastMCP.from_fastapi(
    app=app,
    exclude_tags=["AI Agent调用"],
    include_tags=["用户和家庭管理", "物品管理"],
)


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8001)


# from fastmcp import FastMCP
# from app import app as backend_app  # 你的原始 FastAPI 应用
# from contextvars import ContextVar
# from starlette.middleware.base import BaseHTTPMiddleware
# import httpx

# # 1. 定义 ContextVar
# user_token_ctx: ContextVar[str | None] = ContextVar("user_token", default=None)

# # 2. 定义动态 Auth
# class DynamicTokenAuth(httpx.Auth):
#     def auth_flow(self, request):
#         token = user_token_ctx.get()
#         if token:
#             request.headers["Authorization"] = f"Bearer {token}"
#         yield request

# # 3. 定义中间件
# class AuthPropagationMiddleware(BaseHTTPMiddleware):
#     async def dispatch(self, request, call_next):
#         auth_header = request.headers.get("Authorization")
#         print(f"--- [Middleware] 收到请求: {request.url.path}, Header: {auth_header}") # 调试点 1
#         # 拦截所有进入 FastAPI 的请求头
#         auth_header = request.headers.get("Authorization")
#         token_reset_token = None
        
#         if auth_header and auth_header.startswith("Bearer "):
#             token = auth_header.split(" ")[1]
#             token_reset_token = user_token_ctx.set(token)
        
#         try:
#             return await call_next(request)
#         finally:
#             if token_reset_token:
#                 user_token_ctx.reset(token_reset_token)

# # --- 关键步骤 ---

# # 4. 【修改点】先给你的 backend_app 添加中间件
# # 这样无论谁请求 backend_app（包括 FastMCP），Token 都会被存入 ContextVar
# backend_app.add_middleware(AuthPropagationMiddleware)

# # 5. 再初始化 FastMCP
# mcp = FastMCP.from_fastapi(
#     app=backend_app,
#     httpx_client_kwargs={
#         "auth": DynamicTokenAuth(),
#         "timeout": 30.0
#     }
# )

# if __name__ == "__main__":
#     # 此时，当 Agent 通过 HTTP 访问 MCP Server 时
#     # 流量会经过：Agent -> FastMCP -> backend_app (触发中间件) -> ContextVar -> httpx (触发 Auth) -> 真正的业务接口
#     mcp.run(transport="http", host="0.0.0.0", port=8001)