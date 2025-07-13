from abc import ABC, abstractmethod
from typing import List
from domain.entities.product import Product
from domain.entities.chunk import Chunk


class ProductChunkStrategy(ABC):
    """商品チャンク戦略の抽象インターフェース"""
    
    @abstractmethod
    def create_chunks(self, product: Product) -> List[Chunk]:
        """商品からチャンクのリストを生成"""
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """戦略名を返す"""
        pass 