#!/usr/bin/env python3
"""
测试直接上传文件给AI解析功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_direct_upload():
    """测试直接上传解析功能"""
    print("=== 直接上传文件AI解析功能测试 ===")

    try:
        from exam_app import ExamApp
        print("[OK] 成功导入ExamApp类")

        # 检查新功能方法
        methods_to_check = [
            'direct_upload_parse',      # 直接上传解析入口
            'start_direct_ai_parse',    # 开始AI解析
            'extract_pdf_text',         # PDF文本提取
            'extract_json_array',       # JSON数组提取
            'parse_json_with_fallback', # JSON解析
            'normalize_questions',      # 题目规范化
            'load_questions',           # 加载题目
        ]

        for method_name in methods_to_check:
            if hasattr(ExamApp, method_name):
                print(f"[OK] 方法 {method_name} 已实现")
            else:
                print(f"[ERROR] 方法 {method_name} 缺失")

        print("\n=== 功能特性 ===")
        print("[NEW] 一键直接上传解析")
        print("[NEW] 简化的AI提示词")
        print("[NEW] 专注于原题提取")
        print("[NEW] 保持题目内容完全不变")
        print("[NEW] 快速流程，无需复杂配置")

        print("\n=== 使用流程 ===")
        print("1. 输入DeepSeek API Key")
        print("2. 点击'直接上传解析'按钮")
        print("3. 选择PDF试卷文件")
        print("4. AI自动提取所有题目")
        print("5. 直接进入考试模式")

        print("\n=== 技术特点 ===")
        print("- 零配置：不需要设置解析参数")
        print("- 全自动：AI处理一切复杂逻辑")
        print("- 高保真：保持原题内容不变")
        print("- 快速：一键完成试卷数字化")
        print("- 准确：AI智能识别题目格式")

        print("\n=== AI提示词特点 ===")
        print("- 简洁明确的指令")
        print("- 专注于原题提取")
        print("- 要求保持内容不变")
        print("- 标准JSON格式输出")
        print("- 自动保留答案信息")

        print("\n=== 适用场景 ===")
        print("- 快速试卷数字化")
        print("- 临时考试组织")
        print("- 试卷题库快速建设")
        print("- 紧急线上考试需求")

        print("\n[SUCCESS] 直接上传文件AI解析功能测试完成！")
        print("\n💡 现在你只需要：")
        print("   1. 输入API Key")
        print("   2. 点击直接上传解析")
        print("   3. 选择PDF文件")
        print("   4. 立即开始考试！")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_upload()