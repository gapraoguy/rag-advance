import json
from pathlib import Path
from typing import List, Optional
import logging

from domain.entities.product import Product
from domain.repositories.product_repository import ProductRepository
from config.settings import Settings


logger = logging.getLogger(__name__)


class JsonProductRepository(ProductRepository):
    """JSONファイルから商品データを読み込むリポジトリ実装"""
    
    def __init__(self, settings: Settings):
        self.data_dir = Path(settings.data_directory)
        self.products_file = settings.products_file
        self._products_cache: Optional[List[Product]] = None
    
    def get_all_products(self) -> List[Product]:
        """すべての商品を取得"""
        if self._products_cache is not None:
            return self._products_cache
        
        try:
            file_path = self.data_dir / self.products_file
            if not file_path.exists():
                raise FileNotFoundError(f"Products file not found: {file_path}")
            
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            if "products" not in data:
                raise ValueError("Invalid products file format: 'products' key not found")
            
            self._products_cache = [
                Product.from_dict(product_data) 
                for product_data in data["products"]
            ]
            
            logger.info(f"Loaded {len(self._products_cache)} products from {file_path}")
            return self._products_cache
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise ValueError(f"Invalid JSON in products file: {e}")
        except Exception as e:
            logger.error(f"Failed to load products: {e}")
            raise
    
    def get_product_by_id(self, product_id: str) -> Optional[Product]:
        """IDから商品を取得"""
        products = self.get_all_products()
        for product in products:
            if product.product_id == product_id:
                return product
        return None 