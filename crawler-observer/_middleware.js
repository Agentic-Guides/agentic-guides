// Agentic Guides - AIクローラー観測ミドルウェア
// 各リクエストのUser-Agentを解析し、AIクローラー（GPTBot/ClaudeBot等）を検出してKVに記録する。
// Cloudflare Pages Functionsの _middleware.js として動作する。
// 使用法: 各サイトの functions/_middleware.js に配置し、KVバインディング AGENTIC_AI_CRAWLERS を設定。

// 検出対象のAIクローラー一覧（User-Agent部分一致）
const AI_CRAWLERS = [
  { name: "GPTBot", pattern: "gptbot" },
  { name: "ChatGPT-User", pattern: "chatgpt-user" },
  { name: "ClaudeBot", pattern: "claudebot" },
  { name: "Claude-Web", pattern: "claude-web" },
  { name: "Anthropic-AI", pattern: "anthropic-ai" },
  { name: "PerplexityBot", pattern: "perplexitybot" },
  { name: "Perplexity-User", pattern: "perplexity-user" },
  { name: "Google-Extended", pattern: "google-extended" },
  { name: "Google-Gemini", pattern: "google-gemini" },
  { name: "CCBot", pattern: "ccbot" },
  { name: "Applebot-Extended", pattern: "applebot-extended" },
  { name: "Meta-ExternalAgent", pattern: "meta-externalagent" },
  { name: "Bytespider", pattern: "bytespider" },
  { name: "Amazonbot", pattern: "amazonbot" },
  { name: "CohereAI", pattern: "cohereai" },
  { name: "YouBot", pattern: "youbot" },
  { name: "MistralAI", pattern: "mistral" },
  { name: "AI2Bot", pattern: "ai2bot" },
  { name: "BingBot", pattern: "bingbot" },
  { name: "Anthropic", pattern: "anthropic" },
];

export async function onRequest(context) {
  const { request, env, next, waitUntil } = context;
  const userAgent = request.headers.get("User-Agent") || "";
  const host = request.headers.get("Host") || "";

  // 次のハンドラを呼ぶ（コンテンツ配信は通常通り）
  const response = await next();

  // AIクローラーを検出
  const ua = userAgent.toLowerCase();
  let crawlerName = null;
  for (const c of AI_CRAWLERS) {
    if (ua.includes(c.pattern)) {
      crawlerName = c.name;
      break;
    }
  }

  // AIクローラーならKVに記録（waitUntilで確実に実行）
  if (crawlerName && env.AGENTIC_AI_CRAWLERS) {
    const record = async () => {
      try {
        const today = new Date().toISOString().split("T")[0]; // YYYY-MM-DD
        const site = host.split(".")[0] || "unknown";
        const key = `${today}:${site}:${crawlerName}`;

        // 現在のカウントを取得して+1
        const current = parseInt(await env.AGENTIC_AI_CRAWLERS.get(key, "text") || "0", 10);
        await env.AGENTIC_AI_CRAWLERS.put(key, String(current + 1));

        // 日付の合計も更新
        const dayKey = `${today}:${site}:total`;
        const dayTotal = parseInt(await env.AGENTIC_AI_CRAWLERS.get(dayKey, "text") || "0", 10);
        await env.AGENTIC_AI_CRAWLERS.put(dayKey, String(dayTotal + 1));
      } catch (e) {
        console.log("AI crawler logging error:", e.message);
      }
    };
    if (waitUntil) {
      waitUntil(record());
    } else {
      // waitUntilがない場合はawait（旧ランタイム）
      await record();
    }
  }

  return response;
}
