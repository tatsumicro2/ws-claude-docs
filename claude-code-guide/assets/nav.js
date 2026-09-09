/* サイドバーの開閉・スクロール位置の維持・現在読んでいる節のハイライト */
(function () {
  var sidebar = document.querySelector('.sidebar');
  if (!sidebar) return;

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
    // レイアウト確定が遅れる環境向けにもう一度だけ合わせる
    setTimeout(function () { if (sidebar.scrollTop !== top) sidebar.scrollTop = top; }, 0);
  })();

  sidebar.addEventListener('scroll', throttle(store), { passive: true });
  // 遷移直前にも確実に保存する（スクロール直後のクリックを取りこぼさないため）
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
     ビューポートに「最も広く映っている」節を選ぶ。前の節が端に少し
     残っているだけで、そちらが選ばれてしまうのを防ぐ。 */
  var links = {};
  sidebar.querySelectorAll('.toc-sections a[href*="#"]').forEach(function (a) {
    var id = a.getAttribute('href').split('#')[1];
    if (id) links[id] = a;
  });
  var targets = Object.keys(links)
    .map(function (id) { return document.getElementById(id); })
    .filter(Boolean);
  if (!targets.length) return;

  var current = null;

  function activate(id) {
    if (!id || id === current) return;
    if (current && links[current]) links[current].classList.remove('is-active');
    links[id].classList.add('is-active');
    current = id;
  }

  function pick() {
    var vh = window.innerHeight || document.documentElement.clientHeight;

    // 最下部まで来たら最後の節。短い末尾の節が一度も選ばれないのを避ける
    if (window.scrollY + vh >= document.documentElement.scrollHeight - 2) {
      return targets[targets.length - 1].id;
    }

    var bestId = null;
    var bestArea = 0;
    for (var i = 0; i < targets.length; i++) {
      var r = targets[i].getBoundingClientRect();
      var area = Math.min(r.bottom, vh) - Math.max(r.top, 0);
      if (area > bestArea) { bestArea = area; bestId = targets[i].id; }
    }
    // どれも映っていなければ直前の選択を保つ
    return bestArea > 0 ? bestId : current;
  }

  var update = throttle(function () { activate(pick()); });
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update);
  activate(pick());   // 初期表示は同期で決める
})();
