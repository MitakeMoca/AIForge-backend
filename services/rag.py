from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from IPython.display import display, Markdown
from langchain.indexes import VectorstoreIndexCreator
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import torch
import os
import warnings
import pickle

warnings.filterwarnings("ignore")
loaders = []


def update_loaders(folder_path, save_path=None):
    pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]
    for pdf_file in pdf_files:
        loader = PyPDFLoader(pdf_file)
        loaders.append(loader)

    if save_path:
        with open(save_path, 'wb') as f:
            pickle.dump(loaders, f)
    return loaders


class RAG:
    def __init__(self):
        # 加载保存的 loaders 文件
        print("init")
        loader_files = [
            "D:\\毕设\\AIForge-backend\\data\\paper\\Garbage collection",
            "D:\\毕设\\AIForge-backend\\data\\paper\\Allocation deallocation strategies",
            "D:\\毕设\\AIForge-backend\\data\\paper\\Main Memory",
            "D:\\毕设\\AIForge-backend\\data\\paper\\Memory management"
        ]
        for folder_path in loader_files:
            # 尝试加载保存的 loaders 文件
            save_path = os.path.join(folder_path, "loaders.pkl")
            if os.path.exists(save_path):
                with open(save_path, 'rb') as f:
                    loader_batch = pickle.load(f)
                    loaders.extend(loader_batch)
            else:
                # 如果保存的文件不存在，则重新生成并保存
                loader_batch = update_loaders(folder_path, save_path)
                loaders.extend(loader_batch)
        print("step 0")./
        self.model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
        self.model_name = "BAAI/bge-small-en"
        self.encode_kwargs = {"normalize_embeddings": True}
        self.embeddings = HuggingFaceBgeEmbeddings(
            model_name=self.model_name, model_kwargs=self.model_kwargs, encode_kwargs=self.encode_kwargs
        )
        print("step 1")
        # 创建向量存储需要指定三件事：向量存储类、embedding、包含一个或多个加载器的列表
        self.index = VectorstoreIndexCreator(
            vectorstore_cls=DocArrayInMemorySearch,
            embedding=self.embeddings
        ).from_loaders(loaders)
        print("step 2")
        # 必须再传个 llm
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            openai_api_key='your-api-key',
            openai_api_base='https://api.deepseek.com',
            max_tokens=8192,
            temperature=0.0
        )
        print("step 3")

    def query(self, ques: str):
        # 这里的 index 是一个 RetrievalQA 对象
        query = f"请不要透露出我对你使用了 RAG，我下面将会问你一个关于 Garbage collection 的问题，你也可以辅以相关领域（诸如 Main Memory、Memory management、Memory management）的知识来作答，请不要说任何多余的话，回答问题就好：{ques}"
        print("query")
        response = self.index.query(query, llm=self.llm)
        return response


rag = RAG()
resp = rag.query("并行程序中的垃圾回收是如何工作的？")
print(resp)
