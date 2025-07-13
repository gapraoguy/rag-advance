from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Chunk:
    """チャンクを表すドメインエンティティ"""

    text: str
    metadata: Dict[str, Any]
    chunk_id: str

    def __post_init__(self):
        """バリデーション"""
        if not self.text or not self.text.strip():
            raise ValueError("Chunk text cannot be empty")
        if not self.chunk_id:
            raise ValueError("Chunk ID cannot be empty")
