import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, timezone
from streamlit_gsheets import GSheetsConnection
import os
import io
from break_slider import break_slider

# ==========================================
# 1. ページ設定と時間判定
# ==========================================
st.set_page_config(page_title="PIPPON TIME", layout="centered")

JST = timezone(timedelta(hours=+9), 'JST')
now = datetime.now(JST)
is_night = (now.hour >= 17 or now.hour < 8)
MAIN_GRAY = "#454444"

if is_night:
    bg_color = "#544C78"      # 深いネイビー
    disp_text = "#FDFBF9"     # 少し柔らかい白
    box_bg = "rgba(255, 255, 255, 0.06)"
    clock_col = "#e6eaf2"
else:
    bg_color = "#ffffff"
    disp_text = "#454444"
    box_bg = "#f9f9f9"
    clock_col = "#454444"

# --- Google Sheets 接続設定 ---
secrets = dict(st.secrets["connections"]["gsheets"])
secrets["private_key"] = secrets["private_key"].replace("\\n", "\n")

conn = st.connection("gsheets", type=GSheetsConnection)

URL = "https://docs.google.com/spreadsheets/d/1kNXfJ_olZR_ieVc0HayHad93wG7yv_RcQqPEaPdRT1g/edit?gid=594767002#gid=594767002"

# ==========================================
# セッション状態（ログイン情報）の初期化
# ==========================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "company_id" not in st.session_state:
    st.session_state.company_id = None
if "company_name" not in st.session_state:
    st.session_state.company_name = None

