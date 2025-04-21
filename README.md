# CodeToWiki

## 実行方法

### 必要環境
- Python 3.12以上
- uv

### インストール
```bash
uv sync
```

### 環境変数
```bash
# .env.example をコピーして .env を作成し、必要な値を設定
cp .env.example .env
```

## Docker ComposeでArangoDBを起動

プロジェクトルートにある `docker-compose.yml` を使って ArangoDB を起動します:

```bash
docker compose up -d
```

- Web UI: http://localhost:8529
- デフォルトユーザー: root / 環境変数 `ARANGO_PASSWORD` の値

### 出力ファイル
- 生成されたWikiは `docs/generated_wiki.md` に保存されます。

### コマンド例
```bash
cd src
uv run python -m main --code-dir ./ --output ../docs/generated_wiki.md --log-level INFO
```

