from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAI
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryMemory, CombinedMemory

from utils.logger import logging
from config.config import Config
import traceback
import langchain

langchain.debug = False

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

# support_template = """تأكد من أن إجاباتك على استفسارات المستخدمين شاملة ومفيدة.
#             قم بإنشاء إجابات مفصلة من خلال فحص المعلومات المتاحة في نتائج البحث بعناية.
#             1. قم بفحص السياق المحدد بعناية من المعرفة الخارجية قبل الرد.
#             2. عند الشك، استخدم عبارة "أعتذر، ولكن ذلك خارج نطاق معرفتي الحالي".
#             3. نظم الردود في شرح واضح وخطوة بخطوة.
#             4. قدم الإجابات باللغة العربية.
#             تجنب بدء الردود بكلمات مفتاحية مثل "AI"، "Response"، أو ما شابه.
            # ملخص للمحادثة: {history}
            # المحادثة الحالية: {chat_history_lines}
            # سياق المعرفة الخارجية: {context}

            # استفسار المستخدم: {question}"""

# support_template = """تأكد من أن إجاباتك على استفسارات المستخدمين شاملة ومفيدة.
#             قم بإنشاء إجابات مفصلة من خلال فحص المعلومات المتاحة في نتائج البحث بعناية.
#             1. قم بفحص السياق المحدد بعناية من المعرفة الخارجية قبل الرد.
#             2. عند الشك، استخدم عبارة "أعتذر، ولكن ذلك خارج نطاق معرفتي الحالي".
#             3. نظم الردود في شرح واضح وخطوة بخطوة.
#             4. قدم الإجابات باللغة العربية.
#             تجنب بدء الردود بكلمات مفتاحية مثل "AI"، "Response"، أو ما شابه.
#             سياق المعرفة الخارجية: {context}

#             استفسار المستخدم: {question}"""


support_template = """ 
            Respond to user queries in a concise and respectful manner.
            Formulate clear and comprehensive replies using the search results provided.
            1. Address questions within the given context.
            2. please refrain from inventing responses and kindly respond with "I apologize, but that falls outside of my current scope of knowledge."
            3. Approach each query with a methodical, step-by-step answer.
            4. If question is aksed in arabic, then only generate the output in arabic.
            5. Do not add suffixes, or anything else like AI, AIResponse etc.
            
            Conversation Summary: {history}
            Current Conversation: {chat_history_lines}
            External Knowledge Context: {context}

            User Question: {question}"""



SUPPORT_PROMPT = PromptTemplate(
    template=support_template, input_variables=["context", "question", "history","chat_history_lines"]
    # template=support_template, input_variables=["context", "question"]
)

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


def get_openai_4k(openAILLM,faiss_support_store):
    try:

        # chain_type_kwargs = {"prompt": SUPPORT_PROMPT}
        chain_type_kwargs = {"prompt": SUPPORT_PROMPT, "memory" : memory}
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
