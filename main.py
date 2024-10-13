# main.py

from document_processing import (
    load_documents_from_directory,
    load_documents_from_markdown
)
from retrieval import load_or_create_vector_store
from summarizer import refine_question, summarize_case
from chatbot import answer_question
from config import COLLECTION_NAME, PERSIST_DIRECTORY
from logging_config import logger

def main():
    document_path = 'docs/law-data/case2'  # Specify path (Markdown or PDF)

    # Load and preprocess documents
    if document_path.endswith('.md'):
        documents = load_documents_from_markdown(document_path)
    else:
        documents = load_documents_from_directory(document_path)

    # Load or create vector store
    vector_store = load_or_create_vector_store(documents)

    # User interaction loop
    while True:
        print("\n--- Legal Case Analysis Tool ---")
        print("Select an option:")
        print("1. Ask a question (Q&A)")
        print("2. Summarize a case")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            question = input("Enter your legal question: ")
            # refined_question = refine_question(question)
            # logger.info(f"Refined question: {refined_question}")
            result = answer_question(question, documents, vector_store)
            print("\n--- Answer ---")
            print(result['answer'])
            print("\n--- Sources ---")
            # for item in result['structured_context']:
            #     print(f"File: {item['file_name']}, Page: {item['page_number']}")

        elif choice == '2':
            question = input("Enter your request for case summarization: ")
            refined_question = refine_question(question)
            logger.info(f"Refined question: {refined_question}")
            result = summarize_case(refined_question, documents, vector_store)

            print("\n--- Initial Findings ---")
            print(result['initial_findings'])
            print("\n--- Follow-up Information ---")
            print(result['followup_info'])
            print("\n--- Final Summary ---")
            print(result['final_summary'])
            print("\n--- Sources ---")
            for item in result['structured_context']:
                print(f"File: {item['file_name']}, Page: {item['page_number']}")

        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
