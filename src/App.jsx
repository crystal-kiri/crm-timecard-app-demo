import React, { useState, useEffect } from 'react';

function App() {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen flex items-center justify-center relative p-4 bg-[#F2E9FB] overflow-hidden">
      {/* 夢の中のような背景の光の玉 */}
      <div className="absolute top-[-20%] left-[-10%] w-[600px] h-[600px] bg-[#FFD6EA] rounded-full blur-[120px] opacity-70 animate-pulse" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[700px] h-[700px] bg-[#DBCBFF] rounded-full blur-[150px] opacity-70" />

      {/* メインの巨大な浮き島パネル */}
      <div className="relative z-10 w-full max-w-5xl bg-white/40 backdrop-blur-[40px] rounded-[80px] border-[6px] border-white/80 shadow-[0_50px_100px_-20px_rgba(180,160,230,0.4)] p-12 md:p-20 flex flex-col items-center">
        
        <div className="w-full max-w-3xl flex flex-col md:flex-row gap-16 items-center">
          
          {/* 左：時計ユニット（もっと丸く、もっと立体的に） */}
          <div className="relative flex-1 group">
            <div className="w-[320px] h-[320px] bg-white rounded-[100px] shadow-[20px_20px_60px_rgba(180,160,220,0.3),inset_-10px_-10px_20px_rgba(0,0,0,0.02),inset_10px_10px_20px_rgba(255,255,255,0.9)] flex flex-col items-center justify-center border-[10px] border-[#FDF2FF]">
              {/* 時計のアイコン（ここは本来3Dモデルを置きたい場所） */}
              <div className="text-8xl mb-4 drop-shadow-xl">🕒</div>
              <div className="text-6xl font-[900] text-[#5E5674] tracking-tight">
                {time.toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit' })}
              </div>
              <div className="text-[#A095B1] font-bold text-xl mt-2 tracking-widest uppercase">
                {time.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' })}
              </div>
            </div>
          </div>

          {/* 右：コントロールパネル */}
          <div className="flex-[1.2] w-full space-y-10">
            {/* ユーザー選択（もっとぷっくり） */}
            <div className="relative">
              <select className="w-full bg-white/80 backdrop-blur-md border-none rounded-[35px] py-6 px-10 text-2xl font-black text-[#8A7FB1] shadow-[10px_10px_30px_rgba(0,0,0,0.03),inset_4px_4px_10px_rgba(255,255,255,0.8)] outline-none appearance-none cursor-pointer">
                <option>yurika kiriyama</option>
              </select>
              <div className="absolute right-8 top-1/2 -translate-y-1/2 pointer-events-none text-[#8A7FB1] text-2xl">▼</div>
            </div>

            {/* 打刻ボタン（ここが一番大事：画像のグロス感を再現） */}
            <div className="grid grid-cols-2 gap-8">
              {/* 出勤ボタン：ピンクの飴細工 */}
              <button className="relative h-32 group">
                <div className="absolute inset-0 bg-gradient-to-br from-[#FFB7D9] to-[#FF6B9D] rounded-[40px] border-[5px] border-white shadow-[0_15px_35px_rgba(255,107,157,0.4)] transition-all group-active:translate-y-2 group-active:shadow-none" />
                <div className="absolute inset-0 bg-gradient-to-b from-white/40 to-transparent rounded-[40px] opacity-50" /> {/* ハイライト（光沢） */}
                <span className="relative z-10 text-white text-3xl font-black tracking-widest drop-shadow-md">出勤</span>
              </button>

              {/* 退勤ボタン：紫の飴細工 */}
              <button className="relative h-32 group">
                <div className="absolute inset-0 bg-gradient-to-br from-[#D4C1FF] to-[#9D7BFF] rounded-[40px] border-[5px] border-white shadow-[0_15px_35px_rgba(157,123,255,0.4)] transition-all group-active:translate-y-2 group-active:shadow-none" />
                <div className="absolute inset-0 bg-gradient-to-b from-white/30 to-transparent rounded-[40px] opacity-50" /> {/* ハイライト（光沢） */}
                <span className="relative z-10 text-white text-3xl font-black tracking-widest drop-shadow-md">退勤</span>
              </button>
            </div>

            {/* 休憩スライダー（おもちゃのような質感） */}
            <div className="bg-white/40 p-8 rounded-[40px] shadow-inner border-2 border-white/50">
               <div className="flex justify-between items-end mb-4">
                 <span className="text-[#8A7FB1] text-xl font-black">BREAK TIME</span>
                 <span className="text-3xl font-black text-[#FF6B9D]">60<span className="text-sm ml-1">min</span></span>
               </div>
               <div className="relative h-10 w-full bg-white/80 rounded-full border-4 border-white shadow-inner flex items-center px-1">
                 <div className="h-5 w-[50%] bg-gradient-to-r from-[#FFD600] via-[#FF00E5] to-[#00D1FF] rounded-full shadow-sm" />
                 <div className="absolute left-[50%] w-10 h-10 bg-white border-4 border-[#FFB7D9] rounded-full shadow-md -translate-x-1/2" />
               </div>
            </div>
          </div>
        </div>
        
        {/* フッターアイコンも大きく、もっと「おもちゃ」っぽく */}
        <div className="mt-20 w-full flex justify-around opacity-40 grayscale hover:grayscale-0 transition-all">
          <div className="text-5xl cursor-pointer hover:scale-125 transition-transform">☁️</div>
          <div className="text-5xl cursor-pointer hover:scale-125 transition-transform">📊</div>
          <div className="text-5xl cursor-pointer hover:scale-125 transition-transform">⚙️</div>
        </div>
      </div>
    </div>
  );
}

export default App;