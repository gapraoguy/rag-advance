from typing import List

from domain.entities.chunk import Chunk
from domain.entities.product import Product
from domain.services.product_chunk_strategy import ProductChunkStrategy


class GranularChunkStrategy(ProductChunkStrategy):
    """細粒度分割型チャンク戦略

    商品情報を基本情報と各特徴・各仕様項目に細かく分割する戦略
    """

    @property
    def strategy_name(self) -> str:
        return "granular"

    def create_chunks(self, product: Product) -> List[Chunk]:
        """商品情報を細粒度で分割してチャンクを生成"""
        chunks = []

        chunks.append(self._create_basic_info_chunk(product))
        chunks.extend(self._create_feature_chunks(product))
        chunks.extend(self._create_specification_chunks(product))

        return chunks

    def _create_basic_info_chunk(self, product: Product) -> Chunk:
        """基本情報チャンクを作成"""
        text = f"""商品名: {product.product_name}
カテゴリ: {product.category}
価格: ¥{product.price:,}
説明: {product.description}"""

        metadata = self._create_base_metadata(product)
        metadata.update({"chunk_type": "granular", "chunk_section": "basic_info"})

        return Chunk(text=text, metadata=metadata, chunk_id=f"{product.product_id}_basic_info")

    def _create_feature_chunks(self, product: Product) -> List[Chunk]:
        """各特徴を個別チャンクとして作成"""
        chunks = []

        for idx, feature in enumerate(product.features):
            text = f"""商品名: {product.product_name}

特徴: {feature}"""

            metadata = self._create_base_metadata(product)
            metadata.update(
                {
                    "chunk_type": "granular",
                    "chunk_section": "feature",
                    "feature_index": idx,
                    "feature_content": feature,
                }
            )

            chunk = Chunk(
                text=text,
                metadata=metadata,
                chunk_id=f"{product.product_id}_feature_{idx}",
            )
            chunks.append(chunk)

        return chunks

    def _create_specification_chunks(self, product: Product) -> List[Chunk]:
        """各仕様項目を個別チャンクとして作成"""
        chunks = []

        for key, value in product.specifications.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    chunks.append(
                        self._create_single_spec_chunk(
                            product,
                            f"{key}_{sub_key}",
                            f"{key} - {sub_key}: {sub_value}",
                        )
                    )
            elif isinstance(value, list):
                chunks.append(
                    self._create_single_spec_chunk(
                        product, key, f"{key}: {', '.join(map(str, value))}"
                    )
                )
            else:
                chunks.append(self._create_single_spec_chunk(product, key, f"{key}: {value}"))

        return chunks

    def _create_single_spec_chunk(self, product: Product, spec_key: str, spec_text: str) -> Chunk:
        """単一仕様項目のチャンクを作成"""
        text = f"""商品名: {product.product_name}

仕様: {spec_text}"""

        metadata = self._create_base_metadata(product)
        metadata.update(
            {
                "chunk_type": "granular",
                "chunk_section": "specification",
                "specification_key": spec_key,
                "specification_content": spec_text,
            }
        )

        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{product.product_id}_spec_{spec_key.replace('.', '_').replace('-', '_')}",
        )

    def _create_base_metadata(self, product: Product) -> dict:
        """基本メタデータを作成"""
        return {
            "product_id": product.product_id,
            "product_name": product.product_name,
            "category": product.category,
            "price": product.price,
        }
