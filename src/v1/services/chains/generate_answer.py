from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from src.v1.configs.config import ChatConfig
from src.v1.services.prompt.generate_answer import GENERATE_ANSWER_PROMPT

class GenerateAnswerService:
    def __init__(self):
        self.prompt = GENERATE_ANSWER_PROMPT
        self.llm = ChatOpenAI(model=ChatConfig.model, temperature=0.0)
        self.output_parser = StrOutputParser()
        self.chain = self.prompt | self.llm | self.output_parser

    async def run(self, context, question):
        answer = await self.chain.invoke(
            {
                "context": context,
                "question": question
            }
        )
        return answer
    
    def run_sync(self, context, question):
        answer = self.chain.invoke(
            {
                "context": context,
                "question": question
            }
        )
        return answer