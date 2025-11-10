from flask import Flask, request, jsonify
from flask_cors import CORS
from utils import call_llm
import json

app = Flask(__name__)
# 允许所有来源的跨域请求，这在本地开发中很方便
CORS(app)

@app.route('/parse', methods=['POST'])
def parse_exam():
    """
    接收从前端发送的PDF文本，调用LLM进行解析，并返回结构化的题目数据。
    """
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({"error": "请求中缺少文本内容"}), 400

    pdf_text = data['text']
    text_length = len(pdf_text)
    
    print(f"\n{'='*60}")
    print(f"[解析请求] 接收到文本，长度: {text_length} 字符")
    
    # 限制文本长度以提高响应速度
    max_length = 15000  # 降低到15000字符，约10-15页
    if text_length > max_length:
        pdf_text = pdf_text[:max_length]
        print(f"[提示] 文本过长，已截取前 {max_length} 字符进行解析")
    
    # 优化后的提示词 - 更简洁明确
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
{pdf_text}
---

请返回JSON数组："""

    messages = [{"role": "user", "content": prompt}]

    try:
        print("[处理中] 正在调用 DeepSeek API...")
        import time
        start_time = time.time()
        
        # 调用LLM
        llm_response_str = call_llm(messages)
        
        elapsed = time.time() - start_time
        print(f"[完成] DeepSeek API 响应时间: {elapsed:.1f} 秒")
        
        # 尝试解析LLM返回的JSON字符串
        # 清理可能的markdown标记
        cleaned_response = llm_response_str.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.startswith('```'):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        # 优先截取首尾中括号内的数组，去掉多余前后文
        array_start = llm_response_str.find('[')
        array_end = llm_response_str.rfind(']')
        candidate = cleaned_response
        if array_start != -1 and array_end != -1 and array_end > array_start:
            candidate = llm_response_str[array_start:array_end+1].strip()

        # 先尝试直接解析
        try:
            questions = json.loads(candidate)
        except json.JSONDecodeError as e1:
            # 最小化修复：去除尾随逗号、将单引号替换为双引号、规范化弯引号
            import re as _re
            minimally_fixed = _re.sub(r',\s*([}\]])', r'\1', cleaned_response)
            minimally_fixed = (minimally_fixed
                               .replace("'", '"')
                               .replace("“", '"').replace("”", '"')
                               .replace("‘", '"').replace("’", '"')
                               .replace("`", ''))
            try:
                questions = json.loads(minimally_fixed)
                print("[提示] 通过最小化修复成功解析 JSON")
            except Exception as e2:
                # 备用提取：截取首尾中括号内的内容再次尝试
                start, end = llm_response_str.find('['), llm_response_str.rfind(']')
                if start != -1 and end != -1 and end > start:
                    sliced = llm_response_str[start:end+1]
                    sliced = (_re.sub(r',\s*([}\]])', r'\1', sliced)
                              .replace("'", '"')
                              .replace("“", '"').replace("”", '"')
                              .replace("‘", '"').replace("’", '"')
                              .replace("`", ''))
                    try:
                        questions = json.loads(sliced)
                        print("[提示] 使用备用切片解析成功")
                    except Exception as e3:
                        # 最后尝试：请求模型进行严格 JSON 重写
                        print("[提示] 尝试让 AI 重写为严格 JSON…")
                        repair_prompt = (
                            "请将下面的内容严格转换为有效的 JSON 数组，"
                            "只输出 JSON 数组本身，不要任何解释/注释/代码块标记。\n\n内容如下：\n---\n" + llm_response_str + "\n---"
                        )
                        repair = call_llm([{ "role": "user", "content": repair_prompt }])
                        repaired = repair.strip().strip('`')
                        questions = json.loads(repaired)
                        print("[提示] 通过 AI 重写成功解析 JSON")
                else:
                    raise e1

        print(f"[成功] 解析出 {len(questions)} 道题目")
        print(f"{'='*60}\n")
        return jsonify(questions)

    except json.JSONDecodeError as e:
        print(f"[错误] JSON解析失败: {e}")
        print(f"[原始响应] {llm_response_str[:500]}...")
        # 如果LLM没有返回有效的JSON，则返回错误
        return jsonify({"error": "AI模型未能返回有效的JSON格式", "raw_response": llm_response_str[:1000]}), 500
    except Exception as e:
        print(f"[错误] 调用LLM时发生错误: {str(e)}")
        # 处理其他可能的API调用错误
        return jsonify({"error": f"调用LLM时发生错误: {str(e)}"}), 500

if __name__ == '__main__':
    print("启动模拟考试解析服务器...")
    print("请在浏览器中打开 Exam.html 文件。")
    print("服务器地址: http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
