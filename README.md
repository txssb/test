# AI Reading

一个简单的 Python Web 项目（Flask）。

## 环境要求

- Python 3.10 或更高版本
- Git

## 第一次运行

在项目根目录打开终端，依次执行：

```bash
# 1. 创建虚拟环境
python -m venv .venv

# 2. 激活虚拟环境（Windows PowerShell）
.venv\Scripts\Activate.ps1

# 3. 安装依赖
pip install -r requirements.txt

# 4. 启动网站
python app.py
```

浏览器访问：<http://127.0.0.1:5000>

按 `Ctrl + C` 可停止服务。

## 配置 AI（首次使用必做）

```bash
copy .env.example .env
```

编辑 `.env`，填入你的 API 密钥和模型信息：

| 变量 | 说明 |
|------|------|
| `AI_API_KEY` | API 密钥（必填） |
| `AI_BASE_URL` | 接口地址，OpenAI 默认 `https://api.openai.com/v1` |
| `AI_MODEL` | 模型名，如 `gpt-4o-mini` |

国内大模型（DeepSeek、通义等）一般也兼容此格式，按官方文档填写 `AI_BASE_URL` 和 `AI_MODEL` 即可。

## 功能

- **上传 TXT**：`/upload` 页面上传文本
- **历史记录**：`/history` 查看历史上传，可恢复为当前文本
- **AI 分析**：`/analyze` 栏目编写提示词，控制 AI 如何处理文本
- **接口**：`GET /api/text`、`GET /api/history`、`GET /api/analysis`

## 目录说明

```
ai_reading/
├── app.py            # 路由入口
├── text_store.py     # 当前文本读写
├── history_store.py  # 上传历史记录
├── analysis_store.py # AI 分析结果读写
├── ai_service.py     # 调用 AI API
├── .env.example      # 配置模板（复制为 .env）
├── templates/        # HTML 页面
├── static/           # CSS
└── data/             # 文本与分析结果（不提交 Git）
```

## Git 常用命令

```bash
git status              # 查看改了哪些文件
git add .               # 暂存所有改动
git commit -m "说明"    # 提交一次版本
git log --oneline       # 查看提交历史
```
