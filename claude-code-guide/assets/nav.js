/* サイドバー・ページャ・章カード・フッターを assets/toc.js のデータから描き、
   開閉・スクロール位置の維持・現在読んでいる節のハイライトを行う。
   章ページ自体にはこれらの HTML を持たせない（1 つの章を直しても他の章ファイルが変わらないようにするため）。 */
(function () {
  var data = window.CCGUIDE;
  var wrap = document.querySelector('.wrap');
  var main = document.querySelector('main');
  if (!data || !wrap || !main) return;

  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  var CARET = '<svg viewBox="0 0 16 16" width="9" height="9" aria-hidden="true">' +
    '<path d="M5.5 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" ' +
    'stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var chapters = data.chapters;
  var sections = document.querySelectorAll('section.chapter[data-chapter]');
  // 単一ファイル版（全章が 1 ページ）では Python 側が描いた目次をそのまま使う
  var isSingle = sections.length > 1;
  var current = sections.length === 1 ? parseInt(sections[0].getAttribute('data-chapter'), 10) : null;

  function chapterIndex(num) {
    for (var i = 0; i < chapters.length; i++) if (chapters[i].num === num) return i;
    return -1;
  }

  /* --- サイドバー --- */
  var sidebar = document.querySelector('.sidebar');
  if (!sidebar) {
    var h = ['<a class="sidebar-brand" href="index.html">Claude Code<em>体系的入門</em></a>',
             '<p class="sidebar-label">Contents</p>', '<ol class="toc-tree">'];
    chapters.forEach(function (ch) {
      var cur = ch.num === current;
      var listid = 'toc-sec-' + ch.num;
      h.push('<li><div class="toc-ch-row' + (cur ? ' is-current' : '') + '">' +
        '<a class="toc-ch-link" href="' + ch.file + '"' + (cur ? ' aria-current="page"' : '') + '>' +
        '<span class="toc-num">' + (ch.num < 10 ? '0' : '') + ch.num + '</span><span>' + esc(ch.title) + '</span></a>');
      if (ch.sections.length) {
        h.push('<button class="toc-toggle" type="button" aria-expanded="' + cur + '" aria-controls="' + listid +
          '" aria-label="' + esc(ch.title) + 'の節を開閉">' + CARET + '</button>');
      }
      h.push('</div>');
      if (ch.sections.length) {
        h.push('<ul class="toc-sections" id="' + listid + '"' + (cur ? '' : ' hidden') + '>');
        ch.sections.forEach(function (s) {
          h.push('<li><a href="' + ch.file + '#' + s.id + '">' + esc(s.title) + '</a></li>');
        });
        h.push('</ul>');
      }
      h.push('</li>');
    });
    h.push('</ol>');
    sidebar = document.createElement('nav');
    sidebar.className = 'sidebar';
    sidebar.setAttribute('aria-label', '目次');
    sidebar.innerHTML = h.join('\n');
    wrap.insertBefore(sidebar, wrap.firstChild);
  }

  /* --- ページャ（章ページのみ） --- */
  if (current !== null && !isSingle && !document.querySelector('.pager')) {
    var i = chapterIndex(current);
    var p = [];
    if (i > 0) {
      var prev = chapters[i - 1];
      p.push('<a class="prev" href="' + prev.file + '" rel="prev"><span class="dir">← 第' + prev.num +
        '章</span><span class="name">' + esc(prev.title) + '</span></a>');
    }
    if (i >= 0 && i < chapters.length - 1) {
      var next = chapters[i + 1];
      p.push('<a class="next" href="' + next.file + '" rel="next"><span class="dir">第' + next.num +
        '章 →</span><span class="name">' + esc(next.title) + '</span></a>');
    }
    if (p.length) {
      var pager = document.createElement('nav');
      pager.className = 'pager';
      pager.setAttribute('aria-label', '章の移動');
      pager.innerHTML = p.join('\n');
      sections[0].parentNode.insertBefore(pager, sections[0].nextSibling);
    }
  }

  /* --- 章カード（トップページ） --- */
  var grid = document.querySelector('.index-grid[data-index]');
  if (grid && !grid.children.length) {
    grid.innerHTML = chapters.map(function (ch) {
      return '<li><a class="index-card" href="' + ch.file + '"><span class="n">CHAPTER ' +
        (ch.num < 10 ? '0' : '') + ch.num + '</span><h2>' + esc(ch.title) + '</h2><p>' +
        esc(ch.lede.slice(0, 110)) + '</p><span class="count">' + ch.sections.length + ' sections</span></a></li>';
    }).join('\n');
  }

  /* --- フッター --- */
  if (!main.querySelector('footer')) {
    var footer = document.createElement('footer');
    footer.innerHTML = '<p><strong>' + esc(data.title) + '</strong> — ' + esc(data.footer) + '</p>';
    main.appendChild(footer);
  }

  /* 描画フレームに合わせて間引く。バックグラウンドタブでは
     requestAnimationFrame が止まるため、その場合はタイマーに落とす。 */
  function throttle(fn) {
    var pending = false;
    return function () {
      if (pending) return;
      pending = true;
      var run = function () { pending = false; fn(); };
      if (typeof requestAnimationFrame === 'function' && !document.hidden) requestAnimationFrame(run);
      else setTimeout(run, 100);
    };
  }

  /* --- スクロール位置の維持 ---
     章を選ぶとページが遷移するため、そのままだとサイドバーが毎回先頭に戻る。
     位置を sessionStorage に控えておき、次のページで復元する。 */
  var KEY = 'ccguide:sidebarScroll';

  function store() {
    try { sessionStorage.setItem(KEY, String(sidebar.scrollTop)); } catch (e) { /* 無視 */ }
  }

  (function restore() {
    var saved;
    try { saved = sessionStorage.getItem(KEY); } catch (e) { return; }
    if (saved === null) return;
    var top = parseInt(saved, 10);
    if (isNaN(top)) return;
    sidebar.scrollTop = top;
    setTimeout(function () { if (sidebar.scrollTop !== top) sidebar.scrollTop = top; }, 0);
  })();

  sidebar.addEventListener('scroll', throttle(store), { passive: true });
  window.addEventListener('pagehide', store);

  /* --- 章の開閉 --- */
  sidebar.addEventListener('click', function (e) {
    var btn = e.target.closest('.toc-toggle');
    if (!btn) return;
    var list = document.getElementById(btn.getAttribute('aria-controls'));
    if (!list) return;
    var open = btn.getAttribute('aria-expanded') === 'true';
    btn.setAttribute('aria-expanded', String(!open));
    list.hidden = open;
  });

  /* --- 現在位置のハイライト（スクロールスパイ） ---
     ビューポートに「最も広く映っている」節を選ぶ。 */
  var links = {};
  sidebar.querySelectorAll('.toc-sections a[href*="#"]').forEach(function (a) {
    var id = a.getAttribute('href').split('#')[1];
    if (id) links[id] = a;
  });
  var targets = Object.keys(links)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  if (!targets.length) return;

  var active = null;

  function activate(id) {
    if (!id || id === active) return;
    if (active && links[active]) links[active].classList.remove('is-active');
    links[id].classList.add('is-active');
    active = id;
  }

  function pick() {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    if (window.scrollY + vh >= document.documentElement.scrollHeight - 2) {
      return targets[targets.length - 1].id;
    }
    var bestId = null;
    var bestArea = 0;
    for (var k = 0; k < targets.length; k++) {
      var r = targets[k].getBoundingClientRect();
      var area = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      if (area > bestArea) { bestArea = area; bestId = targets[k].id; }
    }
    return bestArea > 0 ? bestId : active;
  }

  var update = throttle(function () { activate(pick()); });
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  activate(pick());
})();
