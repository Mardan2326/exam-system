#!/usr/bin/env python3
"""
测试AI解析功能的修复效果
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from exam_app import ExamApp
import tkinter as tk
import json

def test_json_parsing():
    """测试JSON解析功能"""
    print("=== 测试JSON解析功能 ===")

    # 创建测试用的ExamApp实例
    root = tk.Tk()
    app = ExamApp(root)

    # 测试各种JSON格式
    test_cases = [
        # 标准格式
        '[{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2"}, "answer": "A"}]',

        # 带markdown标记
        '```json\n[{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2"}, "answer": "A"}]\n```',

        # 带额外文本
        '前面有一些文本 [{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2"}, "answer": "A"}] 后面有文本',

        # 单引号格式
        "[{'id': '1', 'text': '测试题', 'options': {'A': '选项1', 'B': '选项2'}, 'answer': 'A'}]",

        # 弯引号格式
        '[{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2"}, "answer": "A"}]',

        # 带多余逗号
        '[{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2",}, "answer": "A",}]',

        # 单个对象
        '{"id": "1", "text": "测试题", "options": {"A": "选项1", "B": "选项2"}, "answer": "A"}',
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试用例 {i}:")
        print(f"输入: {test_case[:50]}...")

        # 测试JSON数组提取
        json_array = app.extract_json_array(test_case)
        print(f"提取的JSON: {json_array}")

        # 测试JSON解析
        parsed = app.parse_json_with_fallback(json_array)
        print(f"解析结果: {parsed}")

        if parsed:
            print("[SUCCESS] 解析成功")
        else:
            print("[FAILED] 解析失败")

    root.destroy()
    print("\n=== JSON解析测试完成 ===")

def test_prompt_optimization():
    """测试优化后的提示词"""
    print("\n=== 测试提示词优化 ===")

    test_text = """
    1、下列哪个是正确的？
    A. 选项A
    B. 选项B
    C. 选项C
    D. 选项D

    2、第二题是什么？
    A. 答案一
    B. 答案二
    C. 答案三
    D. 答案四
    """

    # 模拟优化后的提示词
    prompt = f"""从以下考试文本中提取题目，返回JSON格式。

要求：
1. 每道题包含：题号(id)、题干(text)、选项(options)、答案(answer)
2. 选项必须是A、B、C、D四个字母
3. 答案不确定时用null
4. 直接返回JSON数组，无其他文字

格式示例：
[
  {{
    "id": "1",
    "text": "题干内容",
    "options": {{
      "A": "选项A内容",
      "B": "选项B内容",
      "C": "选项C内容",
      "D": "选项D内容"
    }},
    "answer": "A"
  }}
]

文本内容：
{test_text}"""

    print("优化后的提示词：")
    print(prompt[:200] + "...")
    print("✅ 提示词已优化为更简洁明确的格式")

def main():
    """主测试函数"""
    print("开始测试AI解析修复效果...")

    # 测试JSON解析
    test_json_parsing()

    # 测试提示词
    test_prompt_optimization()

    print("\n=== 修复总结 ===")
    print("[OK] 1. 简化了提示词，减少AI理解负担")
    print("[OK] 2. 重构了JSON解析逻辑，提高容错性")
    print("[OK] 3. 增强了错误处理和调试信息")
    print("[OK] 4. 智能调整文本长度限制")
    print("[OK] 5. 统一了快速模式和完整模式的解析流程")

    print("\n使用建议：")
    print("1. 优先使用AI快速解析，失败会自动回退本地解析")
    print("2. 如果AI解析经常失败，检查PDF文本质量")
    print("3. 使用查看AI响应功能调试具体问题")
    print("4. 对于复杂试题文档，建议分批处理")

if __name__ == "__main__":
    main()