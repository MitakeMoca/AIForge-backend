from langchain_ollama import ChatOllama


def predict(data):
    llm = ChatOllama(base_url="http://host.docker.internal:11434", model="deepseek-8b")

    result = llm.invoke("Who is Moca?")
    print(result.content)