# ==========================================
# 2. CSSデザイン (ボタン・メッセージ・全体)
# ==========================================
st.markdown(f"""
<style>

.stApp {{
    {"background: linear-gradient(180deg, #161445 0%, #0b0f2a 60%, #020617 100%) !important;" if is_night else f"background-color: {bg_color} !important;"}
    font-family: 'Noto Sans JP', sans-serif;
}}

[data-testid="stAppViewBlockContainer"] {{
    max-width: 500px !important;
    margin: 0 auto;
}}
[data-testid="stMainBlockContainer"] {{
    transform: translateY(-60px);
}}
header, footer {{ visibility: hidden !important; }}

/* タブレット誤操作防止 */
* {{
    user-select: none !important;
    -webkit-user-select: none !important;
    -webkit-tap-highlight-color: transparent !important;
}}
html {{ touch-action: manipulation !important; }}

/* 氏名selectの見た目 */
div[data-baseweb="select"] > div {{
    background-color: #ffffff !important;
    color: #371637 !important;
    height: 64px !important;
    border-radius: 20px !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div[data-testid="stSelectbox"] div[role="button"] {{
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    height: 100% !important;
    font-size: 20px !important;
    font-weight: 500 !important;
}}

div[data-testid="stSelectbox"] input {{
    caret-color: transparent !important;
    cursor: pointer !important;
}}

div[data-testid="stSelectbox"],
div[data-testid="stSelectbox"] * {{
    cursor: pointer !important;
}}

/* 爆速安定ポンッの吹き出しCSS */
.balloon-msg {{
    margin: 20px auto;
    padding: 15px 25px;
    width: 100%;
    text-align: center;
    background-color: #ffffff;
    color: {MAIN_GRAY};
    border-radius: 30px;
    font-weight: 500;
    font-size: 17px;
    position: relative;
    box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    transform: scale(1);
    opacity: 1;
}}

.balloon-msg:after {{
    content: "";
    position: absolute;
    top: -12px;
    left: 50%;
    margin-left: -10px;
    border-bottom: 12px solid #ffffff;
    border-left: 10px solid transparent;
    border-right: 10px solid transparent;
}}

.balloon-pop {{
    animation: popBounce 0.22s cubic-bezier(0.34, 1.56, 0.64, 1) forwards !important;
    transform-origin: center top;
}}

@keyframes popBounce {{
    0% {{ transform: scale(0.6); opacity: 0; }}
    80% {{ transform: scale(1.04); opacity: 1; }}
    100% {{ transform: scale(1); opacity: 1; }}
}}

/* --- 🔴 ボタン全体の配置を「中央」に固定 --- */
div[data-testid="stButton"] {{
    display: flex !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 15px 0 !important;
}}

/* --- 🔵 ボタン単体のデザイン：昼夜の背景に完全同期 --- */
div[data-testid="stButton"] button {{
    width: 320px !important; 
    height: 60px !important;
    margin: 0 auto !important;

    /* 💡 昼夜判定（is_night）に合わせて、ボタンの中身の色を自動で変化させます */
    background: {"linear-gradient(135deg, rgba(16, 20, 56, 0.8) 0%, rgba(7, 10, 30, 0.9) 100%)" if is_night else f"linear-gradient(135deg, rgba(255,255,255,0.9) 0%, {bg_color} 100%)"} !important;
    
    /* 文字色も昼夜で自動切り替え（disp_textに同期） */
    color: {disp_text} !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    letter-spacing: 0.3em !important;
    text-shadow: {"0 0 10px rgba(255, 255, 255, 0.5)" if is_night else "none"} !important;
    
    /* 外枠：極細のグラデーションライン */
    border: 1px solid transparent !important;
    background-origin: border-box !important;
    background-clip: padding-box, border-box !important;
    background-image: 
        {"linear-gradient(135deg, rgba(16, 20, 56, 0.9), rgba(7, 10, 30, 0.95))" if is_night else f"linear-gradient(135deg, {bg_color}, {bg_color})"}, 
        linear-gradient(135deg, #ffeb3b, #ff9800, #e91e63, #3f51b5, #00f2fe) !important;
        
    /* 形状：美しい傾斜角 */
    clip-path: polygon(12px 0%, calc(100% - 12px) 0%, 100% 12px, 100% calc(100% - 12px), calc(100% - 12px) 100%, 12px 100%, 0% calc(100% - 12px), 0% 12px) !important;
    border-radius: 0px !important;
    
    /* 影：昼夜それぞれで不自然じゃない影の強さに調整 */
    box-shadow: {"0 10px 30px rgba(0, 0, 0, 0.4), 0 0 15px rgba(63, 81, 181, 0.3)" if is_night else "0 8px 20px rgba(0,0,0,0.06)"} !important;
    
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1) !important;
}}

/* ✨ ホバー時：横幅が少しだけ広がり、発光が強まる */
div[data-testid="stButton"] button:hover {{
    width: 330px !important;
    opacity: 1 !important;
    box-shadow: 0 0 40px rgba(0, 242, 254, 0.6) !important;
    {"text-shadow: 0 0 15px rgba(255, 255, 255, 1) !" if is_night else ""}
}}

/* ⚡️ クリック時：カチッと沈み込む */
div[data-testid="stButton"] button:active {{
    transform: scale(0.96) !important;
}}

/* Streamlit標準UIを非表示 */
[data-testid="stStatusWidget"] {{ display: none !important; }}
[data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stToolbar"] {{ display: none !important; }}
[data-testid="stHeader"] {{ display: none !important; }}
[data-testid="stToast"] {{ display: none !important; }}
.stSpinner {{ display: none !important; }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔑 顧客ログイン判定処理
# ==========================================
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style="
        background-color: {box_bg};
        padding: 40px 30px;
        border-radius: 24px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 15px 45px rgba(0,0,0,0.3);
        margin-bottom: 25px;
    ">
        <div style="color:{disp_text}; text-align:center; letter-spacing:0.2em; font-size:26px; font-weight:bold; margin-bottom:10px;">CRYSTAL TIME CARD</div>
    </div>
    """, unsafe_allow_html=True)
    
    input_id = st.text_input("COMPANY ID（企業ID）", placeholder="例: test01", key="login_id_input")
    input_pw = st.text_input("PASSWORD（パスワード）", type="password", placeholder="••••••••", key="login_pw_input")
    
    st.markdown("<br>", unsafe_allow_html=True)
    login_clicked = st.button("LOG IN", key="login_btn")
    
    if login_clicked:
        if input_id and input_pw:
            # スプレッドシートの読み込み
            master_df = conn.read(spreadsheet=URL, worksheet="契約企業マスター", ttl=0)
            
            if len(master_df.columns) >= 2:
                id_col = master_df.columns[0]  # 1番左の列
                pw_col = master_df.columns[1]  # 左から2番目の列
                name_col = master_df.columns[2] if len(master_df.columns) > 2 else id_col 
                
                # 💡 IDを文字列・トリム・小文字に
                master_df[id_col] = master_df[id_col].astype(str).str.strip().str.lower()
                
                # 💡 【超重要】パスワードが「1234.0」の文字列になっていたら「.0」を消し去る処理
                master_df[pw_col] = master_df[pw_col].astype(str).str.strip()
                master_df[pw_col] = master_df[pw_col].apply(lambda x: x[:-2] if x.endswith('.0') else x)
                
                # 画面からの入力値
                input_id_clean = str(input_id).strip().lower()
                input_pw_clean = str(input_pw).strip()
                
                # 照合処理
