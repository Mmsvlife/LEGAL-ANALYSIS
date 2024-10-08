import logging
from langchain_community.document_loaders import PyPDFDirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from retrieval import load_or_create_vector_store  # Assuming your vector store loader
from utils import format_context, truncate_context  # For context formatting
from prompts import qa_prompt  # The question-answering prompt
from llm_interface import invoke_llm  # LLM invocation
from retrieval import get_hybrid_retriever
import re


# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def split_documents(documents):
    """Split documents into smaller chunks for better retrieval and context management."""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=512,  # Reduce chunk size to increase granularity
        chunk_overlap=150  # Slight overlap to ensure context is preserved
    )
    
    # Split all documents into chunks
    split_docs = text_splitter.split_documents(documents)
    
    return split_docs


def extract_year_from_context(context):
    """Extract year from context using regex."""
    year_pattern = r"\b(?:19|20)\d{2}\b"  # Matches four-digit years starting with 19xx or 20xx
    years = re.findall(year_pattern, context)
    if years:
        return sorted(years)[0]  # Return the earliest year found
    return "Year not found in context"

def load_and_segment_documents(document_path):
    """Load and split documents into chunks for better retrieval."""
    logger.info(f"Loading and splitting documents from {document_path}...")
    
    # Load documents (modify this as per your document loading logic)
    documents = load_documents_from_directory(document_path)  # or from Markdown, PDF, etc.
    
    # Split documents into smaller chunks for easier processing
    split_docs = split_documents(documents)
    
    logger.info(f"Split documents into {len(split_docs)} chunks.")
    return split_docs

def format_context(chunks):
    """Format document chunks to provide clear context to the LLM."""
    formatted_context = ""
    for chunk in chunks:
        # Use dot notation for accessing page_content and metadata
        formatted_context += f"{chunk.page_content}\n---\n"
    return formatted_context


def retrieve_and_answer_question(question, document_path, vector_store):
    """Retrieve relevant document chunks and pass them to the LLM for answering the question."""
    
    # Load and split documents into chunks
    documents = load_and_segment_documents(document_path)
    
    # Retrieve relevant chunks based on the question
    retriever = get_hybrid_retriever(documents, vector_store)
    relevant_docs = retriever.get_relevant_documents(question)
    
    # Format the relevant chunks into a single context
    formatted_context = format_context(relevant_docs)
    
    # Truncate context if it's too large for the model
    formatted_context = truncate_context(formatted_context, max_tokens=2000)

    # Prepare the prompt for the LLM
    prompt = qa_prompt().format(user_question=question, context=formatted_context)
    
    # Get the answer from the LLM
    answer = invoke_llm(prompt)
    
    # If the LLM didn't provide the year, fall back to regex extraction
    if "year" in question.lower() and "Year not found" not in answer:
        return extract_year_from_context(formatted_context)
    
    return answer



def preprocess_document(document):
    """
    Preprocess document content to clean up unnecessary whitespace and unwanted sections.
    This function can be extended to handle more specific cleaning tasks.
    """
    cleaned_content = document.page_content.replace('\n', ' ').strip() if hasattr(document, 'page_content') else document['content']
    return cleaned_content

def load_documents_from_directory(document_path: str):
    """
    Load and preprocess documents from a directory containing PDFs. Adjust chunk size based on the number of documents.
    """
    logger.info(f"Loading documents from {document_path}...")
    
    # Use the PyPDFDirectoryLoader to load documents
    documents = PyPDFDirectoryLoader(document_path).load_and_split()
    
    # Adjust chunk size and overlap dynamically based on document length
    chunk_size = 1024 if len(documents) > 100 else 512  # Example of adjusting chunk size
    chunk_overlap = 200 if chunk_size == 1024 else 100

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    split_docs = text_splitter.split_documents(documents)

    # Log and preprocess documents
    processed_docs = []
    for idx, doc in enumerate(split_docs):
        cleaned_content = preprocess_document(doc)
        # logger.info(f"Document {idx} preview: {cleaned_content[:500]}")  # Debugging: Print first 500 characters
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    
    return processed_docs

def load_documents_from_markdown(document_path: str):
    """
    Load and preprocess markdown documents from a file.
    """
    logger.info(f"Loading markdown document from {document_path}...")
    
    # Use the UnstructuredMarkdownLoader to load the markdown file
    loader = UnstructuredMarkdownLoader(document_path)
    documents = loader.load()
    
    # Initialize text splitter with default chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1024, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # Log and preprocess documents
    processed_docs = []
    for idx, doc in enumerate(split_docs):
        cleaned_content = preprocess_document(doc)
        logger.info(f"Document {idx} preview: {cleaned_content[:500]}")  # Debugging: Print first 500 characters
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    
    return processed_docs

def load_documents_with_ocr(document_path: str):
    """
    Load documents from a directory using OCR if PDFs contain scanned images or complex formatting.
    """

    logger.info(f"Loading documents from {document_path} with OCR...")
    loader = PyPDFLoader(document_path)
    documents = loader.load_and_split()
    
    # Initialize text splitter with default chunk size and overlap
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(chunk_size=1024, chunk_overlap=200)
    split_docs = text_splitter.split_documents(documents)

    # Log and preprocess documents
    processed_docs = []
    for idx, doc in enumerate(split_docs):
        cleaned_content = preprocess_document(doc)
        logger.info(f"Document {idx} preview: {cleaned_content[:500]}")  # Debugging: Print first 500 characters
        doc.page_content = cleaned_content
        processed_docs.append(doc)
    
    return processed_docs

