import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv


@dataclass
class Settings:
    """アプリケーション設定"""
    openai_api_key: str
    llm_model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-large"
    temperature: float = 0.0
    
    chroma_persist_directory: str = "chroma_db"
    chroma_collection_name: str = "products"
    
    data_directory: str = "data"
    products_file: str = "products_master.json"
    faq_file: str = "faq_database.json"
    support_file: str = "support_info.txt"
    
    default_search_results: int = 3
    
    @classmethod
    def from_env(cls) -> 'Settings':
        """環境変数から設定を読み込み"""
        load_dotenv()
        
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        
        return cls(
            openai_api_key=openai_api_key,
            llm_model=os.getenv("LLM_MODEL", cls.llm_model),
            embedding_model=os.getenv("EMBEDDING_MODEL", cls.embedding_model),
            temperature=float(os.getenv("TEMPERATURE", str(cls.temperature))),
            chroma_persist_directory=os.getenv("CHROMA_PERSIST_DIR", cls.chroma_persist_directory),
            chroma_collection_name=os.getenv("CHROMA_COLLECTION", cls.chroma_collection_name),
            data_directory=os.getenv("DATA_DIR", cls.data_directory),
            products_file=os.getenv("PRODUCTS_FILE", cls.products_file),
            faq_file=os.getenv("FAQ_FILE", cls.faq_file),
            support_file=os.getenv("SUPPORT_FILE", cls.support_file),
            default_search_results=int(os.getenv("DEFAULT_SEARCH_RESULTS", str(cls.default_search_results)))
        ) 