# 数据集处理与模型测试脚本

## 简介

该脚本旨在从 [CMath 数据集](https://huggingface.co/datasets/weitianwen/cmath) 中读取测试数据和验证数据，调用模型 API 生成答案，并评估模型在数据集上的表现。最终，脚本会将测试结果保存为 JSONL 文件。

---

## 主要功能

1. **加载 CMath 数据集**：从 Hugging Face 加载测试集和验证集，并合并为一个完整的数据集。
2. **调用大模型 API**：通过自定义的 `call_model_api` 函数向模型发送问题并获取答案。
3. **解析与评估模型回答**：根据正确答案判断模型回答是否正确。
4. **错误处理与多次尝试**：对于错误的回答，进行最多三次重试。
5. **结果存储与统计**：将所有测试样本的结果保存为 JSONL 文件，并计算模型的最终准确率。

---

## 文件结构

```
.
├── test_code_Cmath.py          # 主脚本
└── test_results.jsonl # 测试结果文件（脚本生成）
```

---

## 环境要求

1. **Python**: 版本 ≥ 3.8
2. **依赖库**:
   - `requests`
   - `json`
   - `time`
   - `datasets`
   - `tqdm`
   - `concurrent.futures`
   - `re`

---

## 使用说明

### 1. 设置模型 API

将脚本中的 `API_URL` 和 `API_KEY` 替换为你的实际模型 API 地址和密钥。

```python
API_URL = 'http://www.science42.vip:40300/api/openAPI/v1/chat/completions'  # 替换为你的API地址
API_KEY = "your-key"  # 替换为你的API密钥
```

### 2. 数据集准备

脚本会自动从 Hugging Face 加载 `CMath` 数据集的 `test` 和 `validation` 部分，并合并为一个完整的数据集。

---

### 3. 运行脚本

直接运行脚本：

```bash
python test_code_Cmath.py
```

运行后，脚本会：
- 调用 API 获取每个样本的模型回答。
- 根据正确答案判断模型回答的正确性。
- 将测试结果保存至 `test_results.jsonl` 文件。

---

### 4. 测试结果文件格式

生成的 `test_results.jsonl` 文件每行包含一个测试样本的结果，格式如下：

```json
{
    "golden": "正确答案",
    "response": "模型生成的回答",
    "is_correct": true,  # 是否正确
    "grade": "样本的年级分类",
    "error": "错误信息（仅当发生错误时存在）"
}
```

---

### 5. 函数说明

#### `call_model_api(prompt)`
- **功能**: 调用指定的模型 API，向模型发送问题，并返回生成的答案。
- **参数**:
  - `prompt`: 问题的完整文本。
- **返回**:
  - 模型的回答字符串。

#### `extract_last_dollars_content(text)`
- **功能**: 提取回答中最后一对 `$$` 包含的内容。
- **参数**:
  - `text`: 模型回答的完整字符串。
- **返回**:
  - 最后一对 `$$` 中的内容。

#### `process_sample(sample)`
- **功能**: 处理单个数据样本，调用模型 API 获取回答，判断是否正确，并返回结果。
- **参数**:
  - `sample`: 数据样本，包含问题、正确答案和分类信息。
- **返回**:
  - 处理结果字典。

#### `save_results_to_file(results, output_file)`
- **功能**: 将所有样本的测试结果保存到 JSONL 文件。
- **参数**:
  - `results`: 包含所有样本处理结果的列表。
  - `output_file`: 保存的文件路径。

#### `read_and_process_dataset(dataset, output_file)`
- **功能**: 并行处理数据集中的样本，并保存结果到文件。
- **参数**:
  - `dataset`: 要处理的数据集。
  - `output_file`: 结果保存路径。

---

## 测试结果

脚本会输出以下信息：
1. **准确率**：例如 `最终准确率: 85.00%`。
2. **错误的样本**：在每次尝试中打印错误信息，便于调试。

---

## 注意事项

1. **API 限制**：
   - 如果 API 调用次数受限，建议调整 `ThreadPoolExecutor` 的线程数。
   - 增加 `time.sleep` 的延迟时间以减少请求频率。

2. **输出文件路径**：
   - 默认文件名为 `test_results.jsonl`，可以根据需要修改保存路径。

3. **自定义数据集**：
   - 如果需要测试其他数据集，可将 `load_dataset` 替换为本地加载逻辑。

---

## 示例运行

运行脚本后，输出如下：

```plaintext
Processing Samples: 100%|███████████████████████████████████| 100/100 [01:30<00:00,  1.10item/s]
最终准确率: 85.00%
```

`test_results.jsonl` 文件示例：

```json
{"golden": "正确答案", "response": "模型回答", "is_correct": true, "grade": "Grade 1"}
{"golden": "正确答案", "response": "错误回答", "is_correct": false, "grade": "Grade 2", "error": "Incorrect after 3 attempts"}
```

---

通过该 README，你可以快速了解如何使用脚本进行数据集测试并分析结果。

