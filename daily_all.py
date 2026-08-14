#!/usr/bin/env python3
"""全サイトを毎日更新するラッパー。cronで実行する。"""
import sys, os, subprocess
sys.path.insert(0, os.path.dirname(__file__))

SITES = ["hojokin-nav", "kakutei-guide", "sumai-loan", "fukugyo-master", "kaigo-seido"]

if __name__ == "__main__":
    results = []
    for slug in SITES:
        r = subprocess.run(
            [sys.executable, os.path.join(os.path.dirname(__file__), "daily_update.py"), slug],
            capture_output=True, text=True, timeout=180
        )
        out = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else "エラー"
        results.append(f"{slug}: {out}")
    print("\n".join(results))
