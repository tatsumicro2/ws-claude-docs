#!/usr/bin/env python3
"""各章の末尾に「この章の持ち帰り」節を追加する。"""
import json
import re
from pathlib import Path

GUIDE = Path(__file__).resolve().parent.parent
TITLE = "この章の持ち帰り"

# chapter num -> (file, 次の節番号, lede, [(覚えること, 効き目, 操作)], 豆知識 HTML)
DATA = {
1: ("ch01-what-is-claude-code.html", 7,
 "この章から実務に持ち帰るのは、<strong>「何に使うかの判断軸」と「初日の 2 手」</strong>です。",
 [("3 要素に還元して考える", "新機能が出るたびに学び直さずに済む。「文字列・関数・ループのどれを触るのか」で位置づけられる", "—"),
  ("起動直後は <code>/init</code> → <code>/doctor</code>", "設定ミスを初日に潰せる。CLAUDE.md のたたき台も同時に手に入る", "<code>/init</code> / <code>/doctor</code>"),
  ("向き不向きは 3 条件で判断する", "「AI に任せて大丈夫か」を感覚ではなく条件の数で説明できる。稟議や見積もりでも使える", "テキスト化できる／機械が合否を出せる／巻き戻せる"),
  ("セッションを開かずに雑務を投げる", "テスト作成・Lint 修正・依存更新など、対話するまでもない作業が数十秒で片づく", "<code>claude \"このリポジトリの構成を3行で\"</code>"),
  ("設定はサーフェス間で共通", "CLI で育てた CLAUDE.md・MCP が、IDE でも Web でもそのまま効く。作り直す必要はない", "—")],
 "<strong>ネイティブインストールは自動更新されますが、Homebrew / WinGet 版は手動更新です。</strong>「記事に載っている機能が自分の環境に無い」の最頻出原因がこれです。<code>claude --version</code> で確認し、パッケージマネージャ経由なら自分で上げてください。"),

2: ("ch02-basics-and-interface.html", 5,
 "日々の生産性はこの層でほぼ決まります。<strong>覚えるキーは 3 つ、フラグは 2 つ</strong>で足ります。",
 [("<code>Shift+Tab</code> で権限モードを回す", "確認ダイアログの頻度を作業内容に合わせて即座に変えられる。日常は acceptEdits が現実的", "default → acceptEdits → plan"),
  ("<code>Esc</code> は「止める」、<code>Esc</code> 2 回は「戻す」", "暴走を 1 打鍵で止められる安心感が、任せられる範囲を広げる。コンテキストは保持される", "<code>Esc</code> / <code>Esc</code> ×2（＝<code>/rewind</code>）"),
  ("<code>Ctrl+O</code> でトランスクリプトを読む", "「なぜその結論になったか」を追える唯一の手段。レビューや障害報告で根拠を示せる", "<code>Ctrl+O</code>（<code>Esc</code> で閉じる）"),
  ("ログ調査はパイプで一撃", "ファイルに保存して読ませる手間が要らない。障害対応の初動が速くなる", "<code>tail -200 app.log | claude -p \"異常があれば教えて\"</code>"),
  ("調査だけさせたいときは plan で起動", "「勝手に直された」が起きない。設計レビュー前の調査に向く", "<code>claude --permission-mode plan</code>")],
 "<strong><code>Esc</code> 2 回が巻き戻しになるのは、入力欄が空のときだけです。</strong>文字が残っていると入力のクリアになります。もう一つ、<code>!</code> のシェルモードは v2.1.186 以降<strong>出力が届くと Claude が自動で応答します</strong>——通常のプロンプトと同じ課金が発生するので、単に手元でコマンドを打ちたいだけなら設定 <code>respondToBashCommands: false</code> で旧挙動に戻せます。"),

3: ("ch03-core-mechanisms.html", 9,
 "ツールの落とし穴を知っているかどうかで、<strong>「なぜか動かない」に費やす時間が変わります</strong>。",
 [("Bash はコマンドごとに別プロセス", "<code>export</code> や venv の有効化が引き継がれない。「環境変数を設定したのに効かない」の正体", "起動前に有効化するか <code>CLAUDE_ENV_FILE</code> で渡す"),
  ("長いコマンドは停止せずバックグラウンドへ", "既定 2 分・上限 10 分を超えると裏に回る。放置すると消費が続く", "<code>/tasks</code> で確認・停止"),
  ("Read は大きいファイルを切る", "「読んだはずなのに後半を知らない」の原因。<code>PARTIAL view</code> の注記を見落とさない", "範囲を指定して読ませ直す"),
  ("Grep と Glob は <code>.gitignore</code> の扱いが逆", "Glob が <code>node_modules</code> やビルド生成物まで拾い、無駄なトークンを食う", "Glob はパターンを絞る（結果は最大 100 件）"),
  ("Edit は 3 検査を通らないと適用されない", "「編集しましたと言うのに変わっていない」を自分で切り分けられる", "①読んでいる ②完全一致 ③一意"),
  ("<code>/context</code> を見る癖をつける", "遅い・高い・指示が効かない、の 3 つとも最初に見るべきはここ", "<code>/context</code>")],
 "<strong>Bash の結果に載る出力は約 30,000 文字までです。</strong>超えるとファイルに保存されパスだけが返るため、長いログを丸ごと読ませたつもりが読まれていないことがあります。<code>BASH_MAX_OUTPUT_LENGTH</code> で最大 150,000 まで広げられますが、そもそも <code>grep</code> で絞ってから渡すほうが速くて安上がりです。"),

4: ("ch04-memory-and-instructions.html", 7,
 "CLAUDE.md は最もコスパの高い投資ですが、<strong>効かせ方を外すと固定費だけが増えます</strong>。",
 [("実際に読まれたかは <code>/context</code> で確認", "読まれていないファイルをいくら書き直しても効かない。診断はここから始める", "<code>/context</code> の Memory files"),
  ("200 行以下・検証可能な粒度で書く", "長いほど遵守率が下がる。「適切に」ではなく「インデントは 2 スペース」と書く", "<code>/init</code> でたたき台 → 削って育てる"),
  ("同じ指摘を 2 回したら追記する", "書くタイミングの判断で迷わなくなる。レビューの手戻りが目に見えて減る", "<code>#</code> でその場からメモリに追記"),
  ("常時ロードを <code>rules</code> に逃がす", "該当ファイルを触ったときだけ読ませれば、毎リクエストの固定費が下がる", "<code>.claude/rules/*.md</code> に <code>paths:</code>"),
  ("絶対に守らせたいことは指示にしない", "CLAUDE.md は「お願い」。禁止事項は強制できる層に置く", "PreToolUse フック or <code>deny</code> ルール")],
 "<strong><code>@</code> インポートの承認ダイアログを一度でも拒否すると、インポートは無効のままになり、ダイアログは二度と表示されません。</strong>「インポートが効かない」の典型的な原因です。もう一つ、プロジェクトルートの CLAUDE.md はセッション開始時に一度だけ読まれるため、<strong>作業中に編集しても、そのセッションには反映されません</strong>（<a href=\"ch07-cost-and-monitoring.html#s7-3\">7-3</a>）。反映は次の <code>/clear</code> か再起動からです。"),

5: ("ch05-best-practices.html", 6,
 "公式のベストプラクティスから、<strong>効果が大きく、今日から変えられるもの</strong>だけを抜きました。",
 [("同じ問題で 2 回失敗したら <code>/clear</code>", "失敗案が積み上がったコンテキストは、そのまま続けても精度が上がらない。作り直すほうが速い", "<code>/clear</code> → 学んだことを織り込んで再依頼"),
  ("必ず検証手段を渡す", "「見張るセッション」と「任せられるセッション」を分ける最大の要因。テスト・ビルド・スクショのどれかを持たせる", "「まず失敗するテストを書いて、その後で修正して」"),
  ("Writer と Reviewer を分ける", "実装に至った思考を知らないレビュアーは確証バイアスが入りにくい。見落としの検出率が上がる", "新しいサブエージェントに差分だけ見せる"),
  ("大きい機能は先にインタビューさせる", "仕様の抜けを実装前に潰せる。SPEC.md が残るのでレビューや引き継ぎにも効く", "AskUserQuestion で質問させ、SPEC.md に落として<strong>新しいセッション</strong>で実装"),
  ("安全なコマンドを許可リストに入れる", "プロンプト疲れが消え、確認の判断力を危険な操作に温存できる", "<code>/permissions</code> に <code>Bash(npm test:*)</code> など")],
 "<strong>小さく明確な修正に Plan Mode は不要です。</strong>公式も「オーバーヘッドになる」と明記しています。プランモードは<strong>間違った問題を解くリスクが高いとき</strong>——影響範囲が読めない、方針が複数ある、既存設計に合わせる必要がある——に限って使うのが、実は最も生産性が高い使い方です。"),

6: ("ch06-progress-and-visibility.html", 8,
 "「今どこにいるか分からない」は、<strong>見たい粒度に応じて別々の道具</strong>で解きます。",
 [("チェックリストが出ないのは仕様", "新しいモデルではタスクツールが既定で無効。不具合と思って調べる時間を節約できる", "<code>CLAUDE_CODE_ENABLE_TODO_TOOLS=1 claude</code>"),
  ("完了条件を宣言して任せる", "「テストが通るまで」を毎ターン別モデルが判定。席を外していても進む", "<code>/goal test/auth のテストが全て通る</code>"),
  ("ステータスラインは自然言語で作れる", "コンテキスト残量が常に見えると、<code>/clear</code> の判断が早くなり事故が減る", "<code>/statusline モデル名と使用率をバーで表示して</code>"),
  ("並列作業は <code>claude agents</code> で 1 画面監視", "どれが入力待ちかが一目で分かる。放置されたセッションが消費し続けるのを防げる", "ターミナルで <code>claude agents</code>"),
  ("ワークフローは 1 ディレクトリで試してから広げる", "いきなり全体にかけると消費が跳ねる。小さく測ってから展開する", "<code>/workflows</code> で消費を確認")],
 "<strong><code>/goal</code> の評価器は、コマンドを実行せずファイルも独自には読みません。</strong>判断材料は Claude が会話に出した内容だけです。つまり条件は「Claude 自身の出力で示せるもの」として書く必要があります。もう一つ、<strong><code>claude agents</code> と <code>/agents</code> は別物</strong>です（後者は v2.1.198 以降、定義ファイルの場所を表示するだけ）。"),

7: ("ch07-cost-and-monitoring.html", 8,
 "コスト削減は精神論ではありません。<strong>効き目の順に 3 つ</strong>やれば大半が片づきます。",
 [("モデル・努力レベル・高速モードは冒頭で固定", "途中で変えるとキャッシュが壊れ、そのターンだけ入力が約 10 倍になる", "<code>/model</code> <code>/effort</code> は作業開始前に"),
  ("継続不要なら <code>/compact</code> ではなく <code>/clear</code>", "<code>/clear</code> は要約を生成しないぶん実質コスト 0。惰性で <code>/compact</code> を打たない", "戻る予定があるなら先に <code>/rename</code>"),
  ("キャッシュ読みは入力の 1/10、出力は入力の 5 倍", "「キャッシュに乗せる」「出力（思考を含む）を無駄に増やさない」の 2 点に集約できる", "単純作業に Opus と高い <code>/effort</code> を使わない"),
  ("原因調査は <code>/usage</code> が最速", "直近の 10% 以上を占める挙動に自動でフラグが立つ。表を上から疑うより速い", "<code>/usage</code>（<code>d</code> / <code>w</code> で期間切替）"),
  ("自分の固定費を一度測る", "毎リクエストに乗る CLAUDE.md・スキル・MCP の総量が分かる。削る優先度が決まる", "<code>CLAUDE_CODE_DISABLE_CLAUDE_MDS=1</code> との差分")],
 "<strong>高速モードを会話の途中で有効にすると、その時点のコンテキスト全体を未キャッシュ単価で払い直します。</strong>深いところで入れるほど高くつくので、使うならセッションの最初からです（課金は 1 会話につき 1 回）。もう一つ、<strong>プロンプトキャッシュは実質的にディレクトリ単位</strong>で、worktree は別扱いのため互いのキャッシュを読みません。並列化の隠れたコストです。"),

8: ("ch08-glossary.html", 3,
 "用語集の実用価値は 2 つ——<strong>古い記事を読むための変換表</strong>と、<strong>混同しやすい語の切り分け</strong>です。",
 [("Headless mode → <strong>Non-interactive mode</strong>", "コミュニティ記事に頻出。同じ <code>-p</code> フラグ、同じ動作", "検索は現行語で引く"),
  ("Custom commands → <strong>Skills</strong>", "<code>.claude/commands/</code> は今も動くが、新規は Skills で作る", "スキルのほうが高機能"),
  ("Slash commands → <strong>Commands</strong>", "製品表記から「Slash」が削除された", "—"),
  ("Session / Turn / Checkpoint", "障害報告や相談で話が噛み合う。Turn は 1 プロンプトへの一連の応答、Checkpoint はプロンプト送信ごとの復元点", "<code>/rewind</code> は Checkpoint を戻す"),
  ("Skill / Subagent の一行判別", "設計会話が速くなる。コンテキストを分けるなら Subagent、分けないなら Skill", "<a href=\"ch09-extension-overview.html#s9-4\">9-4</a> の決め手 1 問")],
 "<strong>Checkpoint は git の代わりになりません。</strong>追跡されるのは<strong>メイン会話がファイル編集ツールで行った変更だけ</strong>で、Bash 経由の変更・サブエージェントの編集・DB やデプロイなどの外部副作用は戻せません。「<code>/rewind</code> があるから大丈夫」という前提で作業を任せるのが、最も危ない誤解です。"),

9: ("ch09-extension-overview.html", 7,
 "5 つの拡張機能は、<strong>決め手の 1 問</strong>と<strong>導入の症状</strong>さえ持っていれば迷いません。",
 [("Skill か Subagent か＝コンテキストを分けるか", "設計の議論が 1 問で終わる。分けない＝Skill、分ける＝Subagent", "大量読み込み・並列なら Subagent"),
  ("Hook か Skill か＝保証が要るか", "「.env を触らせない」は指示ではなく強制で書く。事故の芽を仕組みで潰せる", "ガードレールは PreToolUse フック"),
  ("症状が出てから足す", "最初から全部設定する必要はない。2 回間違えたら CLAUDE.md、3 回貼ったら Skill、毎回コピーしているなら MCP", "<a href=\"#s9-3\">9-3</a> のトリガー表"),
  ("自分専用スキルはコストをゼロにできる", "説明文すら読み込まれなくなる。スキルを増やしても固定費が増えない", "<code>disable-model-invocation: true</code>"),
  ("内訳を数字で見る", "「なんとなく重い」を具体的な削減対象に変えられる", "<code>/context</code> と <code>/mcp</code>")],
 "<strong>名前が衝突したときの挙動は、機能ごとにまったく違います。</strong>CLAUDE.md は<strong>加算</strong>（すべての階層が同時に入る）、Skills と Subagents は<strong>上書き</strong>、MCP サーバーは<strong>1 つの定義が丸ごと採用</strong>（フィールドのマージはしない）、Hooks は<strong>マージ</strong>（登録された全部が発火）。チームで設定を配るときに効いてきます。"),

10: ("ch10-skills.html", 8,
 "スキルは実体が Markdown 1 枚なので、<strong>今日作って今日使えます</strong>。",
 [("まず同梱スキルを使う", "自作より先に、レビューも一括変更も既にある。中身はプロンプトなので自作の参考にもなる", "<code>/code-review</code> <code>/batch</code> <code>/run</code> <code>/debug</code>"),
  ("<code>description</code> が命", "Claude が「使うべきか」を判断する唯一の材料。主要ユースケースを先頭に書く", "<code>when_to_use</code> と合わせて 1,536 文字で切られる"),
  ("<code>!`command`</code> で前処理データを埋め込む", "「Claude に実行させる」のではなく、渡す前にデータを差し込む。往復が減って速い", "<code>!`git diff HEAD`</code>"),
  ("本文は「常時適用される指示」として書く", "呼び出したスキルの本文はセッション中ずっと残る。単発の手順として書くと後で誤作動する", "SKILL.md は 500 行以下、詳細は補助ファイルへ"),
  ("繰り返す手順を見つけたら即スキル化", "同じ手順書を 3 回貼っているなら、それはもうスキル", "<code>~/.claude/skills/&lt;name&gt;/SKILL.md</code>")],
 "<strong><code>allowed-tools</code> が効くのは、そのスキルを呼び出したターンだけです。</strong>次のメッセージを送ると解除されます（本文はコンテキストに残るのに権限は残らない）。セッション全体で確認を省きたいなら <code>permissions.allow</code> に書いてください。もう一つ、<strong><code>~/.claude/skills/</code> をこの手順で初めて作ったときだけ再起動が必要</strong>です（2 つ目以降は不要）。"),

11: ("ch11-subagents.html", 6,
 "サブエージェントは「並列で速い」より、<strong>「メインを汚さない」ことが本体の価値</strong>です。",
 [("調査は明示的に委譲する", "大量のファイル読みが親に載らないので、<strong>合計では安くなることが多い</strong>。本題の議論も濁らない", "「サブエージェントで◯◯を調べて」"),
  ("Explore は軽い", "読み取り専用で CLAUDE.md も git status も読まない。探索の初手として最適", "組み込みの <code>Explore</code>"),
  ("敵対的レビューを型にする", "実装の経緯を知らない相手に差分だけ見せる。見落としが出る", "<code>/code-review</code> がこれを標準化したもの"),
  ("ファイルを作らずに試せる", "サブエージェント定義を書く前に、その場で挙動を確かめられる", "<code>claude --agents '{...}'</code>"),
  ("同じファイルを触るなら worktree で隔離", "並列セッションのファイル競合を防ぐ。変更が無ければ自動で片づく", "<code>claude --worktree</code>")],
 "<strong>日本語版ドキュメントは、この章の数値が古いままです。</strong>ネストの深さを「5 階層・設定不可」としていますが、英語版では<strong>既定 3 階層・環境変数で変更可</strong>。同時実行 20 の上限に至っては日本語版に記載がありません。仕様で迷ったら英語版を見る、が安全です。もう一つ、<strong>「欠落を探せ」と指示されたレビュアーは健全な実装でも必ず何か報告します</strong>——全部追うと過剰実装になるので、正確性か明示要件に関わるものだけを対応対象にしてください。"),

12: ("ch12-hooks.html", 6,
 "フックは<strong>「お願い」を「強制」に変える唯一の層</strong>です。書き方の型さえ知れば 5 分で入ります。",
 [("まず <code>/hooks</code> から入れる", "既存の <code>settings.local.json</code> を上書きして壊す事故を避けられる", "<code>/hooks</code> で対話的に追加"),
  ("パスは stdin の JSON から取る", "編集対象のパスを渡す環境変数は<strong>用意されていない</strong>。ここで詰まる人が多い", "<code>jq -r '.tool_input.file_path'</code>"),
  ("<code>exit 2</code> でブロック、stderr がフィードバック", "禁止するだけでなく「なぜ駄目か」を Claude に伝えて別の手を打たせられる", "<code>echo \"理由\" &gt;&amp;2; exit 2</code>"),
  ("Bash 経由の変更は PostToolUse で捕まらない", "監査目的なら取りこぼす。ターンごとに作業ツリーを走査する形にする", "Stop フックで全体スキャン"),
  ("整形・Lint・通知をここに移す", "毎回頼まなくても必ず走る。レビューでの指摘が定型作業から消える", "<code>PostToolUse</code> に <code>Write|Edit</code> でマッチ")],
 "<strong>フックの種類は 5 つあり、シェルコマンドだけではありません。</strong><code>command</code> のほかに <code>http</code>（POST）、<code>mcp_tool</code>（既存の MCP ツールを呼ぶ）、<code>prompt</code>（LLM に判定させる）、<code>agent</code>（サブエージェントで検証）があります。「機械的には判定できないが必ずチェックしたい」ものを <code>prompt</code> フックに置けるのは、意外と知られていない使い道です。なお <code>exit 2</code> と構造化 JSON の併用はできません。"),

13: ("ch13-mcp.html", 5,
 "MCP は強力ですが、<strong>先に CLI で足りないかを疑う</strong>のが公式の推奨です。",
 [("CLI で届くなら MCP を使わない", "<code>gh</code> <code>aws</code> <code>gcloud</code> が使えるなら、接続もトークンも要らず安い", "公式のベストプラクティスにも明記"),
  ("使っていないサーバーは切る", "ツール定義が固定費として毎リクエストに乗る。数字で確認して落とす", "<code>/mcp</code> でサーバーごとのトークンコスト"),
  ("MCP は能力、Skill は使う知識", "接続しただけでは使いこなせない。スキーマ・典型クエリ・社内ルールはスキルに書く", "セットで用意する"),
  ("チーム共有は <code>.mcp.json</code>", "リポジトリにコミットでき、全員が同じ接続先を持てる", "初回利用時に各自の承認が要る"),
  ("外部を取り込むサーバーはリスク源", "取得したコンテンツに仕込まれた指示で操られうる。提供元を選ぶ", "信頼できる提供元か自作のみ")],
 "<strong><code>/mcp</code> はセッション内コマンドです。</strong>ターミナルに貼ると <code>command not found</code> になります——ターミナル側は <code>claude mcp list</code>。もう一つ、<strong>MCP ツール検索が既定で有効</strong>なので、起動時に読まれるのはツール名だけで、完全な JSON スキーマは必要になってから遅延ロードされます。「MCP を足すと重い」の程度は、昔の記事の印象より軽くなっています。"),

14: ("ch14-plugins.html", 4,
 "プラグインは<strong>「配布のための箱」</strong>。作るタイミングを間違えなければ管理コストは増えません。",
 [("<code>.claude/</code> で試作し、共有段階で箱にする", "最初からプラグインにすると試行錯誤が重い。2 つ目のリポジトリで必要になったときが転換点", "<a href=\"ch09-extension-overview.html#s9-3\">9-3</a> の導入トリガー"),
  ("<code>name</code> が名前空間になる", "チームのスキル名が衝突しない。<code>/my-plugin:review</code> の形で呼べる", "<code>.claude-plugin/plugin.json</code>"),
  ("<code>version</code> を上げると更新が届く", "配布したあとの改善を全員に反映できる。省略すると git の SHA 単位になる", "セマンティックバージョンを付ける"),
  ("ローカル検証してから配る", "壊れたものを配らずに済む", "<code>claude --plugin-dir ./my-plugin</code> → <code>/reload-plugins</code>"),
  ("型付き言語ならコードインテリジェンス", "ファイル全読みが定義ジャンプに置き換わる。速度とコストの両方に効く", "公式マーケットプレイスから導入")],
 "<strong>プラグイン由来のサブエージェントでは <code>hooks</code> / <code>mcpServers</code> / <code>permissionMode</code> が無視されます。</strong>セキュリティ上の制限で、必要なら定義を <code>.claude/agents/</code> にコピーします。裏を返せば、<strong>他人のプラグインのスキルやフックは、あなたの権限で任意のコードを実行しうる</strong>ということです。導入前に中身を読む習慣は、社内配布であっても持っておいてください。"),

15: ("ch15-settings-and-security.html", 9,
 "権限ルールは<strong>評価順を知らないと必ずハマります</strong>。導入審査で問われる論点もここに集約しました。",
 [("評価順は deny → ask → allow", "最初にマッチしたものが結果を決める。ルールの詳細度は順序を変えない", "広い deny は狭い allow より<strong>常に</strong>優先"),
  ("配列型の設定はマージされる", "低優先度のスコープからでも許可を追加できる。チーム設定と個人設定を併用できる", "<code>permissions.allow</code> など"),
  ("権限は <code>/permissions</code> から足す", "既存の <code>settings.local.json</code> をコピペで壊さずに済む", "<code>/permissions</code>"),
  ("<code>/sandbox</code> で確認を減らす", "ファイルシステムとネットワークを分離したうえで、権限プロンプトを減らせる", "<code>/sandbox</code>"),
  ("保護されたパスは事前承認できない", "<code>.git</code> <code>.claude</code> <code>.gitconfig</code> などへの書き込みは <code>permissions.allow</code> でも通らない", "設計どおりの挙動。回避しない")],
 "<strong><code>Bash(aws *)</code> を deny しつつ <code>Bash(aws s3 ls)</code> だけ allow する、という書き方はできません。</strong>広い deny が常に勝つためで、権限設計でいちばん多いつまずきです。もう一つ、導入審査でよく誤解される点——<strong>リポジトリ全体が自動でアップロードされるわけではありません</strong>。送信されるのは Claude が実際に読んだ範囲だけです。商用アカウント（Team / Enterprise / API）はコードを生成モデルの学習に使いません。"),

16: ("ch16-automation-and-sdk.html", 5,
 "対話の外に出すときは、<strong>再現性と権限の 2 点</strong>を先に固めます。",
 [("CI では <code>--bare</code> を付ける", "フック・スキル・MCP・CLAUDE.md の自動検出をスキップし、マシンによらず同じ結果になる（公式推奨）", "ただし認証は <code>ANTHROPIC_API_KEY</code> が必要"),
  ("無人実行は必ずツールを絞る", "権限モードだけに頼らない。事故ったときの被害範囲を先に決めておく", "<code>--allowedTools</code> / <code>--permission-mode dontAsk</code>"),
  ("出力を機械処理するなら構造化する", "パースを正規表現でやらずに済み、パイプラインが壊れにくい", "<code>--output-format json --json-schema</code>"),
  ("<code>-p</code> の実行も後から追える", "CI で何が起きたかをセッションとして再開して調べられる", "<code>--resume</code>（<code>--no-session-persistence</code> で無効化）"),
  ("自動レビューは前処理であって代替ではない", "マージ承認の責任は従来どおり。PR 数と CI 時間の増加も見積もる", "「差分を作成者が説明できること」を条件に")],
 "<strong>定期実行の止め方は、登録方法ごとに違います。</strong>自然文で頼んだタスクは <code>Esc</code> では消えず、「◯◯のタスクをキャンセルして」と頼む必要があります。<code>/loop 10m</code> のような固定間隔も <code>Esc</code> では止まりません（間隔なしの <code>/loop</code> だけは <code>Esc</code> で保留中の起床がクリアされます）。いずれも<strong>作成から 7 日で自動失効</strong>します。もう一つ、<strong><code>-p</code> の非対話実行では信頼検証が無効になります</strong>——プロンプトインジェクション対策が 1 枚薄くなる点は、CI 設計で意識してください。"),

17: ("ch17-learning-roadmap.html", 5,
 "ロードマップの価値は<strong>「次に何をやるか」が常に 1 つに決まる</strong>ことです。",
 [("1 日目は 5 つだけ", "インストール → 質問 → <code>/init</code> → <code>Shift+Tab</code> → <code>/rewind</code>。ここまでで「戻せる」安心感が得られる", "巻き戻せると分かると任せる量が増える"),
  ("1 週目の合格ラインは説明できること", "<code>/doctor</code> と <code>/context</code> の出力を自分の言葉で説明できれば、以降は自力で切り分けられる", "<code>/doctor</code> / <code>/context</code>"),
  ("拡張は症状ドリブンで足す", "「学ぶべき機能」ではなく「今困っていること」から選ぶので、使わない設定が増えない", "<a href=\"ch09-extension-overview.html#s9-3\">9-3</a> のトリガー表"),
  ("チーム展開は強制と指針を分けて設計", "管理設定＝クライアントが強制／管理 CLAUDE.md＝あくまで指示。混ぜると効かない", "<a href=\"#s17-4\">17-4</a>"),
  ("追いかけ方を決めておく", "仕様変更が速い。定点観測の場所を 1 つ決めておけば陳腐化しない", "What's new と <code>/release-notes</code>")],
 "<strong>セッションを離れずに更新履歴を読めます。</strong><code>/release-notes</code> は意外と知られていないコマンドで、「先週まで無かった挙動」に出くわしたときの初手として有効です。週次ダイジェストの What's new と合わせて、月 1 回眺めるだけでも、この資料のような二次情報だけを追うより確実に最新化できます。"),

18: ("ch18-sources.html", 4,
 "情報ソースの持ち帰りは 1 つ——<strong>公式を Claude 自身に読ませる</strong>ことです。",
 [("<code>llms.txt</code> を読ませる", "全ページの機械可読インデックス。仕様で迷ったら本人に最新を引きに行かせるのが最速で確実", "「<code>code.claude.com/docs/llms.txt</code> を見て◯◯の仕様を確認して」"),
  ("日本語版が古いことがある", "本資料でも複数の相違を確認済み（サブエージェントの上限など）。数値と仕様は英語版で裏を取る", "<code>/docs/en/</code> に切り替える"),
  ("旧 URL はリダイレクトされる", "<code>docs.claude.com/ja/docs/claude-code/*</code> のブックマークは新 URL へ更新する", "<code>code.claude.com/docs/*</code>"),
  ("コミュニティ資料は事例集として使う", "アイデアの収集には有用。<strong>仕様の根拠には使わない</strong>", "公式と突き合わせてから採用"),
  ("配布物は必ず中身を読む", "他人のスキル・フック・プラグイン・MCP は、あなたの権限で任意のコードを実行しうる", "信頼できる提供元に限定")],
 "<strong>公式ドキュメントには AI に読ませるための索引が用意されています。</strong><code>llms.txt</code> がそれで、120 ページ超の全ドキュメントが機械可読な形で並んでいます。「この機能の正確な仕様を <code>llms.txt</code> から確認して」と頼めば、二次情報の古さに悩まされずに済みます。この資料を含め、人が書いた解説より公式を引かせるほうが速い場面は多くあります。"),
}


