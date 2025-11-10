"""
PDF 试题模拟考试器 - Tkinter 桌面版
支持本地解析和 AI 解析（DeepSeek）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2  # pyright: ignore[reportMissingImports]
import json
import re
import os
from datetime import datetime, timedelta
import threading
from utils import call_llm


class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 试卷数字化 - 电脑考试系统")
        self.root.geometry("1000x700")
        
        # 数据
        self.questions = []
        self.current_index = 0
        self.user_answers = {}
        self.pdf_text = ""
        self.exam_submitted = False
        self.timer_running = False
        self.time_remaining = 0
        
        # 调试辅助：保存最近一次 AI 返回
        self.last_ai_raw_response = ""
        self.last_ai_candidate_json = ""
        
        # 创建界面
        self.create_ui()
        
    def create_ui(self):
        """创建用户界面"""
        # 顶部控制栏
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        # 文件选择
        ttk.Label(control_frame, text="PDF 文件:").pack(side=tk.LEFT, padx=5)
        self.file_label = ttk.Label(control_frame, text="未选择文件", foreground="gray")
        self.file_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(control_frame, text="📂 选择 PDF", command=self.select_pdf).pack(side=tk.LEFT, padx=5)
        
        # API Key 输入
        ttk.Label(control_frame, text="API Key:").pack(side=tk.LEFT, padx=(15, 5))
        self.api_key_var = tk.StringVar(value="")
        self.api_key_entry = ttk.Entry(control_frame, textvariable=self.api_key_var, width=40)
        self.api_key_entry.pack(side=tk.LEFT)
        
        ttk.Button(control_frame, text="🚀 完整试卷AI解析", command=self.direct_upload_parse).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🚀 本地解析（快速）", command=self.parse_local).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🤖 AI智能解析", command=self.parse_ai).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🔄 重置", command=self.reset).pack(side=tk.LEFT, padx=5)
        
        # 考试时长设置
        ttk.Label(control_frame, text="考试时长(分钟):").pack(side=tk.LEFT, padx=(20, 5))
        self.duration_var = tk.StringVar(value="90")
        ttk.Entry(control_frame, textvariable=self.duration_var, width=5).pack(side=tk.LEFT)
        
        # 计时器
        self.timer_label = ttk.Label(control_frame, text="--:--", font=("Arial", 12, "bold"), foreground="red")
        self.timer_label.pack(side=tk.LEFT, padx=20)
        
        # 状态栏
        status_frame = ttk.Frame(self.root, padding="10")
        status_frame.pack(fill=tk.X)
        
        self.status_label = ttk.Label(status_frame, text="请选择 PDF 文件开始", foreground="blue")
        self.status_label.pack(side=tk.LEFT)
        
        # 进度条
        self.progress = ttk.Progressbar(status_frame, length=200, mode='indeterminate')
        self.progress.pack(side=tk.LEFT, padx=20)
        
        # 调试：查看 AI 原始响应
        self.view_ai_btn = ttk.Button(status_frame, text="🪄 查看AI响应", command=self.show_ai_response, state=tk.DISABLED)
        self.view_ai_btn.pack(side=tk.RIGHT, padx=5)
        
        # 调试：题目质量分析
        self.analyze_btn = ttk.Button(status_frame, text="🔍 质量分析", command=self.analyze_questions, state=tk.DISABLED)
        self.analyze_btn.pack(side=tk.RIGHT)
        
        # 主内容区
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 左侧：题目显示
        left_frame = ttk.LabelFrame(main_frame, text="题目内容", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # 题目信息
        self.question_info_label = ttk.Label(left_frame, text="", font=("Arial", 10, "bold"))
        self.question_info_label.pack(anchor=tk.W, pady=5)
        
        # 题目文本
        self.question_text = scrolledtext.ScrolledText(left_frame, wrap=tk.WORD, height=8, font=("Arial", 11))
        self.question_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # 选项区域
        self.options_frame = ttk.LabelFrame(left_frame, text="选项", padding="10")
        self.options_frame.pack(fill=tk.BOTH, pady=5)
        
        self.option_buttons = []
        self.selected_option = tk.StringVar()
        
        # 导航按钮
        nav_frame = ttk.Frame(left_frame)
        nav_frame.pack(fill=tk.X, pady=10)
        
        self.prev_btn = ttk.Button(nav_frame, text="⬅ 上一题", command=self.prev_question, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)
        
        self.next_btn = ttk.Button(nav_frame, text="下一题 ➡", command=self.next_question, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)
        
        self.submit_btn = ttk.Button(nav_frame, text="📝 提交试卷", command=self.submit_exam, state=tk.DISABLED)
        self.submit_btn.pack(side=tk.RIGHT, padx=5)
        
        # 答题进度
        self.progress_label = ttk.Label(nav_frame, text="答题进度: 0 / 0", font=("Arial", 10))
        self.progress_label.pack(side=tk.RIGHT, padx=20)
        
        # 右侧：题目列表和日志
        right_frame = ttk.Frame(main_frame, width=300)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        
        # 题目列表
        list_frame = ttk.LabelFrame(right_frame, text="题目列表", padding="5")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.question_listbox = tk.Listbox(list_frame, height=15)
        self.question_listbox.pack(fill=tk.BOTH, expand=True)
        self.question_listbox.bind('<<ListboxSelect>>', self.on_question_select)
        
        # 日志区域
        log_frame = ttk.LabelFrame(right_frame, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, font=("Consolas", 9))
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
    def log(self, message):
        """线程安全地添加日志到界面"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        def _append():
            self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
            self.log_text.see(tk.END)
        # 始终通过主线程更新 Tk 控件
        self.root.after(0, _append)
        
    def select_pdf(self):
        """选择 PDF 文件"""
        filename = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path = filename
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            self.log(f"已选择文件: {os.path.basename(filename)}")
            self.status_label.config(text="已选择文件，请点击解析按钮")
            
    def extract_pdf_text(self, pdf_path):
        """提取 PDF 文本 - 完整文件优化版"""
        self.log("📄 开始提取完整PDF文件文本...")
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                self.log(f"📄 PDF 共 {num_pages} 页，准备完整提取")

                text = ""
                for i in range(num_pages):
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text()
                    if page_text is None:
                        page_text = ""

                    # 增强的文本清理
                    page_text = self.clean_page_text(page_text)
                    text += page_text + "\n\n"  # 用双换行分隔页面

                    # 每提取10页显示一次进度
                    if (i + 1) % 10 == 0 or i == num_pages - 1:
                        self.log(f"📄 已提取第 {i+1}/{num_pages} 页 ({(i+1)/num_pages*100:.1f}%)")

                # 完整文件的后处理
                text = self.post_process_full_document(text)

                self.pdf_text = text
                text_length = len(text)
                self.log(f"📄 PDF完整提取完成，共 {text_length} 字符")

                # 智能分析文档质量
                self.analyze_document_quality(text)

                return text
        except Exception as e:
            self.log(f"❌ PDF 提取失败: {e}")
            messagebox.showerror("错误", f"PDF 提取失败: {e}")
            return None

    def analyze_document_quality(self, text):
        """分析文档质量和特征"""
        # 基本统计
        lines = text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]

        # 题目分隔符检测
        question_separators = text.count('、') + text.count('.') + text.count('．')

        # 字符质量分析
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_chars = len([c for c in text if c.isalpha() and ord(c) < 128])

        self.log(f"📊 文档质量分析：")
        self.log(f"   • 总行数：{len(lines)} (非空行：{len(non_empty_lines)})")
        self.log(f"   • 题目分隔符：约 {question_separators} 个")
        self.log(f"   • 中文字符：{chinese_chars} 个")
        self.log(f"   • 英文字符：{english_chars} 个")

        # 质量评估
        if len(text.strip()) < 500:
            self.log("⚠️ 文档内容较少，可能是扫描件或提取不完整")
        elif question_separators < 5:
            self.log("⚠️ 题目分隔符较少，请确认是否为标准试卷格式")
        else:
            self.log("✅ 文档质量良好，适合AI解析")

    def post_process_full_document(self, text):
        """完整文档的后处理 - 优化AI解析"""
        if not text:
            return ""

        import re

        # 标准化题号格式
        text = re.sub(r'(\d+)\s*[、.．]', r'\1. ', text)

        # 标准化选项格式
        text = re.sub(r'([ABCD])\s*[、.．\)）]\s*', r'\1. ', text)

        # 清理页面间的重复内容
        text = re.sub(r'(第\s*\d+\s*页[^\n]*)\n+(第\s*\d+\s*页)', r'\1\n\2', text)

        # 移除页眉页脚（简单模式）
        text = re.sub(r'第\s*\d+\s*页\s*共\s*\d+\s*页', '', text)
        text = re.sub(r'-\s*\d+\s*-', '', text)

        # 确保题目之间有明确分隔
        text = re.sub(r'([.。]\s*)(\d+\.)', r'\1\n\n\2', text)

        # 清理多余空行但保留题目间的分隔
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        return text.strip()

    def clean_page_text(self, page_text):
        """清理单页文本"""
        if not page_text:
            return ""

        # 去除多余空白
        text = ' '.join(page_text.split())

        # 修复常见的PDF提取问题
        text = text.replace(' ', ' ')  # 修复多余空格
        text = text.replace('…', '...')  # 统一省略号

        # 修复题号格式
        import re
        # 确保题号后有正确的标点
        text = re.sub(r'(\d+)([^\d\s.、])', r'\1.\2', text)

        return text

    def post_process_text(self, text):
        """全文后处理"""
        if not text:
            return ""

        import re

        # 确保题目之间有足够分隔
        text = re.sub(r'([.。]\s*)(\d+)', r'\1\n\n\2', text)

        # 修复选项格式
        text = re.sub(r'([A-D])([^\s.、])', r'\1. \2', text)

        # 清理多余空行
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)

        return text.strip()
            
    def parse_local(self):
        """本地解析"""
        if not hasattr(self, 'pdf_path'):
            messagebox.showwarning("提示", "请先选择 PDF 文件！")
            return
            
        self.status_label.config(text="正在本地解析...")
        self.progress.start()
        
        def parse():
            text = self.extract_pdf_text(self.pdf_path)
            if text:
                questions = self.parse_questions_local(text)
                self.root.after(0, self.load_questions, questions)
            self.root.after(0, self.progress.stop)
            
        threading.Thread(target=parse, daemon=True).start()
        
    def parse_questions_local(self, text):
        """本地正则表达式解析"""
        self.log("使用正则表达式解析题目...")
        
        # 分离题目和答案
        parts = text.split('参考答案')
        questions_text = parts[0]
        answers_text = '参考答案' + parts[1] if len(parts) > 1 else ''
        
        # 解析答案
        answers = {}
        if answers_text:
            self.log("解析答案部分...")
            answer_pattern = r'(\d+)\s*、.*?故正确答案为\s*([A-D])'
            for match in re.finditer(answer_pattern, answers_text):
                answers[match.group(1)] = match.group(2).upper()
            self.log(f"找到 {len(answers)} 个答案")
        
        # 解析题目
        questions = []
        question_pattern = r'(\d{1,3})\s*[、.．](.+?)(?=\d{1,3}\s*[、.．]|$)'
        
        for match in re.finditer(question_pattern, questions_text, re.DOTALL):
            q_id = match.group(1)
            q_content = match.group(2).strip()
            
            # 提取选项（兼容半角/全角/括号/小写）
            option_pattern = r'([A-Da-d])\s*[、.．\)）]\s*([^A-Da-d]+?)(?=[A-Da-d]\s*[、.．\)）]|参考答案|答案|解析|$)'
            # 归一化选项键为大写
            options = {}
            
            for opt_match in re.finditer(option_pattern, q_content):
                opt_key = opt_match.group(1).upper()
                opt_text = opt_match.group(2).strip()
                if len(opt_text) > 0 and len(opt_text) < 500:
                    options[opt_key] = opt_text
            
            if len(options) >= 2:
                # 提取题干：使用第一个匹配到的选项位置来切分，避免题干中包含字母 'A' 的误切
                first_option_match = next(re.finditer(option_pattern, q_content), None)
                first_option_pos = first_option_match.start() if first_option_match else -1
                question_text = q_content[:first_option_pos].strip() if first_option_pos > 0 else q_content.strip()

                questions.append({
                    'id': q_id,
                    'text': question_text,
                    'options': options,
                    'answer': answers.get(q_id)
                })
        
        self.log(f"✅ 本地解析完成，共 {len(questions)} 道题")
        return questions
    
    def parse_ai_fast(self):
        """AI 快速解析（优化版）"""
        if not hasattr(self, 'pdf_path'):
            messagebox.showwarning("提示", "请先选择 PDF 文件！")
            return
            
        # 校验 API Key
        api_key = (self.api_key_var.get() or "").strip()
        if not api_key:
            messagebox.showwarning("提示", "请先输入 API Key！")
            return
        
        os.environ["DEEPSEEK_API_KEY"] = api_key
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "已设置"
        self.log(f"已加载 API Key（{masked}）")

        self.status_label.config(text="⚡ AI快速解析中（预计30-60秒）...")
        self.progress.start()
        self.log("⚡ 开始AI快速解析...")
        
        def parse():
            try:
                text = self.extract_pdf_text(self.pdf_path)
                if not text:
                    return
                
                # 快速模式：更严格的文本限制
                max_len = 5000  # 进一步减少到5000字符
                if len(text) > max_len:
                    text = text[:max_len]
                    self.log(f"快速模式：截取前 {max_len} 字符")
                
                # 快速模式的简化提示词
                prompt = f"""提取题目信息，返回JSON数组。

每道题包含：
- id: 题号
- text: 题干
- options: {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}}
- answer: 正确答案(不知道就用null)

直接返回JSON，无其他文字。

{text}"""
                
                messages = [{"role": "user", "content": prompt}]
                
                # 使用更短超时
                response = call_llm(messages, timeout=30)
                
                self.log("⚡ AI快速响应完成")
                self.last_ai_raw_response = response
                self.view_ai_btn.config(state=tk.NORMAL)

                # 使用统一的JSON解析方法
                candidate = self.extract_json_array(response)
                questions = self.parse_json_with_fallback(candidate)
                questions = self.normalize_questions(questions)

                if questions:
                    self.log(f"⚡ 快速解析成功：{len(questions)} 道题")
                    self.root.after(0, self.load_questions, questions)
                    return

                # 快速失败，直接回退本地解析
                self.log("⚡ 快速解析失败，回退本地解析")
                local_q = self.parse_questions_local(text)
                self.root.after(0, self.load_questions, local_q)
                
            except Exception as e:
                self.log(f"❌ 快速解析失败: {e}")
                self.root.after(0, messagebox.showerror, "错误", f"快速解析失败，请尝试本地解析: {e}")
            finally:
                self.root.after(0, self.progress.stop)
                
        threading.Thread(target=parse, daemon=True).start()
        
    def parse_ai(self):
        """AI 解析"""
        if not hasattr(self, 'pdf_path'):
            messagebox.showwarning("提示", "请先选择 PDF 文件！")
            return
            
        # 校验 API Key
        api_key = (self.api_key_var.get() or "").strip()
        if not api_key:
            messagebox.showwarning("提示", "请先输入 API Key 再进行 AI 解析！")
            return
        # 设置到当前会话环境变量，仅本次运行有效
        try:
            os.environ["DEEPSEEK_API_KEY"] = api_key
        except Exception:
            pass
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "已设置"
        self.log(f"已加载 API Key（{masked}）")

        self.status_label.config(text="🤖 AI完整解析中（预计 1-2 分钟）...")
        self.progress.start()
        self.log("🤖 开始 AI 完整解析，耐心等待...")
        
        def parse():
            try:
                text = self.extract_pdf_text(self.pdf_path)
                if not text:
                    return
                
                # 根据文本长度智能调整
                text_len = len(text)
                if text_len > 12000:  # 非常长的文档
                    max_len = 10000
                    self.log(f"📄 文档很长({text_len}字符)，智能截取前 {max_len} 字符")
                elif text_len > 8000:  # 中等长度文档
                    max_len = 8000
                    self.log(f"📄 文档中等长度({text_len}字符)，使用前 {max_len} 字符")
                else:
                    max_len = text_len
                    self.log(f"📄 文档较短({text_len}字符)，完整处理")

                if text_len > max_len:
                    text = text[:max_len]
                
                self.log("正在调用 DeepSeek API...")
                
                # 简化明确的题目解析提示词
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
{text}"""

                messages = [{"role": "user", "content": prompt}]
                response = call_llm(messages)
                
                self.log("DeepSeek 返回成功，正在解析...")

                # 保存原始响应
                self.last_ai_raw_response = response
                self.view_ai_btn.config(state=tk.NORMAL)

                # 简化的JSON提取和清理
                candidate = self.extract_json_array(response)
                self.last_ai_candidate_json = candidate

                # 尝试解析JSON
                questions = self.parse_json_with_fallback(candidate)
                # 统一规范化题目结构（容错 options 列表/数组等形式）
                questions = self.normalize_questions(questions)

                if not questions:
                    self.log("⚠️ AI 返回为空或格式不标准，尝试使用本地正则作为回退…")
                    self.log(f"🔍 调试信息：AI返回原始长度={len(response)}, 提取的JSON长度={len(candidate)}")

                    local_q = self.parse_questions_local(text)
                    if local_q:
                        self.log(f"✅ 回退到本地解析成功，获得 {len(local_q)} 道题")
                        self.root.after(0, self.load_questions, local_q)
                        return
                    else:
                        self.log("❌ 回退本地解析仍未获得题目")
                        self.log("💡 建议：1) 检查PDF文本质量 2) 尝试减少文本长度 3) 使用更清晰的试题文档")
                else:
                    self.log(f"✅ AI 解析成功，共 {len(questions)} 道题（已规范化）")
                    self.analyze_btn.config(state=tk.NORMAL)  # 启用质量分析按钮
                    self.root.after(0, self.load_questions, questions)
                
            except Exception as e:
                self.log(f"❌ AI 解析异常: {type(e).__name__}: {e}")
                error_msg = f"AI 解析出现异常：{type(e).__name__}\n\n建议检查：\n1. API Key 是否正确设置\n2. 网络连接是否正常\n3. PDF 文本是否可以正常提取"
                self.root.after(0, messagebox.showerror, "AI解析异常", error_msg)
            finally:
                self.root.after(0, self.progress.stop)
                
        threading.Thread(target=parse, daemon=True).start()

    def fix_json_format(self, json_str):
        """修复常见的JSON格式问题"""
        # 移除BOM和特殊字符
        json_str = json_str.replace('\ufeff', '')

        # 修复引号问题（将弯引号/单引号正规化为双引号）
        json_str = json_str.replace("'", '"')
        json_str = json_str.replace("“", '"').replace("”", '"').replace("‘", '"').replace("’", '"')
        json_str = json_str.replace("`", '')

        # 修复属性名未加引号的问题
        # 匹配没有引号的属性名
        import re
        # 匹配类似 {id: "value"} 的模式并修复为 {"id": "value"}
        json_str = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', json_str)

        # 修复末尾多余的逗号
        json_str = re.sub(r',\s*}', '}', json_str)
        json_str = re.sub(r',\s*\]', ']', json_str)

        # 注意：不再强制转义换行/回车/制表符，避免破坏 JSON 结构
        return json_str.strip()

    def show_ai_response(self):
        """弹窗展示最近一次 AI 原始响应与候选 JSON 片段"""
        win = tk.Toplevel(self.root)
        win.title("AI 响应预览（仅本次会话）")
        win.geometry("800x600")
        nb = ttk.Notebook(win)
        nb.pack(fill=tk.BOTH, expand=True)
        # 原始响应
        raw_frame = ttk.Frame(nb)
        nb.add(raw_frame, text="原始响应")
        raw_text = scrolledtext.ScrolledText(raw_frame, wrap=tk.WORD)
        raw_text.pack(fill=tk.BOTH, expand=True)
        raw_text.insert(1.0, self.last_ai_raw_response or "(无)")
        raw_text.config(state=tk.DISABLED)
        # 候选 JSON
        cand_frame = ttk.Frame(nb)
        nb.add(cand_frame, text="候选JSON片段")
        cand_text = scrolledtext.ScrolledText(cand_frame, wrap=tk.WORD)
        cand_text.pack(fill=tk.BOTH, expand=True)
        cand_text.insert(1.0, self.last_ai_candidate_json or "(无)")
        cand_text.config(state=tk.DISABLED)

    def normalize_questions(self, data):
        """将多种可能形态的题目结构规范化为标准结构，并进行质量检查
        标准结构：{"id": str, "text": str, "options": {A..D}, "answer": str or None}
        """
        try:
            if isinstance(data, dict):
                if 'questions' in data and isinstance(data['questions'], list):
                    data = data['questions']
                else:
                    # 如果是单题对象，包装成数组
                    data = [data]
            if not isinstance(data, list):
                return []
                
            normalized = []
            for idx, q in enumerate(data, 1):
                if not isinstance(q, dict):
                    continue
                    
                qid = str(q.get('id') or idx)
                text = str(q.get('text') or '').strip()
                opts = q.get('options')
                ans = q.get('answer')
                
                # 质量检查：题干不能太短或包含明显的选项标识
                if len(text) < 5:
                    self.log(f"⚠️ 题目 {qid} 题干过短，跳过")
                    continue
                
                # 检查题干是否误包含下一题信息
                import re
                if re.search(r'\d+[、.．]\s*[^A-D]', text):
                    # 可能包含下一题题号，尝试截取
                    match = re.search(r'(\d+[、.．])', text)
                    if match and match.start() > 20:  # 如果题号出现在较后位置
                        text = text[:match.start()].strip()
                        self.log(f"⚠️ 题目 {qid} 题干包含下题信息，已截取")
                
                # 规范化 options
                opt_map = {}
                if isinstance(opts, dict):
                    # 处理标准的A-D选项
                    option_keys = ['A', 'B', 'C', 'D']
                    available_keys = list(opts.keys())
                    
                    # 优先使用标准键名
                    for key in option_keys:
                        if key in opts:
                            content = str(opts[key]).strip()
                            # 质量检查：选项内容不能太短或包含题号
                            if len(content) < 2:
                                continue
                            if re.match(r'^\d+[、.．]', content):
                                self.log(f"⚠️ 题目 {qid} 选项 {key} 疑似包含题号，跳过")
                                continue
                            # 检查选项是否过长（可能误包含下题）
                            if len(content) > 200:
                                # 寻找可能的截断点
                                cut_match = re.search(r'\d+[、.．]', content)
                                if cut_match:
                                    content = content[:cut_match.start()].strip()
                                    self.log(f"⚠️ 题目 {qid} 选项 {key} 过长，已截取")
                            opt_map[key] = content
                    
                    # 如果标准键名不够，按顺序映射其他键
                    if len(opt_map) < 4:
                        used_keys = set(opt_map.keys())
                        remaining_option_keys = [k for k in option_keys if k not in used_keys]
                        remaining_available_keys = [k for k in available_keys if k not in ['A', 'B', 'C', 'D']]
                        
                        for i, key in enumerate(remaining_available_keys):
                            if i < len(remaining_option_keys):
                                content = str(opts[key]).strip()
                                if len(content) >= 2 and not re.match(r'^\d+[、.．]', content):
                                    opt_map[remaining_option_keys[i]] = content
                                    
                elif isinstance(opts, list):
                    # 列表形式：映射到A-D
                    for i, item in enumerate(opts[:4]):
                        label = chr(ord('A') + i)
                        if isinstance(item, dict):
                            if 'text' in item:
                                content = str(item['text']).strip()
                            else:
                                try:
                                    content = str(next(iter(item.values()))).strip()
                                except Exception:
                                    content = str(item)
                        else:
                            content = str(item).strip()
                        
                        # 质量检查
                        if len(content) >= 2 and not re.match(r'^\d+[、.．]', content):
                            opt_map[label] = content
                
                # 最终质量检查
                if len(opt_map) < 2:
                    self.log(f"⚠️ 题目 {qid} 选项不足，跳过")
                    continue
                    
                # 规范答案
                if isinstance(ans, str):
                    ans = ans.strip().upper()
                    if ans not in opt_map and ans not in ['A', 'B', 'C', 'D']:
                        ans = None
                else:
                    ans = None
                
                normalized.append({
                    'id': qid,
                    'text': text,
                    'options': opt_map,
                    'answer': ans
                })
                
            self.log(f"📊 质量检查完成，有效题目: {len(normalized)}")
            return normalized
        except Exception as e:
            self.log(f"❌ 题目规范化失败: {e}")
            return []

    def repair_json_candidate(self, s: str) -> str:
        """尽力把不完整的 JSON 片段修成可解析的数组字符串。
        策略：
        - 去掉首尾非数组/对象的噪声
        - 如果是对象开头而非数组，用方括号包裹
        - 对方括号进行简单配对裁剪（截到最后一个完整的]）
        - 如果依然无法直接解析，返回原始字符串
        """
        s = (s or '').strip()
        if not s:
            return s
        # 仅保留从第一个'['或'{'开始的内容
        first_arr = s.find('[')
        first_obj = s.find('{')
        start = -1
        if first_arr != -1 and first_obj != -1:
            start = min(first_arr, first_obj)
        else:
            start = max(first_arr, first_obj)
        if start > 0:
            s = s[start:]
        s = s.strip()
        # 如果是对象开头且不是数组，包一层数组
        if s.startswith('{') and not s.startswith('['):
            s = '[' + s
            # 确保以 '}]' 结束
            if not s.rstrip().endswith(']'):
                s = s + ']'
        # 方括号配对裁剪
        stack = 0
        end_index = -1
        for i, ch in enumerate(s):
            if ch == '[':
                stack += 1
            elif ch == ']':
                stack -= 1
                if stack == 0:
                    end_index = i
        if end_index != -1:
            s = s[:end_index+1]
        return s

    def salvage_questions_from_text(self, text: str):
        """从任意文本中提取可能的题目对象，返回数组（尽力而为）。"""
        import re
        candidates = []
        # 粗略匹配包含"id"和"options"键的对象块
        pattern = r'\{[^{}]*"id"\s*:\s*"?[^"]+"?[^{}]*"options"\s*:\s*\{[^{}]*\}[^{}]*\}'
        for m in re.finditer(pattern, text, flags=re.DOTALL):
            obj = m.group(0)
            try:
                fixed = self.fix_json_format(obj)
                q = json.loads(fixed)
                candidates.append(q)
            except Exception:
                continue
        return candidates

    def extract_json_array(self, response):
        """从响应中提取JSON数组，简化版本"""
        if not response:
            return "[]"

        # 清理响应文本
        cleaned = response.strip()

        # 去除markdown代码块标记
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:].strip()
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:].strip()

        if cleaned.endswith('```'):
            cleaned = cleaned[:-3].strip()

        # 查找JSON数组
        start = cleaned.find('[')
        end = cleaned.rfind(']')

        if start != -1 and end != -1 and end > start:
            return cleaned[start:end+1]

        # 如果没找到数组，尝试查找对象并包裹为数组
        obj_start = cleaned.find('{')
        obj_end = cleaned.rfind('}')
        if obj_start != -1 and obj_end != -1 and obj_end > obj_start:
            return "[" + cleaned[obj_start:obj_end+1] + "]"

        return cleaned

    def parse_json_with_fallback(self, json_str):
        """带容错的JSON解析"""
        if not json_str:
            return []

        # 尝试直接解析
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            self.log(f"⚠️ JSON解析失败: {e}")

        # 基本清理后再次尝试
        try:
            cleaned = json_str.replace("'", '"')  # 单引号转双引号
            cleaned = cleaned.replace("“", '"').replace("”", '"')  # 弯引号转直引号
            cleaned = cleaned.replace("‘", '"').replace("’", '"')  # 单弯引号转直引号
            cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)  # 去除多余逗号
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            self.log(f"⚠️ 清理后仍解析失败: {e}")

        # 最后尝试：修复常见的JSON问题
        try:
            fixed = self.fix_json_format(json_str)
            return json.loads(fixed)
        except Exception as e:
            self.log(f"❌ 所有JSON解析尝试都失败: {e}")
            return []

    def extract_questions_fallback(self, response):
        """备用解析方法，从响应中手动提取题目"""
        questions = []

        # 尝试找到JSON数组部分
        import re

        # 查找数组开始和结束
        array_start = response.find('[')
        array_end = response.rfind(']')

        if array_start != -1 and array_end != -1 and array_end > array_start:
            json_part = response[array_start:array_end + 1]

            # 尝试修复JSON
            fixed_json = self.fix_json_format(json_part)

            try:
                questions = json.loads(fixed_json)
            except json.JSONDecodeError:
                # 如果还是失败，尝试手动解析
                # 查找题目对象
                question_pattern = r'\{[^{}]*"id"\s*:\s*"[^"]+"[^{}]*\}'
                matches = re.findall(question_pattern, response)

                for match in matches:
                    try:
                        fixed_match = self.fix_json_format(match)
                        question = json.loads(fixed_match)

                        # 验证必要字段
                        if 'id' in question and 'text' in question and 'options' in question:
                            questions.append(question)
                    except:
                        continue

        return questions

    def load_questions(self, questions):
        """加载题目 - 增强版"""
        if not questions or len(questions) == 0:
            messagebox.showwarning("提示", "未能解析出题目。建议：\n1) 先试 AI 智能解析；\n2) 如 AI 失败，尝试本地解析；\n3) 检查PDF是否为可提取文本格式")
            self.status_label.config(text="解析失败")
            return

        # 统计题目质量
        with_answers = sum(1 for q in questions if q.get('answer'))
        total_questions = len(questions)

        self.questions = questions
        self.current_index = 0
        self.user_answers = {}
        self.exam_submitted = False

        # 显示加载状态
        answer_info = f"（含答案 {with_answers}/{total_questions}）" if with_answers > 0 else "（无答案）"
        self.status_label.config(text=f"✅ 成功加载 {total_questions} 道题目 {answer_info}")

        # 更新题目列表 - 增强显示
        self.question_listbox.delete(0, tk.END)
        for i, q in enumerate(questions, 1):
            answer_mark = " ✓" if q.get('answer') else ""
            display_text = f"{i}. 第 {q['id']} 题{answer_mark}"
            self.question_listbox.insert(tk.END, display_text)

        # 启用按钮
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)

        # 显示第一题
        self.show_question(0)

        # 开始计时
        self.start_timer()

        # 显示成功消息
        self.log(f"✅ 试卷数字化完成！共 {total_questions} 道题，{with_answers} 道有答案")
        messagebox.showinfo("试卷数字化成功",
                          f"成功将纸质试卷数字化！\n\n"
                          f"题目总数：{total_questions} 道\n"
                          f"包含答案：{with_answers} 道\n"
                          f"不含答案：{total_questions - with_answers} 道\n\n"
                          f"现在可以开始在电脑上答题了！")
        
    def show_question(self, index):
        """显示题目"""
        if index < 0 or index >= len(self.questions):
            self.log(f"❌ 无效的题目索引: {index}, 题目总数: {len(self.questions)}")
            return
            
        self.current_index = index
        q = self.questions[index]
        
        self.log(f"📖 显示第 {index + 1} 题 (ID: {q['id']})")
        
        # 更新题目信息
        self.question_info_label.config(
            text=f"第 {index + 1} 题 / 共 {len(self.questions)} 题（原题号 {q['id']}）"
        )
        
        # 显示题目文本
        self.question_text.config(state=tk.NORMAL)  # 先启用编辑
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, q['text'])
        self.question_text.config(state=tk.DISABLED)
        
        # 清空选项
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_buttons = []
        
        # 显示选项
        current_answer = self.user_answers.get(q['id'], '')
        self.selected_option.set(current_answer)
        
        if not q.get('options'):
            self.log(f"⚠️ 第 {q['id']} 题缺少选项数据")
            return
            
        for key in sorted(q['options'].keys()):
            option_text = f"{key}. {q['options'][key]}"
            rb = ttk.Radiobutton(
                self.options_frame,
                text=option_text,
                variable=self.selected_option,
                value=key,
                command=lambda k=key: self.select_answer(k)
            )
            rb.pack(anchor=tk.W, pady=2, fill=tk.X)
            self.option_buttons.append(rb)
        
        # 如果已提交，显示答案
        if self.exam_submitted and q.get('answer'):
            user_answer = self.user_answers.get(q['id'], '')
            correct_answer = q['answer']
            is_correct = user_answer == correct_answer
            
            color = "green" if is_correct else "red"
            status = "✓" if is_correct else "✗"
            
            answer_label = ttk.Label(
                self.options_frame,
                text=f"{status} 正确答案: {correct_answer} | 您的答案: {user_answer or '未答'}",
                foreground=color,
                font=("Arial", 10, "bold")
            )
            answer_label.pack(anchor=tk.W, pady=10)
        
        # 更新列表选中
        self.question_listbox.selection_clear(0, tk.END)
        self.question_listbox.selection_set(index)
        self.question_listbox.see(index)
        
        # 更新导航按钮状态
        self.prev_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if index < len(self.questions) - 1 else tk.DISABLED)
        
        # 更新进度
        self.update_progress()
        
    def select_answer(self, option):
        """选择答案"""
        if self.exam_submitted:
            return
        q = self.questions[self.current_index]
        self.user_answers[q['id']] = option
        self.update_progress()
        self.log(f"第 {q['id']} 题选择: {option}")
        
    def update_progress(self):
        """更新答题进度"""
        answered = len(self.user_answers)
        total = len(self.questions)
        percent = int(answered / total * 100) if total > 0 else 0
        self.progress_label.config(text=f"答题进度: {answered} / {total} ({percent}%)")
        
    def prev_question(self):
        """上一题"""
        self.log(f"🔙 点击上一题，当前索引: {self.current_index}")
        if self.current_index > 0:
            new_index = self.current_index - 1
            self.log(f"🔙 切换到第 {new_index + 1} 题")
            self.show_question(new_index)
        else:
            self.log("🔙 已经是第一题，无法继续向前")
            
    def next_question(self):
        """下一题"""
        self.log(f"🔜 点击下一题，当前索引: {self.current_index}")
        if self.current_index < len(self.questions) - 1:
            new_index = self.current_index + 1
            self.log(f"🔜 切换到第 {new_index + 1} 题")
            self.show_question(new_index)
        else:
            self.log("🔜 已经是最后一题，无法继续向后")
            
    def on_question_select(self, event):
        """题目列表选择"""
        selection = self.question_listbox.curselection()
        self.log(f"📋 题目列表选择事件，选中项: {selection}")
        if selection:
            selected_index = selection[0]
            self.log(f"📋 从列表跳转到第 {selected_index + 1} 题")
            self.show_question(selected_index)
        else:
            self.log("📋 题目列表选择为空")
            
    def start_timer(self):
        """开始计时"""
        try:
            minutes = int(self.duration_var.get())
            self.time_remaining = minutes * 60
            self.timer_running = True
            self.update_timer()
        except:
            pass
            
    def update_timer(self):
        """更新计时器"""
        if not self.timer_running or self.time_remaining <= 0:
            if self.time_remaining <= 0:
                self.timer_label.config(text="00:00")
                messagebox.showinfo("提示", "时间到！试卷将自动提交。")
                self.submit_exam()
            return
            
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
        
        self.time_remaining -= 1
        self.root.after(1000, self.update_timer)
        
    def submit_exam(self):
        """提交试卷"""
        if len(self.questions) == 0:
            messagebox.showwarning("提示", "请先加载题目！")
            return
            
        answered = len(self.user_answers)
        total = len(self.questions)
        
        if answered < total and not self.exam_submitted:
            if not messagebox.askyesno("确认", f"您还有 {total - answered} 道题未作答，确定要提交试卷吗？"):
                return
        
        self.timer_running = False
        self.exam_submitted = True
        self.submit_btn.config(state=tk.DISABLED)
        
        # 计算成绩
        correct = 0
        for q in self.questions:
            if q.get('answer') and self.user_answers.get(q['id']) == q['answer']:
                correct += 1
        
        score = int(correct / total * 100) if total > 0 else 0
        
        # 显示成绩
        result = f"""
