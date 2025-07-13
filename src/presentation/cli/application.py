import logging
import sys
from typing import Optional

from presentation.cli.container import DIContainer
from presentation.cli.handlers import QuestionHandler
from presentation.cli.presenter import CLIPresenter

logger = logging.getLogger(__name__)


class CLIApplication:
    """CLIアプリケーション

    アプリケーションのライフサイクルを管理し、
    各コンポーネントを協調させる
    """

    def __init__(self):
        self.container = DIContainer()
        self.presenter = CLIPresenter()
        self.question_handler: Optional[QuestionHandler] = None

    def initialize(self) -> None:
        """アプリケーションを初期化"""
        try:
            logger.info("Initializing CLI application...")

            self.container.initialize()

            self.question_handler = QuestionHandler(self.container, self.presenter)

            logger.info("CLI application initialized successfully")

        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            self.presenter.show_error(f"設定エラー: {e}")
            self.presenter.show_message("環境変数を確認してください。")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            self.presenter.show_error(f"アプリケーションの初期化に失敗しました: {e}")
            sys.exit(1)

    def run(self) -> None:
        """アプリケーションのメインループを実行"""
        try:
            self.presenter.show_welcome()

            while True:
                try:
                    question = self.presenter.prompt_question()

                    if question.lower() in ["exit", "quit", "終了"]:
                        self.presenter.show_goodbye()
                        break

                    assert self.question_handler is not None
                    self.question_handler.handle_question(question)

                except KeyboardInterrupt:
                    self.presenter.show_interrupt()
                    break

        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
            self.presenter.show_error(f"予期しないエラーが発生しました: {e}")
            sys.exit(1)
