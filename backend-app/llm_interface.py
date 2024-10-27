# llm_interface.py

from langchain_community.chat_models import ChatOllama, ChatOpenAI
from config import MODEL_NAME
from logging_config import logger

def setup_llm(model_name=MODEL_NAME):
    logger.info(f"Setting up LLM with model name: {model_name}")
    return ChatOllama(model=model_name, temperature=0.2)


def invoke_llm(prompt):
    """Wrapper for LLM invocation with error handling."""
    try:
        llm = setup_llm()  # This function sets up the LLM model instance
        response = llm.invoke(prompt)  # Calls the model to generate the response
        return response.content.strip()  # Strips and returns the content of the response
    except Exception as e:
        logger.error(f"Error invoking LLM: {str(e)}")
        return "Error in generating response from LLM."
