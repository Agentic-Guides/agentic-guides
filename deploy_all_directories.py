#!/usr/bin/env python3
"""全ディレクトリサイト（dog-care-directory除く）を一括デプロイ"""
import os, subprocess, sys

BASE = os.path.expanduser("~/Desktop/agentic-sites")
os.chdir(BASE)

# デプロイ対象（dog-care-directory は既にデプロイ済み）
dirs = [d for d in os.listdir(BASE) if d.endswith("-directory") and d != "dog-care-directory"]
dirs.sort()
print(f"デプロイ対象: {len(dirs)} 個")

wrangler = os.path.expanduser("~/AppData/Roaming/npm/wrangler.cmd")
if not os.path.exists(wrangler):
    wrangler = "npx wrangler"

# Cloudflare APIトークン
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
    r = subprocess.run(
        [wrangler, "pages", "deploy", d, "--project-name=" + slug, "--commit-dirty=true", "--branch=main"],
        capture_output=True, text=True, timeout=120, env=env
    )
    if r.returncode == 0:
        ok += 1
        print(f"✅ {slug}")
    else:
        fail += 1
        print(f"❌ {slug}: {r.stderr[-120:]}")

print(f"\n=== 完了: {ok}/{len(dirs)} 成功, {fail} 失敗 ===")
