from document_processing import (
    load_documents_from_directory,
    load_documents_from_markdown
)
from retrieval import load_or_create_vector_store
from summarizer import refine_question, summarize_case
from chatbot import answer_question
from config import COLLECTION_NAME, PERSIST_DIRECTORY
from logging_config import logger
import re
from document_processing import retrieve_and_answer_question

def extract_case_metadata(documents):
    """Extract metadata like case name, year, case number, and potentially other information from legal documents."""
    case_metadata = {}

    # Define regular expressions for metadata extraction
    case_name_pattern = r"([A-Z][a-zA-Z]*\s+v\.\s+[A-Z][a-zA-Z]*)"
    year_pattern = r"\b(?:19|20)\d{2}\b"  # Four-digit years starting with 19 or 20
    # Updated court name pattern to ensure it captures "Court of Appeals of Texas"
    court_name_pattern = r"(Court of Appeals|District Court|Supreme Court|Circuit Court|Family Court|Tribunal)\s+(of\s+[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)"
    case_number_pattern = r"No\.\s*([\w\-–]+)"  # Pattern to match case numbers (e.g., No. 01–93–00091–CV)

    for doc in documents:
        # Extract document content from page_content
        content = doc.page_content if hasattr(doc, 'page_content') else doc['content']

        # Extract the case name (e.g., "Dunnings v. Castro")
        case_name_match = re.search(case_name_pattern, content)
        if case_name_match:
            case_metadata['case_name'] = case_name_match.group(1)

        # Extract all possible years
        years = re.findall(year_pattern, content)
        if years:
            # Convert all matched years to four digits and pick the earliest year
            full_years = re.findall(r"\b(?:19|20)\d{2}\b", content)
            sorted_years = sorted(set(full_years), key=lambda x: int(x))
            case_metadata['year'] = sorted_years[0]  # Pick the oldest year

        # Extract the full court name (e.g., "Court of Appeals of Texas")
        court_match = re.search(court_name_pattern, content, re.IGNORECASE)
        if court_match:
            court_type = court_match.group(1)  # e.g., "Court of Appeals"
            jurisdiction = court_match.group(2).strip()  # e.g., "of Texas"
            full_court_name = f"{court_type} {jurisdiction}"  # Combine for "Court of Appeals of Texas"
            case_metadata['court_name'] = full_court_name

        # Extract the case number (e.g., "No. 01–93–00091–CV")
        case_number_match = re.search(case_number_pattern, content)
        if case_number_match:
            case_metadata['case_number'] = case_number_match.group(1)

        # Log and return as soon as the metadata is found
        if case_metadata:
            break  # Assuming we stop after finding metadata in the first match

    # Log extracted metadata
    logger.info(f"Extracted metadata: {case_metadata}")
    return case_metadata


def main():
    # Load documents and vector store
    document_path = 'docs\law-data\case3'
    if document_path.endswith('.md'):
        documents = load_documents_from_markdown(document_path)
    else:
        documents = load_documents_from_directory(document_path)  # Path to documents
    vector_store = load_or_create_vector_store(documents)
    # Extract case metadata like date and parties
    # Load and preprocess documents
    
    case_metadata = extract_case_metadata(documents)
    logger.info(f"Case Metadata: {case_metadata}")
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

            # Call retrieve_and_answer_question function to get the answer
            answer = retrieve_and_answer_question(
                question=question,
                document_path=document_path,
                vector_store=vector_store
            )
            
            print("\n--- Answer ---")
            print(answer)
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
                print(f"File: {item['file_name']}, Page: {item['page_number']}")
            print("\n--- Additional Info ---")
            print(f"Case Metadata: {case_metadata}")
        elif choice == '3':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please select 1, 2, or 3.")





# def main():
#     document_path = 'docs/law-data/case2'  # Specify path (Markdown or PDF)

#     # Load and preprocess documents
#     if document_path.endswith('.md'):
#         documents = load_documents_from_markdown(document_path)
#     else:
#         documents = load_documents_from_directory(document_path)

#     # Extract case metadata like date and parties
#     case_metadata = extract_case_metadata(documents)
#     logger.info(f"Case Metadata: {case_metadata}")
#     # exit()

#     # Load or create vector store
#     vector_store = load_or_create_vector_store(documents)

#     # User interaction loop
#     while True:
#         print("\n--- Legal Case Analysis Tool ---")
#         print("Select an option:")
#         print("1. Ask a question (Q&A)")
#         print("2. Summarize a case")
#         print("3. Exit")
#         choice = input("Enter your choice (1/2/3): ")

#         if choice == '1':
#             question = input("Enter your legal question: ")
#             refined_question = refine_question(question)
#             logger.info(f"Refined question: {refined_question}")
#             result = answer_question(refined_question, documents, vector_store)
            
#             print("\n--- Answer ---")
#             print(result['answer'])
#             print("\n--- Sources ---")
#             for item in result['structured_context']:
#                 print(f"File: {item['file_name']}, Page: {item['page_number']}")
#             print("\n--- Additional Info ---")
#             print(f"Case Metadata: {case_metadata}")

#         elif choice == '2':
#             question = "Generate the complete summary of the document and provide a concise summary of the case"
#             refined_question = refine_question(question)
#             logger.info(f"Refined question: {refined_question}")
#             result = summarize_case(refined_question, documents, vector_store)

#             print("\n--- Initial Findings ---")
#             print(result['initial_findings'])
#             print("\n--- Follow-up Information ---")
#             print(result['followup_info'])
#             print("\n--- Final Summary ---")
#             print(result['final_summary'])
#             print("\n--- Sources ---")
#             for item in result['structured_context']:
#                 print(f"File: {item['file_name']}, Page: {item['page_number']}")
#             print("\n--- Additional Info ---")
#             print(f"Case Metadata: {case_metadata}")

#         elif choice == '3':
#             print("Exiting...")
#             break
#         else:
#             print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    main()
