from domain.entities.query_result import QueryResult


class CLIPresenter:
    """CLI表示ロジック担当

    ユーザーインターフェースの表示責務を担当する
    """

    def show_welcome(self) -> None:
        """ウェルカムメッセージを表示"""
        print("\n=== TechMart ChatBot ===")
        print("商品情報やFAQについてご質問ください。")
        print("特別なコマンド:")
        print("- 'exit' または 'quit' : 終了")

    def show_message(self, message: str) -> None:
        """一般的なメッセージを表示"""
        print(message)

    def show_error(self, error_message: str) -> None:
        """エラーメッセージを表示"""
        print(f"❌ {error_message}")

    def show_success(self, success_message: str) -> None:
        """成功メッセージを表示"""
        print(f"✅ {success_message}")

    def show_goodbye(self) -> None:
        """終了メッセージを表示"""
        print("\nご利用ありがとうございました。")

    def show_interrupt(self) -> None:
        """中断メッセージを表示"""
        print("\n\n中断されました。")

    def display_query_result(self, result: QueryResult) -> None:
        """検索結果を表示"""
        print("\n" + "=" * 50)
        print("【回答】")
        print("=" * 50)
        print(result.answer)

        if result.source_documents:
            print("\n" + "=" * 50)
            print("【参照した商品情報】")
            print("=" * 50)

            for i, doc in enumerate(result.source_documents, 1):
                print(f"\n--- 参照 {i} ---")
                print(
                    doc.page_content[:200] + "..."
                    if len(doc.page_content) > 200
                    else doc.page_content
                )

                if doc.metadata:
                    data_type = doc.metadata.get("data_type", "product")
                    if data_type == "faq":
                        faq_id = doc.metadata.get("faq_id", "不明")
                        category = doc.metadata.get("category", "不明")
                        print(f"\nFAQ ID: {faq_id}, カテゴリ: {category}")
                    else:
                        product_id = doc.metadata.get("product_id", "不明")
                        product_name = doc.metadata.get("product_name", "不明")
                        print(f"\n商品ID: {product_id}, 商品名: {product_name}")

                if hasattr(doc, "score") and doc.score:
                    print(f"関連度スコア: {doc.score:.4f}")

        print("\n" + "=" * 50 + "\n")

    def prompt_question(self) -> str:
        """質問の入力を促す"""
        return input("ご質問をどうぞ: ").strip()
