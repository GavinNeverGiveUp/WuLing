import sys
from qwen_agent.gui import WebUI
sys.path.append("../")
from AI_AGENT_CTRL import AIClient

client_obj = AIClient()
bot = client_obj.get_AI_client("gavin")

WebUI(bot).run()