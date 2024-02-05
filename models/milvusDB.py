from langchain_community.vectorstores import Milvus
from pymilvus import MilvusException
from langchain_openai import OpenAIEmbeddings
from config.config import Config
import traceback
from utils.logger import logging

try:
    embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY)
except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))

def initializeVectorStore():
    try:
        vector_db = Milvus(
            embeddings,
            connection_args={'uri' : Config.MILVUS_CLUSTER_ENDPOINT, 'token': Config.MILVUS_TOKEN},
            collection_name = Config.MILVUS_COLLECTION_NAME, ## custom collection name 
            search_params = {"metric":"L2","index_type":"FLAT","offset":0}, ## search params
            )

        logging.info(f"vector database initialized")
        return vector_db
    
    except MilvusException as e:
        # print('--'*50)
        logging.info('--'*50)
        logging.error(str(e.message))
        raise e

    except Exception as e:

        logging.info('Error occured in Initialising vector databse.')
        logging.error(traceback.format_exc())
        logging.info(str(e))
        raise e