match = master_df[(master_df[id_col] == input_id_clean) & (master_df[pw_col] == input_pw_clean)]

if not match.empty:
    st.session_state.logged_in = True
    st.session_state.company_id = input_id_clean
    st.session_state.company_name = match.iloc[0][name_col]
    
    # 💡 【追加】ログインに使ったパスワードをセッションに保存しておく
    st.session_state.company_pw = input_pw_clean 
    
    st.rerun()
                else:
                    st.error("企業IDまたはパスワードが正しくありません。")
            else:
                st.error("スプレッドシートの列が足りません。")
        else:
            st.warning("企業IDとパスワードの両方を入力してください。")
    st.stop()


# ==========================================
# 🏢 全社共通のタブ名定義
# ==========================================
staff_tab_name = "全社共通_スタッフ"
data_tab_name = "全社共通_打刻"

if st.sidebar.button("ログアウト", key="logout_btn"):
    st.session_state.logged_in = False
    st.session_state.company_id = None
    st.session_state.company_name = None
    st.rerun()


# ==========================================
# 3. 時計＆星セクション（強制再描画・安定版）
# ==========================================
st.components.v1.html(f"""
    <div id="container" style="width: 100%; height: 180px; position: relative; overflow: hidden; border-radius:20px; cursor: crosshair; background: transparent;">
        <canvas id="bg" style="position: absolute; top:0; left:0; width:100%; height:100%; z-index:1;"></canvas>
        <canvas id="clk" width="160" height="160" style="position: relative; z-index:2; margin: 0 auto; display: block; pointer-events: none;"></canvas>
    </div>
    <script>
    const container = document.getElementById('container');
    const bg = document.getElementById('bg'); const bctx = bg.getContext('2d');
    const clk = document.getElementById('clk'); const cctx = clk.getContext('2d');
    let pts = []; let mouse = {{ x: -1000, y: -1000 }};

    // 💡 画面サイズを確実に取得してキャンバスに割り当てる処理
    function res() {{ 
        bg.width = container.clientWidth || 450; 
        bg.height = 180; 
    }}

    container.addEventListener('mousemove', (e) => {{
        const rect = container.getBoundingClientRect();
        mouse.x = e.clientX - rect.left;
        mouse.y = e.clientY - rect.top;
    }});
    container.addEventListener('mouseleave', () => {{ mouse.x = -1000; mouse.y = -1000; }});

    window.addEventListener('resize', res); 
    res();

    // 💡 画面が切り替わった直後のサイズバグを防ぐため、0.1秒後にもう一度強制リサイズをかける
    setTimeout(res, 100);

    const cols = ["#ffeb3b","#ff9800","#f44336","#e91e63","#3f51b5"];
    for(let i=0; i<30; i++) {{
        pts.push({{
            x: Math.random() * 450, y: Math.random() * 180,
            vx: (Math.random()-0.5) * 0.4, vy: (Math.random()-0.5) * 0.4,
            c: cols[Math.floor(Math.random()*5)], s: Math.random() * 2 + 1
        }});
    }}

    function draw() {{
        bctx.clearRect(0,0,bg.width,bg.height);
        pts.forEach(p => {{
            let dx = mouse.x - p.x; let dy = mouse.y - p.y;
            let dist = Math.sqrt(dx*dx + dy*dy);
            if(dist < 70 && dist > 0) {{
                let force = (70 - dist) / 70;
                p.x -= dx / dist * force * 5;
                p.y -= dy / dist * force * 5;
            }}

            p.x += p.vx; p.y += p.vy;
            if(p.x < 0 || p.x > bg.width) p.vx *= -1;
            if(p.y < 0 || p.y > bg.height) p.vy *= -1;

            bctx.globalAlpha = {0.8 if is_night else 0.4};
            bctx.fillStyle = p.c;
            bctx.beginPath();
            bctx.arc(p.x, p.y, p.s, 0, Math.PI*2);
            bctx.fill();
        }});

        cctx.setTransform(1,0,0,1,0,0);
        cctx.clearRect(0,0,160,160);
        cctx.translate(80,80);
        cctx.font = "500 13px Arial";
        cctx.fillStyle = "{clock_col}";
        cctx.textAlign = "center";

        for(let n=1; n<=12; n++) {{
            cctx.fillText(n, 65*Math.sin(n*Math.PI/6), -65*Math.cos(n*Math.PI/6)+5);
        }}

        let d = new Date();
        let jst = new Date(d.toLocaleString("en-US", {{timeZone: "Asia/Tokyo"}}));
        let h = jst.getHours()%12, m = jst.getMinutes(), s = jst.getSeconds();

        const hand = (r,l,w,c) => {{
            cctx.beginPath();
            cctx.lineWidth = w;
            cctx.lineCap = "round";
            cctx.strokeStyle = c;
            cctx.moveTo(0,0);
            cctx.rotate(r);
            cctx.lineTo(0,-l);
            cctx.stroke();
            cctx.rotate(-r);
        }};

        hand((h*Math.PI/6)+(m*Math.PI/360), 40, 5, "{clock_col}");
        hand(m*Math.PI/30, 60, 3, "{clock_col}");
        hand(s*Math.PI/30, 70, 1.2, "#f44336");

        requestAnimationFrame(draw);
    }}
    draw();
    </script>
""", height=180)

