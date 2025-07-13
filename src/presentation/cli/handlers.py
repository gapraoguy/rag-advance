import logging

from presentation.cli.container import DIContainer
from presentation.cli.presenter import CLIPresenter


logger = logging.getLogger(__name__)


class QuestionHandler:
    """質問応答ハンドラー"""
    
    def __init__(self, container: DIContainer, presenter: CLIPresenter):
        self.container = container
        self.presenter = presenter
    
    def handle_question(self, question: str) -> None:
        """質問を処理して回答を表示"""
        try:
            if not question or not question.strip():
                self.presenter.show_message("質問を入力してください。\n")
                return
            
            self.presenter.show_message("\n回答を生成中...")
            result = self.container.rag_service.answer(question)
            self.presenter.display_query_result(result)
            
        except Exception as e:
            logger.error(f"Error during question processing: {e}")
            self.presenter.show_error(f"エラーが発生しました: {e}")
            self.presenter.show_message("もう一度お試しください。\n")