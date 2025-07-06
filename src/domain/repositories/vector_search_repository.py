from abc import ABC, abstractmethod
from typing import List, Dict, Any
from domain.entities.query_result import Document


class VectorSearchRepository(ABC):
    """ベクトル検索のリポジトリインターフェース"""
    
    @abstractmethod
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]) -> None:
        """ドキュメントをベクトルDBに追加"""
        pass
    
    @abstractmethod
    def search(self, query: str, n_results: int = 3) -> List[Document]:
        """類似度検索を実行"""
        pass
    
    @abstractmethod
    def delete_collection(self) -> None:
        """コレクションを削除"""
        pass 