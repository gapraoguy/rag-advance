import sys
import logging

from presentation.cli.application import CLIApplication
from config.logging_config import setup_logging


def main() -> None:
    """メインエントリーポイント"""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        app = CLIApplication()
        app.initialize()
        app.run()
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 