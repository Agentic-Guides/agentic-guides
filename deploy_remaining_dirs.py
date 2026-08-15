#!/usr/bin/env python3
"""残りのディレクトリサイトを上限に達するまで一括デプロイする。
失敗（プロジェクト上限）したら停止する。
"""
import os, subprocess, sys

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# 既にデプロイ済み（200確認済み）
DONE = {"dog-care-directory","cat-care-directory","diy-home-directory","gardening-directory",
        "cooking-directory","baking-directory","travel-directory","camping-directory",
        "fitness-directory","yoga-directory","car-care-directory"}

# 全98ディレクトリ
ALL = sorted(d for d in os.listdir(BASE) if d.endswith("-directory") and os.path.isdir(d))

# 残り
REMAINING = [s for s in ALL if s not in DONE]

print(f"全{len(ALL)}個、既に{len(DONE)}個、残り{len(REMAINING)}個")

TOKEN = os.environ.get("CLOUDFLARE_API_TOKEN", "")
if not TOKEN:
    print("CLOUDFLARE_API_TOKEN 未設定")
    sys.exit(1)

# wrangler.cmd のフルパス（Windowsでnpxを直接呼べないため）
WRANGLER = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(WRANGLER):
    WRANGLER = "npx wrangler"

ok, fail = 0, 0
for slug in REMAINING:
    # プロジェクト作成（上限で失敗したら停止）
    r = subprocess.run(
        [WRANGLER, "pages", "project", "create", slug, "--production-branch", "main"],
        capture_output=True, text=True, timeout=60,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": TOKEN}
    )
    if "Successfully created" not in r.stdout and "already exists" not in r.stdout:
        print(f"❌ {slug}: プロジェクト作成失敗（上限到達の可能性）")
        print(r.stdout[-300:])
        break
    # デプロイ
    r = subprocess.run(
        [WRANGLER, "pages", "deploy", os.path.join(BASE, slug),
         "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120,
        env={**os.environ, "CLOUDFLARE_API_TOKEN": TOKEN}
    )
    if "Deployment complete" in r.stdout:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"⚠️ {slug}: デプロイ失敗")
        print(r.stdout[-200:])

print(f"\n=== 完了: 成功{ok}, 失敗{fail} ===")
