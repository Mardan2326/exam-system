from openai import OpenAI
import os

def call_llm(messages, api_base="https://api.deepseek.com/v1", model_name="deepseek-chat", timeout=60, max_retries=2):
    """
    调用大语言模型API（默认 DeepSeek）。
    - 强制要求通过环境变量 DEEPSEEK_API_KEY 提供 API Key。
    - 内置超时与简单重试机制。
    """
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("未配置 DEEPSEEK_API_KEY 环境变量，请先设置后再重试")

    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )

    last_err = None
    for attempt in range(max_retries + 1):
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=0.3,
                timeout=timeout
            )
            return response.choices[0].message.content
        except Exception as e:
            last_err = e
            if attempt < max_retries:
                import time
                time.sleep(1.5 * (attempt + 1))
                continue
            raise RuntimeError(f"LLM 调用失败：{e}") from e

if __name__ == "__main__":
    # 测试DeepSeek API
    print("--- Testing DeepSeek API ---")
    deepseek_messages = [{"role": "user", "content": "你没有联网吗！"}]
    deepseek_response = call_llm(deepseek_messages, api_base="https://api.deepseek.com/v1", model_name="deepseek-chat")
    print(f"Prompt: {deepseek_messages[0]['content']}")
    print(f"Response: {deepseek_response}")

    # 测试OpenAI API (如果需要，确保设置 OPENAI_API_KEY)
    # print("\n--- Testing OpenAI API ---")
    # openai_messages = [{"role": "user", "content": "What's the capital of France?"}]
    # openai_response = call_llm(openai_messages, api_base="https://api.openai.com/v1", model_name="gpt-4o")
    # print(f"Prompt: {openai_messages[0]['content']}")
    # print(f"Response: {openai_response}")