# ==========================================
# 4. 操作セクション
# ==========================================
try:
    df_members = conn.read(spreadsheet=URL, worksheet=staff_tab_name, ttl=0)

    if df_members is None or df_members.empty or "名前" not in df_members.columns:
        names = ["スタッフを追加してください"]
    else:
        if "企業ID" in df_members.columns:
            # 型を文字列にして、トリムと小文字化を合わせておく（ログイン処理と合わせるため）
            df_members["企業ID"] = df_members["企業ID"].astype(str).str.strip().str.lower()
            
            # 現在ログインしている企業の行だけを抽出
            df_target_company = df_members[df_members["企業ID"] == st.session_state.company_id]
        else:
            # 万が一「企業ID」列がない場合は、とりあえず全表示（エラー防止）
            df_target_company = df_members

        # 2. 絞り込んだデータから名前のリストを作る
        names = (
            df_target_company["名前"] # df_members から df_target_company に変更
            .dropna()
            .astype(str)
            .str.strip()
            .tolist()
        )
        if not names:
            names = ["スタッフを追加してください"]

except Exception as e:
    initial_staff_df = pd.DataFrame([{"名前": "スタッフを追加してください"}])
    conn.update(spreadsheet=URL, worksheet=staff_tab_name, data=initial_staff_df)
    names = ["スタッフを追加してください"]

st.markdown(
    f'<div style="color:{disp_text}; text-align:center; letter-spacing:0.2em; font-size:22px; margin:10px 0;">{st.session_state.company_name}</div>',
    unsafe_allow_html=True
)

selected_name = st.selectbox("USER", names, label_visibility="collapsed")

st.components.v1.html("""
<script>
(function() {
  const doc = window.parent.document;

  function lockSelectboxTyping() {
    const selectInputs = doc.querySelectorAll('div[data-testid="stSelectbox"] input');

    selectInputs.forEach((input) => {
      input.setAttribute("readonly", "readonly");
      input.setAttribute("inputmode", "none");
      input.setAttribute("autocomplete", "off");
      input.setAttribute("autocorrect", "off");
      input.setAttribute("autocapitalize", "off");
      input.setAttribute("spellcheck", "false");

      input.addEventListener("keydown", (e) => {
        const allowed = ["ArrowUp", "ArrowDown", "Enter", "Escape", "Tab"];
        if (!allowed.includes(e.key)) {
          e.preventDefault();
        }
      });

      input.addEventListener("beforeinput", (e) => {
        e.preventDefault();
      });

      input.addEventListener("input", () => {
        input.value = "";
      });
    });
  }

  lockSelectboxTyping();
  setInterval(lockSelectboxTyping, 500);
})();
</script>
""", height=0)


