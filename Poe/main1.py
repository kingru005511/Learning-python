import os
import fastapi_poe as fp
from dotenv import load_dotenv
from typing import AsyncIterable
from openai import AsyncOpenAI
import traceback

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
    SYSTEM_PROMPT = """"""     # 填写AI的提示词
    # 创建系统提示词文件以备将来使用
    with open("system_prompt.txt", "w", encoding="utf-8") as f:
        f.write(SYSTEM_PROMPT)


class GPT4oBot(fp.PoeBot):
    """
    基于GPT-4o API的Poe机器人，使用官方OpenAI Python库调用API
    """

    async def get_response(self, request: fp.QueryRequest) -> AsyncIterable[fp.PartialResponse]:
        """
        处理用户请求并返回响应
        """
        try:
            # 获取用户消息 - 直接从request.query中提取文本内容
            # 检查query的类型并适当处理
            if hasattr(request, 'query'):
                if isinstance(request.query, list):
                    # 如果query是列表（可能是ProtocolMessage对象列表）
                    print(f"查询是列表类型，长度: {len(request.query)}")
                    # 从最后一个用户消息中提取内容
                    user_messages = [msg for msg in request.query if getattr(msg, 'role', None) == 'user']
                    if user_messages:
                        query = user_messages[-1].content
                    else:
                        query = "你好"  # 默认问候
                else:
                    # 如果query是字符串或其他类型
                    query = str(request.query)
            else:
                query = "你好"  # 默认问候

            print(f"处理用户查询: {query}")

            # 使用官方OpenAI Python库调用API，配置国内代理
            client = AsyncOpenAI(
                api_key=OPENAI_API_KEY,
                base_url="https://openkey.cloud/v1"  # 设置国内代理基础URL
            )

            # 创建简单的消息列表，只包含系统提示词和当前用户查询
            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": query}
            ]

            print("开始调用OpenAI API...")
            # 不使用json.dumps，避免序列化问题
            print(f"消息格式: 系统消息和用户消息 '{query}'")

            # 调用API
            response = await client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                timeout=30
            )

            print("API调用成功，获取到响应")

            # 提取回复内容
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                print(f"返回完整响应，长度: {len(content) if content else 0}")

                # 返回文本内容
                yield fp.PartialResponse(text=content)
            else:
                yield fp.PartialResponse(text="API响应缺少选择字段")

        except Exception as e:
            error_message = f"API调用错误: {str(e)}"
            print(error_message)
            print(f"错误详情: {repr(e)}")
            print("堆栈跟踪:")
            traceback.print_exc()
            yield fp.PartialResponse(text=error_message)

    async def get_settings(self, setting: fp.SettingsRequest) -> fp.SettingsResponse:
        """
        设置机器人配置
        """
        return fp.SettingsResponse(
            server_bot_dependencies={},
            introduction_message=""     # 填写机器人的自我介绍
        )


# 创建FastAPI应用
app = fp.make_app(GPT4oBot(), access_key=POE_ACCESS_KEY)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
