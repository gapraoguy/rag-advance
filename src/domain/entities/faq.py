from dataclasses import dataclass
from typing import Dict, Any


@dataclass
class FAQ:
    """FAQ情報を表すドメインエンティティ"""
    faq_id: str
    category: str
    question: str
    answer: str
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            "faq_id": self.faq_id,
            "category": self.category,
            "question": self.question,
            "answer": self.answer
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FAQ":
        """辞書からFAQインスタンスを作成"""
        return cls(
            faq_id=data["faq_id"],
            category=data["category"],
            question=data["question"],
            answer=data["answer"]
        )
    
    def __str__(self) -> str:
        return f"FAQ({self.faq_id}: {self.question[:50]}...)" 