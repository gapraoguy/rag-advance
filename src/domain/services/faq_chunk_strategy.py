from abc import ABC, abstractmethod
from typing import List
from domain.entities.faq import FAQ
from domain.entities.chunk import Chunk


class FAQChunkStrategy(ABC):
    """FAQ用チャンク戦略の抽象インターフェース"""
    
    @abstractmethod
    def create_chunks_for_faq(self, faq: FAQ) -> List[Chunk]:
        """
        FAQからチャンクのリストを生成
        """
        pass
    
    @abstractmethod
    def create_chunks_for_faqs(self, faqs_by_category: dict) -> list:
        """
        複数FAQからチャンクを生成
        """
        pass
    
    @property
    @abstractmethod
    def strategy_name(self) -> str:
        """戦略名を返す"""
        pass 