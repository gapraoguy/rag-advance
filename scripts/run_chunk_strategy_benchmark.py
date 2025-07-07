#!/usr/bin/env python3

import sys
import os
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.settings import Settings
from application.services.benchmark_service import BenchmarkService
from infrastructure.repositories.json_product_repository import JsonProductRepository
from infrastructure.repositories.chroma_vector_search_repository import ChromaVectorSearchRepository


def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('benchmark.log')
        ]
    )


def main():
    """チャンク戦略ベンチマーク実行"""
    try:
        setup_logging()
        logger = logging.getLogger(__name__)
        
        print("="*60)
        print("チャンク戦略ベンチマーク実行")
        print("="*60)
        
        settings = Settings.from_env()
        logger.info("Settings loaded successfully")
        
        if not settings.openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        product_repo = JsonProductRepository(settings)
        
        def create_vector_repo(strategy: str, clear_existing: bool = True):
            collection_name = f"{settings.chroma_collection_name}_{strategy}"
            strategy_settings = Settings(
                openai_api_key=settings.openai_api_key,
                llm_model=settings.llm_model,
                embedding_model=settings.embedding_model,
                temperature=settings.temperature,
                chroma_persist_directory=settings.chroma_persist_directory,
                chroma_collection_name=collection_name,
                data_directory=settings.data_directory,
                products_file=settings.products_file,
                faq_file=settings.faq_file,
                support_file=settings.support_file,
                default_search_results=settings.default_search_results,
                chunk_strategy=strategy
            )
            
            if clear_existing:
                vector_repo = ChromaVectorSearchRepository(strategy_settings)
                try:
                    vector_repo.delete_collection()
                    logger.info(f"Cleared existing collection: {collection_name}")
                except:
                    pass
                return ChromaVectorSearchRepository(strategy_settings)
            else:
                return ChromaVectorSearchRepository(strategy_settings)
        
        benchmark_service = BenchmarkService(
            product_repo=product_repo,
            settings=settings,
            vector_repo_factory=create_vector_repo
        )
        
        print("\n🚀 ベンチマーク開始...")
        print("以下の戦略を比較評価します:")
        print("- UNIFIED: 全情報統合型")
        print("- SECTION: セクション分割型") 
        print("- GRANULAR: 細粒度分割型")
        print("\nテストクエリ実行中...")
        
        results = benchmark_service.run_full_benchmark(top_k=3)
        
        benchmark_service.print_summary(results)
        
        output_file = benchmark_service.save_benchmark_results(results)
        print(f"\n詳細結果を保存しました: {output_file}")
        
        summary = results.get("summary", {})
        if "performance_overview" in summary:
            unified_f1 = summary["performance_overview"].get("unified", {}).get("f1_score", 0)
            
            best_f1 = 0
            best_strategy = "unified"
            for strategy, metrics in summary["performance_overview"].items():
                if metrics["f1_score"] > best_f1:
                    best_f1 = metrics["f1_score"]
                    best_strategy = strategy
            
            if best_strategy != "unified":
                improvement_pct = ((best_f1 - unified_f1) / unified_f1 * 100) if unified_f1 > 0 else 0
                print(f"\n🎉 Issue #4完了条件達成状況:")
                print(f"最高性能: {best_strategy.upper()}戦略 (F1: {best_f1:.3f})")
                if improvement_pct >= 10:
                    print(f"✅ 10%以上の精度向上を達成! ({improvement_pct:.1f}%向上)")
                else:
                    print(f"⚠️  改善は見られますが10%には届きませんでした ({improvement_pct:.1f}%向上)")
            else:
                print(f"\n📊 統合型戦略が最高性能でした (F1: {best_f1:.3f})")
        
        print("\n✅ ベンチマーク完了!")
        
    except KeyboardInterrupt:
        print("\n❌ ベンチマークが中断されました")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ エラーが発生しました: {e}")
        logger.error(f"Benchmark failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 