import logging
from langchain_community.document_loaders import PyPDFDirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from retrieval import load_or_create_vector_store, get_hybrid_retriever
from utils import truncate_context
from prompts import qa_prompt
from llm_interface import invoke_llm
import re
import os

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_chunks(text,chunk_size = 1000, chunk_overlap = 200):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(text)
    return chunks

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

def format_context_with_hyperlinks(chunks):
    """Format document chunks to provide clear context to the LLM with hyperlinks."""
    formatted_context = ""
    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get('source', 'Unknown source')
        page_number = chunk.metadata.get('page', None)
        hyperlink = create_hyperlink(source, page_number)
        formatted_context += f"{chunk.page_content}\n[Source {i+1}]({hyperlink})\n---\n"
    return formatted_context

def split_documents(documents):
    """Split documents into smaller chunks for better retrieval and context management."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,
        chunk_overlap=150
    )
    return text_splitter.split_documents(documents)

def extract_year_from_context(context):
    """Extract year from context using regex."""
    year_pattern = r"\b(?:19|20)\d{2}\b"
    years = re.findall(year_pattern, context)
    return sorted(years)[0] if years else "Year not found in context"

def load_and_segment_documents(document_path):
    """Load and split documents into chunks for better retrieval."""
    logger.info(f"Loading and splitting documents from {document_path}...")
    documents = load_documents_from_directory(document_path)
    split_docs = split_documents(documents)
    logger.info(f"Split documents into {len(split_docs)} chunks.")
    return split_docs

def retrieve_and_answer_question(question, document_path, vector_store):
    """Retrieve relevant document chunks and pass them to the LLM for answering the question."""
    documents = load_and_segment_documents(document_path)
    retriever = get_hybrid_retriever(documents, vector_store)
    relevant_docs = retriever.get_relevant_documents(question)
    
    formatted_context = format_context_with_hyperlinks(relevant_docs)
    formatted_context = truncate_context(formatted_context, max_tokens=2000)

    prompt = qa_prompt().format(user_question=question, context=formatted_context)
    answer = invoke_llm(prompt)
    
    if "year" in question.lower() and "Year not found" not in answer:
        year = extract_year_from_context(formatted_context)
        answer += f"\n\nExtracted year: {year}"
    
    return answer, relevant_docs

def preprocess_document(document):
    """Preprocess document content to clean up unnecessary whitespace and unwanted sections."""
    cleaned_content = document.page_content.replace('\n', ' ').strip() if hasattr(document, 'page_content') else document['content']
    return cleaned_content

def load_documents_from_directory(document_path: str):
    """Load and preprocess documents from a directory containing PDFs."""
    logger.info(f"Loading documents from {document_path}...")
    documents = PyPDFDirectoryLoader(document_path).load_and_split()
    chunk_size = 1024 if len(documents) > 100 else 512
    chunk_overlap = 200 if chunk_size == 1024 else 100
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(documents)
    processed_docs = []
    for doc in split_docs:
        cleaned_content = preprocess_document(doc)
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    return processed_docs

def load_documents_from_markdown(document_path: str):
    """Load and preprocess markdown documents from a file."""
    logger.info(f"Loading markdown document from {document_path}...")
    loader = UnstructuredMarkdownLoader(document_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=2048, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    processed_docs = []
    for doc in split_docs:
        cleaned_content = preprocess_document(doc)
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    return processed_docs

def load_documents_with_ocr(document_path: str):
    """Load documents from a directory using OCR if PDFs contain scanned images or complex formatting."""
    logger.info(f"Loading documents from {document_path} with OCR...")
    loader = PyPDFLoader(document_path)
    documents = loader.load_and_split()
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1024, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)
    processed_docs = []
    for doc in split_docs:
        cleaned_content = preprocess_document(doc)
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    return processed_docs

# Example usage
if __name__ == "__main__":
    question = "What year was the Declaration of Independence signed?"
    document_path = "./documents"
    vector_store = load_or_create_vector_store(document_path)  # Implement this function based on your vector store setup
    
    answer, source_docs = retrieve_and_answer_question(question, document_path, vector_store)
    print(f"Answer: {answer}\n")
    print("Sources:")
    for i, doc in enumerate(source_docs):
        source = doc.metadata.get('source', 'Unknown source')
        page = doc.metadata.get('page', 'Unknown page')
        print(f"[{i+1}] {source} (Page: {page})")