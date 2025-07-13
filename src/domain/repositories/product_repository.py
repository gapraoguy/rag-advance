from abc import ABC, abstractmethod
from typing import List

from domain.entities.product import Product


class ProductRepository(ABC):
    """商品データアクセス用リポジトリインターフェース"""

    @abstractmethod
    def get_all_products(self) -> List[Product]:
        """すべての商品を取得"""
        pass
