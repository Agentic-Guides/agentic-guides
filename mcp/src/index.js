import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";
import { ARTICLES } from "./articles_data.js";

// Agentic Guides MCP Server
// 全サイトの記事を検索・取得できるツールを提供する。
// エージェントが「Agentic Guides」ブランドの全サイトを1つの窓口から呼べる。

function createServer() {
  const server = new McpServer({
    name: "agentic-guides",
    version: "1.0.0",
  });

  // 記事検索ツール
  server.registerTool(
    "search_articles",
    {
      description: "Search articles across all Agentic Guides sites (grants, taxes, mortgages, side hustles, elder care). Returns matching articles with titles, descriptions, and URLs.",
      inputSchema: {
        query: z.string().describe("Search query, e.g. 'small business grant' or 'mortgage rates'"),
        category: z.string().optional().describe("Optional category filter: Business Grants, Personal Aid, Energy, Startup, Housing, Tax Filing, Freelancer, Deductions, Retirement, e-Filing, Mortgage Basics, Rates, Tax Credits, Down Payment, Refinance, Getting Started, Remote Work, Skills, Taxes, Clients, Medicare, Long-Term Care, Care Services, Care Costs, Family Care"),
        limit: z.number().optional().describe("Max results to return (default 5)"),
      },
    },
    async ({ query, category, limit }) => {
      const raw = (query || "").trim();
      const lim = Math.min(Math.max(limit || 5, 1), 20);

      // ★ 検索は「単語分割 + スコアリング」で行う。
      //    以前は query 全体の部分一致だったため "mortgage rate" のような
      //    複数語クエリが 1 件もヒットしなかった（実測 2026-10-16）。
      //    ストップワードを除いた語ごとに重みを付け、合計スコアで並べる。
      const STOP = new Set([
        "the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "is", "are",
        "how", "what", "when", "why", "best", "guide", "2026", "2025", "us", "my",
      ]);
      const terms = raw
        .toLowerCase()
        .split(/[^a-z0-9]+/)
        .filter((w) => w.length >= 2 && !STOP.has(w));

      let pool = ARTICLES;
      if (category) pool = pool.filter((a) => a.category === category);

      let scored;
      if (terms.length === 0) {
        // クエリ無し（または記号のみ）→ カテゴリ指定があればそれを返す
        scored = pool.slice(0, lim).map((a) => ({ a, score: 0 }));
      } else {
        scored = [];
        for (const a of pool) {
          const title = (a.title || "").toLowerCase();
          const desc = (a.description || "").toLowerCase();
          const cat = (a.category || "").toLowerCase();
          const site = (a.site || "").toLowerCase();
          let score = 0;
          for (const t of terms) {
            if (title.includes(t)) score += 10;   // タイトル一致を最重視
            if (cat.includes(t)) score += 5;      // カテゴリ一致
            if (desc.includes(t)) score += 3;      // 説明文
            if (site.includes(t)) score += 2;      // サイト名
          }
          if (score > 0) scored.push({ a, score });
        }
        // スコア降順 → 同点はタイトル昇順で安定化
        scored.sort((x, y) => y.score - x.score || (x.a.title || "").localeCompare(y.a.title || ""));
        scored = scored.slice(0, lim);
      }

      if (scored.length === 0) {
        return {
          content: [{
            type: "text",
            text: `No articles found for "${raw}"${category ? ` in category "${category}"` : ""}. ` +
                  `Try shorter keywords (e.g. "mortgage" instead of "mortgage rate"), or call list_sites to see all ${new Set(ARTICLES.map((a) => a.slug)).size} sites and their categories.`,
          }],
        };
      }

      const text = scored
        .map(({ a, score }) =>
          `### ${a.title}\n${a.description}\nSite: ${a.site} | Category: ${a.category} | Score: ${score}\nURL: ${a.url}`
        )
        .join("\n\n");

      return { content: [{ type: "text", text }] };
    }
  );

  // サイト一覧ツール
  server.registerTool(
    "list_sites",
    {
      description: "List all Agentic Guides sites and their focus areas.",
      inputSchema: {},
    },
    async () => {
      // ★ サイト一覧は articles_data.js から自動生成する（ハードコードしない）。
      //    記事が1件も無いサイトは出ないため、追加したサイトは自動で現れる。
      const map = new Map();
      for (const a of ARTICLES) {
        if (!map.has(a.slug)) {
          map.set(a.slug, {
            name: a.site,
            url: a.url.split("/articles/")[0],
            count: 0,
            categories: new Set(),
          });
        }
        const e = map.get(a.slug);
        e.count += 1;
        if (a.category) e.categories.add(a.category);
      }
      const sites = [...map.values()].sort((x, y) => y.count - x.count);
      const text =
        `Agentic Guides: ${sites.length} sites, ${ARTICLES.length} articles\n\n` +
        sites
          .map(
            (s) =>
              `- **${s.name}** (${s.count} articles)\n  ${s.url}\n  Categories: ${[...s.categories].slice(0, 8).join(", ")}`
          )
          .join("\n");
      return { content: [{ type: "text", text }] };
    }
  );

  return server;
}

export default {
  fetch(request, env, ctx) {
    return createMcpHandler(createServer)(request, env, ctx);
  },
};
