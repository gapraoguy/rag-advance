from typing import List, Dict
import logging

from domain.entities.product import Product
from domain.entities.chunk import Chunk
from domain.services.chunk_strategy import ChunkStrategy
from domain.services.chunk_strategies.unified_chunk_strategy import UnifiedChunkStrategy
from domain.services.chunk_strategies.section_chunk_strategy import SectionChunkStrategy
from domain.services.chunk_strategies.granular_chunk_strategy import GranularChunkStrategy


logger = logging.getLogger(__name__)


class ChunkService:
    """チャンク生成サービス
    
    異なるチャンク戦略を使用して商品からチャンクを生成する
    """
    
    def __init__(self, strategy_name: str = "unified"):
        self._strategies: Dict[str, ChunkStrategy] = {
            "unified": UnifiedChunkStrategy(),
            "section": SectionChunkStrategy(),
            "granular": GranularChunkStrategy()
        }
        
        self._current_strategy = self._get_strategy(strategy_name)
        logger.info(f"Initialized ChunkService with strategy: {strategy_name}")
    
    def generate_chunks(self, product: Product) -> List[Chunk]:
        """商品からチャンクを生成"""
        try:
            chunks = self._current_strategy.create_chunks(product)
            logger.info(
                f"Generated {len(chunks)} chunks for product {product.product_id} "
                f"using {self._current_strategy.strategy_name} strategy"
            )
            return chunks
        except Exception as e:
            logger.error(f"Failed to generate chunks for product {product.product_id}: {e}")
            raise RuntimeError(f"Failed to generate chunks: {e}")
    
    def generate_chunks_for_products(self, products: List[Product]) -> List[Chunk]:
        """複数商品からチャンクを一括生成"""
        all_chunks = []
        
        for product in products:
            try:
                chunks = self.generate_chunks(product)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Skipping product {product.product_id} due to error: {e}")
                continue
        
        logger.info(f"Generated total {len(all_chunks)} chunks from {len(products)} products")
        return all_chunks
    
    def set_strategy(self, strategy_name: str) -> None:
        """チャンク戦略を変更"""
        old_strategy = self._current_strategy.strategy_name
        self._current_strategy = self._get_strategy(strategy_name)
        logger.info(f"Changed chunk strategy from {old_strategy} to {strategy_name}")
    
    def get_current_strategy_name(self) -> str:
        """現在の戦略名を取得"""
        return self._current_strategy.strategy_name
    
    def get_available_strategies(self) -> List[str]:
        """利用可能な戦略一覧を取得"""
        return list(self._strategies.keys())
    
    def _get_strategy(self, strategy_name: str) -> ChunkStrategy:
        """戦略名から戦略インスタンスを取得"""
        if strategy_name not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise ValueError(f"Unknown strategy: {strategy_name}. Available: {available}")
        
        return self._strategies[strategy_name] 