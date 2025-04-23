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

warnings.filterwarnings("ignore")
loaders = []
folder_path = "D:\\毕设\\AIForge-backend\\data\\paper\\Memory management"
pdf_files = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if file.endswith(".pdf")]
# pdf_files = [folder_path]
print(pdf_files)
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    loaders.append(loader)

model_kwargs = {"device": "cuda" if torch.cuda.is_available() else "cpu"}
model_name = "BAAI/bge-small-en"
encode_kwargs = {"normalize_embeddings": True}
embeddings = HuggingFaceBgeEmbeddings(
    model_name=model_name, model_kwargs=model_kwargs, encode_kwargs=encode_kwargs
)

# 创建向量存储需要指定三件事：向量存储类、embedding、包含一个或多个加载器的列表
for i in range(10):
    print(i)
    index = VectorstoreIndexCreator(
        vectorstore_cls=DocArrayInMemorySearch,
        embedding=embeddings
    ).from_loaders([loaders[i]])

# 必须再传个 llm
llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key='sk-b71092665ded4282aa3ed6b6aab01ae4',
    openai_api_base='https://api.deepseek.com',
    max_tokens=8192,
    temperature=0.0
)

query = "请给我介绍一下你知道的内存回收的前沿话题"

response = index.query(query, llm=llm)
print(response)
print(Markdown(response))
display(Markdown(response))
