
from threading import Thread
import asyncio
from queue import Queue
from utils.handlers import MyCustomHandler
from models.milvusDB import initializeVectorStore
from models.openaiModel import get_openai_4k, getLLM
from utils.logger import logging
import traceback
from fastapi.responses import JSONResponse


streamer_queue = Queue()

vector_db = None
llm = None
llm_chain = None
my_handler = []

def initialisedGlobal():

    global vector_db, llm, llm_chain, my_handler

    vector_db = initializeVectorStore()
    my_handler = MyCustomHandler(streamer_queue)

    logging.info("Vector Database initalized for streaming.")
    llm = getLLM(my_handler)
    logging.info("Open AI Model was initalized for streaming.")
    llm_chain = get_openai_4k(llm, vector_db)

initialisedGlobal()

def generate(query):
    try:
        # llm.invoke(query)
        result = llm_chain.invoke(query)

        logging.info("Result: %s", result)
        return result
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e

def start_generation(query):
    try:
        thread = Thread(target=generate, kwargs={"query": query})
        thread.start()
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e


async def response_generator(query):

    try:
        start_generation(query)

        while True:
            value = streamer_queue.get()
            if value == None:
                break
            yield value
            streamer_queue.task_done()
            await asyncio.sleep(0.05)

    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        logging.info(f'Inside upload data function in app.py {e}')
        await JSONResponse(content={'error': str(e)}, status_code=500)