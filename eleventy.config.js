module.exports = function(eleventyConfig) {
  eleventyConfig.addPassthroughCopy("src/assets");

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

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "../_includes"
    },
    pathPrefix: "/ai-tool-navigator/"
  };
};
