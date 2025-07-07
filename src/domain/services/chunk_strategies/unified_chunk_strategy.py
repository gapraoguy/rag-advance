from typing import List
from domain.entities.product import Product
from domain.entities.chunk import Chunk
from domain.services.chunk_strategy import ChunkStrategy


class UnifiedChunkStrategy(ChunkStrategy):
    """全情報統合型チャンク戦略
    
    商品の全情報を1つのチャンクにまとめる戦略
    """
    
    @property
    def strategy_name(self) -> str:
        return "unified"
    
    def create_chunks(self, product: Product) -> List[Chunk]:
        """商品の全情報を1つのチャンクとして生成"""
        
        features_text = '\n'.join(f"・{feature}" for feature in product.features)
        specs_text = self._format_specifications(product.specifications)
        
        text = f"""商品名: {product.product_name}
カテゴリ: {product.category}
価格: ¥{product.price:,}
説明: {product.description}

特徴:
{features_text}

仕様:
{specs_text}"""
        
        metadata = {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "price": product.price,
            "chunk_type": "unified",
            "chunk_section": "all"
        }
        
        chunk = Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{product.product_id}_unified"
        )
        
        return [chunk]
    
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