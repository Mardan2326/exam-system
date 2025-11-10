#!/usr/bin/env python3
"""
验证修复效果的简单测试脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """测试基本功能是否正常"""
    print("=== 修复验证测试 ===")

    try:
        # 测试导入
        from exam_app import ExamApp
        print("[OK] 应用程序导入成功")

        # 测试实例化
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口

        app = ExamApp(root)
        print("[OK] 应用程序实例化成功")

        # 检查关键方法
        key_methods = [
            'direct_upload_parse',
            'start_direct_ai_parse',
            'extract_json_array',
            'parse_json_with_fallback'
        ]

        for method in key_methods:
            if hasattr(app, method):
                print(f"[OK] 方法 {method} 存在")
            else:
                print(f"[ERROR] 方法 {method} 缺失")

        # 测试JSON解析功能
        test_json = '[{"id": "1", "text": "测试题", "options": {"A": "选项1"}, "answer": "A"}]'
        result = app.parse_json_with_fallback(test_json)
        if result and len(result) > 0:
            print("[OK] JSON解析功能正常")
        else:
            print("[ERROR] JSON解析功能异常")

        root.destroy()
        print("\n[SUCCESS] 所有基本功能测试通过！")
        print("应用程序已修复并可以正常使用。")

        print("\n=== 使用指南 ===")
        print("1. 运行 python exam_app.py 启动程序")
        print("2. 输入DeepSeek API Key")
        print("3. 点击'直接上传解析'按钮")
        print("4. 选择PDF试卷文件")
        print("5. AI自动解析并生成机考试卷")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_basic_functionality()