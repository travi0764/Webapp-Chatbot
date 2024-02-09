
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

support_template = """ 
            Respond to user queries in a concise and respectful manner.
            Formulate clear and comprehensive replies using the search results provided.
            1. Address questions within the given context.
            2. Please refrain from inventing responses and kindly reply with "I apologize, but that falls outside of my current scope of knowledge."
            3. Approach each query with a methodical, step-by-step answer.
            4. If the question is asked in Arabic, generate the output in Arabic.
            5. Do not add suffixes, AI, AIResponse, etc.

            If the query is related to the current context, prioritize generating an answer based on the context. 
            If the query is not directly related to the context or is related to the previous summary, prioritize information from the previous conversation memory.
            Context: {context}

            User Question: {question}"""

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
        if session_id in user_sessions:
            template = support_template + f"""\nPrevious Summary: {user_sessions[session_id]['summary']}"""
        else:
            template = support_template

        llm_chain = get_openai_4k(llm, vector_db, template)
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