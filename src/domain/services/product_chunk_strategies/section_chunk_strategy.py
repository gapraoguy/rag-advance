from typing import List
from domain.entities.product import Product
from domain.entities.chunk import Chunk
from domain.services.product_chunk_strategy import ProductChunkStrategy


class SectionChunkStrategy(ProductChunkStrategy):
    """セクション分割型チャンク戦略
    
    商品情報を基本情報・特徴・仕様の3つのセクションに分割する戦略
    """
    
    @property
    def strategy_name(self) -> str:
        return "section"
    
    def create_chunks(self, product: Product) -> List[Chunk]:
        """商品情報をセクション別に分割してチャンクを生成"""
        chunks = []
        
        chunks.append(self._create_basic_info_chunk(product))
        chunks.append(self._create_features_chunk(product))
        chunks.append(self._create_specifications_chunk(product))
        
        return chunks
    
    def _create_basic_info_chunk(self, product: Product) -> Chunk:
        """基本情報チャンクを作成"""
        text = f"""商品名: {product.product_name}
カテゴリ: {product.category}
価格: ¥{product.price:,}
説明: {product.description}"""
        
        metadata = self._create_base_metadata(product)
        metadata.update({
            "chunk_type": "section",
            "chunk_section": "basic_info"
        })
        
        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{product.product_id}_basic_info"
        )
    
    def _create_features_chunk(self, product: Product) -> Chunk:
        """特徴チャンクを作成"""
        features_text = '\n'.join(f"・{feature}" for feature in product.features)
        
        text = f"""商品名: {product.product_name}

特徴:
{features_text}"""
        
        metadata = self._create_base_metadata(product)
        metadata.update({
            "chunk_type": "section",
            "chunk_section": "features"
        })
        
        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{product.product_id}_features"
        )
    
    def _create_specifications_chunk(self, product: Product) -> Chunk:
        """仕様チャンクを作成"""
        specs_text = self._format_specifications(product.specifications)
        
        text = f"""商品名: {product.product_name}

仕様:
{specs_text}"""
        
        metadata = self._create_base_metadata(product)
        metadata.update({
            "chunk_type": "section",
            "chunk_section": "specifications"
        })
        
        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{product.product_id}_specifications"
        )
    
    def _create_base_metadata(self, product: Product) -> dict:
        """基本メタデータを作成"""
        return {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "price": product.price
        }
    
    def _format_specifications(self, specs: dict) -> str:
        """仕様辞書をテキスト形式にフォーマット"""
        formatted_lines = []
        
        for key, value in specs.items():
            if isinstance(value, dict):
                formatted_lines.append(f"{key}:")
                for sub_key, sub_value in value.items():
                    formatted_lines.append(f"  {sub_key}: {sub_value}")
            elif isinstance(value, list):
                formatted_lines.append(f"{key}: {', '.join(map(str, value))}")
            else:
                formatted_lines.append(f"{key}: {value}")
        
        return '\n'.join(formatted_lines) 