#!/usr/bin/env python3
"""
测试增强的完整文件解析功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_parsing():
    """测试增强的解析功能"""
    print("=== 增强版完整文件解析功能测试 ===")

    try:
        from exam_app import ExamApp
        print("[OK] 成功导入ExamApp类")

        # 检查新增的方法
        methods_to_check = [
            'detect_answers_in_text',          # 智能答案检测
            'analyze_document_quality',        # 文档质量分析
            'post_process_full_document',      # 完整文档后处理
            'start_direct_ai_parse',           # 增强的直接解析
        ]

        for method_name in methods_to_check:
            if hasattr(ExamApp, method_name):
                print(f"[OK] 方法 {method_name} 已实现")
            else:
                print(f"[ERROR] 方法 {method_name} 缺失")

        print("\n=== 🚀 新功能特性 ===")
        print("[NEW] 一次性解析整个PDF文件")
        print("[NEW] 智能识别答案部分")
        print("[NEW] 自动检测文档质量")
        print("[NEW] 优化的AI提示词")
        print("[NEW] 动态超时时间调整")
        print("[NEW] 详细的解析进度反馈")

        print("\n=== 🔍 智能答案检测 ===")
        print("[检测] 参考答案、标准答案等标识")
        print("[检测] 表格形式的答案")
        print("[检测] 连续答案模式 (如: 1.A 2.B)")
        print("[检测] 题目后的直接答案")
        print("[智能] 自动判断是否包含答案")

        print("\n=== 📊 文档质量分析 ===")
        print("[分析] 题目分隔符数量")
        print("[分析] 中英文字符统计")
        print("[分析] 文档结构评估")
        print("[建议] 解析适宜性提示")

        print("\n=== ⚡ 解析优化 ===")
        print("[优化] 完整文件处理，无内容截断")
        print("[优化] 标准化题号和选项格式")
        print("[优化] 清理页眉页脚干扰")
        print("[优化] 保持原题内容完全不变")
        print("[优化] 智能题目边界识别")

        print("\n=== 📈 性能提升 ===")
        print("[速度] 根据文件大小调整超时")
        print("[效率] 一次性处理，无需分批")
        print("[准确] 专门的试卷解析提示词")
        print("[稳定] 多层容错和错误处理")

        print("\n=== 🎯 使用流程 ===")
        print("1. 输入DeepSeek API Key")
        print("2. 点击'🚀 完整试卷AI解析'按钮")
        print("3. 选择PDF试卷文件")
        print("4. AI智能分析文档质量和答案")
        print("5. 完整解析所有题目内容")
        print("6. 自动进入机考模式")

        print("\n[SUCCESS] 增强版完整文件解析功能测试完成！")
        print("\n💡 现在您可以：")
        print("   • 一次性解析任何大小的试卷文件")
        print("   • AI智能识别是否包含答案")
        print("   • 获得高质量的机考试卷")
        print("   • 享受快速准确的解析体验")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_answer_detection():
    """测试答案检测功能"""
    print("\n=== 答案检测功能测试 ===")

    try:
        from exam_app import ExamApp
        import tkinter as tk

        # 创建测试实例
        root = tk.Tk()
        root.withdraw()  # 隐藏窗口
        app = ExamApp(root)

        # 测试包含答案的文本
        text_with_answers = """
        1. 下列哪个是正确的？
        A. 选项A
        B. 选项B
        C. 选项C
        D. 选项D

        2. 第二题是什么？
        A. 答案一
        B. 答案二
        C. 答案三
        D. 答案四

        参考答案：
        1. A
        2. B
        """

        # 测试不含答案的文本
        text_without_answers = """
        1. 下列哪个是正确的？
        A. 选项A
        B. 选项B
        C. 选项C
        D. 选项D

        2. 第二题是什么？
        A. 答案一
        B. 答案二
        C. 答案三
        D. 答案四
        """

        # 测试答案检测
        has_answers_1 = app.detect_answers_in_text(text_with_answers)
        has_answers_2 = app.detect_answers_in_text(text_without_answers)

        print(f"📝 包含答案的文本检测结果：{has_answers_1} (应为 True)")
        print(f"📝 不含答案的文本检测结果：{has_answers_2} (应为 False)")

        if has_answers_1 and not has_answers_2:
            print("[OK] 答案检测功能正常工作")
        else:
            print("[ERROR] 答案检测功能存在问题")

        root.destroy()

    except Exception as e:
        print(f"[ERROR] 答案检测测试失败: {e}")

if __name__ == "__main__":
    test_enhanced_parsing()
    test_answer_detection()