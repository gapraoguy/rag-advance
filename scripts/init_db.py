from config.settings import Settings
from infrastructure.repositories.json_product_repository import JsonProductRepository
from infrastructure.repositories.json_faq_repository import JsonFAQRepository
from infrastructure.repositories.chroma_vector_search_repository import ChromaVectorSearchRepository
from application.services.indexing.indexing_service import IndexingService
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    DB初期化スクリプト

    - 既存Chromaコレクションを削除し、再生成する
    - 実行後、DBはアプリケーションのエントリポイントからそのまま利用可能な状態になる
    """
    logger.info("初期化処理を開始します...")
    settings = Settings.from_env()
    product_repo = JsonProductRepository(settings)
    faq_repo = JsonFAQRepository(settings)
    vector_repo = ChromaVectorSearchRepository(settings)
    indexing_service = IndexingService(product_repo, settings, faq_repo)

    logger.info("既存Chromaコレクションを削除します...")
    vector_repo.delete_collection()

    logger.info("GRANULAR商品戦略xQA_PAIR FAQ戦略でインデックス化を実行します...")
    result = indexing_service.index_data(
        vector_repo,
        product_strategy="granular",
        faq_strategy="qa_pair"
    )
    logger.info(f"インデックス化完了: {result}")
    print("DB初期化が完了しました。詳細:")
    print(result)

if __name__ == "__main__":
    main() 