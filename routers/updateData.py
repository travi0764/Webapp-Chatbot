from langchain_community.vectorstores import Milvus 
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from config.config import Config
from utils.logger import logging
import traceback
import time
from routers.stream import initialisedGlobal
from langchain_openai import OpenAIEmbeddings


embeddings = OpenAIEmbeddings(api_key=Config.OPENAI_API_KEY, model = Config.EMBEDDING_MODEL)
logging.info('Open AI EMbedding Model Initialized.')


def prepare_Documents(input_Documents):
    # We need to split the text that we read into smaller chunks so that during information retreival we don't hit the
    # token size limits.
    try:
        logging.info("Started Splitting Docuements")
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=int(Config.CHUNK_SIZE),
            chunk_overlap=256,
            length_function=len,
        )
        return text_splitter.split_documents(input_Documents)
    except Exception as e:
        logging.info(f"Failed to split the documents: {str(e)}", "ERROR")


def store_vectors(data):
    try:
        if Config.MILVUS_CLUSTER_ENDPOINT:

            CONNECTION_ARGS = {'uri' : Config.MILVUS_CLUSTER_ENDPOINT, 'token': Config.MILVUS_TOKEN}
        else:
            CONNECTION_ARGS = {'host' : Config.MILVUS_HOST, 'port': Config.MILVUS_PORT}
        c = time.time()
        # vector_db = Milvus.from_documents(
        # data,
        # embeddings,
        # connection_args={'uri' : Config.MILVUS_CLUSTER_ENDPOINT, 'token': Config.MILVUS_TOKEN},
        # collection_name = Config.MILVUS_COLLECTION_NAME, ## custom collection name 
        # search_params = {"metric":"L2","index_type":"FLAT","offset":0}, ## search params
        # )
        vector_db = Milvus.from_documents(
        data,
        embeddings,
        connection_args=CONNECTION_ARGS,
        collection_name = Config.MILVUS_COLLECTION_NAME, ## custom collection name 
        search_params = {"metric":"L2","index_type":"FLAT","offset":0}, ## search params
        )
        d = time.time()
        # logging.info(data[0])
        initialisedGlobal()
        logging.info('Calling initialisedGlobal function from store vectors function.')
        logging.info(f"Time taken by {data[0].metadata} for creating embeddings is {d-c}.")
        logging.info('data stored in milvus successfully.')

    except Exception as e:

        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e

def preprocess(file):
    try:
        logging.info(f'filename to be preprocessed {file}')

        try:
            if file.endswith(".docx") or file.endswith(".doc"):
                a = time.time()
                # data = prepare_Documents(Docx2txtLoader(file).load())
                data = prepare_Documents(Docx2txtLoader(file).load())
                b = time.time()

                logging.info(f"Time taken by {file} to load and creating chunks is {b-a}")

            if file.endswith(".pdf"):

                data = prepare_Documents(PyPDFLoader(file).load())

        except Exception as e:
            logging.info(traceback.format_exc())
            logging.error(str(e))
            raise e
        
        logging.info(f'length of data before chunking: {len(data)}')

        preprocessed_data = data
        logging.info(f'Prining length of dataset after chuning {len(preprocessed_data)}')
        return preprocessed_data
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e


def update(filename):

    try:
        preprocessed_data = preprocess(filename)

        store_vectors(preprocessed_data)

        return {'message': 'File uploaded successfully!'}
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        # print(e)
        return {"error" : str(e)}
