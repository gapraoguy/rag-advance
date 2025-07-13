import logging
from typing import Any, Dict, Optional

from application.services.chunk.faq_chunk_service import FAQChunkService
from application.services.chunk.product_chunk_service import ProductChunkService
from config.settings import Settings
from domain.repositories.faq_repository import FAQRepository
from domain.repositories.product_repository import ProductRepository
from domain.repositories.vector_search_repository import VectorSearchRepository

logger = logging.getLogger(__name__)


class IndexingService:
    """ベクトルDBへのインデックス化サービス

    異なるチャンク戦略でデータをベクトルDBにインデックス化する
    """

    def __init__(
        self,
        product_repo: ProductRepository,
        settings: Settings,
        faq_repo: Optional[FAQRepository] = None,
    ):
        self.product_repo = product_repo
        self.faq_repo = faq_repo
        self.settings = settings

    def index_product_with_strategy(
        self, vector_repo: VectorSearchRepository, strategy_name: str
    ) -> Dict[str, Any]:
        """指定された戦略で商品データをインデックス化"""
        try:
            logger.info(f"Starting product indexing with strategy: {strategy_name}")

            products = self.product_repo.get_all_products()
            if not products:
                raise ValueError("No products found to index")

            chunk_service = ProductChunkService(strategy_name)
            chunks = chunk_service.generate_chunks_for_products(products)

            texts = [chunk.text for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]

            vector_repo.add_documents(texts, metadatas, ids)

            result = {
                "strategy": strategy_name,
                "total_products": len(products),
                "total_chunks": len(chunks),
                "chunks_per_product": len(chunks) / len(products),
                "success": True,
            }

            logger.info(
                f"Product indexing completed - Strategy: {strategy_name}, "
                f"Products: {len(products)}, Chunks: {len(chunks)}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to index products with strategy {strategy_name}: {e}")
            raise RuntimeError(f"Product indexing failed: {e}")

    def get_product_chunk_statistics(self, strategy_name: str) -> Dict[str, Any]:
        """指定戦略の商品チャンク統計情報を取得"""
        try:
            products = self.product_repo.get_all_products()
            chunk_service = ProductChunkService(strategy_name)

            all_chunks = []
            chunks_per_product = []

            for product in products:
                chunks = chunk_service.generate_chunks(product)
                all_chunks.extend(chunks)
                chunks_per_product.append(len(chunks))

            text_lengths = [len(chunk.text) for chunk in all_chunks]

            return {
                "strategy": strategy_name,
                "total_products": len(products),
                "total_chunks": len(all_chunks),
                "chunks_per_product": {
                    "min": min(chunks_per_product),
                    "max": max(chunks_per_product),
                    "avg": sum(chunks_per_product) / len(chunks_per_product),
                },
                "text_length": {
                    "min": min(text_lengths),
                    "max": max(text_lengths),
                    "avg": sum(text_lengths) / len(text_lengths),
                },
            }

        except Exception as e:
            logger.error(f"Failed to get product chunk statistics for {strategy_name}: {e}")
            raise RuntimeError(f"Failed to get product statistics: {e}")

    def index_faq_with_strategy(
        self, vector_repo: VectorSearchRepository, strategy_name: str
    ) -> Dict[str, Any]:
        """指定された戦略でFAQデータをインデックス化"""
        try:
            if self.faq_repo is None:
                raise ValueError("FAQ repository is not configured")

            logger.info(f"Starting FAQ indexing with strategy: {strategy_name}")

            faqs = self.faq_repo.get_all_faqs()
            if not faqs:
                raise ValueError("No FAQs found to index")

            faq_chunk_service = FAQChunkService(strategy_name)
            chunks = faq_chunk_service.generate_chunks_for_faqs(faqs)

            texts = [chunk.text for chunk in chunks]
            metadatas = [chunk.metadata for chunk in chunks]
            ids = [chunk.chunk_id for chunk in chunks]

            vector_repo.add_documents(texts, metadatas, ids)

            result = {
                "strategy": strategy_name,
                "total_faqs": len(faqs),
                "total_chunks": len(chunks),
                "chunks_per_faq": len(chunks) / len(faqs),
                "success": True,
            }

            logger.info(
                f"FAQ indexing completed - Strategy: {strategy_name}, "
                f"FAQs: {len(faqs)}, Chunks: {len(chunks)}"
            )

            return result

        except Exception as e:
            logger.error(f"Failed to index FAQs with strategy {strategy_name}: {e}")
            raise RuntimeError(f"FAQ indexing failed: {e}")

    def get_faq_chunk_statistics(self, strategy_name: str) -> Dict[str, Any]:
        """指定戦略のFAQチャンク統計情報を取得"""
        try:
            if self.faq_repo is None:
                raise ValueError("FAQ repository is not configured")

            faqs = self.faq_repo.get_all_faqs()
            faq_chunk_service = FAQChunkService(strategy_name)

            all_chunks = []
            chunks_per_faq = []

            for faq in faqs:
                chunks = faq_chunk_service.generate_chunks(faq)
                all_chunks.extend(chunks)
                chunks_per_faq.append(len(chunks))

            text_lengths = [len(chunk.text) for chunk in all_chunks]

            return {
                "strategy": strategy_name,
                "total_faqs": len(faqs),
                "total_chunks": len(all_chunks),
                "chunks_per_faq": {
                    "min": min(chunks_per_faq) if chunks_per_faq else 0,
                    "max": max(chunks_per_faq) if chunks_per_faq else 0,
                    "avg": (sum(chunks_per_faq) / len(chunks_per_faq) if chunks_per_faq else 0),
                },
                "text_length": {
                    "min": min(text_lengths) if text_lengths else 0,
                    "max": max(text_lengths) if text_lengths else 0,
                    "avg": sum(text_lengths) / len(text_lengths) if text_lengths else 0,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get FAQ chunk statistics for {strategy_name}: {e}")
            raise RuntimeError(f"Failed to get FAQ statistics: {e}")

    def index_data(
        self,
        vector_repo: VectorSearchRepository,
        product_strategy: str,
        faq_strategy: str,
    ) -> Dict[str, Any]:
        """商品とFAQの両データを統合してインデックス化"""
        try:
            logger.info(f"Starting indexing - Product: {product_strategy}, FAQ: {faq_strategy}")

            all_chunks = []

            products = self.product_repo.get_all_products()
            if products:
                chunk_service = ProductChunkService(product_strategy)
                product_chunks = chunk_service.generate_chunks_for_products(products)
                all_chunks.extend(product_chunks)

            if self.faq_repo:
                faqs = self.faq_repo.get_all_faqs()
                if faqs:
                    faq_chunk_service = FAQChunkService(faq_strategy)
                    faq_chunks = faq_chunk_service.generate_chunks_for_faqs(faqs)
                    all_chunks.extend(faq_chunks)

            if not all_chunks:
                raise ValueError("No data found to index")

            texts = [chunk.text for chunk in all_chunks]
            metadatas = [chunk.metadata for chunk in all_chunks]
            ids = [chunk.chunk_id for chunk in all_chunks]

            vector_repo.add_documents(texts, metadatas, ids)

            result = {
                "product_strategy": product_strategy,
                "faq_strategy": faq_strategy,
                "total_products": len(products),
                "total_faqs": len(faqs) if self.faq_repo else 0,
                "total_chunks": len(all_chunks),
                "product_chunks": len(product_chunks) if products else 0,
                "faq_chunks": len(faq_chunks) if self.faq_repo and faqs else 0,
                "success": True,
            }

            logger.info(f"Indexing completed - Total chunks: {len(all_chunks)}")

            return result

        except Exception as e:
            logger.error(f"Failed to index data: {e}")
            raise RuntimeError(f"Indexing failed: {e}")
