import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env.prod")

# 添加src目录到Python路径，使其能正确导入同级目录的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


# 主应用
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# from db.db_tools import init_db_pool
from user.user_mgr import user_app
from fmms.item_mgr import item_app
from ai_agent.agent import ai_app


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """应用生命周期管理"""
#     # 启动时初始化数据库连接池
#     await init_db_pool()
#     print("数据库连接池已初始化")
#     yield
#     # 关闭时可以在这里清理资源
#     print("应用关闭")


app = FastAPI(
    title="家庭物品管理系统",
    root_path="/api",
    redirect_slashes=False,  # 禁用自动重定向
    # lifespan=lifespan
)

# 包含路由器
app.include_router(user_app)
app.include_router(item_app)
app.include_router(ai_app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 替换为你的前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # max_age=600  # 可选：缓存预检结果
)

# 根路径信息
@app.get("/")
async def root():
    return {"message": "家庭物品管理系统API", "version": "1.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
