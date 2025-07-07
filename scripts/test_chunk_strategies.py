#!/usr/bin/env python3

import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent / "src"))

from config.settings import Settings
from infrastructure.repositories.json_product_repository import JsonProductRepository
from application.services.chunk_service import ChunkService


def test_chunk_strategies():
    """チャンク戦略のテストを実行"""
    print("=== チャンク戦略テスト ===\n")
    
    settings = Settings.from_env()
    product_repo = JsonProductRepository(settings)
    
    products = product_repo.get_all_products()
    if not products:
        print("商品データが見つかりません")
        return
    
    test_product = products[0]
    print(f"テスト対象商品: {test_product.product_name} (ID: {test_product.product_id})\n")
    
    strategies = ["unified", "section", "granular"]
    
    for strategy_name in strategies:
        print(f"=== {strategy_name.upper()} 戦略 ===")
        
        chunk_service = ChunkService(strategy_name)
        chunks = chunk_service.generate_chunks(test_product)
        
        print(f"生成されたチャンク数: {len(chunks)}")
        
        for i, chunk in enumerate(chunks, 1):
            print(f"\n--- チャンク {i} ---")
            print(f"ID: {chunk.chunk_id}")
            print(f"メタデータ: {chunk.metadata}")
            print(f"テキスト (最初の200文字):")
            print(chunk.text[:200] + "..." if len(chunk.text) > 200 else chunk.text)
        
        print("\n" + "="*50 + "\n")


if __name__ == "__main__":
    try:
        test_chunk_strategies()
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc() 