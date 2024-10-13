# chatbot.py

from llm_interface import setup_llm
from prompts import qa_prompt
from utils import prepare_context, format_context
from retrieval import get_hybrid_retriever
from logging_config import logger
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.agents import Agent

def answer_question(question, documents, vector_store):
    
    logger.info("Answering user question through chatbot.")
    retriever = get_hybrid_retriever(documents, vector_store)
    llm = setup_llm()

    new_retriever = MultiQueryRetriever.from_llm(retriever=retriever, llm=llm)
    
    relevant_docs = new_retriever.invoke(question)
    print("relevant docs: ", relevant_docs)

    # Ensure that the relevant documents are grounded and relevant to the question
    if not relevant_docs:
        logger.warning("No relevant documents found for the question.")
        return {
            "answer": "I'm sorry, I couldn't find any relevant information.",
            "structured_context": None
        }

    structured_context = prepare_context(relevant_docs)
    formatted_context = format_context(structured_context)

    # Include the formatted context in the prompt to ensure grounding
    prompt = qa_prompt().format(user_question=question, context=formatted_context)
    answer = llm.invoke(prompt)

    return {
        "answer": answer.content,
        "structured_context": structured_context
    }
