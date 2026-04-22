module.exports = function(eleventyConfig) {
  return {
    dir: {
      input: "src",
      output: "_site",
      includes: "../_includes"
    },
    pathPrefix: "/ai-tool-navigator/"
  };
};

eleventyConfig.addCollection("articles", function(collectionApi) {
  return collectionApi.getGlobSrc("src/articles/*.md").sort((a,b) => b.date - a.date);
});
