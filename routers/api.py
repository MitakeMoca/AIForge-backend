from fastapi import APIRouter
from langchain.chat_models import ChatOpenAI
from models import Model
from utils.ResultGenerator import ResultGenerator

api = APIRouter()

@api.post('/model/{model_id}')
async def api_service(model_id: int, secret_key: str, prompt: str):
    model = await Model.find_by_id(model_id)
    if model.secret_key != secret_key:
        return ResultGenerator.gen_fail_result(message="密钥错误")
    llm = ChatOpenAI(
        model='deepseek-chat',
        openai_api_key='sk-b71092665ded4282aa3ed6b6aab01ae4',
        openai_api_base='https://api.deepseek.com',
        max_tokens=8192,
        temperature=0.0
    )
    response = llm.invoke(prompt).content
    return ResultGenerator.gen_success_result(data=response)