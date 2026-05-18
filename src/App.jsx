import React, { useState, useEffect, useRef } from "react";

import clockImg    from "./assets/ui/clock_nohand.png";
import punchInImg  from "./assets/ui/punch_in.png";
import punchOutImg from "./assets/ui/punch_out.png";

import cidleImg from "./assets/pippon/cidle.png";

const MOODS = [
  { tag: "日曜日",   moveInterval: 32, moveStep: 0.42 },
  { tag: "月曜日…", moveInterval: 90, moveStep: 0.12 },
  { tag: "火曜日",   moveInterval: 36, moveStep: 0.38 },
  { tag: "水曜日",   moveInterval: 36, moveStep: 0.38 },
  { tag: "木曜日",   moveInterval: 33, moveStep: 0.40 },
  { tag: "花金!!!",  moveInterval: 16, moveStep: 0.60 },
  { tag: "土曜日",   moveInterval: 28, moveStep: 0.44 },
];

const PUNCH_IN_MSGS  = ["おはようございます！","やっと来たか！","今日もよろしく！","遅いじゃないか👊","おはー！","よし、やるか！","ファイトー！"];
const PUNCH_OUT_MSGS = ["お疲れ様！","帰っていいよ！","よく頑張った！","ゆっくり休んでね","早く帰れ笑","またね〜！","お疲れっした！"];

const DAILY_QUOTES = [
  "今日も一歩ずつ、丁寧に。",
  "小さな積み重ねが大きな変化を生む。",
  "笑顔は最高の仕事道具。",
  "丁寧にやった仕事は、必ず誰かに届く。",
  "今日のあなたの頑張りを、未来の自分が感謝する。",
  "焦らなくていい。着実に進めば必ず前に進んでる。",
  "失敗してもいい。挑戦したことが大事。",
  "今日という日は、二度と来ない。",
  "チームの笑顔があなたの力になる。",
  "休むことも仕事のうち。",
  "完璧じゃなくていい。誠実でいよう。",
  "毎日の積み重ねが、あなたの強さになる。",
];

const WEEK_DAYS = ["月","火","水","木","金","土","日"];
const MAX_H = 9;

function fmtTime(t) {
  if (!t) return null;
  const parts = t.split(":");
  if (parts.length < 2) return null;
  return `${parts[0].padStart(2,"0")}:${parts[1].padStart(2,"0")}`;
}

function currentHHMM() {
  const d = new Date();
  return `${String(d.getHours()).padStart(2,"0")}:${String(d.getMinutes()).padStart(2,"0")}:00`;
}

function todayStr() {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
}

