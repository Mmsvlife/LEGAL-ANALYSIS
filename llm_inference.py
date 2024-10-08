# llm_interface.py

from langchain_community.chat_models import ChatOllama, ChatOpenAI
from config import MODEL_NAME
from logging_config import logger

def setup_llm(model_name=MODEL_NAME):
    logger.info(f"Setting up LLM with model name: {model_name}")
    # Replace with your actual model setup
    return ChatOllama(model=model_name, temperature=0.2)
    # For OpenAI models, uncomment the following line
    # return ChatOpenAI(model_name=model_name, temperature=0.0)
