module.exports = function(eleventyConfig) {
  // CSS等の静的ファイルを _site にコピー
  eleventyConfig.addPassthroughCopy("src/assets");

  eleventyConfig.addCollection("articles", function(collectionApi) {
    return collectionApi.getFilteredByGlob("src/articles/**/*.md").sort((a,b) => b.date - a.date);
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
