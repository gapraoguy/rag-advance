from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Document:
    """検索で取得したドキュメント"""
    page_content: str
    metadata: Dict[str, Any]
    score: float = 0.0


@dataclass
class QueryResult:
    """RAGの検索結果を表すドメインエンティティ"""
    query: str
    answer: str
    source_documents: List[Document]
    
    @property
    def has_answer(self) -> bool:
        """回答が存在するかを判定"""
        return bool(self.answer and self.answer.strip())
    
    @property
    def document_count(self) -> int:
        """参照ドキュメント数を取得"""
        return len(self.source_documents) 