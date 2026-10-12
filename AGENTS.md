# AGENTS.md — agentic-sites

<!-- AI コーディングエージェント（Claude Code / Cursor / Codex / Gemini CLI / Hermes 等）が
     最初に読む指示書。README は人間向け、こちらはエージェント向け。
     形式の詳細: https://agents.md/ -->

[![M8ven Score](https://m8ven.ai/badge/mcp/agentic-guides-agentic-guides-1cf3os)](https://m8ven.ai/mcp/agentic-guides-agentic-guid

## Quickstart

```bash
# <このプロジェクトの起動コマンドを書く>
# <テストコマンドを書く>
```

## プロジェクト構造

- `ai-crypto-newsletter/` — <役割を1行で>
- `ai-tools-directory/` — <役割を1行で>
- `annuity-guide/` — <役割を1行で>
- `appliance-directory/` — <役割を1行で>
- `auto-loan-guide/` — <役割を1行で>
- `baby-directory/` — <役割を1行で>
- `baking-directory/` — <役割を1行で>
- `banking-guide/` — <役割を1行で>

**核（kernel）**: アーキテクチャを定義するディレクトリ。ここへの変更は「毎行レビューされる」
前提で小さく保つ。UI より厳しい基準を適用する。

## 規約

- 既存の仕組みを再利用する。並行する別の仕組みを新設しない。
- 変更したらテストを追加・更新する（誰も頼んでいなくても）。
- コミット前にテストを全部通す。

## 禁止事項

- 認証情報・秘密鍵・トークンを【ファイルに書かない】。環境変数かシークレットストアから読む。
- 確認せずに `git push` しない。確認せずに破壊的操作（削除・上書き）をしない。
- 未確認の数値を結論として書かない。実測してから書く。

## 落とし穴（実際に踏んだものだけ追記する）

- 推測で埋めない。症状と回避策を実測で確認してから書く。

## Windows 固有の注意

- ターミナルは git-bash。PowerShell の組み込みコマンドは動かない。
- ネイティブツール（git / node / python）には `C:/Users/...` 形式のパスを渡す。
- 日本語を含むスクリプトは UTF-8 **BOM 付き** で保存する（PowerShell 5.1 が誤読する）。
- h264 エンコードは**偶数サイズ**が必要（奇数の高さは 0 バイト出力で失敗）。