def build(num, sec, lede, rows, trivia):
    out = ['  <article class="slide" id="s%d-%d" data-slide="%d-%d" data-slide-title="%s">'
           % (num, sec, num, sec, TITLE),
           '    <h3>%d-%d. %s</h3>' % (num, sec, TITLE),
           '    <p>%s</p>' % lede,
           '    <div class="table-scroll">',
           '      <table>',
           '        <thead><tr><th>覚えること</th><th>仕事での効き目</th><th>具体的な操作</th></tr></thead>',
           '        <tbody>']
    for a, b, c in rows:
        out.append('          <tr><td><strong>%s</strong></td><td>%s</td><td>%s</td></tr>' % (a, b, c))
    out += ['        </tbody>', '      </table>', '    </div>',
            '    <div class="note">',
            '      <span class="label">意外と知られていない</span>',
            '      <p>%s</p>' % trivia,
            '    </div>',
            '  </article>']
    return "\n".join(out)


def main():
    toc = json.loads((GUIDE / "toc.json").read_text(encoding="utf-8"))
    for num, (fname, sec, lede, rows, trivia) in sorted(DATA.items()):
        path = GUIDE / fname
        doc = path.read_text(encoding="utf-8")
        assert 'id="s%d-%d"' % (num, sec) not in doc, "%s に既に %d-%d がある" % (fname, num, sec)
        # 章の閉じタグ </section> の直前に差し込む
        marker = "</section>\n\n<!-- PAGER:START -->"
        assert doc.count(marker) == 1, fname
        doc = doc.replace(marker, build(num, sec, lede, rows, trivia) + "\n" + marker)
        path.write_text(doc, encoding="utf-8")

        ch = next(c for c in toc["chapters"] if c["num"] == num)
        ch["sections"].append({"id": "s%d-%d" % (num, sec), "title": TITLE})
        print("%-38s + %d-%d" % (fname, num, sec))

    (GUIDE / "toc.json").write_text(
        json.dumps(toc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("toc.json 更新")


if __name__ == "__main__":
    main()