🎉 考试结束！

总题数: {total}
已作答: {answered}
正确: {correct}
错误: {total - correct}

得分: {correct} / {total}
正确率: {score}%
        """
        
        messagebox.showinfo("考试成绩", result)
        self.log(f"✅ 考试提交成功 - 得分: {correct}/{total} ({score}%)")
        
        # 刷新当前题目显示答案
        self.show_question(self.current_index)
        
    def analyze_questions(self):
        """题目质量分析功能"""
        if not self.questions:
            messagebox.showinfo("提示", "请先加载题目")
            return

        # 统计信息
        total = len(self.questions)
        with_answer = sum(1 for q in self.questions if q.get('answer'))
        without_answer = total - with_answer

        # 选项统计
        option_counts = {}
        for q in self.questions:
            opts = q.get('options', {})
            count = len(opts)
            option_counts[count] = option_counts.get(count, 0) + 1

        # 生成分析报告
        report = f"""📊 题目质量分析报告

📈 基本统计：
• 总题数：{total}
• 有答案：{with_answer} ({with_answer/total*100:.1f}%)
• 无答案：{without_answer} ({without_answer/total*100:.1f}%)

📋 选项分布："""
        for count, num in sorted(option_counts.items()):
            report += f"\n• {count}个选项：{num}题"

        # 质量评估
        report += "\n\n🔍 质量评估："
        if with_answer/total > 0.8:
            report += "✅ 答案完整度高"
        elif with_answer/total > 0.5:
            report += "⚠️ 答案完整度中等"
        else:
            report += "❌ 答案缺失较多"

        if 4 in option_counts and option_counts[4] > total * 0.8:
            report += "\n✅ 选项格式规范"
        else:
            report += "\n⚠️ 选项格式不统一"

        messagebox.showinfo("题目质量分析", report)
        self.log("🔍 完成题目质量分析")

    def generate_mock_exam(self):
        """AI生成模拟试卷"""
        # 校验 API Key
        api_key = (self.api_key_var.get() or "").strip()
        if not api_key:
            messagebox.showwarning("提示", "请先输入 API Key 再使用AI生成功能！")
            return

        # 检查是否已选择文件
        if not hasattr(self, 'pdf_path'):
            result = messagebox.askyesno("提示", "AI生成模拟卷需要基于学习材料。\n\n点击'是'：选择PDF文件作为基础\n点击'否'：手动输入知识点")
            if result:
                # 选择文件
                self.select_pdf()
                if not hasattr(self, 'pdf_path'):
                    return
            else:
                # 手动输入知识点
                self.generate_exam_from_topics()
                return

        # 设置API Key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        masked = api_key[:4] + "..." + api_key[-4:] if len(api_key) > 8 else "已设置"
        self.log(f"已加载 API Key（{masked}）")

        # 显示生成选项对话框
        self.show_exam_generation_dialog()

    def show_exam_generation_dialog(self):
        """显示试卷解析选项对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("AI智能解析试卷")
        dialog.geometry("450x300")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # 说明
        info_label = ttk.Label(dialog, text="AI将完整解析试卷中的所有题目",
                             font=("Arial", 11, "bold"))
        info_label.pack(pady=10)

        # 解析模式
        ttk.Label(dialog, text="解析模式:", font=("Arial", 10)).pack(pady=5)
        mode_var = tk.StringVar(value="完整解析")
        mode_frame = ttk.Frame(dialog)
        mode_frame.pack(pady=5)
        ttk.Radiobutton(mode_frame, text="完整解析（提取所有题目）",
                       variable=mode_var, value="完整解析").pack(anchor=tk.W)
        ttk.Radiobutton(mode_frame, text="快速解析（只提取前20题）",
                       variable=mode_var, value="快速解析").pack(anchor=tk.W)

        # 答案处理
        ttk.Label(dialog, text="答案处理:", font=("Arial", 10)).pack(pady=5)
        answer_var = tk.StringVar(value="自动识别")
        answer_frame = ttk.Frame(dialog)
        answer_frame.pack(pady=5)
        ttk.Radiobutton(answer_frame, text="自动识别答案",
                       variable=answer_var, value="自动识别").pack(anchor=tk.W)
        ttk.Radiobutton(answer_frame, text="忽略答案（只提取题目）",
                       variable=answer_var, value="忽略答案").pack(anchor=tk.W)

        # 附加说明
        tip_text = "提示：AI会尽量保持原题格式，如果解析不完整可以尝试本地解析"
        tip_label = ttk.Label(dialog, text=tip_text, font=("Arial", 9), foreground="gray")
        tip_label.pack(pady=10)

        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)

        def start_parsing():
            mode = mode_var.get()
            answer_mode = answer_var.get()
            dialog.destroy()
            self.start_exam_parsing(mode, answer_mode)

        ttk.Button(button_frame, text="开始解析", command=start_parsing).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def start_exam_parsing(self, mode, answer_mode):
        """开始智能解析试卷"""
        self.status_label.config(text="📋 AI正在智能解析试卷...")
        self.progress.start()
        self.log(f"📋 开始智能解析试卷：{mode}，{answer_mode}")

        def parse():
            try:
                # 提取PDF文本
                text = self.extract_pdf_text(self.pdf_path)
                if not text:
                    self.log("❌ 无法提取PDF文本")
                    return

                # 根据模式调整文本长度
                if mode == "快速解析":
                    max_len = 8000
                    self.log("📄 快速解析模式，限制文本长度")
                else:
                    max_len = 15000
                    self.log("📄 完整解析模式，尽量处理全部内容")

                if len(text) > max_len:
                    text = text[:max_len]
                    self.log(f"📄 文本过长，使用前 {max_len} 字符进行解析")

                # 构建试卷解析提示词
                prompt = self.build_exam_parsing_prompt(text, answer_mode)

                self.log("🤖 正在调用AI智能解析试卷...")
                messages = [{"role": "user", "content": prompt}]

                # 调用AI
                response = call_llm(messages, timeout=120)

                self.log("✅ AI解析完成，正在处理...")
                self.last_ai_raw_response = response
                self.view_ai_btn.config(state=tk.NORMAL)

                # 解析AI返回的题目
                candidate = self.extract_json_array(response)
                questions = self.parse_json_with_fallback(candidate)
                questions = self.normalize_questions(questions)

                if questions:
                    self.log(f"📋 成功解析 {len(questions)} 道题目")
                    self.analyze_btn.config(state=tk.NORMAL)
                    self.root.after(0, self.load_questions, questions)
                else:
                    self.log("❌ AI未能解析出有效题目")
                    self.root.after(0, lambda: messagebox.showwarning("提示", "AI解析失败，请尝试本地解析或检查PDF质量"))

            except Exception as e:
                self.log(f"❌ 智能解析失败: {e}")
                error_msg = f"智能解析试卷时出现错误：{type(e).__name__}\n\n建议检查：\n1. API Key 是否正确\n2. 网络连接是否正常\n3. PDF 文件是否为可提取文本的试卷"
                self.root.after(0, messagebox.showerror, "解析失败", error_msg)
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=parse, daemon=True).start()

    def build_exam_parsing_prompt(self, source_text, answer_mode):
        """构建试卷解析的AI提示词"""
        prompt = f"""请仔细解析以下试卷内容，准确提取所有题目并转换为JSON格式。

重要要求：
1. 完整提取试卷中的每一道题目，不要遗漏
2. 保持原题不变，准确识别题号、题干、选项
3. 选项必须是A、B、C、D格式
4. 确保题目顺序与原试卷一致"""

        if answer_mode == "自动识别":
            prompt += "\n5. 如果能找到答案部分，请标注正确答案；如果找不到，设为null"
        else:
            prompt += "\n5. 忽略答案，所有answer字段设为null"

        prompt += f"""

解析规则：
- 识别题号格式：1.、1、2.、2.、1、2 等
- 题干：题号后到选项A之间的所有内容
- 选项：A.、B.、C.、D. 或 A、B、C、D 或 A)、B)、C)、D) 格式
- 注意区分题目内容，避免把下一题的内容混入当前题

输出格式：严格JSON数组
[
  {{
    "id": "1",
    "text": "题目的完整内容",
    "options": {{
      "A": "选项A的完整内容",
      "B": "选项B的完整内容",
      "C": "选项C的完整内容",
      "D": "选项D的完整内容"
    }},
    "answer": "A"  // 或 null 如果找不到答案
  }}
]

试卷内容：
---
{source_text}
---

请仔细解析并返回JSON数组："""

        return prompt

    def build_mock_exam_prompt(self, source_text, question_count, difficulty, focus_points):
        """构建试卷解析的AI提示词 - 专注于准确提取现有题目"""
        prompt = f"""请仔细解析以下试卷内容，准确提取所有题目并转换为JSON格式。

重要要求：
1. 完整提取试卷中的每一道题目，不要遗漏
2. 保持原题不变，准确识别题号、题干、选项
3. 选项必须是A、B、C、D格式
4. 如果能找到答案，请标注正确答案；如果找不到，设为null
5. 确保题目顺序与原试卷一致

解析规则：
- 识别题号格式：1.、1、2.、2. 等
- 题干：题号后到选项A之间的所有内容
- 选项：A.、B.、C.、D. 或 A、B、C、D 格式
- 答案：通常在题目后或试卷最后的答案部分

输出格式：严格JSON数组
[
  {{
    "id": "1",
    "text": "题目的完整内容",
    "options": {{
      "A": "选项A的完整内容",
      "B": "选项B的完整内容",
      "C": "选项C的完整内容",
      "D": "选项D的完整内容"
    }},
    "answer": "A"  // 或 null 如果找不到答案
  }}
]

试卷内容：
---
{source_text}
---

请仔细解析并返回JSON数组："""

        return prompt

    def generate_exam_from_topics(self):
        """基于手动输入的知识点生成试卷"""
        dialog = tk.Toplevel(self.root)
        dialog.title("输入知识点")
        dialog.geometry("600x400")
        dialog.transient(self.root)
        dialog.grab_set()

        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        ttk.Label(dialog, text="请输入要考察的知识点（每行一个）：", font=("Arial", 10)).pack(pady=10)

        text_widget = tk.Text(dialog, height=15, width=70)
        text_widget.pack(pady=10, padx=20)
        text_widget.insert("1.0", """例如：
1. 人工智能的基本概念
2. 机器学习算法分类
3. 深度学习应用领域
4. 自然语言处理技术
5. 计算机视觉原理""")

        def generate_from_topics():
            topics = text_widget.get("1.0", tk.END).strip()
            if not topics or len(topics) < 20:
                messagebox.showwarning("提示", "请输入足够的知识点内容")
                return

            dialog.destroy()
            self.generate_exam_based_on_topics(topics)

        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="生成试卷", command=generate_from_topics).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=10)

    def generate_exam_based_on_topics(self, topics):
        """基于知识点生成试卷"""
        # 这里可以实现基于知识点生成试卷的逻辑
        # 暂时用通用的生成方法
        self.log("📝 基于知识点生成试卷功能开发中...")
        messagebox.showinfo("提示", "基于知识点生成试卷功能正在开发中，请先使用PDF文件生成")

    def direct_upload_parse(self):
        """直接上传文件给AI解析 - 最简流程"""
        # 校验 API Key
        api_key = (self.api_key_var.get() or "").strip()
        if not api_key:
            messagebox.showwarning("提示", "请先输入 API Key！")
            return

        # 直接选择文件并解析
        filename = filedialog.askopenfilename(
            title="选择试卷PDF文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filename:
            return

        # 设置API Key
        os.environ["DEEPSEEK_API_KEY"] = api_key
        # 格式化API Key显示
        if len(api_key) > 8:
            masked = api_key[:4] + "..." + api_key[-4:]
        else:
            masked = "已设置"
        self.log(f"已加载 API Key（{masked}）")

        # 开始解析
        self.pdf_path = filename
        self.file_label.config(text=os.path.basename(filename), foreground="black")
        self.log(f"选择文件: {os.path.basename(filename)}")

        # 直接调用AI解析
        self.start_direct_ai_parse()

    def start_direct_ai_parse(self):
        """直接AI解析 - 完整文件智能解析版"""
        self.status_label.config(text="🚀 AI正在智能解析完整试卷...")
        self.progress.start()
        self.log("🚀 开始AI完整文件智能解析...")

        def parse():
            try:
                # 提取PDF文本
                text = self.extract_pdf_text(self.pdf_path)
                if not text:
                    self.log("❌ 无法提取PDF文本")
                    return

                self.log(f"📄 提取到 {len(text)} 字符的完整试卷内容")

                # 智能分析文本，检测是否包含答案部分
                has_answers = self.detect_answers_in_text(text)
                answer_hint = "包含答案部分，请智能识别并标注正确答案" if has_answers else "未发现明显答案部分，answer字段设为null"
                self.log(f"🔍 智能检测结果：{answer_hint}")

                # 构建增强的AI提示词 - 支持完整文件解析
                prompt = f"""请完整解析这份试卷的所有内容，准确提取每一道题目并转换为标准JSON格式。

重要要求：
1. 完整提取整份试卷的所有题目，确保不遗漏任何一道题
2. 保持原题内容完全不变，包括题干、选项的原文表述
3. 智能识别并提取答案：{answer_hint}
4. 处理各种题目格式（单选题、多选题标记等）
5. 确保题目顺序与原试卷完全一致

解析规则：
- 题号识别：支持 1.、1、2.、2.、1、2 等各种格式
- 选项识别：支持 A.、B.、C.、D. 或 A、B、C、D 或 A)、B)、C)、D) 等格式
- 答案识别：在题目后、试卷末尾、或"参考答案"部分寻找
- 题目边界：准确区分每道题的开始和结束，避免内容混淆

输出格式（严格JSON数组）：
[
  {{
    "id": "原题号",
    "text": "完整题干内容",
    "options": {{
      "A": "选项A完整内容",
      "B": "选项B完整内容",
      "C": "选项C完整内容",
      "D": "选项D完整内容"
    }},
    "answer": "正确答案字母或null"
  }}
]

注意：如果找不到某道题的答案，answer字段设为null；如果确定找到答案，填入A、B、C或D。

完整试卷内容：
---
{text}
---

请仔细解析并返回标准JSON数组："""

                self.log("🤖 正在调用AI进行完整文件智能解析...")
                messages = [{"role": "user", "content": prompt}]

                # 根据文件大小调整超时时间
                timeout = 180 if len(text) > 10000 else 120
                self.log(f"⏱️ 设置解析超时时间：{timeout}秒")

                # 调用AI
                response = call_llm(messages, timeout=timeout)

                self.log("✅ AI完整解析完成，正在处理结果...")
                self.last_ai_raw_response = response
                self.view_ai_btn.config(state=tk.NORMAL)

                # 解析JSON
                candidate = self.extract_json_array(response)
                questions = self.parse_json_with_fallback(candidate)
                questions = self.normalize_questions(questions)

                if questions:
                    # 统计答案情况
                    with_answers = sum(1 for q in questions if q.get('answer'))
                    total_questions = len(questions)

                    self.log(f"🎉 完整文件解析成功！")
                    self.log(f"📊 提取题目总数：{total_questions} 道")
                    self.log(f"✅ 识别答案数量：{with_answers} 道")
                    self.log(f"📈 答案识别率：{with_answers/total_questions*100:.1f}%")

                    self.analyze_btn.config(state=tk.NORMAL)
                    self.root.after(0, self.load_questions, questions)
                else:
                    self.log("❌ AI未能从完整文件中提取有效题目")
                    self.root.after(0, lambda: messagebox.showwarning(
                        "解析失败",
                        "AI无法解析此试卷。\n\n建议：\n1. 检查PDF是否为可提取文本格式\n2. 确认试卷格式是否清晰\n3. 尝试使用本地解析作为备选"
                    ))

            except Exception as e:
                self.log(f"❌ 完整文件解析失败: {e}")
                self.root.after(0, lambda: messagebox.showerror(
                    "解析失败",
                    f"AI解析完整文件时出现错误：{e}\n\n建议检查：\n1. 网络连接是否正常\n2. API Key是否正确\n3. PDF文件是否过大"
                ))
            finally:
                self.root.after(0, self.progress.stop)

        threading.Thread(target=parse, daemon=True).start()

    def detect_answers_in_text(self, text):
        """智能检测文本中是否包含答案部分"""
        import re

        # 常见的答案标识词汇
        answer_patterns = [
            r'参考答案',
            r'标准答案',
            r'正确答案',
            r'答案[：:]\s*',
            r'解答[：:]\s*',
            r'Answer[：:]\s*',
            r'KEY[：:]\s*',
            r'正确选项[：:]\s*',
            r'选择[：:]\s*[ABCD]',
            r'第\d+题[：:]\s*[ABCD]',
            r'\d+[、.．\)]\s*[ABCD]\s*[,，。；;]',
            r'故选[ABCD]',
            r'答案为[ABCD]',
            r'正确答案是?[ABCD]'
        ]

        # 检测答案模式
        answer_count = 0
        for pattern in answer_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            answer_count += len(matches)
            if len(matches) > 0:
                self.log(f"🔍 发现答案模式：{pattern[:20]}... (匹配{len(matches)}处)")

        # 检测连续的答案模式（如 "1.A 2.B 3.C"）
        continuous_pattern = r'(\d+[、.．\)]\s*[ABCD](?:\s*[,，；;]\s*\d+[、.．\)]\s*[ABCD]){2,})'
        continuous_matches = re.findall(continuous_pattern, text, re.IGNORECASE)
        if continuous_matches:
            self.log(f"🔍 发现连续答案模式：{len(continuous_matches)}处")
            answer_count += len(continuous_matches)

        # 检测表格形式的答案
        table_pattern = r'\|\s*题号\s*\|\s*答案\s*\|'
        table_matches = re.findall(table_pattern, text, re.IGNORECASE)
        if table_matches:
            self.log(f"🔍 发现表格答案格式")
            answer_count += len(table_matches)

        # 判断是否包含答案
        has_answers = answer_count >= 3  # 至少找到3个答案相关模式
        self.log(f"🔍 答案检测结果：发现 {answer_count} 个答案标识，{'包含答案' if has_answers else '不含答案'}")

        return has_answers

    def reset(self):
        """重置"""
        if messagebox.askyesno("确认", "确定要重置吗？所有答题记录将被清除。"):
            self.questions = []
            self.current_index = 0
            self.user_answers = {}
            self.exam_submitted = False
            self.timer_running = False

            self.file_label.config(text="未选择文件", foreground="gray")
            self.status_label.config(text="请选择 PDF 文件开始")
            self.timer_label.config(text="--:--")
            self.progress_label.config(text="答题进度: 0 / 0")

            self.question_listbox.delete(0, tk.END)
            self.question_text.config(state=tk.NORMAL)
            self.question_text.delete(1.0, tk.END)
            self.question_text.config(state=tk.DISABLED)

            for widget in self.options_frame.winfo_children():
                widget.destroy()

            self.prev_btn.config(state=tk.DISABLED)
            self.next_btn.config(state=tk.DISABLED)
            self.submit_btn.config(state=tk.DISABLED)

            self.log("✅ 已重置")


def main():
    root = tk.Tk()
    app = ExamApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
