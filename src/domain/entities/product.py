from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Product:
    """商品情報を表すドメインエンティティ"""

    product_id: str
    product_name: str
    category: str
    price: int
    description: str
    features: list[str]
    specifications: Dict[str, Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Product":
        """辞書形式のデータからProductインスタンスを作成"""
        return cls(
            product_id=data.get("product_id", ""),
            product_name=data.get("product_name", ""),
            category=data.get("category", ""),
            price=data.get("price", 0),
            description=data.get("description", ""),
            features=data.get("features", []),
            specifications=data.get("specifications", {}),
        )

    def to_text(self) -> str:
        """検索用のテキスト表現を生成"""
        features_text = "\n".join(f"・{feature}" for feature in self.features)
        specs_text = "\n".join(f"{k}: {v}" for k, v in self.specifications.items())

        return f"""商品名: {self.product_name}
カテゴリ: {self.category}
価格: ¥{self.price:,}
説明: {self.description}

特徴:
{features_text}

仕様:
{specs_text}"""
