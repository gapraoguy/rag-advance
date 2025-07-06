from abc import ABC, abstractmethod
from typing import List, Optional
from domain.entities.product import Product


class ProductRepository(ABC):
    """商品データのリポジトリインターフェース"""
    
    @abstractmethod
    def get_all_products(self) -> List[Product]:
        """すべての商品を取得"""
        pass
    
    @abstractmethod
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """IDから商品を取得"""
        pass 