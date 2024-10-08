from llm_interface import setup_llm
from prompts import (
    refine_question_prompt,
    extract_key_case_info,
    followup_case_questions,
    consolidate_and_summarize_case
)
from utils import prepare_context, format_context
from retrieval import get_hybrid_retriever
from logging_config import logger

# Wrapper for LLM invocation with error handling
def invoke_llm(prompt):
    """Wrapper for LLM invocation with error handling."""
    try:
        llm = setup_llm()
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        logger.error(f"Error invoking LLM: {str(e)}")
        return "Error in generating response from LLM."

# Function to truncate context if too long
def truncate_context(context, max_tokens=2000):
    """Truncate context to fit within a specific token limit."""
    words = context.split()
    if len(words) > max_tokens:
        truncated_context = ' '.join(words[:max_tokens])
        logger.warning(f"Context was too long, truncated to {max_tokens} tokens.")
        return truncated_context
    return context

# Function to handle cases where no relevant data is found
def handle_insufficient_data(data):
    """Handle cases where no relevant data is retrieved."""
    if not data:
        logger.warning("No relevant data found.")
        return "No relevant data found for the given question."
    return data

# Refining the user's question using LLM
def refine_question(question):
    logger.info("Refining user question.")
    prompt = refine_question_prompt().format(user_question=question)
    refined_question = invoke_llm(prompt)
    return refined_question

# Summarizing the legal case
def summarize_case(question, documents, vector_store):
    """
    Summarize the legal case based on the provided question and documents.
    Works for various legal cases, including civil, criminal, regulatory, and more.

    For civil cases, ensure extraction of contract disputes, negligence claims, etc.
    For criminal cases, include charges, indictments, and possible penalties.
    For administrative/regulatory cases, include citations to relevant laws or codes.
    """
    logger.info("Starting case summarization process.")
    retriever = get_hybrid_retriever(documents, vector_store)

    # Step 1: Retrieve relevant documents based on the initial question
    relevant_docs = retriever.get_relevant_documents(question)
    structured_context = prepare_context(relevant_docs)
    structured_context = handle_insufficient_data(structured_context)
    formatted_context = format_context(structured_context)
    formatted_context = truncate_context(formatted_context)

    # Step 2: Extract Key Case Information
    prompt = extract_key_case_info().format(context=formatted_context)
    initial_findings = invoke_llm(prompt)

    # Step 3: Follow-up Questions and Additional Search
    additional_docs = retriever.get_relevant_documents(initial_findings)
    additional_context = prepare_context(additional_docs)
    additional_context = handle_insufficient_data(additional_context)
    formatted_additional_context = format_context(additional_context)
    formatted_additional_context = truncate_context(formatted_additional_context)

    followup_prompt = followup_case_questions().format(
        initial_context=initial_findings,
        additional_context=formatted_additional_context
    )
    followup_info = invoke_llm(followup_prompt)

    # Step 4: Consolidate Findings and Draft Summary
    consolidate_prompt = consolidate_and_summarize_case().format(
        initial_findings=initial_findings,
        followup_info=followup_info
    )
    final_summary = invoke_llm(consolidate_prompt)

    return {
        "initial_findings": initial_findings,
        "followup_info": followup_info,
        "final_summary": final_summary,
        "structured_context": structured_context
    }
