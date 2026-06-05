module.exports = function(eleventyConfig) {
  const { DateTime } = require("luxon");

  // ISO-8601 (YYYY-MM-DD) — <time> の datetime 属性用
  eleventyConfig.addFilter("isoDate", function(d) {
    return DateTime.fromJSDate(new Date(d), { zone: "Asia/Tokyo" }).toFormat("yyyy-MM-dd");
  });

  // 和暦表示 (2026年6月4日) — 表示テキスト用
  eleventyConfig.addFilter("jpDate", function(d) {
    return DateTime.fromJSDate(new Date(d), { zone: "Asia/Tokyo" }).toFormat("yyyy年M月d日");
  });

  eleventyConfig.addPassthroughCopy("src/assets");
  // IndexNow キーファイル (src直下の16進.txt) をルートへコピー
  eleventyConfig.addPassthroughCopy("src/*.txt");

  eleventyConfig.addCollection("articles", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/**/*.md").sort((a,b) => b.date - a.date);
  });

  eleventyConfig.addCollection("tagList", function(collectionApi) {
    const tagSet = new Set();
    const SYSTEM_TAGS = new Set(["post", "posts", "article", "articles", "all"]);
    collectionApi.getFilteredByGlob("src/articles/**/*.md")
      .filter(item => !item.data.eleventyExcludeFromCollections)
      .forEach(item => {
        (item.data.tags || []).forEach(tag => {
          if (!SYSTEM_TAGS.has(tag)) tagSet.add(tag);
        });
      });
    return [...tagSet].sort();
  });

  // 関連記事フィルタ: 同タグ共有数×10 + 新しさボーナス、最大件数指定可
  eleventyConfig.addFilter("relatedTo", function(articles, currentPage, limit) {
    if (!articles || !currentPage) return [];
    limit = limit || 4;
    const currentUrl = currentPage.url;
    const currentTags = (currentPage.data && currentPage.data.tags) || [];
    const currentDate = currentPage.date ? new Date(currentPage.date).getTime() : Date.now();

    const scored = articles
      .filter(p => p.url !== currentUrl)
      .map(p => {
        const tags = (p.data && p.data.tags) || [];
        const common = tags.filter(t => currentTags.includes(t)).length;
        const ageDays = Math.abs((currentDate - new Date(p.date).getTime()) / 86400000);
        const recency = ageDays < 180 ? (180 - ageDays) / 30 : 0;
        return { post: p, score: common * 10 + recency, common: common };
      })
      .filter(x => x.common > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit)
      .map(x => x.post);

    // フォールバック: 共通タグ0件なら最新N件
    if (scored.length === 0) {
      return articles
        .filter(p => p.url !== currentUrl)
        .sort((a, b) => new Date(b.date) - new Date(a.date))
        .slice(0, limit);
    }
    return scored;
  });

  // CTA プレースホルダ置換: <!-- CTA:KEY --> を _data/cta.js のHTMLに差し替え
  // 対象: HTML出力ファイル全て。マッチしないキーは元のコメントを残す。
  eleventyConfig.addTransform("ctaReplace", function(content, outputPath) {
    if (!outputPath || !outputPath.endsWith(".html")) return content;
    const ctaMap = require("./_data/cta.js");
    return content.replace(/<!--\s*CTA:([A-Z0-9_]+)\s*-->/g, function(match, key) {
      if (ctaMap[key]) {
        return ctaMap[key];
      }
      console.warn("[ctaReplace] 未定義のCTAキー: " + key);
      return match;
    });
  });


  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "../_includes"
    },
    pathPrefix: "/ai-tool-navigator/"
  };
};
