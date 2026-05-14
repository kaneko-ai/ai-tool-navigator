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

  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "../_includes"
    },
    pathPrefix: "/ai-tool-navigator/"
  };
};
