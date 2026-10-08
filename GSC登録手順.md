# ★ GSC（Google Search Console）登録手順 — ハブサイト

> 対象: ★https://ai-directory-hub.pages.dev/
> 所要: ★3分（ボスが1回操作するだけ）

---

## ★★★ なぜ「URLプレフィックス」を使うのか（実測）

```
★GSCには2種類のプロパティがある:
   ① ドメインプロパティ   → ★DNSレコード確認が必要
   ② ★URLプレフィックス   → ★ファイルを置く or metaタグ

★★pages.dev は Cloudflare が管理するドメイン
   → ★★ボスは DNS を編集できない
   → ★★だから【URLプレフィックス】を使う（ファイルを置くだけ）
```

---

## ★★★ 手順（ボスがやること）

### STEP 1
```
1. https://search.google.com/search-console を開く
   ログイン: ★hohohoriririhoribanzai@gmail.com（Cloudflareと同じ）
2. 左上のプロパティ選択 → 「+ プロパティを追加」
3. ★右側の【URLプレフィックス】を選ぶ（左のドメインではない）
4. 入力: ★https://ai-directory-hub.pages.dev/
```

### STEP 2: 所有権の確認
```
1. 「HTMLファイル」の方法を選ぶ（推奨）
2. ★google から始まる .html ファイルをダウンロード
   （例: google1a2b3c4d5e6f7g8h.html）
3. ★★そのファイルをオイラに渡す（Telegramに添付 or パスを教える）
   → オイラがハブに置いてデプロイする
4. 「確認」を押す → ★完了
```

**★オイラに渡すものが無い場合（別の方法）:**
```
★「HTMLタグ」を選ぶ → <meta name="google-site-verification" content="XXXX"> が出る
★→ ★その XXXX をオイラに教えてくれ
   → ★オイラが全ページの head に入れてデプロイする
```

### STEP 3: サイトマップ送信（オイラが値を用意済み）
```
GSC 左メニュー → 「サイトマップ」
入力: ★sitemap.xml
→ ★これだけで72サイトがクロール対象になる
```

---

## ★★ オイラが既にやった準備（実測）

```
★★① robots.txt の Sitemap URL 修正（バグだった）
★★② sitemap.xml に72サイト全部（正しいURL）
★★③ llms.txt に72サイト索引（AIエージェント用）
★★④ canonical 全ページ正しい
★★⑤ Googlebot 視点での動作確認済み
```

## ★★ 相乗効果（GSC + 既存プロパティ）

```
★ボスは既に elderly-tips を GSC に登録済み
★★→ 同じ Google アカウントで追加すれば【所有権確認が自動になる場合がある】
   （同一ドメインでなくても、同じ確認トークンが使えることがある）
```

## ★★ 補足: 独自ドメインを取る場合

**★もし将来【独自ドメイン】（例: ai-directory-hub.com）を取れば:**
```
★★ドメインプロパティが使える ＝ ★DNS確認できる
★★そして SEO の評価も【.pages.dev より高い】
★Cloudflare Registrar で原価登録（〜$7.85/年・マークアップなし）
```

## 関連
[[scs-security-business]]・[[agentic-sites]]
