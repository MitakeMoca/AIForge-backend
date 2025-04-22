import requests


def predict(data):
    # Ollama 服务的 URL
    url = "http://host.docker.internal:11434/api/generate"  # 使用 host.docker.internal 访问宿主机

    # 构造请求数据
    payload = {
        "model": "deepseek-8b",
        "messages": [{"role": "user", "content": data}]
    }

    try:
        # 发送 POST 请求
        response = requests.post(url, json=payload)
        response.raise_for_status()  # 检查请求是否成功

        # 获取响应内容
        result = response.json()
        print(result.get("content"))
    except requests.RequestException as e:
        print("[ERROR] ", e)