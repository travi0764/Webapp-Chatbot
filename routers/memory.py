from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from config.config import Config
import langchain

langchain.debug = True

# summary_prompt = """Given the combined summary of the previous conversation and the ongoing chat, Provide a summary of the chat conversation so far, covering the main topics, user queries, and noteworthy responses.
# Ensure the summary is clear and can be easily referenced in future prompts.Do not add suffixes, or anything else.
# Limit the summary length to 1500 tokens for optimal readability.
# {summary}

# {chat_history}"""
summary_prompt = """Progressively summarize the lines of conversation provided, adding onto the previous summary returning a new summary.\n\nEXAMPLE\nCurrent summary:\nThe human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good.\n\nNew lines of conversation:\nHuman: Why do you think artificial intelligence is a force for good?\nAI: Because artificial intelligence will help humans reach their full potential.\n\nNew summary:\nThe human asks what the AI thinks of artificial intelligence. The AI thinks artificial intelligence is a force for good because it will help humans reach their full potential.\nEND OF EXAMPLE

Current summary:{summary}

New lines of conversation:{chat_history}
New summary:"""

SUM_PROPMT = PromptTemplate(
    input_variables=['summary', 'chat_history'],
    template=summary_prompt
)

model = ChatOpenAI(api_key=Config.OPENAI_API_KEY)
chain_sum = LLMChain(llm=model, prompt=SUM_PROPMT)

def summarize(summary, chat_conversation):
    conversation = ""
    for key, value in chat_conversation[0].items():
        conversation +=f"{key}: {value}\n"
    res = chain_sum.invoke({"summary": summary, 'chat_history':conversation})

    return res['text']