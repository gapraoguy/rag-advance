import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

from config.settings import Settings
from domain.repositories.vector_search_repository import VectorSearchRepository

logger = logging.getLogger(__name__)


class SearchEvaluationService:
    """検索評価サービス

    テストクエリを使用して検索精度を評価する
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.test_queries = self._load_test_queries()

    def _load_test_queries(self) -> List[Dict[str, Any]]:
        """テストクエリを読み込み"""
        try:
            test_queries_path = Path(self.settings.data_directory) / "test_queries.json"

            if not test_queries_path.exists():
                raise FileNotFoundError(f"Test queries file not found: {test_queries_path}")

            with open(test_queries_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            queries = data.get("test_queries", [])
            logger.info(f"Loaded {len(queries)} test queries")
            return queries

        except Exception as e:
            logger.error(f"Failed to load test queries: {e}")
            raise RuntimeError(f"Failed to load test queries: {e}")

    def evaluate_strategy(
        self, vector_repo: VectorSearchRepository, strategy_name: str, top_k: int = 3
    ) -> Dict[str, Any]:
        """指定戦略の検索精度を評価"""
        try:
            logger.info(f"Evaluating strategy: {strategy_name}")

            query_results = []
            total_precision = 0.0
            total_recall = 0.0
            total_f1 = 0.0
            relevant_found = 0

            for test_query in self.test_queries:
                query_id = test_query["query_id"]
                query_text = test_query["query"]
                query_type = test_query["query_type"]

                expected_products = set(test_query.get("expected_products", []))
                expected_faqs = set(test_query.get("expected_faqs", []))

                try:
                    search_results = vector_repo.search(query_text, top_k)

                    found_products = set()
                    found_faqs = set()

                    for doc in search_results:
                        data_type = doc.metadata.get("data_type", "product")
                        if data_type == "faq" and "faq_id" in doc.metadata:
                            found_faqs.add(doc.metadata["faq_id"])
                        elif "product_id" in doc.metadata:
                            found_products.add(doc.metadata["product_id"])

                    if expected_faqs:
                        precision, recall, f1 = self._calculate_metrics(expected_faqs, found_faqs)
                        has_relevant = len(expected_faqs.intersection(found_faqs)) > 0
                    else:
                        precision, recall, f1 = self._calculate_metrics(
                            expected_products, found_products
                        )
                        has_relevant = len(expected_products.intersection(found_products)) > 0

                    if has_relevant:
                        relevant_found += 1

                    query_result = {
                        "query_id": query_id,
                        "query": query_text,
                        "query_type": query_type,
                        "expected_products": list(expected_products),
                        "expected_faqs": list(expected_faqs),
                        "found_products": list(found_products),
                        "found_faqs": list(found_faqs),
                        "precision": precision,
                        "recall": recall,
                        "f1_score": f1,
                        "has_relevant": has_relevant,
                        "search_results": [
                            {
                                "id": doc.metadata.get(
                                    (
                                        "faq_id"
                                        if doc.metadata.get("data_type") == "faq"
                                        else "product_id"
                                    ),
                                    "unknown",
                                ),
                                "data_type": doc.metadata.get("data_type", "product"),
                                "chunk_section": doc.metadata.get("chunk_section", "unknown"),
                                "score": doc.score,
                                "text_preview": doc.page_content[:100] + "...",
                            }
                            for doc in search_results
                        ],
                    }

                    query_results.append(query_result)

                    total_precision += precision
                    total_recall += recall
                    total_f1 += f1

                except Exception as e:
                    logger.error(f"Failed to evaluate query {query_id}: {e}")
                    continue

            num_queries = len(query_results)

            evaluation_result = {
                "strategy": strategy_name,
                "total_queries": num_queries,
                "top_k": top_k,
                "overall_metrics": {
                    "avg_precision": (total_precision / num_queries if num_queries > 0 else 0.0),
                    "avg_recall": (total_recall / num_queries if num_queries > 0 else 0.0),
                    "avg_f1_score": total_f1 / num_queries if num_queries > 0 else 0.0,
                    "hit_rate": (relevant_found / num_queries if num_queries > 0 else 0.0),
                },
                "query_type_breakdown": self._analyze_by_query_type(query_results),
                "detailed_results": query_results,
            }

            logger.info(
                f"Strategy {strategy_name} evaluation completed - "
                f"Avg F1: {evaluation_result['overall_metrics']['avg_f1_score']:.3f}, "
                f"Hit Rate: {evaluation_result['overall_metrics']['hit_rate']:.3f}"
            )

            return evaluation_result

        except Exception as e:
            logger.error(f"Failed to evaluate strategy {strategy_name}: {e}")
            raise RuntimeError(f"Evaluation failed: {e}")

    def _calculate_metrics(self, expected: set, found: set) -> Tuple[float, float, float]:
        """Precision, Recall, F1スコアを計算"""
        if len(found) == 0:
            precision = 0.0
        else:
            precision = len(expected.intersection(found)) / len(found)

        if len(expected) == 0:
            recall = 0.0
        else:
            recall = len(expected.intersection(found)) / len(expected)

        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)

        return precision, recall, f1

    def _analyze_by_query_type(
        self, query_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, float]]:
        """クエリタイプ別の性能分析"""
        type_stats = {}

        for result in query_results:
            query_type = result["query_type"]

            if query_type not in type_stats:
                type_stats[query_type] = {
                    "count": 0,
                    "total_precision": 0.0,
                    "total_recall": 0.0,
                    "total_f1": 0.0,
                    "hits": 0,
                }

            stats = type_stats[query_type]
            stats["count"] += 1
            stats["total_precision"] += result["precision"]
            stats["total_recall"] += result["recall"]
            stats["total_f1"] += result["f1_score"]
            if result["has_relevant"]:
                stats["hits"] += 1

        for query_type, stats in type_stats.items():
            count = stats["count"]
            type_stats[query_type] = {
                "count": count,
                "avg_precision": stats["total_precision"] / count,
                "avg_recall": stats["total_recall"] / count,
                "avg_f1_score": stats["total_f1"] / count,
                "hit_rate": stats["hits"] / count,
            }

        return type_stats

    def compare_strategies(self, strategy_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """戦略間の比較分析"""
        try:
            comparison = {
                "strategies_compared": list(strategy_results.keys()),
                "metrics_comparison": {},
                "best_strategy": {},
                "improvement_analysis": {},
            }

            for metric in ["avg_precision", "avg_recall", "avg_f1_score", "hit_rate"]:
                comparison["metrics_comparison"][metric] = {}

                for strategy, result in strategy_results.items():
                    value = result["overall_metrics"][metric]
                    comparison["metrics_comparison"][metric][strategy] = value

            for metric in ["avg_precision", "avg_recall", "avg_f1_score", "hit_rate"]:
                metric_values = comparison["metrics_comparison"][metric]
                best_strategy = max(metric_values.items(), key=lambda x: x[1])
                comparison["best_strategy"][metric] = {
                    "strategy": best_strategy[0],
                    "value": best_strategy[1],
                }

            if "unified" in strategy_results:
                baseline = strategy_results["unified"]["overall_metrics"]

                for strategy, result in strategy_results.items():
                    if strategy == "unified":
                        continue

                    current = result["overall_metrics"]
                    improvement = {}

                    for metric in [
                        "avg_precision",
                        "avg_recall",
                        "avg_f1_score",
                        "hit_rate",
                    ]:
                        baseline_value = baseline[metric]
                        current_value = current[metric]

                        if baseline_value > 0:
                            improvement_pct = (
                                (current_value - baseline_value) / baseline_value
                            ) * 100
                        else:
                            improvement_pct = 0.0

                        improvement[metric] = {
                            "baseline": baseline_value,
                            "current": current_value,
                            "improvement_pct": improvement_pct,
                        }

                    comparison["improvement_analysis"][strategy] = improvement

            return comparison

        except Exception as e:
            logger.error(f"Failed to compare strategies: {e}")
            raise RuntimeError(f"Strategy comparison failed: {e}")
