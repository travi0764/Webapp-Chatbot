import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    # Milvus Configuration
    MILVUS_COLLECTION_NAME = os.getenv('MILVUS_COLLECTION_NAME')
    MILVUS_TOKEN = os.getenv('MILVUS_TOKEN')
    MILVUS_CLUSTER_ENDPOINT = os.getenv('MILVUS_CLUSTER_ENDPOINT')

    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL')

    CHUNK_SIZE = os.getenv('CHUNK_SIZE', 1024)

    # Add other configuration variables as needed
    