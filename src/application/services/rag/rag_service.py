from typing import List, Dict, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from domain.entities.query_result import QueryResult, Document
from domain.repositories.vector_search_repository import VectorSearchRepository
from config.settings import Settings


logger = logging.getLogger(__name__)


class RAGService:
    """RAGを使用した質問応答サービス"""
    
    def __init__(self, vector_search_repo: VectorSearchRepository, settings: Settings):
        self.vector_search_repo = vector_search_repo
        self.settings = settings
        
        try:
            self.llm = ChatOpenAI(
                model=settings.llm_model,
                temperature=settings.temperature,
            )
            
            self.prompt = ChatPromptTemplate.from_messages([
                ("system", "あなたはECサイトの商品案内・FAQ対応AIアシスタントです。提供された商品情報やFAQ情報を基に、ユーザーの質問に対して正確で分かりやすい回答を提供してください。"),
                ("human", """以下の情報を参考に、質問に回答してください。

{context}

質問: {question}

回答:""")
            ])
            
            self.chain = (
                {"context": self._format_documents, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
            )
            
            logger.info("Initialized RAG service")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            raise RuntimeError(f"Failed to initialize RAG service: {e}")
    
    def answer(self, question: str) -> QueryResult:
        """質問に対する回答を生成"""
        try:
            if not question or not question.strip():
                raise ValueError("Question cannot be empty")
            
            documents = self.vector_search_repo.search(
                query=question,
                n_results=self.settings.default_search_results
            )
            
            if not documents:
                logger.warning(f"No documents found for query: {question}")
                return QueryResult(
                    query=question,
                    answer="申し訳ございません。お探しの商品情報やFAQが見つかりませんでした。別の言葉で質問を言い換えていただくか、カテゴリを指定してお試しください。",
                    source_documents=[]
                )
            
            answer = self.chain.invoke({
                "documents": documents,
                "question": question
            })
            
            logger.info(f"Generated answer for question: {question[:50]}...")
            
            return QueryResult(
                query=question,
                answer=answer,
                source_documents=documents
            )
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise RuntimeError(f"Failed to generate answer: {e}")
    
    def _format_documents(self, inputs: Dict[str, Any]) -> str:
        """ドキュメントをコンテキスト用にフォーマット"""
        documents: List[Document] = inputs.get("documents", [])
        
        if not documents:
            return ""
        
        formatted_docs = []
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            data_type = metadata.get("data_type", "product")
            
            if data_type == "faq":
                title = f"【FAQ情報{i}】"
                category = metadata.get("category", "不明")
                formatted_docs.append(
                    f"{title}\n"
                    f"カテゴリ: {category}\n"
                    f"{doc.page_content}\n"
                )
            else:
                title = f"【商品情報{i}】"
                product_name = metadata.get("product_name", "不明")
                price = metadata.get("price", "不明")
                formatted_docs.append(
                    f"{title}\n"
                    f"商品名: {product_name}, 価格: ¥{price:,}\n" if isinstance(price, (int, float)) else f"商品名: {product_name}, 価格: {price}\n"
                    f"{doc.page_content}\n"
                )
        
        return "\n\n".join(formatted_docs) 