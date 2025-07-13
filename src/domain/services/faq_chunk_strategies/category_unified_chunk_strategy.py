from typing import List, Dict
from domain.entities.faq import FAQ
from domain.entities.chunk import Chunk
from domain.services.faq_chunk_strategy import FAQChunkStrategy


class CategoryUnifiedChunkStrategy(FAQChunkStrategy):
    """カテゴリ統合型チャンク戦略
    
    同一カテゴリの複数FAQを一つのチャンクにまとめる戦略
    """
    
    @property
    def strategy_name(self) -> str:
        return "category_unified"
    
    def create_chunks_for_faq(self, faq: FAQ) -> List[Chunk]:
        """
        この戦略では個別FAQのチャンク化はサポートしない
        """
        raise NotImplementedError("This strategy does not support individual FAQ chunking.")
    
    def create_chunks_for_faqs(self, faqs_by_category: Dict[str, List[FAQ]]) -> List[Chunk]:
        """
        カテゴリごとに複数FAQをまとめたチャンクのリストを生成
        """
        chunks = []
        for category, faqs in faqs_by_category.items():
            if not faqs:
                continue
            qa_pairs = []
            faq_ids = []
            for faq in faqs:
                qa_pairs.append(f"Q: {faq.question}\nA: {faq.answer}")
                faq_ids.append(faq.faq_id)
            text = f"カテゴリ: {category}\n\n{chr(10).join([f'{i+1}. {qa}' for i, qa in enumerate(qa_pairs)])}"
            metadata = {
                "category": category,
                "chunk_type": "category_unified",
                "data_type": "faq",
                "faq_ids": ",".join(faq_ids),
                "faq_count": len(faqs)
            }
            chunk = Chunk(
                text=text,
                metadata=metadata,
                chunk_id=f"category_{category.replace(' ', '_').lower()}_unified"
            )
            chunks.append(chunk)
        return chunks 