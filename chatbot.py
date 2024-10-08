# chatbot.py

from llm_interface import setup_llm
from prompts import qa_prompt
from utils import prepare_context, format_context
from retrieval import get_hybrid_retriever
from logging_config import logger

def answer_question(question, documents, vector_store):
    logger.info("Answering user question through chatbot.")
    retriever = get_hybrid_retriever(documents, vector_store)
    relevant_docs = retriever.get_relevant_documents(question)
    structured_context = prepare_context(relevant_docs)
    formatted_context = format_context(structured_context)

    llm = setup_llm()
    prompt = qa_prompt().format(user_question=question, context=formatted_context)
    answer = llm.invoke(prompt)

    return {
        "answer": answer.content,
        "structured_context": structured_context
    }
