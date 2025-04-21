# arango_client.py
from typing import List, Dict
import os
from arango import ArangoClient
from arango.exceptions import DatabaseCreateError
import logging

logger = logging.getLogger(__name__)


class ArangoWikiClient:
    def __init__(self):
        endpoint = os.getenv("ARANGO_ENDPOINT", "http://localhost:8529")
        user = os.getenv("ARANGO_USER", "root")
        pwd = os.getenv("ARANGO_PASSWORD", "")
        client = ArangoClient(hosts=[endpoint])
        db_name = os.getenv("ARANGO_DB", "codewiki")
        # 認証付きで system DB 経由でデータベース作成
        system_db = client.db("_system", username=user, password=pwd)
        try:
            system_db.create_database(db_name)
            logger.info(f"データベース作成: {db_name}")
        except DatabaseCreateError:
            logger.info(f"データベース {db_name} は既に存在します, 作成をスキップ")
        except Exception as e:
            logger.error(f"データベース作成失敗: {e}")
            raise
        self.db = client.db(db_name, username=user, password=pwd)

    def save_analysis(self, analysis: List[Dict]):
        if not self.db.has_collection("files"):
            self.db.create_collection("files")
        col = self.db.collection("files")
        for entry in analysis:
            try:
                col.insert(entry)
                logger.info(f"保存成功: {entry['file']}")
            except Exception as e:
                logger.error(f"ArangoDB保存エラー: {entry['file']} - {e}")
