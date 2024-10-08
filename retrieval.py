# retrieval.py

import os
from langchain_community.vectorstores import Chroma
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from config import EMBEDDING_MODEL_NAME, PERSIST_DIRECTORY, COLLECTION_NAME
from logging_config import logger

model_kwargs = {'trust_remote_code': True}
EMBEDDING_FUNCTION = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME, model_kwargs=model_kwargs)

def load_or_create_vector_store(documents):
    if os.path.exists(PERSIST_DIRECTORY) and len(os.listdir(PERSIST_DIRECTORY)) > 0:
        logger.info(f"Loading existing vector store from {PERSIST_DIRECTORY}")
        vector_store = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=EMBEDDING_FUNCTION,
            collection_name=COLLECTION_NAME
        )
    else:
        logger.info(f"Creating new vector store in {PERSIST_DIRECTORY}")
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=EMBEDDING_FUNCTION,
            persist_directory=PERSIST_DIRECTORY,
            collection_name=COLLECTION_NAME
        )
        vector_store.persist()
    return vector_store

def get_hybrid_retriever(documents, vector_store):
    # Use BM25 keyword search, as it's better for questions like "filed", "ruling"
    bm25_retriever = BM25Retriever.from_documents(documents, search_kwargs={'k': 5})
    
    # Vector similarity search for more complex, context-based questions
    chroma_retriever = vector_store.as_retriever(search_kwargs={'k': 5})
    
    # Increase weight for BM25 for date-related queries
    fusion_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, chroma_retriever],
        weights=[0.8, 0.2]  # Prioritize keyword-based retrieval for date-related questions
    )
    return fusion_retriever

