from langchain_ollama import ChatOllama
import sys
import io


def predict(data):
    llm = ChatOllama(base_url="http://host.docker.internal:11434", model="deepseek-8b")
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    result = llm.invoke("Who is Moca?")
    print(result.content)
