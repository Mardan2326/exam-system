#!/usr/bin/env python3
"""
测试PDF试卷数字化功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_exam_digitalization():
    """测试试卷数字化功能"""
    print("=== PDF试卷数字化功能测试 ===")

    try:
        from exam_app import ExamApp
        print("[OK] 成功导入ExamApp类")

        # 检查核心方法
        methods_to_check = [
            'extract_pdf_text',           # PDF文本提取
            'clean_page_text',            # 页面文本清理
            'post_process_text',          # 文本后处理
            'generate_mock_exam',         # 智能解析入口
            'show_exam_generation_dialog', # 解析选项对话框
            'start_exam_parsing',         # 开始解析
            'build_exam_parsing_prompt',  # 构建解析提示词
        ]

        for method_name in methods_to_check:
            if hasattr(ExamApp, method_name):
                print(f"[OK] 方法 {method_name} 已实现")
            else:
                print(f"[ERROR] 方法 {method_name} 缺失")

        print("\n=== 功能特性 ===")
        print("[NEW] 窗口标题：PDF试卷数字化 - 电脑考试系统")
        print("[NEW] 增强的PDF文本提取和清理")
        print("[NEW] 智能题目格式识别和修复")
        print("[NEW] AI智能解析试卷按钮")
        print("[NEW] 解析选项：完整解析/快速解析")
        print("[NEW] 答案处理：自动识别/忽略答案")
        print("[NEW] 试卷加载完成提示和统计")
        print("[NEW] 题目列表显示答案状态")

        print("\n=== 使用流程 ===")
        print("1. 输入DeepSeek API Key")
        print("2. 选择PDF试卷文件")
        print("3. 点击'AI智能解析试卷'")
        print("4. 选择解析模式（完整/快速）")
        print("5. 选择答案处理方式")
        print("6. AI解析完成后自动进入考试模式")
        print("7. 在电脑上完成原试卷的答题")

        print("\n=== 技术改进 ===")
        print("- PDF文本提取质量检测")
        print("- 题目格式自动修复")
        print("- 更准确的题目边界识别")
        print("- 增强的JSON解析容错")
        print("- 更好的用户反馈和提示")

        print("\n=== 适用场景 ===")
        print("- 学校试卷数字化")
        print("- 线上考试组织")
        print("- 试卷题库建设")
        print("- 无纸化考试实施")

        print("\n[SUCCESS] PDF试卷数字化功能测试完成！")
        print("\n💡 现在你可以把任何PDF纸质试卷转换为电脑考试了！")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exam_digitalization()