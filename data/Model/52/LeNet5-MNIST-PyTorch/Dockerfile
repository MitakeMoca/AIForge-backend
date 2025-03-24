# 选择适合的基础镜像，比如 PyTorch 官方的
FROM python:3.10

# 工作目录
WORKDIR /app

# 把所有代码复制进去
COPY . .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 默认运行命令（可改）
CMD ["python", "train.py"]
