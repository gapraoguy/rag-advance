import logging
from typing import Dict, List

from domain.entities.chunk import Chunk
from domain.entities.faq import FAQ
from domain.services.faq_chunk_strategies.category_unified_chunk_strategy import (
    CategoryUnifiedChunkStrategy,
)
from domain.services.faq_chunk_strategies.qa_pair_chunk_strategy import QAPairChunkStrategy
from domain.services.faq_chunk_strategies.qa_separate_chunk_strategy import QASeparateChunkStrategy
from domain.services.faq_chunk_strategy import FAQChunkStrategy

logger = logging.getLogger(__name__)


class FAQChunkService:
    """FAQ用チャンク生成サービス

    異なるFAQチャンク戦略を使用してFAQからチャンクを生成する
    """

    def __init__(self, strategy_name: str = "qa_pair"):
        self._strategies = self._initialize_strategies()
        self._current_strategy = self._get_strategy(strategy_name)
        logger.info(f"Initialized FAQChunkService with strategy: {strategy_name}")

    def _initialize_strategies(self) -> Dict[str, FAQChunkStrategy]:
        """利用可能な戦略を初期化"""
        return {
            "qa_pair": QAPairChunkStrategy(),
            "qa_separate": QASeparateChunkStrategy(),
            "category_unified": CategoryUnifiedChunkStrategy(),
        }

    def _get_strategy(self, strategy_name: str) -> FAQChunkStrategy:
        """戦略名から戦略インスタンスを取得"""
        if strategy_name not in self._strategies:
            available = ", ".join(self._strategies.keys())
            raise ValueError(
                f"Unknown FAQ strategy: {strategy_name}. Available strategies: {available}"
            )

        return self._strategies[strategy_name]

    def generate_chunks(self, faq: FAQ) -> List[Chunk]:
        """FAQからチャンクを生成"""
        try:
            chunks = self._current_strategy.create_chunks_for_faq(faq)
            logger.info(
                f"Generated {len(chunks)} chunks for FAQ {faq.faq_id} "
                f"using {self._current_strategy.strategy_name} strategy"
            )
            return chunks
        except Exception as e:
            logger.error(f"Failed to generate chunks for FAQ {faq.faq_id}: {e}")
            raise RuntimeError(f"Chunk generation failed for FAQ {faq.faq_id}: {e}")

    def generate_chunks_for_faqs(self, faqs: List[FAQ]) -> List[Chunk]:
        """複数FAQからチャンクを一括生成"""
        if self._current_strategy.strategy_name == "category_unified":
            return self._generate_category_unified_chunks(faqs)

        all_chunks = []

        for faq in faqs:
            try:
                chunks = self.generate_chunks(faq)
                all_chunks.extend(chunks)
            except Exception as e:
                logger.warning(f"Skipping FAQ {faq.faq_id} due to error: {e}")
                continue

        logger.info(f"Generated total {len(all_chunks)} chunks from {len(faqs)} FAQs")
        return all_chunks

    def _generate_category_unified_chunks(self, faqs: List[FAQ]) -> List[Chunk]:
        """カテゴリ統合戦略で複数FAQからチャンクを生成"""
        faqs_by_category = {}

        for faq in faqs:
            if faq.category not in faqs_by_category:
                faqs_by_category[faq.category] = []
            faqs_by_category[faq.category].append(faq)

        strategy = self._strategies["category_unified"]
        chunks = strategy.create_chunks_for_faqs(faqs_by_category)

        logger.info(
            f"Generated {len(chunks)} category-unified chunks from "
            f"{len(faqs)} FAQs across {len(faqs_by_category)} categories"
        )

        return chunks
