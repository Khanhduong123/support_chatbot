from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate


system_message = """
    Your name is Jarvis - an AI assistant.
"""

user_message = """
Given the following conversation and follow up question, rephrase the follow up question to be a standalone question, in its original language.
Conversation history:
    {conversation_history}
Follow question: 
    {question}
Standalone question:
"""


CONDENSE_QUESTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(user_message)
    ]
)