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

## 目录说明

```
ai_reading/
├── app.py           # 网站主程序（路由写在这里）
├── requirements.txt # 第三方库列表
├── templates/       # HTML 页面
├── static/          # CSS、图片等静态文件
└── .gitignore       # 告诉 Git 哪些文件不要提交
```

## Git 常用命令

```bash
git status              # 查看改了哪些文件
git add .               # 暂存所有改动
git commit -m "说明"    # 提交一次版本
git log --oneline       # 查看提交历史
```
