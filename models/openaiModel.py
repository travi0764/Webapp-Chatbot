from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory, CombinedMemory

from utils.logger import logging
from config.config import Config
import traceback
import langchain

langchain.debug = True

try:
    logging.info('Initializing Memory Format.')
    conv_memory = ConversationBufferWindowMemory(
        memory_key="chat_history_lines", input_key="question", k = 4
    )
    summary_memory = ConversationSummaryMemory(llm=ChatOpenAI(model='gpt-4', api_key=Config.OPENAI_API_KEY), max_token_limit=1000, input_key="question")
    memory = CombinedMemory(memories=[conv_memory, summary_memory])
    logging.info('Memory Format initialised successfully.')

except Exception as e:
    logging.info('Error occured in Initialising vector databse.')
    logging.error(traceback.format_exc())
    logging.info(str(e))
    raise e

support_template = """ 
        Respond to user queries in a concise and respectful manner.
        Formulate clear and comprehensive replies using the provided search result,summary and current conversation.
        1. Analyze questions to determine the appropriate source for answers: context, summary, or current conversation.
        2. If the question is asked in Arabic, generate the output in Arabic.
        3. Do not add suffixes, AI, AIResponse, etc.

        Previous Summary: {previous_summary}
        Current Conversation: {current_chat}
        Context: {context}

        If the query is related to the current context, prioritize generating an answer based on the context. 
        If the query is not directly related to the context or is related to the previous summary, prioritize information from the previous conversation memory.
        If the information can be added to the current conversation context, acknowledge with "Okay, I will remember it."

        When searching for answers:
        - Prioritize information from the current conversation chat.
        - If the answer is not found in the context, refer to the previous summary and current conversation.

        Ensure to balance between context, summary, and current conversation to provide the most relevant responses.

        User's Question : {question}
        """


# template = support_template.format(app=app, context=context)

SUPPORT_PROMPT = PromptTemplate(
    template=support_template, input_variables=["context", "question", "previous_summary","current_chat"]
    # template=support_template, input_variables=["context", "question"]
)

# print("~~"*50)
# print(f"Printing Prompt template {SUPPORT_PROMPT}")

def getLLM(handler):
    try:
        # memory = ConversationBufferWindowMemory(memory_key='history', return_messages=True, k = 3, input_key="question")
        openai = ChatOpenAI(model_name = Config.OPENAI_MODEL,
                            openai_api_key=Config.OPENAI_API_KEY,
                            streaming=True,  # ! important
                            callbacks=[handler]  # ! important
                            )
        logging.info(f"OpenAI model we are using {Config.OPENAI_MODEL}")
        logging.info(f"Milvus database we are using {Config.MILVUS_COLLECTION_NAME}")
        return openai
    except Exception as e:
        print(str(e))
        logging.info(traceback.format_exc())
        logging.error(str(e))


def get_openai_4k(openAILLM,faiss_support_store, summary, current_chat):
    try:
        prompt_new = SUPPORT_PROMPT.partial(previous_summary = summary,current_chat = current_chat)
        chain_type_kwargs = {"prompt": prompt_new}
        # chain_type_kwargs = {"prompt": SUPPORT_PROMPT, "memory" : memory}
        faiss_support_qa = RetrievalQA.from_chain_type(
            llm=openAILLM,
            chain_type="stuff",
            retriever=faiss_support_store.as_retriever(),
            chain_type_kwargs=chain_type_kwargs,
            # combine_docs_chain_kwargs = chain_type_kwargs,
            return_source_documents=True,
        )
        return faiss_support_qa
    except Exception as e:
        logging.info('error occured in get open ai model.')
        logging.error(traceback.format_exc())
        logging.error(str(e))
        raise e
