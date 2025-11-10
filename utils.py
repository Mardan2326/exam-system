from openai import OpenAI
import os

def call_llm(messages, api_base="https://api.deepseek.com/v1", model_name="deepseek-chat"):
    """
    调用大语言模型API。
    默认为DeepSeek API，但可以通过参数切换。
    """
    # 优先使用环境变量，如果没有则使用默认值
    api_key = os.environ.get("DEEPSEEK_API_KEY", "sk-d3b4f1486e844536a7c62592bc673bb2")
    
    if not api_key or api_key == "sk-d3b4f1486e844536a7c62592bc673bb2":
        print("⚠️ 警告：正在使用默认的 API Key，建议设置环境变量 DEEPSEEK_API_KEY")
    
    client = OpenAI(
        api_key=api_key,
        base_url=api_base
    )

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.3  # 降低温度以提高解析准确性和一致性
    )
    return response.choices[0].message.content

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
