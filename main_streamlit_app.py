import os
import time
from typing import Dict, List, Optional
import streamlit as st
from document_processing import (
    load_documents_from_directory,
    load_or_create_vector_store,
    retrieve_and_answer_question,
    load_documents_from_markdown
)
from summarizer import summarize_case
from config import COLLECTION_NAME, PERSIST_DIRECTORY
from logging_config import logger
from testcase import extract_case_metadata
import re

def main():
    # Set app title and sidebar menu
    st.set_page_config(layout="wide")
    st.title("Legal Case Analysis Tool")
    selected_option = st.sidebar.selectbox("Choose an option", ("Ask a question (Q&A)", "Summarize a case"))

    if selected_option == "Ask a question (Q&A)":
        # Load documents and vector store
        document_path = st.text_input("Enter the path to the PDF or markdown document:", "")
        if not document_path:
            st.error("Please enter the path to the document.")
            return

        if document_path.endswith(".md"):
            documents = load_documents_from_markdown(document_path)
        else:
            documents = load_documents_from_directory(document_path)

        vector_store = load_or_create_vector_store([documents])

        # Get user input for the question to ask
        question = st.text_input("Enter your legal question:", "")
        if not question:
            st.error("Please enter a question.")
            return

        # Call retrieve_and_answer_question function to get the answer
        logger.info(f"Asking '{question}'...")
        answer = retrieve_and_answer_question(
            question=question,
            document_path=document_path,
            vector_store=vector_store
        )

        st.success(f"Answer: {answer}")
    elif selected_option == "Summarize a case":

        # Load and preprocess documents
        document_path = st.text_input("Enter the path to the PDF or markdown document:", "")
        if not document_path:
            st.error("Please enter the path to the document.")
            return  # Specify path (Markdown or PDF)
        if document_path.endswith(".md"):
            documents = load_documents_from_markdown(document_path)
        else:
            documents = load_documents_from_directory(document_path)
        vector_store = load_or_create_vector_store(documents)

        # Extract case metadata like date and parties
        logger.info("Extracting case metadata...")
        case_metadata = extract_case_metadata(documents)

        # Summarize the case
        summarized_result = summarize_case(question=f"Generate the complete summary of the document and provide a concise summary of the case and here is the case metadata for your better retrival Metadata : {case_metadata}", documents=documents, vector_store=vector_store)

        st.write("--- Initial Findings ---")
        st.write(summarized_result['initial_findings'])
        st.write("\n--- Follow-up Information ---")
        st.write(summarized_result['followup_info'])
        st.write("\n--- Final Summary ---")
        st.write(summarized_result['final_summary'])
        st.write("\n--- Sources ---")
        for item in summarized_result['structured_context']:
            st.write(f"File: {item['file_name']}, Page: {item['page_number']}")
        st.write("\n--- Additional Info ---")
        st.write(f"Case Metadata: {case_metadata}")

if __name__ == "__main__":
    main()
