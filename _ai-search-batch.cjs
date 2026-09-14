#!/usr/bin/env node
// agentic-sites 全サイトを AI Search に一括登録（web-crawler）
// OAuthトークンは ~/.wrangler/config/default.toml から読む
const fs = require("fs");
const os = require("os");
const path = require("path");

const ACC = "c1af587d36d1b6cb2848fc4e5546923d";
// OAuthトークン（ai-search:write 権限）を wrangler config から読む
const cfg = fs.readFileSync(path.join(os.homedir(), ".wrangler", "config", "default.toml"), "utf8");
const t = cfg.match(/^oauth_token\s*=\s*"([^"]+)"/m);
const OAUTH = t ? t[1] : null;
if (!OAUTH) { console.error("OAuth token not found"); process.exit(1); }

const targets = JSON.parse(fs.readFileSync(path.join(__dirname, "_ai-search-targets.json"), "utf8"));
// 既に作ったパイロットはスキップ
const SKIP = new Set(["pg-investing-guide"]);
const done = new Set();
const failed = [];
(async () => {
  for (const name of targets) {
    if (SKIP.has(name)) continue;
    const url = `https://${name}.pages.dev/`;
    try {
      const r = await fetch(`https://api.cloudflare.com/client/v4/accounts/${ACC}/ai-search/namespaces/default/instances`, {
        method: "POST",
        headers: { "Authorization": `Bearer ${OAUTH}`, "Content-Type": "application/json" },
        body: JSON.stringify({ id: name, type: "web-crawler", source: url }),
      });
      const j = await r.json();
      if (j.success) { done.add(name); console.log(`OK   ${name}`); }
      else { failed.push(`${name}: ${JSON.stringify(j.errors)||j}`); console.log(`FAIL ${name}: ${(j.errors||[{message:r.status}]).map(e=>e.message).join(",")}`); }
    } catch (e) { failed.push(`${name}: ${e.message}`); console.log(`ERR  ${name}: ${e.message}`); }
    // レート制限対策: 少し待機
    await new Promise(res => setTimeout(res, 400));
  }
  console.log(`\n== 完了: 成功 ${done.size} / 失敗 ${failed.length} ==`);
  if (failed.length) { console.log("失敗一覧:\n" + failed.join("\n")); }
  fs.writeFileSync(path.join(__dirname, "_ai-search-batch-result.txt"),
    `成功: ${done.size}\n失敗: ${failed.length}\n\n失敗詳細:\n${failed.join("\n")}`,
  );
})();
