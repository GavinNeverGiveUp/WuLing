from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastmcp import Client

from ai_agent.AI_AGENT_CTRL import AIClient, gen_mcp_conf, get_user_history_messages
from auth.auth_handler import get_current_user
from schema.models import ChatRequest, ChatResponse, MessageResponse
from utils.func_utils import  get_user_id_by_username

ai_app = APIRouter(prefix="/ai", tags=["AI Agent调用"])

@ai_app.post("/chat", response_model=ChatResponse)
async def chat(ChatRequest: ChatRequest, request: Request, current_user: str = Depends(get_current_user)):

    # 获取用户ID
    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 生成mcp专属配置
    jwt_token = auth_header = request.headers.get("Authorization")
    if not jwt_token:
        raise HTTPException(status_code=400, detail="当前账号未登录")
    jwt_token = jwt_token.split(" ")[-1]
    
    mcp_conf = gen_mcp_conf(jwt_token)

    async with Client(mcp_conf) as mcp_client:

        agent = AIClient(mcp_client, jwt_token)
        agent_ans = await agent.chat(user_id, ChatRequest.message)
        
        return {
            "message": agent_ans
        }

    
@ai_app.get("/messages", response_model=List[MessageResponse])
async def get_user_history_message(limit: int = 20, current_user: str = Depends(get_current_user)):

    user_id = get_user_id_by_username(current_user)
    if not user_id:
        raise HTTPException(status_code=404, detail="用户不存在")

    messages = get_user_history_messages(user_id, limit)
    return messages