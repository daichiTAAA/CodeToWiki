# analyzer.py
import os
from dotenv import load_dotenv
import time

load_dotenv()

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# ロガー初期化
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# LLMとEmbeddingの初期化（APIキーは環境変数で管理）
llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)


# レートリミット時のリトライ関数
def invoke_with_retry(prompt: str, retries: int = 5, delay: float = 1.0):
    for i in range(retries):
        try:
            return llm.invoke(prompt)
        except Exception as e:
            msg = str(e)
            if "Rate limit" in msg or "429" in msg:
                sleep = delay * (2**i)
                logger.warning(f"Rate limitエラー, {sleep}s後にリトライします: {e}")
                time.sleep(sleep)
                continue
            raise
    raise e


def extract_code_entities(code: str) -> Dict[str, Any]:
    """
    コードからクラス・関数名を抽出（簡易版）。
    """
    classes = []
    functions = []
    for line in code.splitlines():
        if line.strip().startswith("class "):
            cname = line.split()[1].split("(")[0]
            classes.append(cname)
        if line.strip().startswith("def "):
            fname = line.split()[1].split("(")[0]
            functions.append(fname)
    return {"classes": classes, "functions": functions}


def _process_file(path, code_dir):
    try:
        logger.info(f"解析中: {path}")
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        entities = extract_code_entities(code)
        summary_resp = invoke_with_retry(
            f"次のPythonコードの要点を200字以内で要約してください:\n\n{code[:2000]}"
        )
        summary = getattr(summary_resp, "content", str(summary_resp))
        chunks = text_splitter.split_text(code)
        embeddings_list = [embeddings.embed_query(c) for c in chunks]
        return {
            "file": os.path.relpath(path, code_dir),
            "classes": entities["classes"],
            "functions": entities["functions"],
            "summary": summary,
            "embeddings": embeddings_list,
        }
    except Exception as e:
        logger.error(f"エラー: {path} を処理中に {e}")
        return None


def analyze_codebase(code_dir: str) -> List[Dict]:
    """
    指定ディレクトリ配下の.pyファイルを解析し、
    LLMで要約・Embeddingを生成して返す。
    """
    results = []
    paths = []
    for root, dirs, files in os.walk(code_dir):
        # 仮想環境や隠しディレクトリを除外
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                paths.append(os.path.join(root, file))
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(_process_file, p, code_dir): p for p in paths}
        for fut in as_completed(futures):
            entry = fut.result()
            if entry:
                results.append(entry)
    return results
