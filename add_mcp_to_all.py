#!/usr/bin/env python3
"""既存の全サイトに .well-known/mcp.json を一括追加する。
site_builder.build_mcp_json を再利用し、各サイトディレクトリに書き出す。
"""
import sys, os, json
BASE = os.path.expanduser("~/Desktop/agentic-sites")
sys.path.insert(0, BASE)
import site_builder as sb

def add_mcp_to_all():
    # 全サイトディレクトリを走査（ディレクトリ名=slug）
    count = 0
    for slug in sorted(os.listdir(BASE)):
        d = os.path.join(BASE, slug)
        if not os.path.isdir(d) or slug.startswith(".") or slug.startswith("_"):
            continue
        # サイト設定を取得（英語優先、なければ日本語）
        site = None
        for lang in ("en", "ja"):
            try:
                site = sb.get_site(slug, lang=lang)
                if site:
                    break
            except Exception:
                continue
        if not site:
            continue
        # mcp.json を書き出す
        wk = os.path.join(d, ".well-known")
        os.makedirs(wk, exist_ok=True)
        mcp = sb.build_mcp_json(site)
        with open(os.path.join(wk, "mcp.json"), "w", encoding="utf-8") as f:
            f.write(mcp)
        count += 1
        print(f"  {slug}: mcp.json 追加")
    print(f"✅ {count}サイトに mcp.json を追加")

if __name__ == "__main__":
    add_mcp_to_all()
