import sys
import logging
from typing import Optional

from config.settings import Settings
from infrastructure.repositories.json_product_repository import JsonProductRepository
from infrastructure.repositories.chroma_vector_search_repository import ChromaVectorSearchRepository
from application.services.rag_service import RAGService
from domain.entities.query_result import QueryResult


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIApplication:
    """CLIアプリケーション"""
    
    def __init__(self):
        self.settings: Optional[Settings] = None
        self.rag_service: Optional[RAGService] = None
    
    def setup(self) -> None:
        """アプリケーションの初期設定"""
        try:
            logger.info("Loading settings...")
            self.settings = Settings.from_env()
            
            logger.info("Initializing repositories...")
            vector_search_repo = ChromaVectorSearchRepository(self.settings)
            
            logger.info("Initializing services...")
            self.rag_service = RAGService(vector_search_repo, self.settings)
            
            logger.info("Application setup completed")
            
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            print(f"\n設定エラー: {e}")
            print("環境変数を確認してください。")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to setup application: {e}")
            print(f"\nアプリケーションの初期化に失敗しました: {e}")
            sys.exit(1)
    
    def run(self) -> None:
        """メインの実行ループ"""
        assert self.rag_service is not None, "RAG service not initialized"
        
        print("\n=== TechMart ChatBot ===")
        print("商品についてご質問ください。終了するには 'exit' または 'quit' と入力してください。\n")
        
        while True:
            try:
                question = input("ご質問をどうぞ: ").strip()
                
                if question.lower() in ['exit', 'quit', '終了']:
                    print("\nご利用ありがとうございました。")
                    break
                
                if not question:
                    print("質問を入力してください。\n")
                    continue
                
                print("\n回答を生成中...")
                result = self.rag_service.answer(question)
                
                self._display_result(result)
                
            except KeyboardInterrupt:
                print("\n\n中断されました。")
                break
            except Exception as e:
                logger.error(f"Error during question processing: {e}")
                print(f"\nエラーが発生しました: {e}")
                print("もう一度お試しください。\n")
    
    def _display_result(self, result: QueryResult) -> None:
        """検索結果を表示"""
        print("\n" + "="*50)
        print("【回答】")
        print("="*50)
        print(result.answer)
        
        if result.source_documents:
            print("\n" + "="*50)
            print("【参照した商品情報】")
            print("="*50)
            
            for i, doc in enumerate(result.source_documents, 1):
                print(f"\n--- 参照 {i} ---")
                print(doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content)
                
                if doc.metadata:
                    print(f"\nメタデータ: {doc.metadata}")
                
                if hasattr(doc, 'score') and doc.score:
                    print(f"関連度スコア: {doc.score:.4f}")
        
        print("\n" + "="*50 + "\n")


def main():
    """メインエントリーポイント"""
    app = CLIApplication()
    
    try:
        app.setup()
        app.run()
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"\n予期しないエラーが発生しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 