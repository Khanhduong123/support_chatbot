from langchain.schema import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.v1.services.prompt.condense_question import CONDENSE_QUESTION_PROMPT
from src.v1.configs.config import ChatConfig

class CondenseQuestionService:
    def __init__(self) -> None:
        self.prompt = CONDENSE_QUESTION_PROMPT
        self.llm = ChatOpenAI(model=ChatConfig.model, temperature=0.0)
        self.output_parser = StrOutputParser() 
        self.chain = self.prompt | self.llm | self.output_parser


    def format_conversation_history(self, conservation_history):
        buffer= []

        for chat in conservation_history:
            buffer.append(HumanMessage(content=chat["question"]))
            buffer.append(AIMessage(content=chat["answer"]))
        
        return buffer
    
    async def run(self, conversation_history, question):
        """
        Condense the question based on the conversation history.
        """
        if not conversation_history:
            return question
        
        conversation_history = self.format_conversation_history(conversation_history)
        new_question = await self.chain.invoke(
            {
                "question": question,
                "conversation_history": conversation_history
            }
        )

        return new_question
    

    def run_sync(self, chat_history, question):
        """
        Condense the question based on the conversation history.
        """
        if not chat_history:
            return question
        
        chat_history = self.format_conversation_history(chat_history)
        new_question = self.chain.invoke(
            {
                "question": question,
                "conversation_history": chat_history
            }
        )

        return new_question
