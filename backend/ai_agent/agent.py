import logging
import os
import time
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request
from fastmcp import Client

from ai_agent.AI_AGENT_CTRL import AIClient, gen_mcp_conf, get_user_history_messages
from auth.auth_handler import get_current_user
from schema.models import ChatRequest, ChatResponse, MessageResponse
from utils.func_utils import get_user_id_by_username


logger = logging.getLogger(__name__)
ai_app = APIRouter(prefix="/ai", tags=["AI Agent调用"])

_LOG_AI_SUCCESS_DETAIL = os.getenv("LOG_AI_SUCCESS_DETAIL", "false").strip().lower() in {
    "1", "true", "yes", "on"
}


def _log_ai_success(event: str, extra: dict) -> None:
    # 默认不在 INFO 重复打印成功日志，避免与全局请求日志重复。
    if _LOG_AI_SUCCESS_DETAIL:
        logger.info(event, extra=extra)
    else:
        logger.debug(event, extra=extra)


@ai_app.post("/chat", response_model=ChatResponse)
async def chat(ChatRequest: ChatRequest, request: Request, current_user: str = Depends(get_current_user)):
    message_length = len(ChatRequest.message or "")
    start_time = time.perf_counter()

    # 获取用户ID
    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 生成mcp专属配置
    jwt_token = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=400, detail="当前账号未登录")
    jwt_token = jwt_token.split(" ")[-1]

    try:
        mcp_conf = gen_mcp_conf(jwt_token)

        async with Client(mcp_conf) as mcp_client:
            agent = AIClient(mcp_client, jwt_token)
            agent_ans = await agent.chat(user_id, ChatRequest.message)
    except Exception:
        logger.exception(
            "ai_chat_failed",
            extra={
                "user_id": user_id,
                "message_length": message_length,
                "path": request.url.path,
            },
        )
        raise

    latency_ms = round((time.perf_counter() - start_time) * 1000, 2)
    _log_ai_success(
        "ai_chat_completed",
        {
            "user_id": user_id,
            "message_length": message_length,
            "latency_ms": latency_ms,
            "path": request.url.path,
        },
    )

    return {
        "message": agent_ans
    }


@ai_app.get("/messages", response_model=List[MessageResponse])
async def get_user_history_message(limit: int = 20, current_user: str = Depends(get_current_user)):
    start_time = time.perf_counter()

    user_id = await get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    messages = await get_user_history_messages(user_id, limit)

    _log_ai_success(
        "ai_messages_loaded",
        {
            "user_id": user_id,
            "limit": limit,
            "result_count": len(messages),
            "latency_ms": round((time.perf_counter() - start_time) * 1000, 2),
            "path": "/ai/messages",
        },
    )

    return messages
