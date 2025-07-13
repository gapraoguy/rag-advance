from abc import ABC, abstractmethod
from typing import List

from domain.entities.faq import FAQ


class FAQRepository(ABC):
    """FAQデータアクセス用リポジトリインターフェース"""

    @abstractmethod
    def get_all_faqs(self) -> List[FAQ]:
        """全てのFAQを取得"""
        pass

    @abstractmethod
    def get_faqs_by_category(self, category: str) -> List[FAQ]:
        """カテゴリで絞り込みFAQを取得"""
        pass

    @abstractmethod
    def get_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        pass
