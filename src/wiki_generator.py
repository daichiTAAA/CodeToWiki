# wiki_generator.py
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def generate_wiki(analysis: List[Dict]) -> str:
    """
    解析結果からMarkdown形式のWikiを生成
    LLM要約やベクトル情報も記載
    """
    logger.info(f"Wiki生成: {len(analysis)} ファイルを含むMarkdownを作成")
    lines = ["# コード自動Wiki\n"]
    for entry in analysis:
        lines.append(f"## {entry['file']}")
        if entry.get("summary"):
            lines.append(f"> 要約: {entry['summary']}")
        if entry["classes"]:
            lines.append("### クラス:")
            for c in entry["classes"]:
                lines.append(f"- {c}")
        if entry["functions"]:
            lines.append("### 関数:")
            for f in entry["functions"]:
                lines.append(f"- {f}")
        if entry.get("embeddings"):
            lines.append(f"*ベクトル数: {len(entry['embeddings'])}*\n")
        lines.append("")
    return "\n".join(lines)
