// _data/cta.js
// CTAプレースホルダ → HTML置換マップ
// 使い方: 記事本文中に <!-- CTA:A8_NEURODIVE --> 等を配置すると、
// eleventy.config.js の addTransform でビルド時にこのHTMLに置換される。

module.exports = {
  // 対応タグ（Phase C 決定木 条件B）: career, ai-engineer-career, career-change, data-science, reskill, ai-learning
  // 禁止タグ: english-learning 系（広告主審査中、CTA配置自体を省略）
  A8_NEURODIVE: `
<div class="cta-box" style="border:1px solid #ddd;padding:16px;margin:24px 0;background:#f9fafb;border-radius:8px;">
  <p style="margin:0 0 8px 0;font-weight:bold;">▼ AI・データサイエンスを学んで転職したい方へ</p>
  <p style="margin:0 0 12px 0;font-size:14px;color:#555;">就労移行支援「Neuro Dive」では、AI・データサイエンスを実務レベルで学べるカリキュラムを提供しています。</p>
  <p style="margin:0;">
    <a href="https://px.a8.net/svt/ejp?a8mat=4B3KUO+2T7PMA+47GS+HV7V6" rel="nofollow noopener" target="_blank">AIやデータサイエンスが学べるIT特化の就労移行支援【Neuro Dive】</a>
  </p>
  <img border="0" width="1" height="1" src="https://www12.a8.net/0.gif?a8mat=4B3KUO+2T7PMA+47GS+HV7V6" alt="">
  <p style="margin:8px 0 0 0;font-size:11px;color:#888;">※本リンクはアフィリエイト広告を含みます</p>
</div>
`.trim(),

  // 対応タグ（Phase C 決定木 条件A）: freelance, freelance-board, side-business, independence, independent
  A8_FREELANCEBOARD: `
<div class="cta-box" style="border:1px solid #ddd;padding:16px;margin:24px 0;background:#f9fafb;border-radius:8px;">
  <p style="margin:0 0 8px 0;font-weight:bold;">▼ フリーランス案件を探している方へ</p>
  <p style="margin:0 0 12px 0;font-size:14px;color:#555;">国内のフリーランスエンジニア向け案件を横断検索できる「フリーランスボード」で、希望条件に合う案件を探せます。</p>
  <p style="margin:0;text-align:center;">
    <a href="https://px.a8.net/svt/ejp?a8mat=4B3KUO+2TT582+5R1M+62MDD" rel="nofollow noopener" target="_blank">
      <img border="0" width="300" height="250" alt="フリーランスボード" src="https://www25.a8.net/svt/bgt?aid=260507472171&wid=001&eno=01&mid=s00000026833001020000&mc=1">
    </a>
  </p>
  <img border="0" width="1" height="1" src="https://www13.a8.net/0.gif?a8mat=4B3KUO+2TT582+5R1M+62MDD" alt="">
  <p style="margin:8px 0 0 0;font-size:11px;color:#888;">※本リンクはアフィリエイト広告を含みます</p>
</div>
`.trim(),

  // 対応タグ（Phase C 決定木 条件C）: blog, wordpress, server, site-building
  // 注: もしも経由リンクは現在URL未配置（差し替え提携先承認待ち）
  MOSHIMO_CONOHA_WING: `
<div class="cta-box" style="border:1px solid #ddd;padding:16px;margin:24px 0;background:#f9fafb;border-radius:8px;">
  <p style="margin:0 0 8px 0;font-weight:bold;">▼ ブログ運営をはじめたい方へ</p>
  <p style="margin:0 0 12px 0;font-size:14px;color:#555;">国内大手のレンタルサーバー「ConoHa WING」は、WordPressに最適化された高速サーバーです。</p>
  <p style="margin:0 0 0 0;font-size:12px;color:#888;">※もしもアフィリエイト経由のリンクは審査完了後に差し替え予定</p>
</div>
`.trim()
};
