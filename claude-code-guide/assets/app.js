// 「試してみる」コードのコマンド単位コピー
(function(){
  var ICON_COPY = '<svg viewBox="0 0 16 16" width="11" height="11" aria-hidden="true" focusable="false">' +
    '<rect x="1.9" y="4.9" width="8.2" height="9.2" rx="1.4" fill="none" stroke="currentColor" stroke-width="1.5"/>' +
    '<path d="M5.4 2.4h6.3a2 2 0 0 1 2 2v6.3" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>';
  var ICON_OK = '<svg viewBox="0 0 16 16" width="11" height="11" aria-hidden="true" focusable="false">' +
    '<path d="M2.6 8.6l3.4 3.4 7-7.4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  function fallbackCopy(text){
    var ta = document.createElement('textarea');
    ta.value = text;
    ta.setAttribute('readonly','');
    ta.style.position = 'fixed';
    ta.style.top = '-1000px';
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand('copy'); } catch(e){ ok = false; }
    document.body.removeChild(ta);
    return ok;
  }

  function selectNode(node){
    if (!node || !window.getSelection) return;
    var range = document.createRange();
    range.selectNodeContents(node);
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(range);
  }

  function copyText(text, onDone){
    var settled = false;
    var finish = function(ok){ if (settled) return; settled = true; onDone(ok); };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(function(){ finish(true); }, function(){ finish(fallbackCopy(text)); });
      setTimeout(function(){ if (!settled) finish(fallbackCopy(text)); }, 600);   // 応答しない環境への保険
    } else {
      finish(fallbackCopy(text));
    }
  }

  // 各コマンドにコピーボタンを付ける
  document.querySelectorAll('.try .cmd').forEach(function(cmd){
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'line-copy';
    b.title = 'このコマンドをコピー';
    b.setAttribute('aria-label', 'このコマンドをコピー');
    b.innerHTML = ICON_COPY;
    b.addEventListener('click', function(ev){
      ev.stopPropagation();
      copyText(cmd.dataset.copy || '', function(ok){
        if (!ok) selectNode(cmd);
        b.innerHTML = ok ? ICON_OK : ICON_COPY;
        b.classList.toggle('done', ok);
        b.title = ok ? 'コピーしました' : '選択しました。手動でコピーしてください';
        setTimeout(function(){
          b.innerHTML = ICON_COPY;
          b.classList.remove('done');
          b.title = 'このコマンドをコピー';
        }, 1400);
      });
    });
    cmd.appendChild(b);
  });
})();

// 目次のスクロールスパイ（現在の章をハイライト）
(function(){
  var links = Array.prototype.slice.call(document.querySelectorAll('.toc a'));
  var map = {};
  links.forEach(function(a){ map[a.getAttribute('href').slice(1)] = a; });
  var obs = new IntersectionObserver(function(entries){
    entries.forEach(function(e){
      var a = map[e.target.id];
      if(!a) return;
      if(e.isIntersecting){
        links.forEach(function(l){ l.style.background=''; l.style.color=''; });
        a.style.background = 'var(--accent-bg)';
        a.style.color = 'var(--accent)';
      }
    });
  }, { rootMargin: '-10% 0px -80% 0px' });
  document.querySelectorAll('.chapter').forEach(function(c){ obs.observe(c); });
})();
