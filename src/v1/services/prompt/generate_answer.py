from langchain.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate


system_message = """
    Your name is Jarvis - an AI assistant.
"""

user_message = """
Instructions: Compose a comprehensive reply to the question using the search results given.
If the search result does not relate to the question or no search result is provided,
simply state "No Answer".
Do not use prior knowledge to answer the question.
If the search results mention multiple subjects with the same name, create separate answers for each.
Only include information found in the search result and don't add any additional information.
Make sure the answer is correct and don't output false content.
Ignore outlier search results which has nothing to do with the question.
Only answer what is asked. The answer should be short and concise. Don't add prior knowledge to the answer.
Answer step-by-step.
Don't use prior knowledge to answer.

Search result:
----------------------
    {context}
----------------------

Question: {question}
Answer:
"""

GENERATE_ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(system_message),
        HumanMessagePromptTemplate.from_template(user_message),
    ]
)