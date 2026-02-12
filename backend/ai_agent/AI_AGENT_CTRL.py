import asyncio
from copy import deepcopy
import json
import os
from typing import Optional
from openai import OpenAI
from db.db_tools import get_db
from setting import MCP_CONF, QWEN_API
from fastmcp import Client

 
class AIClient(object):
    ai_agent_pool = {}

    def __init__(self, mcp_client, jwt):

        # MCP服务器
        self.mcp_client = mcp_client

        # LLM 配置
        self.llm = OpenAI(
            # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为：api_key="sk-xxx",
            # 新加坡和北京地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
            api_key=QWEN_API,
            # 以下是北京地域base_url
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",            
        )
        self.llm_model = "qwen-plus"
        self.name="FMMS小助手"
        self.description="家庭物资管理小助手部署"

        # 系统消息
        self.system_message = "你是拥有SQLite记忆，会调用方法，管理物资的小助手"

        # 初始化mcp服务
        self.tools = None
        self.jwt = jwt
    
    def _save_message(self, user_id, role, content, tool_calls=None, tool_call_id=None, tool_name=None):
        """将单条消息存入数据库"""
        with get_db() as db:
            # 如果是 assistant 且带工具调用，把 tool_calls 转成 JSON 字符串存起来
            t_calls_json = None
            if tool_calls:
                # 兼容处理：将 OpenAI 的 ToolCall 对象转为可序列化的字典
                t_calls_json = json.dumps([tc.model_dump() for tc in tool_calls])
            db.execute(
                "INSERT INTO messages (user_id, role, content, tool_calls, tool_call_id, tool_name) VALUES (?, ?, ?, ?, ?, ?)",
                    (user_id, role, content, t_calls_json, tool_call_id, tool_name)
            )
            db.commit()

    def _get_history(self, user_id, limit=50):
        """获取某个用户的历史记录"""
        with get_db() as db:
            # 获取最近的 limit 条记录，并按时间正序排列
            query = f"""
                SELECT role, content, tool_calls, tool_call_id, tool_name FROM (
                SELECT * FROM messages WHERE user_id = ? ORDER BY created_at DESC LIMIT ?
                ) ORDER BY created_at ASC
            """
            cursor = db.cursor()
            cursor.execute(query, (user_id, limit))
            rows = cursor.fetchall()
                
            history = [{"role": "system", "content": f"{self.system_message}"}]
            for role, content, t_calls, t_id, t_name in rows:
                msg = {"role": role, "content": content or ""}
                
                # 关键修复：恢复 tool_calls
                if t_calls:
                    msg["tool_calls"] = json.loads(t_calls)
                
                # 关键修复：恢复 tool 消息必需的元数据
                if role == "tool":
                    msg["tool_call_id"] = t_id
                    msg["name"] = t_name
                
                history.append(msg)
            return history
        
    def _convert_tools(self, mcp_tools):
        """将 MCP 工具格式转换为 OpenAI 兼容格式"""
        openai_tools = []
        
        for tool in mcp_tools:
            # 确保工具是mcp.types.Tool
            tool = dict(tool)
            if not isinstance(tool, dict):
                continue
                
            # 构建 OpenAI 格式的工具定义
            openai_tool = {
                "type": "function",
                "function": {
                    "name": tool.get("name", ""),
                    "description": tool.get("description", ""),
                    "parameters": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            }
            
            # 处理输入模式
            input_schema = tool.get("inputSchema", {})
            if isinstance(input_schema, dict):
                # 复制属性
                if "properties" in input_schema:
                    openai_tool["function"]["parameters"]["properties"] = input_schema["properties"].copy()
                if "required" in input_schema:
                    openai_tool["function"]["parameters"]["required"] = input_schema["required"].copy()
                if "type" in input_schema:
                    openai_tool["function"]["parameters"]["type"] = input_schema["type"]
            
            openai_tools.append(openai_tool)
        
        return openai_tools
            
    async def chat(self, user_id, user_input):
        # 1. 保存并获取历史
        self._save_message(user_id, "user", user_input)

        # 2. 获取 MCP 工具
        mcp_tools = await self.mcp_client.list_tools()
        openai_tools = self._convert_tools(mcp_tools)

        while True:
            messages = self._get_history(user_id)

            response = self.llm.chat.completions.create(
                model=self.llm_model,
                messages=messages,
                tool_choice="auto",
                tools=openai_tools
            )
            
            response_msg = response.choices[0].message
            
            # 关键：保存 AI 的原始回复（即使包含 tool_calls）
            # 注意：OpenAI SDK 对象需要转成字符串或提取内容保存
            self._save_message(
                user_id=user_id,
                role="assistant",
                content=response_msg.content,
                tool_calls=response_msg.tool_calls
            )

            if response_msg.tool_calls:
                for tool_call in response_msg.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    result = await self.mcp_client.call_tool(func_name, arguments=func_args)
                    tool_result_text = result.content[0].text
                    
                    # 保存工具执行结果
                    self._save_message(
                        user_id=user_id,
                        role="tool",
                        content=tool_result_text,
                        tool_call_id=tool_call.id,
                        tool_name=func_name
                    )
                continue
            else:
                return response_msg.content
            
def gen_mcp_conf(user_jwt):
    conf = deepcopy(MCP_CONF).get("mcpServers", None)

    if not conf:
        raise Exception("MCP服务未正常配置")

    for ser_name, ser_conf in conf.items():
        if ser_name == "FMMS":
            ser_conf["headers"] = {"Authorization": f"Bearer {user_jwt}"}
            
    return {
        "mcpServers": conf
    }

def get_user_history_messages(user_id: str, limit=20) -> Optional[str]:
    """
        查询最近limit条数量的历史对话消息
    """
    with get_db() as conn:
        cursor = conn.cursor()
        query = f"""
            SELECT role, content FROM (
                SELECT * FROM messages WHERE user_id = ? AND role in ("user", "assistant") AND tool_calls IS NULL ORDER BY created_at DESC LIMIT ?
            )ORDER BY created_at ASC
        """
        cursor.execute(query, (user_id, limit))
        rows = cursor.fetchall()
        return [{"role": row[0], "content": row[1]} for row in rows]
