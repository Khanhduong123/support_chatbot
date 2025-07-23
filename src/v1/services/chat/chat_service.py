from typing import Dict
from langchain.callbacks import AsyncIteratorCallbackHandler
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI

from src.v1.configs.config import ChatConfig
from src.v1.services.prompt.generate_answer import GENERATE_ANSWER_PROMPT
from src.v1.services.chains.condense_question import CondenseQuestionService
from src.v1.services.chains.generate_answer import GenerateAnswerService
from src.v1.models.model import ChatConversation, ChatMessage

class ChatService:
    def __init__(self):
        self.document_service = None
        self.condense_question_service = CondenseQuestionService()
        self.generate_answer_service = GenerateAnswerService()
        self.llm = ChatOpenAI(model=ChatConfig.model, temperature=0.0, verbose=True)

        self.streaming_chain = GENERATE_ANSWER_PROMPT | self.llm_streaming

        self.conversations: Dict[str, Dict[int, Dict]] = {}
    
    async def get_relevant_docs(self, question):
        relevant_docs = await self.document_service.search(question, top_k=ChatConfig.document_top_k)

        query_context = relevant_docs['content']
        rel_doc = [{
                "page": int(relevant_docs["page"]),
                "document_name": relevant_docs["document_name"],
                "document_id": relevant_docs["document_id"],
                "content": relevant_docs["content"]
            }]
        return  {"context": query_context, "relevant_docs": rel_doc}

    def get_relevant_document_sync(self, question):
        relevant_docs = self.document_service.search(question, top_k=ChatConfig.document_top_k)

        query_context = relevant_docs['content']
        rel_doc = [{
                "page": int(relevant_docs["page"]),
                "document_name": relevant_docs["document_name"],
                "document_id": relevant_docs["document_id"],
                "content": relevant_docs["content"]
            }]
        return  {"context": query_context, "relevant_docs": rel_doc}
    
    def get_answer_sync(self, question):

        query_result = self.get_relevant_document_sync(question=question)
        answer = self.generate_answer_chain.run_sync(
            context=query_result["context"], question=question
        )

        if answer == "No Answer":
            answer = ChatConfig.PROMPT_NOT_FOUND
            relevant_docs = []

        else:
            relevant_docs = query_result["relevant_docs"]

        # LOGGER.info(f"Answer: {answer}")

        return {"question": question, "answer": answer, "relevant_docs": relevant_docs}
    

    async def get_answer(self, db, user_id, session_id: str, question: str):
        # 1️⃣ Kiểm tra hoặc tạo conversation
        conversation = db.query(ChatConversation).filter_by(session_id=session_id, user_id=user_id).first()
        if not conversation:
            conversation = ChatConversation(user_id=user_id, session_id=session_id)
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

        # 2️⃣ Lấy history từ db
        history_messages = (
            db.query(ChatMessage)
            .filter_by(conversation_id=conversation.conversation_id)
            .order_by(ChatMessage.created_at)
            .all()
        )
        conversation_history = [{"question": m.user_question, "answer": m.ai_answer} for m in history_messages]

        # 3️⃣ Condense question
        condensed_question = await self.condense_question_service.run(
            conversation_history=conversation_history, question=question
        )

        # 4️⃣ Lấy tài liệu liên quan
        query_result = await self.get_relevant_docs(condensed_question)

        # 5️⃣ Gọi LLM trả lời
        answer = await self.generate_answer_service.run(
            context=query_result["context"], question=condensed_question
        )

        if answer == "No Answer":
            answer = ChatConfig.PROMPT_NOT_FOUND
            relevant_docs = []
        else:
            relevant_docs = query_result["relevant_docs"]

        # 6️⃣ Lưu message mới
        for doc in relevant_docs:
            chat_message = ChatMessage(
                conversation_id=conversation.conversation_id,
                user_question=condensed_question,
                ai_answer=answer,
                document_id=doc["document_id"],
                page=doc["page"],
                document_name=doc["document_name"],
                document_content=doc["content"],
            )
            db.add(chat_message)
        db.commit()

        # 7️⃣ Trả kết quả cho FE
        return {
            "question": condensed_question,
            "answer": answer,
            "relevant_docs": relevant_docs
        }



    async def get_answer(self, session_id, conversation_id, question):
        # Retrieve conversation from mongo database
        # conversation_history = await get_conversation_history(session_id=session_id)
        conversation_history = self.conversations.get(session_id, {}).get(conversation_id, {}).get("history", [])
        # LOGGER.info(f"Conversation History") 
        # LOGGER.info(conversation_history)

        question = await self.condense_question_chain.run(
            conversation_history=conversation_history, question=question
        )

        # LOGGER.info(f"Condense question: {question}")


        query_result = await self.get_relevant_document(question=question)

        answer = await self.generate_answer_chain.run(
            context=query_result["context"], question=question
        )

        if answer == "No Answer":
            answer = ChatConfig.PROMPT_NOT_FOUND
            relevant_docs = []

        else:
            relevant_docs = query_result["relevant_docs"]

        if session_id not in self.conversations:
            self.conversations[session_id] = {}
        if conversation_id not in self.conversations[session_id]:
            self.conversations[session_id][conversation_id] = {"history": []}

        self.conversations[session_id][conversation_id]["history"].append({
            "question": question,
            "answer": answer,
            "relevant_docs": relevant_docs,
        })

        # LOGGER.info(f"Answer: {answer}")

        return {"question": question, "answer": answer, "relevant_docs": relevant_docs}
