import logging
from typing import Optional

from application.services.rag.rag_service import RAGService
from config.settings import Settings
from infrastructure.repositories.chroma_vector_search_repository import ChromaVectorSearchRepository
from infrastructure.repositories.json_faq_repository import JsonFAQRepository
from infrastructure.repositories.json_product_repository import JsonProductRepository

# from application.services.indexing.indexing_service import IndexingService


logger = logging.getLogger(__name__)


class DIContainer:
    """Dependency Injection コンテナ

    アプリケーションの依存関係を管理し、適切な順序で初期化を行う
    """

    def __init__(self):
        self._settings: Optional[Settings] = None
        self._product_repo: Optional[JsonProductRepository] = None
        self._faq_repo: Optional[JsonFAQRepository] = None
        self._vector_repo: Optional[ChromaVectorSearchRepository] = None
        # self._indexing_service: Optional[IndexingService] = None
        self._rag_service: Optional[RAGService] = None

    def initialize(self) -> None:
        """依存関係を初期化"""
        try:
            logger.info("Loading settings...")
            self._settings = Settings.from_env()

            logger.info("Initializing repositories...")
            self._product_repo = JsonProductRepository(self._settings)

            self._faq_repo = JsonFAQRepository(self._settings)

            self._vector_repo = ChromaVectorSearchRepository(self._settings)

            logger.info("Initializing services...")
            # self._indexing_service = IndexingService(
            #     self._product_repo,
            #     self._settings,
            #     cast(Optional[JsonFAQRepository], self._faq_repo)
            # )
            self._rag_service = RAGService(self._vector_repo, self._settings)

            logger.info("Dependency injection completed")

        except Exception as e:
            logger.error(f"Failed to initialize dependencies: {e}")
            raise RuntimeError(f"Dependency initialization failed: {e}")

    @property
    def settings(self) -> Settings:
        """設定を取得"""
        if self._settings is None:
            raise RuntimeError("Settings not initialized. Call initialize() first.")
        return self._settings

    @property
    def product_repo(self) -> JsonProductRepository:
        """商品リポジトリを取得"""
        if self._product_repo is None:
            raise RuntimeError("Product repository not initialized. Call initialize() first.")
        return self._product_repo

    @property
    def faq_repo(self) -> Optional[JsonFAQRepository]:
        """FAQリポジトリを取得"""
        return self._faq_repo

    @property
    def vector_repo(self) -> ChromaVectorSearchRepository:
        """ベクトルリポジトリを取得"""
        if self._vector_repo is None:
            raise RuntimeError("Vector repository not initialized. Call initialize() first.")
        return self._vector_repo

    # @property
    # def indexing_service(self) -> IndexingService:
    #     """インデキシングサービスを取得"""
    #     if self._indexing_service is None:
    #         raise RuntimeError("Indexing service not initialized. Call initialize() first.")
    #     return self._indexing_service

    @property
    def rag_service(self) -> RAGService:
        """RAGサービスを取得"""
        if self._rag_service is None:
            raise RuntimeError("RAG service not initialized. Call initialize() first.")
        return self._rag_service
