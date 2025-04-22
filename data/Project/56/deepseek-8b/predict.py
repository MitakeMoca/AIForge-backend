from ollama import chat


def predict(data):
    # 使用非流式方式获取整体输出
    response = chat(
        model='deepseek-8b',
        messages=[{'role': 'user', 'content': data}],
        stream=False
    )

    # 获取整体输出
    content = response['message']['content']

    # 打印到控制台
    print(content)