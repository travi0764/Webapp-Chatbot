
from threading import Thread
import asyncio
from queue import Queue
from utils.handlers import MyCustomHandler
from models.milvusDB import initializeVectorStore
from models.openaiModel import get_openai_4k, getLLM
from utils.logger import logging
import traceback
from fastapi.responses import JSONResponse
from routers.memory import summarize


streamer_queue = Queue()
user_sessions = {}

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
    # llm_chain = get_openai_4k(llm, vector_db)

initialisedGlobal()


def store_conversation(session_id: str, question: str, response: str):
    if session_id not in user_sessions:
        user_sessions[session_id] = {'chat_history' : [], 'summary' : None}
        user_sessions[session_id]['chat_history'].append({"Human": question, "AI": response['result']})
        user_sessions[session_id]['summary'] = summarize('', user_sessions[session_id]['chat_history'][-1:])
    else:
        user_sessions[session_id]['chat_history'].append({"Human": question, "AI": response['result']})
        user_sessions[session_id]['summary'] = summarize(user_sessions[session_id]['summary'], user_sessions[session_id]['chat_history'][-1:])

    print('=='*50)
    print(session_id)
    print(user_sessions[session_id])
    print('=='*50)

def generate(query, session_id):
    global support_template
    try:
        summary = ''
        current_chat = ''
        if session_id not in user_sessions:

            llm_chain = get_openai_4k(llm, vector_db, summary,current_chat)
        else:
            summary = user_sessions[session_id]['summary']
            current_chat = ''
            for ele in user_sessions[session_id]['chat_history'][-3:]:
                for key, value in ele.items():
                    current_chat +=f"{key}: {value}\n"
            llm_chain = get_openai_4k(llm, vector_db, summary,current_chat)
        
        result = llm_chain.invoke({'query' : query})

        store_conversation(session_id, query, result)

        logging.info("Result: %s", result)
        return result
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e

def start_generation(query, session_id):
    try:
        thread = Thread(target=generate, kwargs={"query": query, "session_id" : session_id})
        thread.start()
    except Exception as e:
        logging.info(traceback.format_exc())
        logging.error(str(e))
        raise e


async def response_generator(query, session_id):

    try:
        start_generation(query, session_id)

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