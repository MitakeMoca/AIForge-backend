import subprocess


def predict(data):
    # 构造 Ollama 命令
    command = [
        "ollama",  # Ollama 命令行工具的名称
        "run",  # 假设 `run` 是运行模型的子命令
        "deepseek-8b",  # 模型名称
        data  # 输入数据
    ]

    try:
        # 使用 subprocess.run 执行命令
        # 显式指定 encoding='utf-8'，确保正确处理输出
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', check=True)

        # 捕获标准输出
        if result.stdout:
            output = result.stdout.strip()
            print(output)
        else:
            print("No Result!")
    except subprocess.CalledProcessError as e:
        # 捕获错误信息
        if e.stderr:
            print(e.stderr.strip())
        else:
            print("Model Run Failed!")
    except UnicodeDecodeError as e:
        print(e)
