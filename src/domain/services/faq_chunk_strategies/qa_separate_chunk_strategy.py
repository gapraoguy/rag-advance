from typing import List
from domain.entities.faq import FAQ
from domain.entities.chunk import Chunk
from domain.services.faq_chunk_strategy import FAQChunkStrategy


class QASeparateChunkStrategy(FAQChunkStrategy):
    """QA 分離型チャンク戦略
    
    質問と回答を別々のチャンクに分ける戦略
    """
    
    @property
    def strategy_name(self) -> str:
        return "qa_separate"
    
    def create_chunks_for_faq(self, faq: FAQ) -> List[Chunk]:
        """質問と回答を別々のチャンクとして生成"""
        chunks = []
        
        question_chunk = self._create_question_chunk(faq)
        answer_chunk = self._create_answer_chunk(faq)
        
        chunks.append(question_chunk)
        chunks.append(answer_chunk)
        
        return chunks
    
    def create_chunks_for_faqs(self, faqs_by_category: dict) -> list:
        """
        この戦略では複数FAQをまとめたチャンクのリストの生成はサポートしない
        """
        raise NotImplementedError("This strategy does not support generating a list of chunks from multiple FAQs.")
    
    def _create_question_chunk(self, faq: FAQ) -> Chunk:
        """質問チャンクを作成"""
        text = f"""FAQ質問: {faq.question}
カテゴリ: {faq.category}
FAQ ID: {faq.faq_id}"""
        
        metadata = {
            "faq_id": faq.faq_id,
            "category": faq.category,
            "chunk_type": "qa_separate",
            "chunk_section": "question",
            "data_type": "faq",
            "question": faq.question,
            "related_answer": faq.answer
        }
        
        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{faq.faq_id}_question"
        )
    
    def _create_answer_chunk(self, faq: FAQ) -> Chunk:
        """回答チャンクを作成"""
        text = f"""FAQ回答: {faq.answer}
関連質問: {faq.question}
カテゴリ: {faq.category}
FAQ ID: {faq.faq_id}"""
        
        metadata = {
            "faq_id": faq.faq_id,
            "category": faq.category,
            "chunk_type": "qa_separate",
            "chunk_section": "answer",
            "data_type": "faq",
            "answer": faq.answer,
            "related_question": faq.question
        }
        
        return Chunk(
            text=text,
            metadata=metadata,
            chunk_id=f"{faq.faq_id}_answer"
        ) 