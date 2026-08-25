#!/usr/bin/env python3
"""Pagesプロジェクトが存在しないディレクトリを、プロジェクト作成→デプロイ"""
import os, subprocess

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

dirs = [d for d in os.listdir(BASE) if d.endswith("-directory") and d != "dog-care-directory"]
dirs.sort()

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

env = dict(os.environ)
envfile = os.path.join(BASE, ".env")
if os.path.exists(envfile):
    for line in open(envfile, encoding="utf-8"):
        if line.startswith("CLOUDFLARE_API_TOKEN="):
            env["CLOUDFLARE_API_TOKEN"] = line.split("=", 1)[1].strip()

ok = 0
fail = 0
for slug in dirs:
    d = os.path.join(BASE, slug)
    if not os.path.isdir(d):
        continue
    # 1. プロジェクト作成（存在しなければ）
    r = subprocess.run(
        [wrangler, "pages", "project", "create", slug, "--production-branch=main"],
        capture_output=True, text=True, timeout=60, env=env
    )
    # 2. デプロイ
    r2 = subprocess.run(
        [wrangler, "pages", "deploy", d, "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120, env=env
    )
    if r2.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ {slug}: {r2.stderr[-100:]}")

print(f"\n=== 完了: {ok}/{len(dirs)} 成功, {fail} 失敗 ===")
