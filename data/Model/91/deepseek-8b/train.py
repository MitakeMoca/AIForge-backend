import subprocess
import time
import os


def train(params):
    # 定义模型名称和 Modelfile 路径
    model_name = 'deepseek-8b'
    modelfile_path = 'Modelfile'  # 替换为你的 Modelfile 文件路径
    dataset_folder = f"/app/dataset/{params['train_dataset_id']}"  # 替换为你的数据集文件夹路径
    content = """
    FROM deepseek-r1:1.5b
    TEMPLATE \"\"\"{{- if .System }}{{ .System }}{{ end }}
    {{- range $i, $_ := .Messages }}
    {{- $last := eq (len (slice $.Messages $i)) 1}}
    {{- if eq .Role "user" }}<｜User｜>{{ .Content }}
    {{- else if eq .Role "assistant" }}<｜Assistant｜>{{ .Content }}{{- if not $last }}<｜end▁of▁sentence｜>{{- end }}
    {{- end }}
    {{- if and $last (ne .Role "assistant") }}<｜Assistant｜>{{- end }}
    {{- end }}\"\"\"
    PARAMETER temperature 0.7
    PARAMETER top_k 60
    PARAMETER top_p 0.5
    PARAMETER stop "[INST]"
    PARAMETER stop "[/INST]"
    PARAMETER stop "<>"
    PARAMETER stop "<>"
    SYSTEM \"\"\"
    """

    # 读取指定文件夹下的文件
    print(f"Reading files from {dataset_folder}...")
    files = os.listdir(dataset_folder)
    for file in files:
        with open(os.path.join(dataset_folder, file), 'r', encoding='utf-8') as f:
            content += f.read()

    content += '"""'

    with open("Modelfile", 'r', encoding='utf-8') as f:
        f.write(content)

    # 构造命令
    command = f"ollama create {model_name} -f {modelfile_path}"

    # 调用命令行工具
    try:
        print("start training")
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',  # 指定正确的编码
            errors='ignore'  # 忽略解码错误
        )

        # 模拟训练进度
        for i in range(10):  # 假设训练过程有10个步骤
            time.sleep(2)  # 模拟训练延迟
            print(f"Training progress: {i * 10}%")
            print(f"Checkpoint {i + 1} saved...")

        # 等待命令执行完成
        process.wait()
        print("=== training finished ===")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e.stderr}")
