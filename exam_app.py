"""
PDF 试题模拟考试器 - Tkinter 桌面版
支持本地解析和 AI 解析（DeepSeek）
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
import json
import re
from datetime import datetime, timedelta
import threading
from utils import call_llm


class ExamApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF 试题模拟考试器")
        self.root.geometry("1000x700")
        
        # 数据
        self.questions = []
        self.current_index = 0
        self.user_answers = {}
        self.pdf_text = ""
        self.exam_submitted = False
        self.timer_running = False
        self.time_remaining = 0
        
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
        ttk.Button(control_frame, text="🚀 本地解析（快速）", command=self.parse_local).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="🤖 AI解析（推荐）", command=self.parse_ai).pack(side=tk.LEFT, padx=5)
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
        """添加日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update()
        
    def select_pdf(self):
        """选择 PDF 文件"""
        filename = filedialog.askopenfilename(
            title="选择 PDF 文件",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.pdf_path = filename
            import os
            self.file_label.config(text=os.path.basename(filename), foreground="black")
            self.log(f"已选择文件: {os.path.basename(filename)}")
            self.status_label.config(text="已选择文件，请点击解析按钮")
            
    def extract_pdf_text(self, pdf_path):
        """提取 PDF 文本"""
        self.log("正在提取 PDF 文本...")
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                self.log(f"PDF 共 {num_pages} 页")
                
                text = ""
                for i in range(num_pages):
                    page = pdf_reader.pages[i]
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    self.log(f"已提取第 {i+1}/{num_pages} 页")
                
                self.pdf_text = text
                self.log(f"提取完成，共 {len(text)} 字符")
                return text
        except Exception as e:
            self.log(f"❌ PDF 提取失败: {e}")
            messagebox.showerror("错误", f"PDF 提取失败: {e}")
            return None
            
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
            
            # 提取选项
            option_pattern = r'([A-D])\s*[、.．]([^A-D]+?)(?=[A-D]\s*[、.．]|参考答案|答案|解析|$)'
            options = {}
            
            for opt_match in re.finditer(option_pattern, q_content):
                opt_key = opt_match.group(1)
                opt_text = opt_match.group(2).strip()
                if len(opt_text) > 0 and len(opt_text) < 500:
                    options[opt_key] = opt_text
            
            if len(options) >= 2:
                # 提取题干
                first_option_pos = q_content.find('A')
                question_text = q_content[:first_option_pos].strip() if first_option_pos > 0 else q_content[:100]
                
                questions.append({
                    'id': q_id,
                    'text': question_text,
                    'options': options,
                    'answer': answers.get(q_id)
                })
        
        self.log(f"✅ 本地解析完成，共 {len(questions)} 道题")
        return questions
        
    def parse_ai(self):
        """AI 解析"""
        if not hasattr(self, 'pdf_path'):
            messagebox.showwarning("提示", "请先选择 PDF 文件！")
            return
            
        self.status_label.config(text="AI 正在解析（预计 1-3 分钟）...")
        self.progress.start()
        self.log("⏳ 开始 AI 解析，请耐心等待...")
        
        def parse():
            try:
                text = self.extract_pdf_text(self.pdf_path)
                if not text:
                    return
                
                # 限制文本长度
                max_len = 15000
                if len(text) > max_len:
                    text = text[:max_len]
                    self.log(f"文本过长，截取前 {max_len} 字符")
                
                self.log("正在调用 DeepSeek API...")
                
                prompt = f"""请解析以下考试题目文本，提取所有题目并返回JSON数组。

要求：
1. 每道题包含: "id"(题号), "text"(题干), "options"(选项对象), "answer"(正确答案字母或null)
2. 只返回纯JSON数组，不要任何其他文字
3. 如果找不到答案，设置 "answer": null
4. 确保JSON格式正确

示例格式：
[{{"id": "1", "text": "题目内容", "options": {{"A": "选项A", "B": "选项B", "C": "选项C", "D": "选项D"}}, "answer": "A"}}]

文本内容：
---
{text}
---

请返回JSON数组："""

                messages = [{"role": "user", "content": prompt}]
                response = call_llm(messages)
                
                self.log("DeepSeek 返回成功，正在解析...")
                
                # 清理响应
                cleaned = response.strip()
                if cleaned.startswith('```json'):
                    cleaned = cleaned[7:]
                if cleaned.startswith('```'):
                    cleaned = cleaned[3:]
                if cleaned.endswith('```'):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                questions = json.loads(cleaned)
                self.log(f"✅ AI 解析成功，共 {len(questions)} 道题")
                
                self.root.after(0, self.load_questions, questions)
                
            except Exception as e:
                self.log(f"❌ AI 解析失败: {e}")
                self.root.after(0, messagebox.showerror, "错误", f"AI 解析失败: {e}")
            finally:
                self.root.after(0, self.progress.stop)
                
        threading.Thread(target=parse, daemon=True).start()
        
    def load_questions(self, questions):
        """加载题目"""
        if not questions or len(questions) == 0:
            messagebox.showwarning("提示", "未能解析出题目，请检查 PDF 格式")
            self.status_label.config(text="解析失败")
            return
            
        self.questions = questions
        self.current_index = 0
        self.user_answers = {}
        self.exam_submitted = False
        
        self.status_label.config(text=f"✅ 成功加载 {len(questions)} 道题目")
        
        # 更新题目列表
        self.question_listbox.delete(0, tk.END)
        for i, q in enumerate(questions, 1):
            self.question_listbox.insert(tk.END, f"{i}. 第 {q['id']} 题")
        
        # 启用按钮
        self.prev_btn.config(state=tk.NORMAL)
        self.next_btn.config(state=tk.NORMAL)
        self.submit_btn.config(state=tk.NORMAL)
        
        # 显示第一题
        self.show_question(0)
        
        # 开始计时
        self.start_timer()
        
    def show_question(self, index):
        """显示题目"""
        if index < 0 or index >= len(self.questions):
            return
            
        self.current_index = index
        q = self.questions[index]
        
        # 更新题目信息
        self.question_info_label.config(
            text=f"第 {index + 1} 题 / 共 {len(self.questions)} 题（原题号 {q['id']}）"
        )
        
        # 显示题目文本
        self.question_text.delete(1.0, tk.END)
        self.question_text.insert(1.0, q['text'])
        self.question_text.config(state=tk.DISABLED)
        
        # 清空选项
        for widget in self.options_frame.winfo_children():
            widget.destroy()
        self.option_buttons = []
        
        # 显示选项
        self.selected_option.set(self.user_answers.get(q['id'], ''))
        
        for key in sorted(q['options'].keys()):
            rb = ttk.Radiobutton(
                self.options_frame,
                text=f"{key}. {q['options'][key]}",
                variable=self.selected_option,
                value=key,
                command=lambda k=key: self.select_answer(k)
            )
            rb.pack(anchor=tk.W, pady=2)
            self.option_buttons.append(rb)
        
        # 如果已提交，显示答案
        if self.exam_submitted and q.get('answer'):
            answer_label = ttk.Label(
                self.options_frame,
                text=f"✓ 正确答案: {q['answer']}",
                foreground="green",
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
        if self.current_index > 0:
            self.show_question(self.current_index - 1)
            
    def next_question(self):
        """下一题"""
        if self.current_index < len(self.questions) - 1:
            self.show_question(self.current_index + 1)
            
    def on_question_select(self, event):
        """题目列表选择"""
        selection = self.question_listbox.curselection()
        if selection:
            self.show_question(selection[0])
            
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
