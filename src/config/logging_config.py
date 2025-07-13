import logging
from typing import Optional, List


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    format_string: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> None:
    """ログ設定を初期化
    
    Args:
        level: ログレベル（デフォルト: INFO）
        log_file: ログファイル名（Noneの場合はコンソールのみ）
        format_string: ログフォーマット
    """
    handlers: List[logging.Handler] = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=handlers
    )
    
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING) 