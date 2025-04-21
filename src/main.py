# main.py
from analyzer import analyze_codebase
from arango_client import ArangoWikiClient
from wiki_generator import generate_wiki
import os
from dotenv import load_dotenv
import argparse
import logging

# .envファイルから環境変数を読み込む
load_dotenv()

SRC_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SRC_DIR)
CODE_DIR = os.path.join(PROJECT_ROOT, "src")


def main():
    parser = argparse.ArgumentParser(description="コードベースからWikiを生成するツール")
    parser.add_argument(
        "--code-dir", default=CODE_DIR, help="解析対象のコードディレクトリ"
    )
    parser.add_argument(
        "--output",
        default=os.path.join(PROJECT_ROOT, "docs", "generated_wiki.md"),
        help="出力先Markdownファイルパス",
    )
    parser.add_argument("--log-level", default="INFO", help="ログレベル")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s: %(message)s",
    )
    logging.info(f"解析開始: {args.code_dir}")

    analysis_results = analyze_codebase(args.code_dir)

    arango = ArangoWikiClient()
    arango.save_analysis(analysis_results)

    wiki_md = generate_wiki(analysis_results)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(wiki_md)

    logging.info(f"Wiki生成が完了しました: {args.output}")


if __name__ == "__main__":
    main()
