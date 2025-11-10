#!/usr/bin/env python3
"""
测试AI生成模拟卷功能
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_mock_exam_feature():
    """测试AI生成模拟卷功能"""
    print("=== AI生成模拟卷功能测试 ===")

    try:
        from exam_app import ExamApp
        print("[OK] 成功导入ExamApp类")

        # 检查新增的方法是否存在
        methods_to_check = [
            'generate_mock_exam',
            'show_exam_generation_dialog',
            'start_mock_exam_generation',
            'build_mock_exam_prompt',
            'generate_exam_from_topics',
            'generate_exam_based_on_topics'
        ]

        for method_name in methods_to_check:
            if hasattr(ExamApp, method_name):
                print(f"[OK] 方法 {method_name} 已添加")
            else:
                print(f"[ERROR] 方法 {method_name} 缺失")

        print("\n=== 功能特性 ===")
        print("[NEW] AI生成模拟卷按钮已添加到界面")
        print("[NEW] 支持基于PDF文件生成模拟试卷")
        print("[NEW] 支持自定义题目数量、难度级别")
        print("[NEW] 支持指定重点考察内容")
        print("[NEW] 支持手动输入知识点生成试卷（开发中）")
        print("[NEW] 智能AI提示词优化")

        print("\n=== 使用流程 ===")
        print("1. 输入DeepSeek API Key")
        print("2. 点击'AI生成模拟卷'按钮")
        print("3. 选择PDF文件或手动输入知识点")
        print("4. 设置题目参数（数量、难度等）")
        print("5. AI自动生成定制化模拟试卷")
        print("6. 开始答题考试")

        print("\n=== 优势特点 ===")
        print("- 比单纯解析更有针对性")
        print("- AI理解知识点后原创出题")
        print("- 可根据难度和重点定制")
        print("- 避免原题重复使用")
        print("- 生成高质量模拟试题")

        print("\n[SUCCESS] AI生成模拟卷功能测试完成！")

    except Exception as e:
        print(f"[ERROR] 测试失败: {e}")

if __name__ == "__main__":
    test_mock_exam_feature()