import os
import fastapi_poe as fp
from dotenv import load_dotenv
from typing import AsyncIterable
from openai import AsyncOpenAI
import traceback
import time

# 加载环境变量
load_dotenv()

# 获取API密钥
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
POE_ACCESS_KEY = os.getenv("POE_ACCESS_KEY")

# 读取系统提示词
try:
    with open("system_prompt.txt", "r", encoding="utf-8") as f:
        SYSTEM_PROMPT = f.read()
except FileNotFoundError:
    SYSTEM_PROMPT = """"""        # PROMPT
    # 创建系统提示词文件以备将来使用
    with open("system_prompt.txt", "w", encoding="utf-8") as f:
        f.write(SYSTEM_PROMPT)


class GPT4oBot(fp.PoeBot):
    """
    基于 GPT-4.1 的 Poe 机器人，支持上下文管理与流式输出
    """
    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        try:
            # 1. 提取并映射历史消息
            messages_list = []
            if isinstance(request.query, list):
                for msg in request.query:
                    # 仅使用支持的角色，否则映射为 assistant
                    role = msg.role if msg.role in {
                        "system", "assistant", "user", "function", "tool", "developer"
                    } else "assistant"
                    messages_list.append({"role": role, "content": msg.content})
            else:
                messages_list = [{"role": "user", "content": str(request.query)}]

            # 2. 可选截断历史，防止超出上下文窗口
            MAX_HISTORY = 10
            if len(messages_list) > MAX_HISTORY:
                messages_list = messages_list[-MAX_HISTORY:]

            # 3. 构建最终 messages 列表
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages_list

            # 4. 初始化 OpenAI 客户端
            client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url="https://openkey.cloud/v1"
            )

            # 调用 Chat Completion 流式接口
            response = await client.chat.completions.create(
                model="gpt-4.1",
                messages=messages,
                stream=True,
                timeout=30
            )

            # 5. 流式输出逻辑
            buffer = ""
            last_flush = time.time()
            async for chunk in response:
                if not getattr(chunk, "choices", None):
                    continue
                for choice in chunk.choices:
                    token = getattr(choice.delta, "content", None)
                    if token:
                        buffer += token
                now = time.time()
                if buffer.endswith((".", "。", ",", "，", " ", "\n")) or (now - last_flush) > 0.1:
                    yield fp.PartialResponse(text=buffer)
                    buffer = ""
                    last_flush = now

            # flush 剩余内容
            if buffer:
                yield fp.PartialResponse(text=buffer)

        except Exception as e:
            # 捕获并返回错误信息
            error_info = f"API调用错误: {e}"
            traceback.print_exc()
            yield fp.PartialResponse(text=error_info)

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        """
        设置机器人配置
        """
        return fp.SettingsResponse(
            server_bot_dependencies={},
            introduction_message="I'm Lester Crest, mastermind and hacker genius. Welcome to the BlindLine communication system. Paige and I will be your mentors and train you to be a true information hunter."
        )


# 创建FastAPI应用
app = fp.make_app(GPT4oBot(), access_key=POE_ACCESS_KEY)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
