import requests
import json
import time
from datasets import load_dataset
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import re
import json
from collections import Counter

# 配置模型 API
API_URL = 'http://www.science42.vip:40300/api/openAPI/v1/chat/completions'# 替换为你的API地址
API_KEY = "your_key"  # 替换为你的API密钥
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def call_model_api(prompt):
    """
    调用大模型 API，获取模型回答。
    Args:
        prompt (str): 输入提示词
    Returns:
        str: 模型生成的回答
    """
    data = {
        "context": ["你是一位优秀的科学家"],  # 将 context 修改为一个列表
        "question": prompt,  # 问题内容
        "stream": False
    }

    # 调用 API 获取模型回答
    response = requests.post(API_URL, headers=HEADERS, json=data, verify=False)
    
    if response.status_code == 200:
        try:
            response_data = response.json()  # 将响应内容解析为 JSON 格式
            # 访问返回数据中的内容
            if "choices" in response_data and isinstance(response_data["choices"], list):
                model_answer = response_data["choices"][0]["message"]  # 提取模型生成的文本
                return model_answer
            else:
                raise Exception("API 返回的格式不正确。")
        except Exception as e:
            raise Exception(f"解析 JSON 响应时出错: {e}")
    else:
        raise Exception(f"API Error: {response.status_code}, {response.text}")

# 读取本地的 cmath.jsonl 文件
input_file = load_dataset("weitianwen/cmath", split="test")
output_file = "/path/to/your/output.jsonl"

def process_sample(sample):
    """
    处理数据集中的每个样本，获取模型的回答并保存结果
    """
    input_text = sample["question"]  # 问题
    true_answer = sample["golden"]  # 正确答案
    grade=sample['grade']

    # 构造 Prompt
    prompt = f"请你根据以下数学问题，逐步分析并给出答案。问题：{input_text}。请按照以下格式作答：给出分析过程，如“首先xxx；其次xxx；最后xxx”；最后给出总结答案，格式为 “$$ 3 $$”，在此之后不再有任何输出"

    try:
        # 调用 API 获取模型回答
        response = call_model_api(prompt).strip()  # 获取模型的答案
        print(f"问题: {input_text}\n模型回答: {response}\n")

        # 确保对 response 和 true_answer 进行 UTF-8 编码
        encoded_response = response.encode('utf-8').decode('utf-8')
        encoded_true_answer = true_answer.encode('utf-8').decode('utf-8') if isinstance(true_answer, str) else true_answer
        print(encoded_response)

        # 检查 golden 和 response 是否相等
        is_correct = (encoded_true_answer.strip() == extract_last_dollars_content(encoded_response).strip())

        # 使用 UTF-8 编码将数据写入文件，确保存储中文字符而不是 Unicode 转义字符
        if is_correct:
            with open(output_file, "a", encoding="utf-8") as f:  # 使用 "a" 模式以文本模式写入文件，并指定 UTF-8 编码
                f.write(json.dumps({
                    "golden": encoded_true_answer,
                    "response": extract_last_dollars_content(encoded_response),
                    "is_correct": is_correct,  # 添加是否相等的字段
                    'grade':grade
                }, ensure_ascii=False) + "\n")
        else:
            # 如果 is_correct 为 False，进行最多 3 次尝试
            attempts = 0
            while attempts < 3:
                print(f"第 {attempts + 1} 次尝试...")
                response = call_model_api(prompt).strip()
                # 重新判断是否正确
                encoded_response = response.encode('utf-8').decode('utf-8')
                is_correct = (encoded_true_answer.strip() == extract_last_dollars_content(encoded_response).strip())

                if is_correct:
                    print("模型预测正确，跳出循环。")
                    break  # 如果预测正确，跳出循环

                attempts += 1

            # 如果三次都失败，才将 sample 存储到文件
            if not is_correct:
                print(f"三次尝试都未通过，问题仍未解答正确: {input_text}")
                # 将整个 sample 数据存入 False_data.jsonl 文件
                sample['response']=encoded_response
                with open('/path/to/your/False_data.jsonl', "a", encoding="utf-8") as f:
                    f.write(json.dumps(sample, ensure_ascii=False) + "\n")

        time.sleep(1)  # 控制请求速率，避免超出 API 限制
        
    except Exception as e:
        print(f"API 调用失败: {e}")
        # 将错误信息作为一部分存入 output_file
        with open('/path/to/your/error_file.jsonl', "a", encoding="utf-8") as f:
            # 错误信息包含在 JSON 记录中
            f.write(json.dumps({"sample": sample, "error":"error ,"+str(e)}, ensure_ascii=False) + "\n")

def extract_last_dollars_content(text):
    """
    从文本中提取最后一对 $$ 框住的内容
    """
    # 使用正则表达式匹配所有 $$ 中的内容
    matches = re.findall(r"\$\$(.*?)\$\$", text)
    
    # 返回最后一个匹配的内容，如果有的话
    if matches:
        return matches[-1].strip()
    return None


# 从本地 JSONL 文件读取数据并处理
def read_and_process_file():
    samples = [sample for sample in input_file]

    with ThreadPoolExecutor(max_workers=6) as executor:
        # 使用 tqdm 包装 samples，显示进度条
        for _ in tqdm(executor.map(process_sample, samples), total=len(samples), desc="cmath_2", unit="item"):
            pass

# 执行处理函数
read_and_process_file()

# 创建一个 Counter 用于统计 grade 的不同值
grade_counts_true = Counter()

# 读取文件并统计 'grade' 字段的不同值
with open(file_path, 'r', encoding='utf-8') as f:
    for line in f:
        try:
            # 解析每行的 JSON 数据
            data = json.loads(line.strip())
            # 获取 'grade' 字段并更新计数
            grade_value = data.get('grade')
            grade_counts[grade_value] += 1
        except json.JSONDecodeError:
            print(f"Error decoding line: {line}")

# 输出不同值的数量
print("grade value counts:")
list_1=[]
for value, count in grade_counts.items():
    list_1.append(count)
    print(f"Value {value}: {count} occurrences")
print(list_1)