// ---- スタッフ選択 ----
function StaffPicker({ value, onChange, names }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);
  useEffect(() => {
    const close = (e) => { if (ref.current && !ref.current.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", close);
    return () => document.removeEventListener("mousedown", close);
  }, []);
  return (
    <div ref={ref} className="relative w-full select-none">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center gap-2 bg-white/90 border border-white shadow-sm hover:bg-white transition-colors"
        style={{ borderRadius: "1.2vw", padding: "0.7vw 1.2vw", fontSize: "0.95vw" }}
      >
        <span style={{ fontSize: "1.1vw" }}>👤</span>
        <span className="flex-1 text-left font-bold text-purple-700">{value || "スタッフを選択"}</span>
        <span className="text-purple-300 font-bold" style={{ fontSize: "0.7vw" }}>▼</span>
      </button>
      {open && (
        <div className="absolute left-0 right-0 bg-white/98 backdrop-blur border border-purple-100 shadow-xl z-50 overflow-hidden"
          style={{ top: "calc(100% + 0.3vw)", borderRadius: "1.2vw" }}>
          {names.map(name => (
            <button key={name} onClick={() => { onChange(name); setOpen(false); }}
              className={`w-full text-left flex items-center gap-2 hover:bg-purple-50 transition-colors
                ${name === value ? "bg-pink-50 text-pink-500" : "text-purple-700"}`}
              style={{ padding: "0.6vw 1.2vw", fontSize: "0.9vw", fontWeight: 600 }}>
              <span style={{ fontSize: "0.85vw" }}>{name === value ? "✓" : "  "}</span>
              {name}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

// ---- 今週の記録バーチャート ----
function WeeklyChart({ weekData }) {
  const today = new Date().getDay(); // 0=日
  const hours = weekData.map(d => d.hours);
  const totalH = hours.reduce((a,b) => a+b, 0);
  const hm = (h) => `${Math.floor(h)}:${String(Math.round((h%1)*60)).padStart(2,"0")}`;
  return (
    <div className="bg-white/75 border border-white shadow-sm flex flex-col h-full"
      style={{ borderRadius: "1.2vw", padding: "0.8vw 0.9vw" }}>
      <div className="flex items-center gap-1 mb-1">
        <span style={{ fontSize: "0.9vw" }}>📊</span>
        <span className="font-black text-purple-800" style={{ fontSize: "0.75vw" }}>今週の記録</span>
      </div>
      <div className="flex items-end justify-between flex-1 px-1" style={{ gap: "0.3vw", minHeight: 0 }}>
        {WEEK_DAYS.map((day, i) => {
          const dayNum = (i + 1) % 7; // 月=1,火=2,...,日=0
          const isToday = dayNum === today;
          const h = hours[i] ?? 0;
          const pct = Math.min(h / MAX_H, 1);
          return (
            <div key={day} className="flex flex-col items-center flex-1" style={{ gap: "0.2vw" }}>
              <div className="w-full rounded-t-full overflow-hidden relative"
                style={{ height: "4.5vw", background: "rgba(200,180,240,0.15)" }}>
                <div className="absolute bottom-0 left-0 right-0 rounded-t-full"
                  style={{
                    height: `${pct * 100}%`,
                    background: isToday
                      ? "linear-gradient(180deg,#F472B6,#EC4899)"
                      : "linear-gradient(180deg,#C084FC,#A855F7)",
                    opacity: h === 0 ? 0.2 : 1,
                  }} />
              </div>
              <span style={{ fontSize: "0.6vw", fontWeight: 700, color: isToday ? "#EC4899" : "#a78bca" }}>{day}</span>
            </div>
          );
        })}
      </div>
      <div className="mt-1 pt-1 border-t border-purple-100/50 flex items-baseline justify-between">
        <span className="text-purple-400 font-bold" style={{ fontSize: "0.65vw" }}>今週合計</span>
        <span className="font-black text-purple-700" style={{ fontSize: "1.0vw" }}>{hm(totalH)}</span>
      </div>
    </div>
  );
}

// ---- 本日の記録 ----
function TodayRecord({ punchIn, punchOut, breakMin, jissabaki }) {
  const Row = ({ icon, label, value, color }) => (
    <div className="flex items-center" style={{ gap: "0.5vw" }}>
      <div className="flex items-center justify-center rounded-full"
        style={{ width: "1.6vw", height: "1.6vw", background: color + "22", flexShrink: 0 }}>
        <span style={{ fontSize: "0.8vw" }}>{icon}</span>
      </div>
      <span className="text-purple-400 font-bold" style={{ fontSize: "0.65vw", minWidth: "2.5vw" }}>{label}</span>
      <span className="font-black ml-auto" style={{ fontSize: "1vw", color }}>
        {value ?? <span style={{ color: "#d8c4f0" }}>--:--</span>}
      </span>
    </div>
  );
  return (
    <div className="bg-white/75 border border-white shadow-sm flex flex-col h-full"
      style={{ borderRadius: "1.2vw", padding: "0.8vw 0.9vw", gap: "0.5vw" }}>
      <div className="flex items-center gap-1 mb-0.5">
        <span style={{ fontSize: "0.9vw" }}>🕐</span>
        <span className="font-black text-purple-800" style={{ fontSize: "0.75vw" }}>本日の記録</span>
      </div>
      <Row icon="☀️" label="出勤"   value={punchIn}                              color="#F472B6" />
      <Row icon="🌙" label="退勤"   value={punchOut}                             color="#A78BFA" />
      <Row icon="☕" label="休憩"   value={breakMin != null ? `${breakMin} min` : null} color="#FBBF24" />
      <Row icon="⚡" label="実稼働" value={jissabaki}                            color="#34D399" />
    </div>
  );
}

// ---- カレンダー ----
function MiniCalendar() {
  const today = new Date();
  const [year, setYear]   = useState(today.getFullYear());
  const [month, setMonth] = useState(today.getMonth());
  const firstDay    = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const prevLast    = new Date(year, month, 0).getDate();
  const DAYS = ["日","月","火","水","木","金","土"];

  const cells = [];
  for (let i = 0; i < firstDay; i++)     cells.push({ d: prevLast - firstDay + 1 + i, cur: false });
  for (let d = 1; d <= daysInMonth; d++) cells.push({ d, cur: true });
  while (cells.length % 7 !== 0)         cells.push({ d: cells.length - daysInMonth - firstDay + 1, cur: false });

  const isToday = c => c.cur && c.d === today.getDate() && month === today.getMonth() && year === today.getFullYear();
  const prevM = () => month === 0  ? (setYear(y=>y-1), setMonth(11)) : setMonth(m=>m-1);
  const nextM = () => month === 11 ? (setYear(y=>y+1), setMonth(0))  : setMonth(m=>m+1);

  return (
    <div className="bg-white/80 border border-white shadow-sm flex flex-col h-full"
      style={{ borderRadius: "1.2vw", padding: "0.8vw 0.9vw" }}>
      <div className="flex items-center justify-between mb-1">
        <div className="flex items-center gap-1">
          <span style={{ fontSize: "0.85vw" }}>📅</span>
          <span className="font-black text-purple-800" style={{ fontSize: "0.75vw" }}>{year}年{month+1}月</span>
        </div>
        <div className="flex items-center gap-0.5 bg-purple-50 rounded-full px-1 border border-purple-100">
          <button onClick={prevM} className="w-4 h-4 flex items-center justify-center text-purple-400 hover:text-purple-600 font-bold text-xs">‹</button>
          <button onClick={nextM} className="w-4 h-4 flex items-center justify-center text-purple-400 hover:text-purple-600 font-bold text-xs">›</button>
        </div>
      </div>
      <div className="grid grid-cols-7">
        {DAYS.map((d,i) => (
          <div key={d} className={`text-center font-bold ${i===0?"text-red-400":i===6?"text-blue-400":"text-gray-400"}`}
            style={{ fontSize: "0.6vw" }}>{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-y-0.5 mt-0.5 flex-1">
        {cells.map((c,i) => {
          const col = i % 7;
          const tod = isToday(c);
          return (
            <div key={i} className="flex items-center justify-center">
              <span className={`w-4 h-4 flex items-center justify-center rounded-full font-medium
                ${tod ? "bg-pink-400 text-white font-black shadow" : ""}
                ${!tod && c.cur && col===0 ? "text-red-400" : ""}
                ${!tod && c.cur && col===6 ? "text-blue-400" : ""}
                ${!tod && c.cur && col!==0 && col!==6 ? "text-gray-700" : ""}
                ${!c.cur ? "text-gray-300" : ""}
              `} style={{ fontSize: "0.6vw" }}>{c.d}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

const EMPTY_WEEK = WEEK_DAYS.map(() => ({ hours: 0 }));

// ---- メインアプリ ----
export default function App() {
  const [pipponX, setPipponX]     = useState(20);
  const [pipponDir, setPipponDir] = useState(1);
  const [toast, setToast]         = useState(null);
  const [breakMin, setBreakMin]   = useState(60);
  const [staffList, setStaffList] = useState([]);
  const [selectedName, setSelectedName] = useState("");
  const [todayRec, setTodayRec]   = useState({ punch_in: "", punch_out: "", break_min: 60, jissabaki: "" });
  const [weekData, setWeekData]   = useState(EMPTY_WEEK);
  const [saving, setSaving] = useState(false);
  const [now, setNow]       = useState(new Date());
  const toastTimer = useRef(null);
  const mood       = MOODS[new Date().getDay()];
  const dailyQuote = DAILY_QUOTES[new Date().getDate() % DAILY_QUOTES.length];

  // 時計（毎秒更新）
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000);
    return () => clearInterval(id);
  }, []);

  // ぴぽん移動
  useEffect(() => {
    const id = setInterval(() => {
      setPipponX(prev => {
        const next = prev + mood.moveStep * pipponDir;
        if (next >= 80) { setPipponDir(-1); return 80; }
        if (next <= 2)  { setPipponDir(1);  return 2;  }
        return next;
      });
    }, mood.moveInterval);
    return () => clearInterval(id);
  }, [pipponDir, mood]);

  // スタッフリスト取得
  useEffect(() => {
    fetch("/api/staff")
      .then(r => r.json())
      .then(data => {
        if (data.names && data.names.length > 0) {
          setStaffList(data.names);
          setSelectedName(data.names[0]);
        }
      })
      .catch(() => {});
  }, []);

  // 名前が変わったら記録・週データ取得
  useEffect(() => {
    if (!selectedName) return;
    fetch(`/api/record?name=${encodeURIComponent(selectedName)}&date=${todayStr()}`)
      .then(r => r.json())
      .then(data => {
        if (!data.error) setTodayRec(data);
      })
      .catch(() => {});
    fetch(`/api/weekly?name=${encodeURIComponent(selectedName)}`)
      .then(r => r.json())
      .then(data => {
        if (data.week) setWeekData(data.week);
      })
      .catch(() => {});
  }, [selectedName]);

  const showToast = (msg, type) => {
    clearTimeout(toastTimer.current);
    setToast({ msg, type });
    toastTimer.current = setTimeout(() => setToast(null), 4000);
  };

  const handlePunchIn = async () => {
    if (!selectedName || saving) return;
    const time = currentHHMM();
    setSaving(true);
    try {
      const res = await fetch("/api/punch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: selectedName, type: "in", time, break_min: breakMin }),
      });
      const data = await res.json();
      if (data.ok) {
        setTodayRec(prev => ({ ...prev, punch_in: data.punch_in, break_min: breakMin }));
        showToast(PUNCH_IN_MSGS[Math.floor(Math.random() * PUNCH_IN_MSGS.length)], "in");
      }
    } catch(e) {
      showToast("通信エラー。もう一度試してね", "err");
    } finally {
      setSaving(false);
    }
  };

  const handlePunchOut = async () => {
    if (!selectedName || saving) return;
    const time = currentHHMM();
    setSaving(true);
    try {
      const res = await fetch("/api/punch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: selectedName, type: "out", time, break_min: breakMin }),
      });
      const data = await res.json();
      if (data.ok) {
        // Refresh today's record (to get jissabaki from server)
        const rec = await fetch(`/api/record?name=${encodeURIComponent(selectedName)}&date=${todayStr()}`).then(r=>r.json());
        if (!rec.error) setTodayRec(rec);
        // Refresh weekly
        const wk = await fetch(`/api/weekly?name=${encodeURIComponent(selectedName)}`).then(r=>r.json());
        if (wk.week) setWeekData(wk.week);
        showToast(PUNCH_OUT_MSGS[Math.floor(Math.random() * PUNCH_OUT_MSGS.length)], "out");
      }
    } catch(e) {
      showToast("通信エラー。もう一度試してね", "err");
    } finally {
      setSaving(false);
    }
  };

  const displayPunchIn  = fmtTime(todayRec.punch_in);
  const displayPunchOut = fmtTime(todayRec.punch_out);
  const displayBreak    = todayRec.break_min != null ? Number(todayRec.break_min) : breakMin;
  const displayJissa    = todayRec.jissabaki || null;

  return (
    <div className="w-screen h-screen bg-gradient-to-br from-[#F3E8FF] via-[#FBF0FF] to-[#FFE8F5] flex items-center justify-center overflow-hidden">
      <div
        className="bg-white/40 backdrop-blur-2xl border border-white/80 shadow-[0_20px_70px_rgba(160,100,230,0.22)] flex flex-col"
        style={{
          width: "min(95vw, calc(95vh * 4 / 3))",
          height: "min(95vh, calc(95vw * 3 / 4))",
          borderRadius: "2.5vw",
          padding: "2vw",
          gap: "1vw",
        }}
      >
        <div className="flex flex-1 min-h-0" style={{ gap: "2vw" }}>

          {/* ===== 左: 時計 + ぴぽん ===== */}
          <div className="flex flex-col items-center flex-shrink-0" style={{ width: "22%" }}>
            {/* 時計（画像 + SVG針） */}
            <div className="relative w-full flex-shrink-0" style={{ maxHeight: "42%" }}>
              <img src={clockImg} alt="clock" className="w-full object-contain drop-shadow-xl" />
              {/* SVG針オーバーレイ：clock.pngの文字盤中心 ≈ 50% / 50% */}
              <svg className="absolute inset-0 w-full h-full" viewBox="0 0 315 305" style={{ pointerEvents: "none" }}>
                {(() => {
                  const h = now.getHours() % 12, m = now.getMinutes(), s = now.getSeconds();
                  const cx = 157, cy = 152;
                  const hAngle = (h * 30 + m * 0.5 + s * (0.5/60)) - 90;
                  const mAngle = (m * 6 + s * 0.1) - 90;
                  const sAngle = s * 6 - 90;
                  const hand = (angle, len, w, color) => {
                    const rad = angle * Math.PI / 180;
                    return { x2: cx + Math.cos(rad) * len, y2: cy + Math.sin(rad) * len, w, color };
                  };
                  const hd = hand(hAngle, 62, 5, "#A78BFA");
                  const md = hand(mAngle, 88, 3.5, "#F472B6");
                  const sd = hand(sAngle, 92, 1.5, "#EF4444");
                  return <>
                    {[hd, md, sd].map((d, i) => (
                      <line key={i} x1={cx} y1={cy} x2={d.x2} y2={d.y2}
                        stroke={d.color} strokeWidth={d.w} strokeLinecap="round" />
                    ))}
                    <circle cx={cx} cy={cy} r={5} fill="#A78BFA" />
                    <circle cx={cx} cy={cy} r={2} fill="white" />
                  </>;
                })()}
              </svg>
            </div>
            {/* デジタル時刻（時計の下） */}
            <div className="flex flex-col items-center leading-none" style={{ marginTop: "0.3vw" }}>
              <span className="font-black text-purple-700 tabular-nums" style={{ fontSize: "1.8vw" }}>
                {String(now.getHours()).padStart(2,"0")}:{String(now.getMinutes()).padStart(2,"0")}
              </span>
              <span className="font-medium text-purple-300" style={{ fontSize: "0.62vw", marginTop: "0.1vw" }}>
                {now.toLocaleDateString("ja-JP",{month:"numeric",day:"numeric",weekday:"short"})}
              </span>
            </div>

            {/* メッセージ帯 */}
            <div className="w-full flex items-center justify-center" style={{ minHeight: "2.4vw" }}>
              {toast && (
                <div className="animate-speech w-full text-center font-bold"
                  style={{
                    borderRadius: "999px", padding: "0.5vw 1vw", fontSize: "0.82vw",
                    background: toast.type === "in"
                      ? "linear-gradient(135deg,#FFD6E8,#FFB3D1)"
                      : toast.type === "out"
                      ? "linear-gradient(135deg,#E8D6FF,#C9B3FF)"
                      : "linear-gradient(135deg,#FFE8D6,#FFCBA3)",
                    color: toast.type === "in" ? "#b0275f" : toast.type === "out" ? "#5b27b0" : "#a05000",
                    border: toast.type === "in" ? "1px solid #f9a8d4" : toast.type === "out" ? "1px solid #c4b5fd" : "1px solid #fcd9a8",
                    boxShadow: "0 4px 14px rgba(160,80,220,0.15)",
                  }}>
                  {toast.type === "in" ? "☀️" : toast.type === "out" ? "🌙" : "⚠️"} {toast.msg}
                </div>
              )}
            </div>

            {/* ぴぽんステージ */}
            <div className="relative w-full flex-1">
              <div className="absolute bottom-0 left-2 right-2 h-px bg-gradient-to-r from-transparent via-purple-200/50 to-transparent" />
              <div className="absolute top-0 left-1 text-[0.65vw] text-purple-300 font-bold select-none">{mood.tag}</div>
              <div className="absolute bottom-1"
                style={{ left: `${pipponX}%`, transform: "translateX(-50%)", transition: "left 55ms linear" }}>
                <div className="absolute bottom-0 left-1/2 -translate-x-1/2 rounded-full blur-sm"
                  style={{ width: "4vw", height: "0.7vw", background: "radial-gradient(ellipse, rgba(120,50,180,0.2) 0%, transparent 70%)" }} />
                <div style={{ transform: `scaleX(${pipponDir})` }}>
                  <img src={cidleImg} alt="pippon" draggable={false} className="select-none walk-bob"
                    style={{ width: "6vw", height: "6vw", objectFit: "contain", "--walk-dur": "1.4s" }} />
                </div>
              </div>
            </div>
          </div>

          {/* ===== 右: コントロール ===== */}
          <div className="flex flex-col flex-1 min-w-0 min-h-0" style={{ gap: "0.8vw" }}>

            {/* スタッフ選択 */}
            <StaffPicker value={selectedName} onChange={setSelectedName} names={staffList} />

            {/* 打刻ボタン */}
            <div className="flex" style={{ gap: "1vw" }}>
              <button onClick={handlePunchIn} disabled={saving || !selectedName}
                className="flex-1 hover:scale-105 active:scale-95 transition-transform duration-150 focus:outline-none disabled:opacity-50 disabled:scale-100">
                <img src={punchInImg} alt="出勤する" className="w-full h-auto block drop-shadow-md" style={{ borderRadius: "1vw" }} />
              </button>
              <button onClick={handlePunchOut} disabled={saving || !selectedName}
                className="flex-1 hover:scale-105 active:scale-95 transition-transform duration-150 focus:outline-none disabled:opacity-50 disabled:scale-100">
                <img src={punchOutImg} alt="退勤する" className="w-full h-auto block drop-shadow-md" style={{ borderRadius: "1vw" }} />
              </button>
            </div>

            {/* 休憩スライダー */}
            <div className="bg-white/75 border border-white shadow-sm flex-shrink-0"
              style={{ borderRadius: "1.2vw", padding: "0.65vw 1.1vw" }}>
              <div className="flex items-center" style={{ gap: "0.5vw", marginBottom: "0.35vw" }}>
                <span style={{ fontSize: "0.9vw" }}>☕</span>
                <span className="font-bold text-purple-500" style={{ fontSize: "0.75vw" }}>休憩時間（分）</span>
              </div>
              <div className="flex items-center" style={{ gap: "1vw" }}>
                <input type="range" min="0" max="120" value={breakMin}
                  onChange={e => setBreakMin(Number(e.target.value))}
                  className="flex-1 cursor-pointer" />
                <span className="text-purple-800 font-black" style={{ fontSize: "1.05vw", minWidth: "3.5vw", textAlign: "right" }}>
                  {breakMin} <span className="text-purple-400 font-normal" style={{ fontSize: "0.7vw" }}>min</span>
                </span>
              </div>
            </div>

            {/* 下段3列：今週の記録 / 本日の記録 / カレンダー */}
            <div className="flex flex-1 min-h-0" style={{ gap: "0.8vw" }}>
              <div className="flex-1 min-w-0 min-h-0"><WeeklyChart weekData={weekData} /></div>
              <div className="flex-1 min-w-0 min-h-0">
                <TodayRecord
                  punchIn={displayPunchIn}
                  punchOut={displayPunchOut}
                  breakMin={displayBreak}
                  jissabaki={displayJissa}
                />
              </div>
              <div className="flex-1 min-w-0 min-h-0"><MiniCalendar /></div>
            </div>
          </div>
        </div>

        {/* フッター */}
        <div className="flex items-center justify-center gap-1.5 flex-shrink-0">
          <span className="text-pink-300" style={{ fontSize: "0.8vw" }}>💬</span>
          <p className="text-purple-400 font-bold tracking-wide select-none" style={{ fontSize: "0.72vw" }}>
            {dailyQuote}
          </p>
        </div>
      </div>
    </div>
  );
}
