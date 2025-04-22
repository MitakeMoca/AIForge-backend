from ollama import chat


def predict(data):
    # 打开文件以写入
    stream = chat(
        model='deepseek-8b',
        messages=[{'role': 'user', 'content': data}],
        stream=True,
    )

    for chunk in stream:
        content = chunk['message']['content']
        print(content, end='', flush=True)  # 打印到控制台

    print("\n")