# --- メッセージ初期化 ---
if 'msg' not in st.session_state:
    st.session_state.msg = "打刻してください"

def calc_work_duration(start_str, end_str, break_minutes):
    if pd.isna(start_str) or pd.isna(end_str):
        return None

    try:
        start_dt = datetime.strptime(str(start_str), "%H:%M")
        end_dt = datetime.strptime(str(end_str), "%H:%M")
        break_minutes = int(break_minutes) if pd.notna(break_minutes) else 0

        total_minutes = int((end_dt - start_dt).total_seconds() // 60) - break_minutes

        if total_minutes < 0:
            total_minutes = 0

        hours = total_minutes // 60
        minutes = total_minutes % 60
        return f"{hours:02d}:{minutes:02d}"
    except Exception:
        return None


def save_to_gsheets(name, action, break_minutes=0):
    now_jst = datetime.now(JST)
    today = now_jst.strftime('%Y-%m-%d')
    time_str = now_jst.strftime('%H:%M')

    try:
        df = conn.read(spreadsheet=URL, worksheet=data_tab_name, ttl=0)
    except Exception:
        df = pd.DataFrame(columns=["名前", "日付", "出勤", "退勤", "休憩(分)", "実稼働"])

    if df is None or df.empty:
        df = pd.DataFrame(columns=["名前", "日付", "出勤", "退勤", "休憩(分)", "実稼働"])

    for col in ["名前", "日付", "出勤", "退勤", "休憩(分)", "実稼働"]:
        if col not in df.columns:
            df[col] = None

    df = df[["名前", "日付", "出勤", "退勤", "休憩(分)", "実稼働"]].copy()
    
    df = df.reset_index(drop=True)
    df["名前"] = df["名前"].astype("string")
    df["日付"] = df["日付"].astype("string")
    df["出勤"] = df["出勤"].astype("string")
    df["退勤"] = df["退勤"].astype("string")
    df["休憩(分)"] = df["休憩(分)"].astype("Int64")
    df["実稼働"] = df["実稼働"].astype("string")

    today_rows = df[(df["名前"] == name) & (df["日付"] == today)]

    if action == "出勤":
        if not today_rows.empty:
            idx = today_rows.index[-1]
            if pd.notna(df.loc[idx, "出勤"]) and pd.isna(df.loc[idx, "退勤"]):
                st.warning("すでに出勤済みです")
                return False
        
        new_row = pd.DataFrame([{
    "企業ID": st.session_state.company_id,
    "名前": name,
    "日付": today,
    "出勤": time_str,
    "退勤": None,
    "休憩(分)": None,
    "実稼働": None
}])

        df = pd.concat([df, new_row], ignore_index=True)
        if "企業ID" in df.columns:
            df.loc[df["企業ID"].isna(), "企業ID"] = st.session_state.company_id
    
    elif action == "退勤":
        if today_rows.empty:
            st.error("先に出勤を押してください")
            return False
        
        idx = today_rows.index[-1]
        
        if pd.notna(df.loc[idx, "退勤"]):
            st.warning("すでに退勤済みです")
            return False

        df.loc[idx, "退勤"] = time_str
        df.loc[idx, "休憩(分)"] = break_minutes
        df.loc[idx, "実稼働"] = calc_work_duration(
            df.loc[idx, "出勤"], df.loc[idx, "退勤"], df.loc[idx, "休憩(分)"]
        )

    out_df = df.reset_index(drop=True)
    out_df = out_df[["名前","日付", "出勤", "退勤", "休憩(分)", "実稼働"]].copy()
    
    conn.update(spreadsheet=URL, worksheet=data_tab_name, data=out_df)
    return True


selected_break = break_slider(
    label="今日の休憩時間",
    min_value=0,
    max_value=60,
    step=5,
    value=60,
    text_color=disp_text,
    key="break_slider",
)

balloon_spot = st.empty()

st.markdown('<div class="timecard-buttons">', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    if st.button("出 勤", key="in"):
        if selected_name == "スタッフを追加してください":
            st.warning("管理者メニューからスタッフを追加してください。")
        else:
            st.session_state.msg = f"✨ {selected_name}さん、おはよう！"
            save_to_gsheets(selected_name, "出勤", selected_break)

with c2:
    if st.button("退 勤", key="out"):
        if selected_name == "スタッフを追加してください":
            st.warning("管理者メニューからスタッフを追加してください。")
        else:
            st.session_state.msg = f"🌙 {selected_name}さん、お疲れ様！"
            save_to_gsheets(selected_name, "退勤", selected_break)
st.markdown('</div>', unsafe_allow_html=True)

balloon_spot.markdown(f"""
<div id="live-balloon" class="balloon-msg balloon-pop">{st.session_state.msg}</div>
""", unsafe_allow_html=True)


# ==========================================
# 🛠 5. 管理者メニュー（実運用・爆速設計版）
# ==========================================
with st.expander("🛠 管理者メニュー"):
    pw = st.text_input("パスワード", type="password")

    if pw == st.session_state.get("company_pw")::
        tab1, tab2, tab3 = st.tabs(["📊 打刻データ出力", "👥 スタッフ管理", "📈 集計"])

        with tab1:
            st.write("### 📄 税理士提出用ファイルの作成")
            try:
                # 全データから、ログイン中の「企業ID」の打刻だけをシュッと絞り込んで表示
                df_all_raw = conn.read(spreadsheet=URL, worksheet=data_tab_name, ttl=0)
                if df_all_raw is not None and not df_all_raw.empty and "企業ID" in df_all_raw.columns:
                    df = df_all_raw[df_all_raw["企業ID"] == st.session_state.company_id].copy()
                    # 画面表示用に「企業ID」の列は隠す（見栄えのため）
                    df_display = df.drop(columns=["企業ID"], errors="ignore")
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                else:
                    st.info("データがまだありません")
            except:
                st.info("データがまだありません")

        with tab2:
            try:
                # 全スタッフから、ログイン中の「企業ID」のスタッフだけを絞り込む
                df_all_m = conn.read(spreadsheet=URL, worksheet=staff_tab_name, ttl=0)
                if df_all_m is None or df_all_m.empty:
                    df_all_m = pd.DataFrame(columns=['企業ID', '名前'])
                
                # 自分の会社分を抽出
                df_m = df_all_m[df_all_m['企業ID'] == st.session_state.company_id].copy()
                curr_names = df_m['名前'].tolist() if not df_m.empty else []
            except:
                df_all_m = pd.DataFrame(columns=['企業ID', '名前'])
                df_m = pd.DataFrame(columns=['企業ID', '名前'])
                curr_names = []

            st.markdown("### スタッフの追加")
            new_n = st.text_input("新しい名前を入力", key="new_staff_input")

            if st.button("新規登録", key="admin_add"):
                if new_n and new_n not in curr_names:
                    # 初期文字の削除判定（自分の会社のデータ内だけで判定）
                    if "【テスト用】スタッフを追加してください" in curr_names:
                        df_m = df_m[df_m['名前'] != "【テスト用】スタッフを追加してください"]
                        # 元の全体データからも該当行を消す
                        df_all_m = df_all_m[~((df_all_m['企業ID'] == st.session_state.company_id) & (df_all_m['名前'] == "【テスト用】スタッフを追加してください"))]
                    
                    # 登録データにしっかり「企業ID」を持たせる！
                    new_staff_df = pd.DataFrame([{'企業ID': st.session_state.company_id, '名前': new_n}])
                    
                    # 全体データに対して合体させる
                    updated_df = pd.concat([df_all_m, new_staff_df], ignore_index=True)
                    conn.update(spreadsheet=URL, worksheet=staff_tab_name, data=updated_df)
                    st.success(f"{new_n}さんを登録しました")
                    st.rerun()

            st.divider()

            if curr_names and curr_names != ["【テスト用】スタッフを追加してください"]:
                st.markdown("### 登録内容の変更・削除")
                target = st.selectbox("対象のスタッフを選択", curr_names)
                renamed = st.text_input("名前を修正する", value=target)

                c1_admin, c2_admin = st.columns(2)

                with c1_admin:
                    if st.button("上書き保存", key="admin_save"):
                        # 「自社の対象者」だけをピンポイントに書き換える（他社を巻き込まない）
                        mask = (df_all_m['企業ID'] == st.session_state.company_id) & (df_all_m['名前'] == target)
                        df_all_m.loc[mask, '名前'] = renamed
                        
                        conn.update(spreadsheet=URL, worksheet=staff_tab_name, data=df_all_m)
                        st.success("修正しました")
                        st.rerun()

                with c2_admin:
                    if "delete_confirm" not in st.session_state:
                        st.session_state.delete_confirm = False

                    if not st.session_state.delete_confirm:
                        if st.button("この人を削除", key="admin_del_pre"):
                            st.session_state.delete_confirm = True
                            st.rerun()
                    else:
                        st.warning(f"【確認】本当に {target} さんを消しますか？")
                        col_yes, col_no = st.columns(2)

                        with col_yes:
                            if st.button("🔴 削除実行", key="admin_del_final"):
                                # 自社の対象者だけを排除する
                                df_all_m = df_all_m[~((df_all_m['企業ID'] == st.session_state.company_id) & (df_all_m['名前'] == target))]
                                
                                # もし自社のスタッフが誰もいなくなったら、テスト用文字を戻す（自社枠として）
                                if df_all_m[df_all_m['企業ID'] == st.session_state.company_id].empty:
                                    fallback_df = pd.DataFrame([{"企業ID": st.session_state.company_id, "名前": "【テスト用】スタッフを追加してください"}])
                                    df_all_m = pd.concat([df_all_m, fallback_df], ignore_index=True)
                                
                                conn.update(spreadsheet=URL, worksheet=staff_tab_name, data=df_all_m)
                                st.session_state.delete_confirm = False
                                st.rerun()

                        with col_no:
                            if st.button("キャンセル", key="admin_del_cancel"):
                                st.session_state.delete_confirm = False
                                st.rerun()  # 💡 r.rerun() から修正しました！
            else:
                st.info("登録されているスタッフがいません。")

        with tab3:
            st.markdown("""
                <style>
                [data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #31333F !important; }
                [data-testid="stMetricLabel"] { font-size: 14px !important; color: #555555 !important; }
                [data-testid="stMetric"] { background-color: #f8f9fa; padding: 10px 15px; border-radius: 6px; border: 1px solid #eceeef; }
                </style>
            """, unsafe_allow_html=True)

            st.markdown("### 📈 スタッフ別・月別集計ダッシュボード")
            try:
                # 集計用データも、自社分だけにガッツリ絞り込む
                df_all_calc = conn.read(spreadsheet=URL, worksheet=data_tab_name, ttl=0)
                if df_all_calc is not None and not df_all_calc.empty and "企業ID" in df_all_calc.columns:
                    df = df_all_calc[df_all_calc["企業ID"] == st.session_state.company_id].copy()
                else:
                    df = None
            except:
                df = None

            if df is None or df.empty or "実稼働" not in df.columns:
                st.info("集計するデータがまだありません")
            else:
                df_calc = df.dropna(subset=["日付", "名前"]).copy()
                df_calc["日付"] = pd.to_datetime(df_calc["日付"], errors="coerce")
                df_calc["月"] = df_calc["日付"].dt.to_period("M").astype(str)

                months = sorted(df_calc["月"].dropna().unique(), reverse=True)
                if not months:
                    st.info("有効な月別データがありません")
                else:
                    selected_month = st.selectbox("対象月を選択", months, key="report_month_select")
                    filtered = df_calc[df_calc["月"] == selected_month].copy()

                    def to_total_minutes(val):
                        if pd.isna(val) or val in ["None", "nan", "", "<NA>"]: return 0
                        try:
                            h, m = map(int, str(val).split(':'))
                            return h * 60 + m
                        except: return 0

                    filtered["稼働分"] = filtered["実稼働"].apply(to_total_minutes)

                    def format_minutes_to_str(mins):
                        h = mins // 60
                        m = mins % 60
                        return f"{h:02d}:{m:02d}"

                    st.markdown("#### 🔍 スタッフ個別の勤怠詳細")
                    active_staffs = sorted(filtered["名前"].unique())
                    
                    if not active_staffs:
                        st.info("選択された月の打刻データがありません")
                    else:
                        target_staff = st.selectbox("スタッフを選択してください", active_staffs, key="staff_detail_select", label_visibility="collapsed")
                        
                        staff_detail = filtered[filtered["名前"] == target_staff].copy()
                        staff_detail["日付_表示"] = staff_detail["日付"].dt.strftime('%Y-%m-%d')
                        staff_detail = staff_detail.sort_values("日付", ascending=False)
                        
                        display_detail = staff_detail[["日付_表示", "出勤", "退勤", "休憩(分)", "実稼働"]].rename(columns={"日付_表示": "日付"})
                        display_detail = display_detail.fillna("-").replace({"None": "-", "nan": "-", "": "-"})
                        st.dataframe(display_detail, use_container_width=True, hide_index=True)
                        
                        staff_total_mins = staff_detail["稼働分"].sum()
                        staff_total_str = format_minutes_to_str(staff_total_mins)
                        staff_total_hours = round(staff_total_mins / 60, 2)
                        staff_days = len(staff_detail)
                        
                        col_metric1, col_metric2, col_metric3 = st.columns(3)
                        with col_metric1: st.metric(label="当月出勤日数", value=f"{staff_days} 日")
                        with col_metric2: st.metric(label="総稼働時間", value=staff_total_str)
                        with col_metric3: st.metric(label="給与計算用時間", value=f"{staff_total_hours} h")
                        
                        # ダウンロードするCSVからも「企業ID」を除外して綺麗にする
                        staff_download_df = staff_detail.drop(columns=["月", "稼働分", "日付_表示"], errors="ignore")
                        if "企業ID" in staff_download_df.columns:
                            staff_download_df = staff_download_df.drop(columns=["企業ID"])
                        
                        csv_individual = staff_download_df.to_csv(index=False).encode("utf-8-sig")
                        st.download_button(
                            label=f"📥 {target_staff}さんの勤怠CSVをダウンロード",
                            data=csv_individual,
                            file_name=f"勤怠_{target_staff}_{selected_month}.csv",
                            mime="text/csv",
                            key="btn_download_individual",
                            use_container_width=True
                        )
                    
                    st.markdown("#### 👥 全スタッフの月間集計一覧")
                    summary = filtered.groupby("名前").agg(出勤回数=("日付", "count"), 総稼働分=("稼働分", "sum")).reset_index()
                    summary["総稼働時間"] = summary["総稼働分"].apply(format_minutes_to_str)
                    summary["総稼働時間(時間)"] = (summary["総稼働分"] / 60).round(2)

                    disp_summary = summary[["名前", "出勤回数", "総稼働時間", "総稼働時間(時間)"]]
                    disp_summary = disp_summary.fillna("-").replace({"None": "-", "nan": "-", "": "-"})
                    st.dataframe(disp_summary, use_container_width=True, hide_index=True)

                    # 全員分の提出用CSVからも他社データを完全に排除、かつ「企業ID」列を消して出力
                    csv_data = filtered.drop(columns=["月", "稼働分"], errors="ignore")
                    if "企業ID" in csv_data.columns:
                        csv_data = csv_data.drop(columns=["企業ID"])
                        
                    csv_all = csv_data.to_csv(index=False).encode("utf-8-sig")
                    
                    st.download_button(
                        "📥 全員分の月間CSVダウンロード（税理士提出用）",
                        data=csv_all,
                        file_name=f"勤怠一覧_全員_{selected_month}.csv",
                        mime="text/csv",
                        key="btn_download_all",
                        use_container_width=True
                    )

        # 🎨 あなたのサイバーグラデーションCSSをここに完璧に統合！
        st.markdown("""
            <style>
            div[data-testid="stExpander"] button[kind="secondary"],
            div[data-testid="stExpander"] button[kind="primary"] {
                width: 100% !important; height: 50px !important; background-color: transparent !important; font-size: 16px !important; border: 1px solid !important;
                border-image: linear-gradient(90deg, #ffeb3b, #ff9800, #f44336, #e91e63, #3f51b5) 1 !important;
                clip-path: polygon(10px 0%, calc(100% - 10px) 0%, 100% 10px, 100% calc(100% - 10px), calc(100% - 10px) 100%, 10px 100%, 0% calc(100% - 10px), 0% 10px) !important;
                margin-top: 10px !important;
            }
            div[data-testid="stExpander"] div[data-baseweb="input"] button { clip-path: none !important; border: none !important; border-image: none !important; height: auto !important; width: auto !important; }
            </style>
        """, unsafe_allow_html=True)

    else:
        # パスワードが一致しない場合の処理（if pw == "0123": にインデントの縦ラインを合わせてあります）
        st.info("正しいパスワードを入力してください。")
