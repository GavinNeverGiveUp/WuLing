

import os
from pathlib import Path
import secrets
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

# 加载配置
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.prod")


# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT配置
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8
# ACCESS_TOKEN_EXPIRE_MINUTES = 2

# qwen模型API
QWEN_API = os.getenv("QWEN_API")


# MCP配置
# MCP_CONF_JSON = os.path.join(os.path.dirname(__file__), "conf", "mcp_conf.json")
MCP_CONF = {
    "mcpServers": {
        "FMMS": {
            # Remote HTTP/SSE server
            "transport": "http",  # or "sse" 
            "url": "http://127.0.0.1:8001/mcp",
            # "headers": {"Authorization": "Bearer token"},
            # "auth": "oauth"  # or bearer token string
        },
        "amap-maps": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "@amap/amap-maps-mcp-server"
                ],
            "env": {
                "AMAP_MAPS_API_KEY": os.getenv("AMAP_MAPS_API_KEY")
            }
        },
        "howtocook-mcp": {
            "transport": "stdio",
            "command": "npx",
            "args": [
                "-y",
                "howtocook-mcp"
            ]
        } 
    }
}