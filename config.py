# config.py

import os

# Global Variables
MODEL_NAME = 'mistral'  # Replace with your actual model
EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-large-en-v1.5"  # HuggingFace embedding model
PERSIST_DIRECTORY = 'storage-db/law2'
COLLECTION_NAME = 'law'

# OpenAI API Key (if using OpenAI models)
# os.environ["OPENAI_API_KEY"] = "your_openai_api_key"

