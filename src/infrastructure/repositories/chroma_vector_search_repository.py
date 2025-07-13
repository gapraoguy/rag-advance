from typing import List, Dict, Any
import logging

from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

from domain.entities.query_result import Document
from domain.repositories.vector_search_repository import VectorSearchRepository
from config.settings import Settings


logger = logging.getLogger(__name__)


class ChromaVectorSearchRepository(VectorSearchRepository):
    """Chromaを使用したベクトル検索リポジトリ実装"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            self.embeddings = OpenAIEmbeddings(
                model=settings.embedding_model,
            )
            self.db = Chroma(
                collection_name=settings.chroma_collection_name,
                embedding_function=self.embeddings,
                persist_directory=settings.chroma_persist_directory
            )
            logger.info(f"Initialized Chroma DB at {settings.chroma_persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma DB: {e}")
            raise RuntimeError(f"Failed to initialize vector search: {e}")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """ドキュメントをベクトルDBに追加"""
        try:
            if len(texts) != len(metadatas) or len(texts) != len(ids):
                raise ValueError("texts, metadatas, and ids must have the same length")
            
            self.db.add_texts(texts=texts, metadatas=metadatas, ids=ids)
            logger.info(f"Added {len(texts)} documents to Chroma DB")
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            raise RuntimeError(f"Failed to add documents to vector DB: {e}")
    
    def search(self, query: str, n_results: int = 3) -> List[Document]:
        """類似度検索を実行"""
        try:
            if not query or not query.strip():
                raise ValueError("Query cannot be empty")
            
            if n_results < 1:
                raise ValueError("n_results must be at least 1")
            
            results = self.db.similarity_search_with_score(query, k=n_results)
            
            documents = []
            for langchain_doc, score in results:
                doc = Document(
                    page_content=langchain_doc.page_content,
                    metadata=langchain_doc.metadata,
                    score=float(score)
                )
                documents.append(doc)
            
            logger.info(f"Found {len(documents)} documents for query: {query[:50]}...")
            return documents
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise RuntimeError(f"Failed to search documents: {e}")
    
    def delete_collection(self) -> None:
        """コレクションを削除"""
        try:
            self.db.delete_collection()
            logger.info(f"Deleted collection: {self.settings.chroma_collection_name}")
        except Exception as e:
            logger.error(f"Failed to delete collection: {e}")
            raise RuntimeError(f"Failed to delete collection: {e}") 