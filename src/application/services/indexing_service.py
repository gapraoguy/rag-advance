from typing import List, Dict, Any
import logging

from domain.repositories.vector_search_repository import VectorSearchRepository
from domain.repositories.product_repository import ProductRepository
from application.services.chunk_service import ChunkService
from config.settings import Settings


logger = logging.getLogger(__name__)


class IndexingService:
    """ベクトルDBへのインデックス化サービス
    
    異なるチャンク戦略でデータをベクトルDBにインデックス化する
    """
    
    def __init__(
        self,
        product_repo: ProductRepository,
        settings: Settings
    ):
        self.product_repo = product_repo
        self.settings = settings
    
    def index_with_strategy(
        self,
        vector_repo: VectorSearchRepository,
        strategy_name: str
    ) -> Dict[str, Any]:
        """指定された戦略でデータをインデックス化"""
        try:
            logger.info(f"Starting indexing with strategy: {strategy_name}")
            
            products = self.product_repo.get_all_products()
            if not products:
                raise ValueError("No products found to index")
            
            chunk_service = ChunkService(strategy_name)
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
                "success": True
            }
            
            logger.info(
                f"Indexing completed - Strategy: {strategy_name}, "
                f"Products: {len(products)}, Chunks: {len(chunks)}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to index with strategy {strategy_name}: {e}")
            raise RuntimeError(f"Indexing failed: {e}")
    
    def get_chunk_statistics(self, strategy_name: str) -> Dict[str, Any]:
        """指定戦略のチャンク統計情報を取得"""
        try:
            products = self.product_repo.get_all_products()
            chunk_service = ChunkService(strategy_name)
            
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
                    "avg": sum(chunks_per_product) / len(chunks_per_product)
                },
                "text_length": {
                    "min": min(text_lengths),
                    "max": max(text_lengths),
                    "avg": sum(text_lengths) / len(text_lengths)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get chunk statistics for {strategy_name}: {e}")
            raise RuntimeError(f"Failed to get statistics: {e}") 