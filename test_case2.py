from document_processing import (
    load_documents_from_directory,
    load_documents_from_markdown,
    retrieve_and_answer_question
)
from retrieval import load_or_create_vector_store
from summarizer import refine_question, summarize_case
from chatbot import answer_question
from config import COLLECTION_NAME, PERSIST_DIRECTORY
from logging_config import logger
import re
import os

def create_hyperlink(document_path, page_number=None):
    """
    Create a hyperlink to the document.
    If page_number is provided, it will link to the specific page in the PDF.
    """
    base_url = "file://"  # Change this to your document server's base URL if applicable
    full_path = os.path.abspath(document_path)
    if page_number is not None and document_path.lower().endswith('.pdf'):
        return f"{base_url}{full_path}#page={page_number}"
    return f"{base_url}{full_path}"

def extract_case_metadata(documents):
    """Extract metadata like case name, year, case number, and potentially other information from legal documents."""
    case_metadata = {}

    # Define regular expressions for metadata extraction
    case_name_pattern = r"([A-Z][a-zA-Z]*\s+v\.\s+[A-Z][a-zA-Z]*)"
    year_pattern = r"\b(?:19|20)\d{2}\b"
    court_name_pattern = r"(Court of Appeals|District Court|Supreme Court|Circuit Court|Family Court|Tribunal)\s+(of\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)"
    case_number_pattern = r"No\.\s*([\w\-–]+)"

    for doc in documents:
        content = doc.page_content if hasattr(doc, 'page_content') else doc['content']

        case_name_match = re.search(case_name_pattern, content)
        if case_name_match:
            case_metadata['case_name'] = case_name_match.group(1)

        years = re.findall(year_pattern, content)
        if years:
            full_years = re.findall(r"\b(?:19|20)\d{2}\b", content)
            sorted_years = sorted(set(full_years), key=lambda x: int(x))
            case_metadata['year'] = sorted_years[0]

        court_match = re.search(court_name_pattern, content, re.IGNORECASE)
        if court_match:
            court_type = court_match.group(1)
            jurisdiction = court_match.group(2).strip()
            full_court_name = f"{court_type} {jurisdiction}"
            case_metadata['court_name'] = full_court_name

        case_number_match = re.search(case_number_pattern, content)
        if case_number_match:
            case_metadata['case_number'] = case_number_match.group(1)

        if case_metadata:
            break

    logger.info(f"Extracted metadata: {case_metadata}")
    return case_metadata

def main():
    document_path = 'docs\law-data\pate'
    if document_path.endswith('.md'):
        documents = load_documents_from_markdown(document_path)
    else:
        documents = load_documents_from_directory(document_path)
    vector_store = load_or_create_vector_store(documents)
    
    case_metadata = extract_case_metadata(documents)
    logger.info(f"Case Metadata: {case_metadata}")

    while True:
        print("\n--- Legal Case Analysis Tool ---")
        print("Select an option:")
        print("1. Ask a question (Q&A)")
        print("2. Summarize a case")
        print("3. Exit")
        choice = input("Enter your choice (1/2/3): ")

        if choice == '1':
            question = input("Enter your legal question: ")

            answer, source_docs = retrieve_and_answer_question(
                question=question,
                document_path=document_path,
                vector_store=vector_store
            )
            
            print("\n--- Answer ---")
            print(answer)
            print("\n--- Sources ---")
            for i, doc in enumerate(source_docs):
                source = doc.metadata.get('source', 'Unknown source')
                page = doc.metadata.get('page', 'Unknown page')
                hyperlink = create_hyperlink(source, page)
                print(f"[{i+1}] {hyperlink} (Page: {page})")
            print("\n--- Additional Info ---")
            print(f"Case Metadata: {case_metadata}")
        
        elif choice == '2':
            question = "Generate the complete summary of the document and provide a concise summary of the case"
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
                hyperlink = create_hyperlink(item['file_name'], item['page_number'])
                print(f"File: {hyperlink}, Page: {item['page_number']}")
            print("\n--- Additional Info ---")
            print(f"Case Metadata: {case_metadata}")
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()