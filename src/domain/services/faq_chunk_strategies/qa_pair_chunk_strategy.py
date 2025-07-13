from typing import List
from domain.entities.faq import FAQ
from domain.entities.chunk import Chunk
from domain.services.faq_chunk_strategy import FAQChunkStrategy


class QAPairChunkStrategy(FAQChunkStrategy):
    """Q&A ペア型チャンク戦略
    
    質問と回答を一つのチャンクにまとめる戦略
    """
    
    @property
    def strategy_name(self) -> str:
        return "qa_pair"
    
    def create_chunks_for_faq(self, faq: FAQ) -> List[Chunk]:
        """質問と回答をペアにしたチャンクを生成"""
        
        text = f"""Q: {faq.question}

A: {faq.answer}"""
        
        metadata = {
            "faq_id": faq.faq_id,
            "category": faq.category,
            "chunk_type": "qa_pair",
            "data_type": "faq",
            "question": faq.question,
            "answer": faq.answer
        }
        
        chunk = Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{faq.faq_id}_qa_pair"
        )
        
        return [chunk] 

    def create_chunks_for_faqs(self, faqs_by_category: dict) -> list:
        """
        この戦略では複数FAQをまとめたチャンクのリストの生成はサポートしない
        """
        raise NotImplementedError("This strategy does not support generating a list of chunks from multiple FAQs.")