# EvalGenAITool

一个用于评估生成式 AI 模型的批处理工具，支持文本生成图像、图像生成图像、文本生成视频和图像生成视频等多种生成任务。

## 功能特性

- **多模型支持**：同时测试多个 AI 模型，方便对比效果
- **批量处理**：从 CSV 文件读取提示词，批量生成结果
- **结果保存**：自动保存生成结果的 URL 到 CSV 文件
- **统计分析**：自动统计各模型的成功率
- **日志记录**：详细的日志输出，方便调试和追踪

## 支持的任务类型

1. **Text-to-Image**：文本生成图像
2. **Image-to-Image**：图像生成图像（图像编辑）
3. **Text-to-Video**：文本生成视频
4. **Image-to-Video**：图像生成视频

## 环境要求

- Python 3.7+
- fal.ai API 密钥

## 安装步骤

### 1. 克隆仓库

```bash
git clone https://github.com/Woody112210/EvalGenAITool.git
cd EvalGenAITool
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置 API 密钥

复制示例配置文件并编辑：

```bash
cp config.example.yaml config.yaml
```

编辑 `config.yaml` 文件，将 `YOUR_API_KEY_HERE` 替换为您的实际 fal.ai API 密钥：

```yaml
fal_key: "your-actual-api-key-here"
```

**注意**：`config.yaml` 文件已被添加到 `.gitignore`，不会被提交到 Git 仓库，以保护您的 API 密钥安全。

## 使用方法

### 文本生成图像

```bash
cd scripts
python text_to_image_batch.py
```

输入文件：`prompts/text2image_prompts.csv`  
输出文件：`output/text_to_image_results_YYYYMMDD_HHMMSS.csv`

### 图像生成图像

```bash
cd scripts
python image_to_image_batch.py
```

输入文件：`prompts/image2image_prompts.csv`  
输出文件：`output/image_to_image_results_YYYYMMDD_HHMMSS.csv`

### 文本生成视频

```bash
cd scripts
python text_to_video_batch.py
```

输入文件：`prompts/text2video_prompts.csv`  
输出文件：`output/text_to_video_results_YYYYMMDD_HHMMSS.csv`

### 图像生成视频

```bash
cd scripts
python image_to_video_batch.py
```

输入文件：`prompts/image2video_prompts.csv`  
输出文件：`output/image_to_video_results_YYYYMMDD_HHMMSS.csv`

## 提示词文件格式

### Text-to-Image / Text-to-Video

CSV 文件需包含 `prompt` 列：

```csv
prompt
"A cute cat playing with a ball"
"A beautiful sunset over the ocean"
```

### Image-to-Image / Image-to-Video

CSV 文件需包含 `prompt` 和 `image_path` 列：

```csv
prompt,image_path
"Make it more colorful",images/cat.jpg
"Add snow effect",images/landscape.png
```

## 配置文件说明

`config.yaml` 文件包含以下配置：

- **fal_key**：fal.ai API 密钥
- **text_to_image_models**：文本生成图像模型配置
- **image_to_image_models**：图像生成图像模型配置
- **text_to_video_models**：文本生成视频模型配置
- **image_to_video_models**：图像生成视频模型配置

每个模型配置包含：
- `model_path`：模型在 fal.ai 上的路径
- `params`：额外的模型参数（可选）

## 项目结构

```
EvalGenAITool/
├── config.yaml              # 配置文件（需自行创建，包含 API 密钥）
├── config.example.yaml      # 配置文件示例
├── requirements.txt         # Python 依赖
├── README.md               # 项目说明文档
├── .gitignore              # Git 忽略文件配置
├── scripts/                # 脚本目录
│   ├── utils.py            # 通用工具模块
│   ├── text_to_image_batch.py
│   ├── image_to_image_batch.py
│   ├── text_to_video_batch.py
│   └── image_to_video_batch.py
├── prompts/                # 提示词文件目录
│   ├── text2image_prompts.csv
│   ├── image2image_prompts.csv
│   ├── text2video_prompts.csv
│   └── image2video_prompts.csv
├── images/                 # 输入图像目录
└── output/                 # 输出结果目录
```

## 优化改进

本项目最近进行了以下优化：

1. **代码重构**：提取通用功能到 `utils.py` 模块，减少代码重复
2. **路径处理统一**：使用统一的路径处理方法，支持相对路径和绝对路径
3. **日志系统改进**：添加详细的日志记录，支持不同日志级别
4. **错误处理增强**：改进异常处理和错误提示
5. **类型注解**：添加类型注解，提高代码可读性
6. **配置安全**：将敏感信息移至示例配置，添加 `.gitignore` 保护
7. **文档完善**：添加详细的 README 文档

## 注意事项

- 请确保 API 密钥有足够的配额
- 视频生成任务可能需要较长时间，请耐心等待
- 输出文件会自动添加时间戳，避免覆盖
- 建议先用少量提示词测试，确认配置正确后再批量处理

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题，请在 GitHub 上提交 Issue。
