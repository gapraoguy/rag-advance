import json
from typing import Dict, Any, List, Optional
from pathlib import Path
import logging
from datetime import datetime

from config.settings import Settings
from domain.repositories.product_repository import ProductRepository
from domain.repositories.vector_search_repository import VectorSearchRepository
from application.services.indexing_service import IndexingService
from application.services.search_evaluation_service import SearchEvaluationService


logger = logging.getLogger(__name__)


class BenchmarkService:
    """ベンチマーク実行サービス
    
    全チャンク戦略の比較評価を実行する
    """
    
    def __init__(
        self,
        product_repo: ProductRepository,
        settings: Settings,
        vector_repo_factory=None
    ):
        self.settings = settings
        self.product_repo = product_repo
        self.indexing_service = IndexingService(product_repo, settings)
        self.evaluation_service = SearchEvaluationService(settings)
        self.vector_repo_factory = vector_repo_factory
    
    def run_full_benchmark(self, top_k: int = 3) -> Dict[str, Any]:
        """全チャンク戦略の完全ベンチマークを実行"""
        if self.vector_repo_factory is None:
            raise ValueError("vector_repo_factory is required for benchmark execution")
            
        try:
            logger.info("Starting full benchmark evaluation")
            start_time = datetime.now()
            
            logger.info("Step 1: Indexing all strategies")
            indexing_results = {}
            strategies = ["unified", "section", "granular"]
            
            for strategy in strategies:
                try:
                    vector_repo = self.vector_repo_factory(strategy, True)
                    indexing_results[strategy] = self.indexing_service.index_with_strategy(
                        vector_repo, strategy
                    )
                except Exception as e:
                    logger.error(f"Failed to index strategy {strategy}: {e}")
                    indexing_results[strategy] = {
                        "strategy": strategy,
                        "success": False,
                        "error": str(e)
                    }
            
            logger.info("Step 2: Evaluating search performance")
            evaluation_results = {}
            
            for strategy in strategies:
                if indexing_results[strategy]["success"]:
                    try:
                        vector_repo = self.vector_repo_factory(strategy, False)
                        evaluation_results[strategy] = self.evaluation_service.evaluate_strategy(
                            vector_repo, strategy, top_k
                        )
                        
                    except Exception as e:
                        logger.error(f"Failed to evaluate strategy {strategy}: {e}")
                        evaluation_results[strategy] = {
                            "strategy": strategy,
                            "success": False,
                            "error": str(e)
                        }
                else:
                    logger.warning(f"Skipping evaluation for {strategy} due to indexing failure")
                    evaluation_results[strategy] = {
                        "strategy": strategy,
                        "success": False,
                        "error": "Indexing failed"
                    }
            
            logger.info("Step 3: Comparing strategies")
            successful_evaluations = {
                k: v for k, v in evaluation_results.items() 
                if v.get("success", True) and "overall_metrics" in v
            }
            
            if len(successful_evaluations) > 1:
                comparison = self.evaluation_service.compare_strategies(successful_evaluations)
            else:
                comparison = {"error": "Not enough successful evaluations for comparison"}
            
            logger.info("Step 4: Collecting chunk statistics")
            chunk_statistics = {}
            for strategy in ["unified", "section", "granular"]:
                try:
                    chunk_statistics[strategy] = self.indexing_service.get_chunk_statistics(strategy)
                except Exception as e:
                    logger.error(f"Failed to get statistics for {strategy}: {e}")
                    chunk_statistics[strategy] = {"error": str(e)}
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            benchmark_result = {
                "benchmark_info": {
                    "timestamp": start_time.isoformat(),
                    "duration_seconds": duration,
                    "top_k": top_k,
                    "total_test_queries": len(self.evaluation_service.test_queries)
                },
                "indexing_results": indexing_results,
                "chunk_statistics": chunk_statistics,
                "evaluation_results": evaluation_results,
                "strategy_comparison": comparison,
                "summary": self._generate_summary(evaluation_results, comparison)
            }
            
            logger.info(f"Full benchmark completed in {duration:.2f} seconds")
            return benchmark_result
            
        except Exception as e:
            logger.error(f"Benchmark failed: {e}")
            raise RuntimeError(f"Benchmark execution failed: {e}")
    
    def _generate_summary(
        self,
        evaluation_results: Dict[str, Any],
        comparison: Dict[str, Any]
    ) -> Dict[str, Any]:
        """ベンチマーク結果のサマリーを生成"""
        try:
            summary = {
                "best_strategies": {},
                "performance_overview": {},
                "recommendations": []
            }
            
            successful_results = {
                k: v for k, v in evaluation_results.items() 
                if v.get("success", True) and "overall_metrics" in v
            }
            
            if not successful_results:
                summary["error"] = "No successful evaluations to summarize"
                return summary
            
            if "best_strategy" in comparison:
                summary["best_strategies"] = comparison["best_strategy"]
            
            for strategy, result in successful_results.items():
                metrics = result["overall_metrics"]
                summary["performance_overview"][strategy] = {
                    "f1_score": round(metrics["avg_f1_score"], 3),
                    "precision": round(metrics["avg_precision"], 3),
                    "recall": round(metrics["avg_recall"], 3),
                    "hit_rate": round(metrics["hit_rate"], 3)
                }
            
            if "improvement_analysis" in comparison:
                unified_baseline = evaluation_results.get("unified", {}).get("overall_metrics", {})
                
                for strategy, improvement in comparison["improvement_analysis"].items():
                    f1_improvement = improvement.get("avg_f1_score", {}).get("improvement_pct", 0)
                    
                    if f1_improvement > 10:
                        summary["recommendations"].append(
                            f"{strategy}戦略は統合型に比べてF1スコアが{f1_improvement:.1f}%向上しており、推奨されます"
                        )
                    elif f1_improvement > 0:
                        summary["recommendations"].append(
                            f"{strategy}戦略は統合型に比べて{f1_improvement:.1f}%の改善が見られます"
                        )
                    else:
                        summary["recommendations"].append(
                            f"{strategy}戦略は統合型と比較して改善が見られませんでした"
                        )
            
            if summary["best_strategies"].get("avg_f1_score"):
                best_overall = summary["best_strategies"]["avg_f1_score"]["strategy"]
                best_value = summary["best_strategies"]["avg_f1_score"]["value"]
                summary["recommendations"].append(
                    f"総合的には{best_overall}戦略が最も高いF1スコア({best_value:.3f})を達成しました"
                )
            
            return summary
            
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")
            return {"error": f"Summary generation failed: {e}"}
    
    def save_benchmark_results(
        self,
        results: Dict[str, Any],
        output_file: Optional[str] = None
    ) -> str:
        """ベンチマーク結果をファイルに保存"""
        try:
            if output_file is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"benchmark_results_{timestamp}.json"
            
            benchmark_dir = Path(self.settings.data_directory) / "benchmark_results"
            benchmark_dir.mkdir(exist_ok=True)
            
            output_path = benchmark_dir / output_file
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Benchmark results saved to: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {e}")
            raise RuntimeError(f"Failed to save results: {e}")
    
    def print_summary(self, results: Dict[str, Any]) -> None:
        """ベンチマーク結果のサマリーを表示"""
        try:
            print("\n" + "="*60)
            print("チャンク戦略ベンチマーク結果")
            print("="*60)
            
            info = results.get("benchmark_info", {})
            print(f"実行時刻: {info.get('timestamp', 'N/A')}")
            print(f"実行時間: {info.get('duration_seconds', 0):.2f}秒")
            print(f"テストクエリ数: {info.get('total_test_queries', 0)}件")
            print(f"Top-K: {info.get('top_k', 3)}")
            
            summary = results.get("summary", {})
            if "performance_overview" in summary:
                print("\n--- 性能概要 ---")
                for strategy, metrics in summary["performance_overview"].items():
                    print(f"{strategy.upper()}戦略:")
                    print(f"  F1スコア: {metrics['f1_score']:.3f}")
                    print(f"  精度: {metrics['precision']:.3f}")
                    print(f"  再現率: {metrics['recall']:.3f}")
                    print(f"  ヒット率: {metrics['hit_rate']:.3f}")
            
            if "best_strategies" in summary:
                print("\n--- 最高性能戦略 ---")
                for metric, best in summary["best_strategies"].items():
                    if isinstance(best, dict):
                        print(f"{metric}: {best['strategy'].upper()} ({best['value']:.3f})")
            
            if "recommendations" in summary and summary["recommendations"]:
                print("\n--- 推奨事項 ---")
                for i, rec in enumerate(summary["recommendations"], 1):
                    print(f"{i}. {rec}")
            
            print("\n" + "="*60)
            
        except Exception as e:
            logger.error(f"Failed to print summary: {e}")
            print(f"サマリー表示エラー: {e}") 