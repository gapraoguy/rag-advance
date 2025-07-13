import json
from typing import List, Optional
from pathlib import Path
import logging

from domain.entities.faq import FAQ
from domain.repositories.faq_repository import FAQRepository
from config.settings import Settings


logger = logging.getLogger(__name__)


class JsonFAQRepository(FAQRepository):
    """JSONファイルからFAQデータを読み込むリポジトリ実装
    
    制限事項:
    - ファイル更新の自動検知なし（アプリ再起動まで古いキャッシュを使用）
    - 全FAQに差分があった場合、リアルタイム反映不可
    - プロトタイプ用途に適している
    """
    
    def __init__(self, settings: Settings):
        self.data_dir = Path(settings.data_directory)
        self.faq_file = settings.faq_file
        self._faqs_cache: Optional[List[FAQ]] = None
        self._categories_cache: Optional[List[str]] = None
    
    def get_all_faqs(self) -> List[FAQ]:
        """全てのFAQを取得
        
        注意: ファイル変更があっても初回読み込み後はキャッシュを返す
        リアルタイム更新が必要な場合はアプリケーション再起動が必要
        """
        if self._faqs_cache is not None:
            return self._faqs_cache.copy()
        
        try:
            file_path = self.data_dir / self.faq_file
            if not file_path.exists():
                raise FileNotFoundError(f"FAQ file not found: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "faqs" not in data:
                raise ValueError("Invalid FAQ file format: 'faqs' key not found")
            
            self._faqs_cache = [
                FAQ.from_dict(faq_data) 
                for faq_data in data["faqs"]
            ]
            
            categories = set(faq.category for faq in self._faqs_cache)
            self._categories_cache = sorted(list(categories))
            
            logger.info(f"Loaded {len(self._faqs_cache)} FAQs with {len(self._categories_cache)} categories from {file_path}")
            return self._faqs_cache.copy()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise ValueError(f"Invalid JSON in FAQ file: {e}")
        except Exception as e:
            logger.error(f"Failed to load FAQs: {e}")
            raise
    
    def get_faqs_by_category(self, category: str) -> List[FAQ]:
        """カテゴリで絞り込みFAQを取得"""
        faqs = self.get_all_faqs()
        return [faq for faq in faqs if faq.category == category]
    
    def get_categories(self) -> List[str]:
        """利用可能なカテゴリ一覧を取得"""
        if self._categories_cache is not None:
            return self._categories_cache.copy()
        
        self.get_all_faqs()
        return self._categories_cache.copy() if self._categories_cache else [] 