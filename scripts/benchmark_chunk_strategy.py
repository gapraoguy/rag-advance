import sys
import logging
from pathlib import Path
import os

sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.settings import Settings
from infrastructure.repositories.json_product_repository import JsonProductRepository
from infrastructure.repositories.json_faq_repository import JsonFAQRepository
from infrastructure.repositories.chroma_vector_search_repository import ChromaVectorSearchRepository
from application.services.indexing.indexing_service import IndexingService
from application.services.benchmark.chunk_strategy_evaluation_service import SearchEvaluationService
from config.logging_config import setup_logging


def main():
    """FAQ＋商品データの統合チャンク戦略ベンチマークを実行するスクリプト"""
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        log_file_path = os.path.join(log_dir, "chunk_strategy_benchmark.log")
        setup_logging(log_file=log_file_path)
        logger = logging.getLogger(__name__)
        
        print("="*60)
        print("統合チャンク戦略ベンチマーク実行")
        print("="*60)
        
        settings = Settings.from_env()
        settings.chroma_persist_directory = str(Path(settings.chroma_persist_directory) / "benchmark")
        logger.info("Settings loaded successfully")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        product_repo = JsonProductRepository(settings)
        faq_repo = JsonFAQRepository(settings)
        
        print(f"\n✅ データ読み込み完了")
        print(f"  - 商品数: {len(product_repo.get_all_products())}")
        print(f"  - FAQ数: {len(faq_repo.get_all_faqs())}")
        print(f"  - FAQカテゴリ: {', '.join(faq_repo.get_categories())}")
        
        def create_vector_repo(product_strategy: str, faq_strategy: str, clear_existing: bool = True):
            collection_name = f"integrated_{product_strategy}_{faq_strategy}"
            if clear_existing:
                vector_repo = ChromaVectorSearchRepository(settings)
                try:
                    vector_repo.delete_collection()
                    logger.info(f"Cleared existing collection: {collection_name}")
                except:
                    pass
                return ChromaVectorSearchRepository(settings)
            else:
                return ChromaVectorSearchRepository(settings)
        
        print("\n🚀 ベンチマーク開始...")
        print("以下の戦略組み合わせを比較評価します:")
        
        strategy_list = [
            ("unified", "qa_pair"),
            ("section", "qa_pair"),
            ("granular", "qa_pair"),
            ("section", "qa_separate"),
            ("granular", "qa_separate"),
            ("unified", "category_unified")
        ]
        for product_strategy, faq_strategy in strategy_list:
            print(f"- 商品: {product_strategy.upper()} + FAQ: {faq_strategy.upper()}")
        print("\nテストクエリ実行中...")
        
        results = {}
        indexing_results = {}
        
        for product_strategy, faq_strategy in strategy_list:
            combination_name = f"{product_strategy}+{faq_strategy}"
            print(f"\n--- {combination_name} ---")
            try:
                vector_repo = create_vector_repo(product_strategy, faq_strategy, True)
                indexing_service = IndexingService(product_repo, settings, faq_repo)
                print(f"  インデキシング中...")
                indexing_result = indexing_service.index_data(
                    vector_repo, product_strategy, faq_strategy
                )
                indexing_results[combination_name] = indexing_result
                print(f"  - 総チャンク数: {indexing_result['total_chunks']}")
                print(f"  - 商品チャンク: {indexing_result['product_chunks']}")
                print(f"  - FAQチャンク: {indexing_result['faq_chunks']}")
                print(f"  評価実行中...")
                evaluation_service = SearchEvaluationService(settings)
                eval_result = evaluation_service.evaluate_strategy(
                    vector_repo, combination_name, top_k=3
                )
                results[combination_name] = eval_result
                overall_metrics = eval_result["overall_metrics"]
                print(f"  結果:")
                print(f"    - F1スコア: {overall_metrics['avg_f1_score']:.3f}")
                print(f"    - 精度: {overall_metrics['avg_precision']:.3f}")
                print(f"    - 再現率: {overall_metrics['avg_recall']:.3f}")
                print(f"    - ヒット率: {overall_metrics['hit_rate']:.3f}")
            except Exception as e:
                logger.error(f"Failed to benchmark {combination_name}: {e}")
                print(f"  ❌ エラー: {e}")
                continue
        print("\n📊 ベンチマーク結果分析")
        if len(results) > 1:
            evaluation_service = SearchEvaluationService(settings)
            comparison = evaluation_service.compare_strategies(results)
            print("\n=== 最高性能戦略 ===")
            for metric, best in comparison["best_strategy"].items():
                if isinstance(best, dict):
                    print(f"{metric}: {best['strategy']} ({best['value']:.3f})")
            print("\n=== 性能比較表 ===")
            print(f"{'戦略組み合わせ':<20} {'F1':<6} {'精度':<6} {'再現率':<6} {'ヒット率':<6} {'チャンク数':<8}")
            print("-" * 60)
            for combination_name, eval_result in results.items():
                metrics = eval_result["overall_metrics"]
                indexing_info = indexing_results.get(combination_name, {})
                total_chunks = indexing_info.get("total_chunks", 0)
                print(f"{combination_name:<20} "
                      f"{metrics['avg_f1_score']:<6.3f} "
                      f"{metrics['avg_precision']:<6.3f} "
                      f"{metrics['avg_recall']:<6.3f} "
                      f"{metrics['hit_rate']:<6.3f} "
                      f"{total_chunks:<8}")
        print("\n✅ ベンチマーク完了!")
        
    except KeyboardInterrupt:
        print("\n❌ ベンチマークが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        logger.error(f"Integrated benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 